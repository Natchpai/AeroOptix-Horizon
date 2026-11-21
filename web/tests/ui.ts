/**
 * Browser checks on the built site, in the installed Microsoft Edge (in CI,
 * Playwright's bundled Chromium):
 * pages load, diagram lines are straight, link labels are clear, SVG
 * exports are plain valid SVG, phone width has no sideways scroll and opens
 * diagrams at a readable zoom, the light theme passes the same checks, and
 * a hash link changed in an open tab shows the new view, and Ctrl+K on a
 * decision or an open item (open or closed) opens its row on its page,
 * a next-action task chip opens its Checklist row, and an Overview
 * revision chip opens its Spec history row, the Power budget page
 * draws one bar per Rail summary row, every Decisions Date cell holds
 * its text inside the cell, every page has its own browser tab title, and
 * the diagram view tabs fit at phone width.
 *
 * Run after `npm run build`: `npm run test:ui`. Set UI_BROWSER to pick a
 * Playwright channel (default `msedge` locally; `chromium` when CI is set).
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
    const nodes = q('.react-flow__node-block').map((e) =>
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

/** The diagram view tabs fit inside their row and the viewport. */
async function viewTabsFit(page: Page, where: string) {
  const out = await page.evaluate(() => {
    const tabs = document.querySelector('[data-view-tabs]')
    if (!tabs) return ['no view tabs']
    const edge = Math.min(
      window.innerWidth,
      tabs.parentElement!.getBoundingClientRect().right
    )
    return [...tabs.querySelectorAll('button')]
      .map((b) => ({ name: b.textContent, right: b.getBoundingClientRect().right }))
      .filter((b) => b.right > edge + 0.5)
      .map((b) => `tab "${b.name}" ends at ${b.right} px, past ${edge} px`)
  })
  for (const o of out) fail(where, o)
}

