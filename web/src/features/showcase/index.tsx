import { Box, Camera, Image } from 'lucide-react'
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
    title: '3D board viewer',
    text: 'Rotate the board in the browser, from a GLB model exported from KiCad 10.',
    icon: Box,
    color: 'var(--bus-spi)',
  },
  {
    title: 'Renders',
    text: 'Top and bottom renders of the PCB once the layout starts.',
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

export function Showcase() {
  return (
    <>
      <SiteHeader title='Showcase' />
      <Main className='space-y-6'>
        <div>
          <h1 className='text-2xl font-bold tracking-tight'>Showcase</h1>
          <p className='text-muted-foreground'>
            Project output will appear here. The board is still in schematic
            capture, so there is no PCB, render or photo yet.
          </p>
        </div>
        <div className='grid gap-4 md:grid-cols-3'>
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
