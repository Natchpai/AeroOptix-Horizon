import React from 'react'
import { useNavigate } from '@tanstack/react-router'
import {
  type Mcu,
  blocks,
  busInfo,
  ids,
  idTitle,
  links,
  linkForPin,
  mcuInfo,
  pins,
  sourceUrl,
} from '@/data'
import {
  ArrowRight,
  Box,
  Cable,
  ChevronRight,
  Cpu,
  FileText,
  Laptop,
  Moon,
  Sun,
} from 'lucide-react'
import { useSearch } from '@/context/search-provider'
import { useTheme } from '@/context/theme-provider'
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command'
import { sidebarData } from './layout/data/sidebar-data'
import { ScrollArea } from './ui/scroll-area'

const isExternal = (url: string) => /^https?:\/\//.test(url)

/** Spec IDs worth searching for; the other kinds stay in the spec. */
const searchable = Object.values(ids).filter((s) =>
  ['IF', 'DEC', 'OPEN', 'SEN', 'PWR', 'FUN'].includes(s.kind)
)

export function CommandMenu() {
  const navigate = useNavigate()
  const { setTheme } = useTheme()
  const { open, setOpen } = useSearch()

  const runCommand = React.useCallback(
    (command: () => unknown) => {
      setOpen(false)
      command()
    },
    [setOpen]
  )

  return (
    <CommandDialog modal open={open} onOpenChange={setOpen}>
      <CommandInput placeholder='Search pins, signals, blocks, IF/DEC/OPEN IDs…' />
      <CommandList>
        <ScrollArea type='hover' className='h-96 pe-1'>
          <CommandEmpty>No results found.</CommandEmpty>

          {sidebarData.navGroups
            .filter((g) => g.title !== 'Links')
            .map((group) => (
              <CommandGroup key={group.title} heading={group.title}>
                {group.items.flatMap((navItem, i) => {
                  if (navItem.url && !isExternal(String(navItem.url)))
                    return [
                      <CommandItem
                        key={`${navItem.url}-${i}`}
                        value={navItem.title}
                        onSelect={() =>
                          runCommand(() =>
                            navigate({ to: navItem.url as never })
                          )
                        }
                      >
                        <ArrowRight className='size-3 text-muted-foreground/80' />
                        {navItem.title}
                      </CommandItem>,
                    ]
                  return (navItem.items ?? []).map((sub, j) => (
                    <CommandItem
                      key={`${navItem.title}-${sub.title}-${j}`}
                      value={`${navItem.title} ${sub.title}`}
                      onSelect={() =>
                        runCommand(() =>
                          navigate({
                            to: sub.url as never,
                            search: sub.search as never,
                          })
                        )
                      }
                    >
                      <ArrowRight className='size-3 text-muted-foreground/80' />
                      {navItem.title} <ChevronRight /> {sub.title}
                    </CommandItem>
                  ))
                })}
              </CommandGroup>
            ))}

          <CommandGroup heading='Blocks'>
            {blocks.map((b) => (
              <CommandItem
                key={b.id}
                value={`block ${b.label} ${b.sub ?? ''} ${b.level}`}
                onSelect={() =>
                  runCommand(() =>
                    navigate({
                      to: '/diagram',
                      search: { level: b.level, block: b.id },
                    })
                  )
                }
              >
                <Box className='size-3.5' />
                <span>{b.label}</span>
                <span className='truncate font-mono text-xs text-muted-foreground'>
                  {b.sub}
                </span>
                <span className='ms-auto text-[10px] text-muted-foreground'>
                  {b.level}
                </span>
              </CommandItem>
            ))}
          </CommandGroup>

          <CommandGroup heading='Links'>
            {links
              .filter((l) => l.level === 'board' || l.pins?.length)
              .map((l) => (
                <CommandItem
                  key={l.id}
                  value={`link ${l.label} ${l.from} ${l.to} ${l.refs.join(' ')}`}
                  onSelect={() =>
                    runCommand(() =>
                      navigate({
                        to: '/diagram',
                        search: { level: l.level, link: l.id },
                      })
                    )
                  }
                >
                  <Cable
                    className='size-3.5'
                    style={{ color: busInfo[l.bus].color }}
                  />
                  <span className='font-mono text-xs'>{l.label}</span>
                  <span className='truncate text-xs text-muted-foreground'>
                    {blocks.find((b) => b.id === l.from)?.label} →{' '}
                    {blocks.find((b) => b.id === l.to)?.label}
                  </span>
                </CommandItem>
              ))}
          </CommandGroup>

          {(Object.keys(mcuInfo) as Mcu[]).map((mcu) => (
            <CommandGroup key={mcu} heading={`${mcuInfo[mcu].part} pins`}>
              {pins[mcu].map((p) => (
                <CommandItem
                  key={`${mcu}-${p.pin}`}
                  value={`${mcu} ${p.pin} ${p.signal} ${p.function} ${p.refs.join(' ')}`}
                  onSelect={() =>
                    runCommand(() =>
                      navigate({ to: '/pinout', search: { mcu, pin: p.pin } })
                    )
                  }
                >
                  <Cpu className='size-3.5' />
                  <span className='w-12 font-mono text-xs font-semibold'>
                    {p.pin}
                  </span>
                  <span className='font-mono text-xs'>{p.signal}</span>
                  <span className='truncate text-xs text-muted-foreground'>
                    {p.function}
                  </span>
                  {linkForPin(mcu, p.pin) && (
                    <span className='ms-auto text-[10px] text-primary'>
                      on diagram
                    </span>
                  )}
                </CommandItem>
              ))}
            </CommandGroup>
          ))}

          <CommandGroup heading='Spec IDs'>
            {searchable.map((s) => (
              <CommandItem
                key={s.id}
                value={`${s.id} ${idTitle(s.id)}`}
                onSelect={() =>
                  runCommand(() =>
                    window.open(
                      sourceUrl(s.file, s.line),
                      '_blank',
                      'noreferrer'
                    )
                  )
                }
              >
                <FileText className='size-3.5' />
                <span className='w-16 font-mono text-xs font-semibold'>
                  {s.id}
                </span>
                <span className='truncate text-xs'>{idTitle(s.id)}</span>
                {s.closed && (
                  <span className='ms-auto text-[10px] text-muted-foreground'>
                    closed
                  </span>
                )}
              </CommandItem>
            ))}
          </CommandGroup>

          <CommandSeparator />
          <CommandGroup heading='Theme'>
            <CommandItem onSelect={() => runCommand(() => setTheme('light'))}>
              <Sun /> <span>Light</span>
            </CommandItem>
            <CommandItem onSelect={() => runCommand(() => setTheme('dark'))}>
              <Moon className='scale-90' />
              <span>Dark</span>
            </CommandItem>
            <CommandItem onSelect={() => runCommand(() => setTheme('system'))}>
              <Laptop />
              <span>System</span>
            </CommandItem>
          </CommandGroup>
        </ScrollArea>
      </CommandList>
    </CommandDialog>
  )
}
