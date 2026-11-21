import { useEffect } from 'react'
import { meta } from '@/data'
import { Badge } from '@/components/ui/badge'
import { ConfigDrawer } from '@/components/config-drawer'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { Header } from './header'

const SITE = 'AeroOptix-Horizon'

type SiteHeaderProps = {
  title?: React.ReactNode
  /** Browser tab title; defaults to `title` when that is a string. */
  pageTitle?: string
  fixed?: boolean
}

/** Page header: title, phase badge, search, theme and layout settings. */
export function SiteHeader({ title, pageTitle, fixed }: SiteHeaderProps) {
  const page = pageTitle ?? (typeof title === 'string' ? title : undefined)
  useEffect(() => {
    document.title = page ? `${page} · ${SITE}` : SITE
    return () => {
      document.title = SITE
    }
  }, [page])

  return (
    <Header fixed={fixed}>
      <div className='me-auto min-w-0 truncate text-sm font-medium'>
        {title}
      </div>
      <Badge
        variant='outline'
        className='hidden border-status-open/50 bg-status-open/10 text-status-open md:inline-flex'
        title={meta.specStatus}
      >
        {meta.phase} · not for fabrication
      </Badge>
      <Search placeholder='Search pins, IDs…' />
      <ThemeSwitch />
      <ConfigDrawer />
    </Header>
  )
}
