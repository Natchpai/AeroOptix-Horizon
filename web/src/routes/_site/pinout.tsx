import { createFileRoute } from '@tanstack/react-router'
import { PinoutPage } from '@/features/pinout'

type PinoutSearch = {
  mcu?: 'h743' | 'f100'
  /** Highlighted pin name, e.g. PA5. */
  pin?: string
}

export const Route = createFileRoute('/_site/pinout')({
  validateSearch: (s: Record<string, unknown>): PinoutSearch => ({
    mcu: s.mcu === 'f100' ? 'f100' : s.mcu === 'h743' ? 'h743' : undefined,
    pin: typeof s.pin === 'string' ? s.pin : undefined,
  }),
  component: PinoutPage,
})
