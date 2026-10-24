import { createFileRoute } from '@tanstack/react-router'
import { Showcase } from '@/features/showcase'

export const Route = createFileRoute('/_site/showcase')({
  component: Showcase,
})
