import { Link } from '@tanstack/react-router'
import { commitUrl, meta } from '@/data'
import { useLayout } from '@/context/layout-provider'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  useSidebar,
} from '@/components/ui/sidebar'
import { BrandLogo, CoopLogo } from '@/components/brand-logo'
import { sidebarData } from './data/sidebar-data'
import { NavGroup } from './nav-group'

/**
 * Callback ref: sets `data-fade` on the sidebar content while nav links sit
 * hidden below its bottom edge, so a CSS mask can fade them out above the
 * footer. A ref, not an effect, so it also runs when the mobile sheet opens.
 */
function fadeWhenMore(el: HTMLDivElement | null) {
  if (!el) return
  const update = () => {
    const more = el.scrollTop + el.clientHeight < el.scrollHeight - 1
    el.toggleAttribute('data-fade', more)
  }
  update()
  el.addEventListener('scroll', update, { passive: true })
  // a sub-menu opening changes the children's size, not the box's
  const ro = new ResizeObserver(update)
  ro.observe(el)
  for (const child of el.children) ro.observe(child)
  return () => {
    el.removeEventListener('scroll', update)
    ro.disconnect()
  }
}

export function AppSidebar() {
  const { collapsible, variant } = useLayout()
  const { setOpenMobile } = useSidebar()
  return (
    <Sidebar collapsible={collapsible} variant={variant}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size='lg' asChild>
              <Link to='/' onClick={() => setOpenMobile(false)}>
                <BrandLogo className='size-8 shrink-0' />
                <div className='grid flex-1 text-start text-sm leading-tight'>
                  <span className='truncate font-bold tracking-tight'>
                    AeroOptix-Horizon
                  </span>
                  <span className='truncate text-xs text-muted-foreground'>
                    Flight controller {meta.boardRevision}
                  </span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent
        ref={fadeWhenMore}
        className='group-data-[collapsible=icon]:[mask-image:none]! data-fade:[mask-image:linear-gradient(to_bottom,black_calc(100%-2.5rem),transparent)]'
      >
        {sidebarData.navGroups.map((props) => (
          <NavGroup key={props.title} {...props} />
        ))}
      </SidebarContent>
      <SidebarFooter>
        <div className='rounded-md border border-status-open/40 bg-status-open/10 px-3 py-2 text-xs leading-snug group-data-[collapsible=icon]:hidden'>
          <span className='font-semibold text-status-open'>{meta.phase}</span>
          <span className='text-muted-foreground'>
            {' '}
            · spec rev {meta.specRevision} · not for fabrication
          </span>
          <a
            href={commitUrl(meta.build.commit)}
            target='_blank'
            rel='noreferrer'
            className='mt-1 block text-[11px] text-muted-foreground hover:text-foreground'
          >
            Build{' '}
            <span className='font-mono'>{meta.build.commit.slice(0, 7)}</span> ·{' '}
            {meta.build.date}
          </a>
        </div>
        <div className='flex items-center gap-2 px-1 text-[11px] text-muted-foreground group-data-[collapsible=icon]:hidden'>
          In co-op with
          <CoopLogo className='h-4 w-6 shrink-0' />
        </div>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
