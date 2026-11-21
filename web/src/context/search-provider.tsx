import {
  createContext,
  lazy,
  Suspense,
  useContext,
  useEffect,
  useState,
} from 'react'

// The menu and its search index load on their own, so the first page does
// not wait for them; they are fetched when the browser is idle, or on the
// first Ctrl+K.
const loadMenu = () => import('@/components/command-menu')
const CommandMenu = lazy(() =>
  loadMenu().then((m) => ({ default: m.CommandMenu }))
)

type SearchContextType = {
  open: boolean
  setOpen: React.Dispatch<React.SetStateAction<boolean>>
}

const SearchContext = createContext<SearchContextType | null>(null)

type SearchProviderProps = {
  children: React.ReactNode
}

export function SearchProvider({ children }: SearchProviderProps) {
  const [open, setOpen] = useState(false)
  // mount the menu once it has been opened, then keep it
  const [used, setUsed] = useState(false)
  if (open && !used) setUsed(true)

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }
    document.addEventListener('keydown', down)
    const idle = window.requestIdleCallback
      ? window.requestIdleCallback(() => void loadMenu())
      : window.setTimeout(() => void loadMenu(), 2000)
    return () => {
      document.removeEventListener('keydown', down)
      if (window.cancelIdleCallback) window.cancelIdleCallback(idle)
      else window.clearTimeout(idle)
    }
  }, [])

  return (
    <SearchContext value={{ open, setOpen }}>
      {children}
      {used && (
        <Suspense fallback={null}>
          <CommandMenu />
        </Suspense>
      )}
    </SearchContext>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export const useSearch = () => {
  const searchContext = useContext(SearchContext)

  if (!searchContext) {
    throw new Error('useSearch has to be used within SearchProvider')
  }

  return searchContext
}
