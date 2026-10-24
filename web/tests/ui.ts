/**
 * Browser checks on the built site, in the installed Microsoft Edge:
 * pages load, diagram lines are straight, link labels are clear, SVG
 * exports are plain valid SVG, and phone width has no sideways scroll.
 *
 * Run after `npm run build`: `npm run test:ui`. Local only (CI has no Edge).
 * Exits 1 and lists every failure.
 */
import { readFileSync } from 'node:fs'
import {
  chromium,
  type Browser,
  type Page,
  type Route,
} from 'playwright-core'
import { preview } from 'vite'

const PORT = 4174
const BASE = `http://localhost:${PORT}/AeroOptix-Horizon/#/`

const failures: string[] = []
const fail = (where: string, msg: string) => failures.push(`${where}: ${msg}`)
const fontWarnings = new Set<string>()

/**
 * Google Fonts, fetched once per run and then served from memory: each new
 * browser context would fetch them again, and repeated fetches get slow.
 */
const FONTS = /^https:\/\/fonts\.(googleapis|gstatic)\.com\//
const fontCache = new Map<
  string,
  { status: number; headers: Record<string, string>; body: Buffer }
>()
async function serveFont(route: Route) {
  const url = route.request().url()
  let hit = fontCache.get(url)
  if (!hit) {
    try {
      const res = await route.fetch()
      hit = {
        status: res.status(),
        headers: res.headers(),
        body: await res.body(),
      }
      fontCache.set(url, hit)
    } catch {
      return route.abort()
    }
  }
  return route.fulfill(hit)
}

async function open(
  browser: Browser,
  route: string,
  opts: { width?: number; theme?: 'dark' | 'light' } = {}
) {
  const ctx = await browser.newContext({
    viewport: { width: opts.width ?? 1440, height: 900 },
    acceptDownloads: true,
  })
  if (opts.theme)
    await ctx.addCookies([
      {
        name: 'vite-ui-theme',
        value: opts.theme,
        url: `http://localhost:${PORT}`,
      },
    ])
  // tsx compiles the page-side functions with esbuild's __name helper
  await ctx.addInitScript('window.__name = (f) => f')
  await ctx.route(FONTS, serveFont)
  const page = await ctx.newPage()
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  // Google Fonts can be slow to load or never load: wait for the page's own
  // content, then give the fonts a while, since label widths depend on them
  await page.goto(BASE + route, { waitUntil: 'domcontentloaded' })
  const canvas = route.startsWith('diagram') && !route.includes('link=')
  await page.waitForSelector(canvas ? '.react-flow__edge path[id]' : 'main', {
    state: 'attached',
  })
  const fonts = await page.evaluate(() =>
    Promise.race([
      document.fonts.ready.then(() => true),
      new Promise<boolean>((done) => setTimeout(() => done(false), 10000)),
    ])
  )
  if (!fonts) fontWarnings.add(route)
  // a diagram view fits itself to the canvas with a short animation
  await page.waitForTimeout(canvas ? 800 : 300)
  return { page, errors, close: () => ctx.close() }
}

/** Every edge path is one straight line (within 0.5 px). */
async function straightLines(page: Page, where: string) {
  const bent = await page.evaluate(() =>
    [...document.querySelectorAll('.react-flow__edge path[id]')]
      .map((el) => {
        const n = el.getAttribute('d')!.match(/-?\d+(\.\d+)?/g)!.map(Number)
        const xs = n.filter((_, i) => i % 2 === 0)
        const ys = n.filter((_, i) => i % 2 === 1)
        const dx = Math.max(...xs) - Math.min(...xs)
        const dy = Math.max(...ys) - Math.min(...ys)
        return { id: el.id, off: Math.min(dx, dy) }
      })
      .filter((e) => e.off > 0.5)
  )
  for (const e of bent) fail(where, `link ${e.id} is bent by ${e.off} px`)
}

