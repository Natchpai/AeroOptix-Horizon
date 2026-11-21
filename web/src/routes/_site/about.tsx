import { createFileRoute } from '@tanstack/react-router'
import { AboutPage } from '@/features/about'

export const Route = createFileRoute('/_site/about')({
  component: AboutPage,
})
