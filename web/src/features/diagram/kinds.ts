import { type Block, type BlockKind, busInfo } from '@/data'
import {
  Box,
  Cable,
  CircuitBoard,
  Cpu,
  Gauge,
  Network,
  Plug,
  ToggleRight,
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
  bus: { label: 'Shared bus', icon: Network, color: 'var(--bus-i2c)' },
  connector: { label: 'Connector', icon: Plug, color: 'var(--bus-debug)' },
  io: { label: 'On-board I/O', icon: ToggleRight, color: 'var(--bus-gpio)' },
  external: { label: 'External device', icon: Box, color: 'var(--bus-usb)' },
}

/** A block on one power rail takes the rail colour; others their kind's. */
export function blockColor(block: Block) {
  return block.rail ? busInfo[block.rail].color : kindInfo[block.kind].color
}