/** At phone width a diagram opens at a readable zoom (canvas.tsx READABLE). */
async function readableZoom(page: Page, where: string) {
  const zoom = await page.evaluate(() => {
    const t = getComputedStyle(
      document.querySelector('.react-flow__viewport')!
    ).transform
    return Number(t.match(/matrix\(([^,]+)/)?.[1] ?? 1)
  })
  if (zoom < 0.34) fail(where, `opens at zoom ${zoom.toFixed(2)}, below 0.35`)
}

/**
 * Same-tab links: change the hash in an open tab, as pasting a URL does, and
 * check that the page shows the new view, not the old one.
 */
async function sameTabLinks(browser: Browser) {
  const v = await open(browser, 'diagram?level=system')
  const go = async (hash: string) => {
    await v.page.evaluate((h) => {
      location.hash = h
    }, hash)
    await v.page.waitForTimeout(1200)
  }
  const state = () =>
    v.page.evaluate(() => ({
      blocks: [...document.querySelectorAll('.react-flow__node-block')].map(
        (e) => (e as HTMLElement).dataset.id
      ),
      selected: [...document.querySelectorAll('.react-flow__node.selected')].map(
        (e) => (e as HTMLElement).dataset.id
      ),
      pinRow:
        document.querySelector('tr[data-state=selected]')?.textContent ?? '',
      text: document.querySelector('main')?.textContent ?? '',
    }))
  const where = 'same-tab link'

  await go('#/diagram?level=board&block=h743')
  let s = await state()
  if (!s.blocks.includes('j-gps') || s.blocks.includes('fc'))
    fail(where, 'level=board did not replace the Overview')
  if (!s.selected.includes('h743')) fail(where, 'block=h743 is not selected')

  await go('#/diagram?level=power')
  s = await state()
  if (!s.blocks.includes('pw-r5v') || s.blocks.includes('j-gps'))
    fail(where, 'level=power did not replace the System view')
  if (s.selected.length) fail(where, `power view keeps a selection: ${s.selected}`)

  await go('#/pinout?mcu=f100&pin=PA8')
  s = await state()
  if (!s.text.includes('LQFP48')) fail(where, 'mcu=f100 did not open the F100 pinout')
  if (!s.pinRow.includes('PA8')) fail(where, 'pin=PA8 is not the selected row')

  for (const e of v.errors) fail(where, `page error: ${e}`)
  await v.close()
}

/**
 * Ctrl+K on an ID opens its row on the site page, in the same tab. `item`
 * is the start of the result text, `row` the id of the row it must select.
 */
async function searchOpensRow(
  browser: Browser,
  id: string,
  page: string,
  group = 'Spec IDs',
  item = id,
  row = `row-${id}`
) {
  const where = `Ctrl+K ${id}`
  const v = await open(browser, '')
  await v.page.keyboard.press('Control+k')
  await v.page.getByPlaceholder(/Search pins/).fill(id)
  await v.page.waitForTimeout(300)
  // Links and pins citing the ID can rank above it, so pick the result in
  // its group instead of pressing Enter on the top hit.
  const escaped = item.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  // a bare ID must not match a longer one; other items end in other text
  const end = item === id ? '(?![\\d])' : ''
  await v.page
    .locator('[cmdk-group]')
    .filter({ hasText: group })
    .locator('[cmdk-item]')
    .filter({ hasText: new RegExp(`^${escaped}${end}`) })
    .first()
    .click()
  await v.page.waitForTimeout(1000)
  const [hash, selected] = await v.page.evaluate(() => [
    location.hash,
    document.querySelector('tr[data-state=selected]')?.id ?? '',
  ])
  if (!hash.includes(page)) fail(where, `went to ${hash || 'nowhere'}`)
  if (selected !== row) fail(where, `selected row is "${selected}"`)
  for (const e of v.errors) fail(where, `page error: ${e}`)
  await v.close()
}

/** A task chip in the Overview next action opens its row on the Checklist. */
async function taskChipOpensRow(browser: Browser) {
  const where = 'next-action task chip'
  const v = await open(browser, '')
  const chip = v.page.locator('a[href*="checklist?id=P"]').first()
  const id = ((await chip.textContent()) ?? '').trim()
  if (!/^P\d-\d{3}$/.test(id)) fail(where, `no task chip found ("${id}")`)
  await chip.click()
  await v.page.waitForTimeout(1000)
  const [hash, row] = await v.page.evaluate(() => [
    location.hash,
    document.querySelector('tr[data-state=selected]')?.id ?? '',
  ])
  if (!hash.includes('checklist') || !hash.includes(id))
    fail(where, `went to ${hash || 'nowhere'}`)
  if (row !== `row-${id}`) fail(where, `selected row is "${row}"`)
  for (const e of v.errors) fail(where, `page error: ${e}`)
  await v.close()
}

/**
 * An ID chip opens its row on the site page: DEC on Decisions, OPEN on Open
 * items, a requirement on Traceability. In a closed Spec history row a chip
 * click opens the row instead.
 */
async function chipsOpenSitePages(browser: Browser) {
  const where = 'ID chip'
  const v = await open(browser, 'history?rev=0.86')
  const selected = () =>
    v.page.evaluate(() => [
      location.hash,
      document.querySelector('tr[data-state=selected]')?.id ?? '',
    ])
  for (const [id, page] of [
    ['DEC-106', 'decisions'],
    ['OPEN-031', 'open'],
    ['IF-048', 'trace'],
  ] as const) {
    await v.page.evaluate(() => {
      location.hash = '#/history?rev=%220.86%22'
    })
    await v.page.waitForTimeout(800)
    await v.page
      .locator('tr[data-state=selected] a', { hasText: new RegExp(`^${id}$`) })
      .first()
      .click()
    await v.page.waitForTimeout(1000)
    const [hash, row] = await selected()
    if (!hash.includes(`/${page}`) || !hash.includes(id))
      fail(where, `${id} went to ${hash}`)
    if (row !== `row-${id}`) fail(where, `${id}: selected row is "${row}"`)
  }
  // a chip in a closed history row opens that row, not the chip's page
  await v.page.evaluate(() => {
    location.hash = '#/history'
  })
  await v.page.waitForTimeout(800)
  await v.page.locator('#rev-0\\.85 a', { hasText: /^DEC-/ }).first().click()
  await v.page.waitForTimeout(800)
  const [hash, row] = await selected()
  if (!hash.includes('history') || row !== 'rev-0.85')
    fail(where, `closed-row chip went to ${hash}, row "${row}"`)
  for (const e of v.errors) fail(where, `page error: ${e}`)
  await v.close()
}

/** In an opened table row every cell is top-aligned, so the ID stays at the top. */
async function openRowTopAligned(browser: Browser) {
  for (const route of [
    'decisions?id=DEC-050',
    'open?id=OPEN-023',
    'checklist?id=P3-007',
    'history?rev=0.86',
    'trace?id=IF-010',
  ]) {
    const where = `/${route} cell alignment`
    const v = await open(browser, route)
    const bad = await v.page.evaluate(() => {
      const row = document.querySelector('tr[data-state=selected]')
      if (!row) return ['no selected row']
      return [...row.querySelectorAll('td')]
        .map((td, i) => [i, getComputedStyle(td).verticalAlign] as const)
        .filter(([, a]) => a !== 'top')
        .map(([i, a]) => `cell ${i} is ${a}`)
    })
    for (const b of bad) fail(where, b)
    for (const e of v.errors) fail(where, `page error: ${e}`)
    await v.close()
  }
}

/** The Power budget page draws one bar per Rail summary row, in both themes. */
async function powerBars(browser: Browser) {
  const summary = JSON.parse(
    readFileSync(
      new URL('../src/data/generated/power.json', import.meta.url),
      'utf8'
    )
  ).summary as { rail: string }[]
  for (const theme of ['dark', 'light'] as const) {
    const where = `/power bars ${theme}`
    const v = await open(browser, 'power', { theme })
    const bars = await v.page.evaluate(() =>
      [...document.querySelectorAll('[data-rail-bar]')].map((e) => ({
        rail: (e as HTMLElement).dataset.railBar ?? '',
        width: e.getBoundingClientRect().width,
      }))
    )
    const want = summary.map((s) => s.rail).join(', ')
    const got = bars.map((b) => b.rail).join(', ')
    if (got !== want) fail(where, `bars are [${got}], not [${want}]`)
    for (const b of bars)
      if (b.width < 100) fail(where, `${b.rail} bar is ${b.width} px wide`)
    for (const e of v.errors) fail(where, `page error: ${e}`)
    await v.close()
  }
}

/**
 * Every page sets its own browser tab title, ending with the site name, also
 * after moving between pages in one tab.
 */
async function pageTitles(browser: Browser) {
  const where = 'tab titles'
  const v = await open(browser, '')
  const seen = new Map<string, string>()
  for (const route of [
    '',
    'diagram?level=system',
    'diagram?level=board',
    'diagram?level=power',
    'diagram?level=board&link=b-link',
    'pinout?mcu=h743',
    'pinout?mcu=f100',
    'decisions',
    'open',
    'checklist',
    'history',
    'trace',
    'power',
    'showcase',
    'about',
  ]) {
    await v.page.evaluate((h) => {
      location.hash = h
    }, `#/${route}`)
    await v.page.waitForTimeout(800)
    const title = await v.page.title()
    if (!title.endsWith('AeroOptix-Horizon'))
      fail(where, `/${route} title "${title}" does not end with the site name`)
    const other = seen.get(title)
    if (other !== undefined)
      fail(where, `/${route} has the same title as /${other}: "${title}"`)
    seen.set(title, route)
  }
  for (const e of v.errors) fail(where, `page error: ${e}`)
  await v.close()
}

/** Every Decisions Date cell holds its text inside the cell, at 1440 px. */
async function decisionDatesFit(browser: Browser) {
  const where = '/decisions date cells'
  const v = await open(browser, 'decisions')
  const date = await v.page.evaluate(() => {
    const ths = [...document.querySelectorAll('thead th')]
    return ths.findIndex((th) => th.textContent?.trim() === 'Date')
  })
  if (date < 0) fail(where, 'no Date column')
  const wide = await v.page.evaluate((col) => {
    const out: string[] = []
    for (const tr of document.querySelectorAll('tbody tr[id^="row-"]')) {
      const td = tr.children[col] as HTMLElement | undefined
      if (!td) continue
      const box = td.getBoundingClientRect()
      const pad = parseFloat(getComputedStyle(td).paddingRight)
      const right = Math.max(
        ...[...td.querySelectorAll('*')].map(
          (e) => e.getBoundingClientRect().right
        ),
        box.left
      )
      if (td.scrollWidth > td.clientWidth || right > box.right - pad + 0.5)
        out.push(`${tr.id}: "${td.textContent}" is wider than its cell`)
    }
    return out
  }, date)
  for (const w of wide) fail(where, w)
  for (const e of v.errors) fail(where, `page error: ${e}`)
  await v.close()
}

/** A revision chip on the Overview opens its row on Spec history. */
async function revChipOpensRow(browser: Browser) {
  const where = 'Overview revision chip'
  const v = await open(browser, '')
  const chip = v.page.locator('a[href*="history?rev="]').first()
  const rev = ((await chip.textContent()) ?? '').replace('rev', '').trim()
  await chip.click()
  await v.page.waitForTimeout(1000)
  const [hash, row] = await v.page.evaluate(() => [
    location.hash,
    document.querySelector('tr[data-state=selected]')?.id ?? '',
  ])
  if (!hash.includes('history')) fail(where, `went to ${hash || 'nowhere'}`)
  if (row !== `rev-${rev}`) fail(where, `selected row is "${row}"`)
  // 0.10 and 0.1 both exist; a link must keep the trailing zero
  await v.page.evaluate(() => {
    location.hash = '#/history?rev=%220.10%22'
  })
  await v.page.waitForTimeout(1000)
  const ten = await v.page.evaluate(
    () => document.querySelector('tr[data-state=selected]')?.id ?? ''
  )
  if (ten !== 'rev-0.10') fail(where, `rev "0.10" selected "${ten}"`)
  for (const e of v.errors) fail(where, `page error: ${e}`)
  await v.close()
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
  const channel = process.env.UI_BROWSER ?? (process.env.CI ? '' : 'msedge')
  const browser = await chromium.launch(channel ? { channel } : {})
  try {
    // pages load without errors, both themes
    for (const theme of ['dark', 'light'] as const)
      for (const route of [
        '',
        'diagram?level=system',
        'diagram?level=board',
        'diagram?level=board&link=b-link',
        'diagram?level=power',
        'pinout?mcu=h743',
        'pinout?mcu=f100',
        'decisions',
        'decisions?id=DEC-050',
        'open',
        'open?id=OPEN-023',
        'open?closed=true',
        'checklist',
        'checklist?id=P3-007',
        'checklist?gate=P3&status=OPEN',
        'history',
        'history?rev=0.86',
        'trace',
        'trace?id=IF-010',
        'trace?flag=task',
        'power',
        'showcase',
        'about',
      ]) {
        const v = await open(browser, route, { theme })
        for (const e of v.errors) fail(`/${route} ${theme}`, `page error: ${e}`)
        await v.close()
      }

    // light theme: the three views draw the same way as in dark
    for (const route of [
      'diagram?level=system',
      'diagram?level=board',
      'diagram?level=power',
    ]) {
      const v = await open(browser, route, { theme: 'light' })
      await straightLines(v.page, `/${route} light`)
      await clearLabels(v.page, `/${route} light`)
      await v.close()
    }

    await sameTabLinks(browser)
    await searchOpensRow(browser, 'DEC-050', 'decisions')
    await searchOpensRow(browser, 'OPEN-023', '/open')
    await searchOpensRow(browser, 'OPEN-001', '/open')
    await searchOpensRow(browser, 'PWR-011', '/trace')
    await searchOpensRow(browser, 'P3-007', '/checklist', 'Checklist tasks')
    // 0.10 and 0.1 both exist; the result must open 0.10
    await searchOpensRow(
      browser,
      '0.10',
      '/history',
      'Spec revisions',
      'rev 0.10',
      'rev-0.10'
    )
    await taskChipOpensRow(browser)
    await revChipOpensRow(browser)
    await powerBars(browser)
    await decisionDatesFit(browser)
    await pageTitles(browser)
    await openRowTopAligned(browser)
    await chipsOpenSitePages(browser)

    // diagram drawing, with nothing and with a block selected
    for (const route of [
      'diagram?level=system',
      'diagram?level=board',
      'diagram?level=system&block=servos',
      'diagram?level=system&block=gps',
      'diagram?level=system&block=pm02d',
      'diagram?level=system&block=o-servo',
      'diagram?level=board&block=f100',
      'diagram?level=board&block=h743',
      'diagram?level=board&block=j-servo',
      'diagram?level=power',
      'diagram?level=power&block=pw-r5v',
      'diagram?level=power&block=pw-pm02d',
      'diagram?level=power&block=pw-r3v3',
      'diagram?level=power&block=pw-imu',
      'diagram?level=board&block=i2c2',
      'diagram?level=board&block=p-f100dbg',
      'diagram?level=board&block=j-gps',
      'diagram?level=board&block=buzzer',
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
        ['diagram?level=power', 'Export SVG'],
        ['pinout?mcu=h743', 'SVG'],
        ['pinout?mcu=f100', 'SVG'],
      ]) {
        const v = await open(browser, route, { theme })
        await svgExport(v.page, button, `/${route} ${theme} export`)
        await v.close()
      }

    // phone width, both themes
    for (const theme of ['dark', 'light'] as const)
      for (const route of [
        '',
        'diagram?level=system',
        'diagram?level=board',
        'diagram?level=power',
        'pinout?mcu=h743',
        'pinout?mcu=f100',
        'decisions?id=DEC-050',
        'open?id=OPEN-023',
        'open?closed=true&id=OPEN-001',
        'checklist',
        'checklist?id=P3-007',
        'history?rev=0.86',
        'trace',
        'trace?id=IF-010',
        'power',
        'showcase',
        'about',
      ]) {
        const v = await open(browser, route, { width: 390, theme })
        const where = `/${route} at 390 px ${theme}`
        await noSideScroll(v.page, where)
        if (route.startsWith('diagram')) {
          await readableZoom(v.page, where)
          await viewTabsFit(v.page, where)
        }
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
