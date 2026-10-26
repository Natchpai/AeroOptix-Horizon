import { cn } from '@/lib/utils'

const base = import.meta.env.BASE_URL

/** A logo with a light-theme and a dark-theme file. */
function ThemedImage({
  light,
  dark,
  alt,
  className,
}: {
  light: string
  dark: string
  alt: string
  className?: string
}) {
  return (
    <span className={cn('relative inline-flex items-center', className)}>
      <img
        src={`${base}images/${light}`}
        alt={alt}
        className='h-full w-full object-contain dark:hidden'
      />
      <img
        src={`${base}images/${dark}`}
        alt={alt}
        className='hidden h-full w-full object-contain dark:block'
      />
    </span>
  )
}

/** Team logo (AeroOptix flame). The dark variant has a white plane. */
export function BrandLogo({ className }: { className?: string }) {
  return (
    <ThemedImage
      light='aeroOptix_light_logo.png'
      dark='aeroOptix_dark_logo.png'
      alt='AeroOptix logo'
      className={className}
    />
  )
}

/** Co-op partner mark (nP), shown small as a credit. */
export function CoopLogo({ className }: { className?: string }) {
  return (
    <ThemedImage
      light='np_light_theme.png'
      dark='np_dark_theme.png'
      alt='nP'
      className={className}
    />
  )
}
