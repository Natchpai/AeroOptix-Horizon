import type { BlockKind } from '@/data'
import {
  Box,
  Cable,
  CircuitBoard,
  Cpu,
  Gauge,
  Plug,
  Zap,
  type LucideIcon,
} from 'lucide-react'

export const kindInfo: Record<
  BlockKind,
  { label: string; icon: LucideIcon; color: string }
> = {
  board: { label: 'Board', icon: CircuitBoard, color: 'var(--brand)' },
  mcu: { label: 'MCU', icon: Cpu, color: 'var(--brand)' },
  sensor: { label: 'Sensor', icon: Gauge, color: 'var(--bus-i2c)' },
  power: { label: 'Power part', icon: Zap, color: 'var(--bus-power)' },
  rail: { label: 'Power rail', icon: Cable, color: 'var(--bus-power)' },
  connector: {
    label: 'Connector / on-board I/O',
    icon: Plug,
    color: 'var(--bus-debug)',
  },
  external: { label: 'External device', icon: Box, color: 'var(--bus-usb)' },
}