/** No link label covers a block, another label or a line other than its own. */
async function clearLabels(page: Page, where: string) {
  const hits = await page.evaluate(() => {
    type Box = { name: string; l: number; t: number; r: number; b: number }
    const box = (e: Element, name: string, grow = 0): Box => {
      const x = e.getBoundingClientRect()
      return {
        name,
        l: x.left - grow,
        t: x.top - grow,
        r: x.right + grow,
        b: x.bottom + grow,
      }
    }
    const hit = (a: Box, c: Box, m = 0) =>
      a.l < c.r - m && c.l < a.r - m && a.t < c.b - m && c.t < a.b - m
    const q = (s: string) => [...document.querySelectorAll(s)]
    const labels = q('.react-flow__edgelabel-renderer > div').map((e) =>
      box(e, `label "${e.textContent}"`)
    )
    const nodes = q('.react-flow__node').map((e) =>
      box(e, `block ${(e as HTMLElement).dataset.id}`)
    )
    const lines = q('.react-flow__edge path[id]').map((e) =>
      box(e, `line ${e.id}`, 1)
    )
    const out: string[] = []
    labels.forEach((a, i) => {
      const cx = (a.l + a.r) / 2
      const cy = (a.t + a.b) / 2
      const own = lines.find(
        (e) => cx >= e.l - 1 && cx <= e.r + 1 && cy >= e.t - 1 && cy <= e.b + 1
      )
      for (const c of labels.slice(i + 1))
        if (hit(a, c)) out.push(`${a.name} covers ${c.name}`)
      for (const n of nodes)
        if (hit(a, n, -2)) out.push(`${a.name} covers ${n.name}`)
      for (const e of lines)
        if (e !== own && hit(a, e)) out.push(`${a.name} covers ${e.name}`)
    })
    return out
  })
  for (const h of hits) fail(where, h)
}

async function noSideScroll(page: Page, where: string) {
  const [sw, w] = await page.evaluate(() => [
    document.documentElement.scrollWidth,
    window.innerWidth,
  ])
  if (sw > w) fail(where, `scrolls sideways (${sw} px wide at ${w} px)`)
}

/** Click an export button; the file must be valid SVG with plain colours. */
async function svgExport(page: Page, button: string, where: string) {
  const download = page.waitForEvent('download', { timeout: 15000 })
  await page.getByRole('button', { name: button, exact: true }).click()
  const file = await (await download).path()
  const svg = readFileSync(file, 'utf8')
  const parseError = await page.evaluate(
    (s) =>
      new DOMParser()
        .parseFromString(s, 'image/svg+xml')
        .querySelector('parsererror')?.textContent ?? null,
    svg
  )
  if (parseError) fail(where, `export is not valid XML: ${parseError}`)
  const css = svg.match(/var\(|color-mix|oklab|class="/)
  if (css) fail(where, `export still has CSS: ${css[0]}`)
}

async function main() {
  process.env.VITE_CONFIG_NATIVE_IGNORE_WARNING = 'true'
  const server = await preview({
    preview: { port: PORT, strictPort: true, open: false },
    logLevel: 'warn',
  })
  const browser = await chromium.launch({ channel: 'msedge' })
  try {
    // pages load without errors
    for (const route of [
      '',
      'diagram?level=system',
      'diagram?level=board',
      'diagram?level=board&link=b-link',
      'pinout?mcu=h743',
      'pinout?mcu=f100',
    ]) {
      const v = await open(browser, route)
      for (const e of v.errors) fail(`/${route}`, `page error: ${e}`)
      await v.close()
    }

    // diagram drawing, with nothing and with a block selected
    for (const route of [
      'diagram?level=system',
      'diagram?level=board',
      'diagram?level=system&block=servos',
      'diagram?level=system&block=gps',
      'diagram?level=board&block=f100',
      'diagram?level=board&block=h743',
      'diagram?level=board&block=j-servo',
    ]) {
      const v = await open(browser, route)
      await straightLines(v.page, `/${route}`)
      await clearLabels(v.page, `/${route}`)
      await v.close()
    }

    // SVG export, both themes
    for (const theme of ['dark', 'light'] as const)
      for (const [route, button] of [
        ['diagram?level=system', 'Export SVG'],
        ['diagram?level=board', 'Export SVG'],
        ['pinout?mcu=h743', 'SVG'],
        ['pinout?mcu=f100', 'SVG'],
      ]) {
        const v = await open(browser, route, { theme })
        await svgExport(v.page, button, `/${route} ${theme} export`)
        await v.close()
      }

    // phone width
    for (const route of ['', 'diagram?level=board', 'pinout?mcu=h743']) {
      const v = await open(browser, route, { width: 390 })
      await noSideScroll(v.page, `/${route} at 390 px`)
      await v.close()
    }
  } finally {
    await browser.close()
    await server.close()
  }

  if (fontWarnings.size)
    console.warn(
      `test:ui: web fonts did not load on ${fontWarnings.size} page(s); ` +
        'label checks ran with fallback fonts'
    )
  if (failures.length) {
    console.error(`test:ui: ${failures.length} failure(s)`)
    for (const f of failures) console.error(`  - ${f}`)
    process.exit(1)
  }
  console.log('test:ui: OK')
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
