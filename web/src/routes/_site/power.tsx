import { createFileRoute } from '@tanstack/react-router'
import { PowerPage } from '@/features/power'

export const Route = createFileRoute('/_site/power')({
  component: PowerPage,
})
