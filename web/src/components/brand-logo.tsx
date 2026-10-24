import { cn } from '@/lib/utils'

const base = import.meta.env.BASE_URL

/** Club logo. The dark variant has the navy letters recoloured to light. */
export function BrandLogo({ className }: { className?: string }) {
  return (
    <span className={cn('relative inline-flex items-center', className)}>
      <img
        src={`${base}images/logo-light.png`}
        alt='AeroOptix logo'
        className='h-full w-full object-contain dark:hidden'
      />
      <img
        src={`${base}images/logo-dark.png`}
        alt='AeroOptix logo'
        className='hidden h-full w-full object-contain dark:block'
      />
    </span>
  )
}
