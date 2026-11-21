/**
 * JSX typing for the `<model-viewer>` web component (@google/model-viewer),
 * with only the attributes the Showcase uses.
 */
import 'react'

declare module 'react' {
  namespace JSX {
    interface IntrinsicElements {
      'model-viewer': React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement>,
        HTMLElement
      > & {
        src?: string
        alt?: string
        'camera-controls'?: boolean
        'camera-orbit'?: string
        'touch-action'?: string
        'interaction-prompt'?: string
        'shadow-intensity'?: string
        'shadow-softness'?: string
        'tone-mapping'?: string
        exposure?: string
        'environment-image'?: string
      }
    }
  }
}
