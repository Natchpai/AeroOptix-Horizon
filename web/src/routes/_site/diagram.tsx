import { createFileRoute } from '@tanstack/react-router'
import { DiagramPage } from '@/features/diagram'

type DiagramSearch = {
  level?: 'system' | 'board'
  /** Selected link: opens the interface (signal and pin) view. */
  link?: string
  /** Selected block: opens its detail panel. */
  block?: string
}

export const Route = createFileRoute('/_site/diagram')({
  validateSearch: (s: Record<string, unknown>): DiagramSearch => ({
    level:
      s.level === 'board'
        ? 'board'
        : s.level === 'system'
          ? 'system'
          : undefined,
    link: typeof s.link === 'string' ? s.link : undefined,
    block: typeof s.block === 'string' ? s.block : undefined,
  }),
  component: DiagramPage,
})
