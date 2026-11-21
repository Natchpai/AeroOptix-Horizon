import { useEffect, useRef, useState } from 'react'
import { meta } from '@/data'
import { Box, Camera, Download, Image } from 'lucide-react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Main } from '@/components/layout/main'
import { SiteHeader } from '@/components/layout/site-header'

const planned = [
  {
    title: 'Renders',
    text: 'Top and bottom renders of the PCB once the layout is checked.',
    icon: Image,
    color: 'var(--bus-uart)',
  },
  {
    title: 'Photos and tests',
    text: 'Bring-up photos and bench results, after boards are built.',
    icon: Camera,
    color: 'var(--bus-i2c)',
  },
]

const model = meta.boardModel

/** The part of the model-viewer scene-graph API that fixMaterials uses. */
type ViewerMaterial = {
  pbrMetallicRoughness: {
    baseColorFactor: [number, number, number, number]
    setMetallicFactor: (v: number) => void
    setRoughnessFactor: (v: number) => void
  }
}

/**
 * The KiCad GLB sets only a base colour per material, so glTF reads every
 * material as rough metal (metallic 1, roughness 1), and the board, chips and
 * plastics all look grey and flat. Sort the materials by colour and give
 * each kind a plausible finish. The GLB file itself is not changed.
 */
function fixMaterials(materials: ViewerMaterial[]) {
  // [metallic, roughness] per kind
  const finish = {
    mask: [0, 0.3], // green solder mask, translucent and glossy
    silk: [0, 0.8], // white silkscreen, translucent
    gold: [1, 0.3], // gold pins and pads
    tin: [1, 0.35], // tinned leads
    plastic: [0, 0.55], // board body, chip packages, housings
  } as const
  for (const m of materials) {
    const pbr = m.pbrMetallicRoughness
    const [r, g, b, a] = pbr.baseColorFactor
    const max = Math.max(r, g, b)
    const min = Math.min(r, g, b)
    const sat = max ? (max - min) / max : 0
    let kind: keyof typeof finish = 'plastic'
    if (a < 1 && g > r && g > b && max < 0.4) kind = 'mask'
    else if (a < 1 && min > 0.8) kind = 'silk'
    else if (sat > 0.45 && r > 0.6 && g > 0.35 && b < 0.45) kind = 'gold'
    else if (sat < 0.15 && max > 0.55 && max < 0.72) kind = 'tin'
    pbr.setMetallicFactor(finish[kind][0])
    pbr.setRoughnessFactor(finish[kind][1])
  }
}

export function Showcase() {
  return (
    <>
      <SiteHeader title='Showcase' />
      <Main className='space-y-6'>
        <div>
          <h1 className='text-2xl font-bold tracking-tight'>Showcase</h1>
          <p className='text-muted-foreground'>
            The board as it stands in KiCad. Renders and photos follow later.
          </p>
        </div>
        {model ? <BoardViewer /> : <NoModel />}
        <div className='grid gap-4 md:grid-cols-2'>
          {planned.map((p) => (
            <Card key={p.title} className='border-dashed'>
              <CardHeader>
                <span
                  className='mb-2 flex size-10 items-center justify-center rounded-lg'
                  style={{
                    color: p.color,
                    background: `color-mix(in oklab, ${p.color} 15%, transparent)`,
                  }}
                >
                  <p.icon className='size-5' />
                </span>
                <CardTitle>{p.title}</CardTitle>
                <CardDescription>{p.text}</CardDescription>
              </CardHeader>
              <CardContent>
                <span className='text-xs font-medium text-muted-foreground'>
                  Coming later
                </span>
              </CardContent>
            </Card>
          ))}
        </div>
      </Main>
    </>
  )
}

function BoardViewer() {
  const ref = useRef<HTMLElement>(null)
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading')
  const [progress, setProgress] = useState(0)
  const src = `${import.meta.env.BASE_URL}${model!.file}`
  const mb = (model!.bytes / 1e6).toFixed(1)

  // The viewer (three.js) is loaded only on this page.
  useEffect(() => {
    import('@google/model-viewer').catch(() => setState('error'))
  }, [])

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const onProgress = (e: Event) =>
      setProgress(
        (e as CustomEvent<{ totalProgress: number }>).detail.totalProgress
      )
    const onLoad = () => {
      const viewer = el as HTMLElement & {
        model?: { materials: ViewerMaterial[] }
      }
      if (viewer.model) fixMaterials(viewer.model.materials)
      setState('ready')
    }
    const onError = () => setState('error')
    el.addEventListener('progress', onProgress)
    el.addEventListener('load', onLoad)
    el.addEventListener('error', onError)
    return () => {
      el.removeEventListener('progress', onProgress)
      el.removeEventListener('load', onLoad)
      el.removeEventListener('error', onError)
    }
  }, [])

  return (
    <Card className='gap-3 overflow-hidden'>
      <CardHeader className='flex flex-row flex-wrap items-start justify-between gap-2'>
        <div className='space-y-1'>
          <CardTitle className='flex items-center gap-2 text-base'>
            <Box className='size-4 text-primary' /> 3D board
          </CardTitle>
          <CardDescription>
            Board {meta.boardRevision} · exported {model!.date} from KiCad{' '}
            {meta.kicad} · {mb} MB. Drag to turn, scroll or pinch to zoom.
          </CardDescription>
        </div>
        <div className='flex items-center gap-2'>
          <span className='rounded-md border border-status-open/50 px-2 py-0.5 text-xs font-medium text-status-open'>
            {meta.phase} layout · not for fabrication
          </span>
          <a
            href={src}
            download
            className='inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-xs hover:border-primary/60 hover:text-primary'
          >
            <Download className='size-3.5' /> GLB
          </a>
        </div>
      </CardHeader>
      <CardContent className='px-0'>
        <div className='relative h-[60vh] min-h-80 bg-[radial-gradient(ellipse_at_center,color-mix(in_oklab,var(--brand)_14%,transparent),transparent_70%)]'>
          <model-viewer
            ref={ref}
            src={src}
            alt='AeroOptix-Horizon flight controller PCB, 3D model from KiCad'
            camera-controls
            camera-orbit='30deg 55deg auto'
            touch-action='pan-y'
            interaction-prompt='none'
            shadow-intensity='1'
            shadow-softness='0.5'
            exposure='1'
            environment-image='legacy'
            tone-mapping='neutral'
            style={{ width: '100%', height: '100%', background: 'transparent' }}
          />
          {state !== 'ready' && (
            <div className='pointer-events-none absolute inset-0 flex items-center justify-center'>
              <span className='rounded-md bg-background/80 px-3 py-1.5 text-sm text-muted-foreground'>
                {state === 'error'
                  ? 'The board model could not load.'
                  : `Loading board model… ${Math.round(progress * 100)} %`}
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

function NoModel() {
  return (
    <Card className='border-dashed'>
      <CardHeader>
        <CardTitle className='flex items-center gap-2 text-base'>
          <Box className='size-4 text-primary' /> 3D board
        </CardTitle>
        <CardDescription>
          No board model yet. It appears here once a GLB is exported from KiCad
          into <code>web/public/models/</code>.
        </CardDescription>
      </CardHeader>
    </Card>
  )
}
