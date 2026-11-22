import type { KnipConfig } from 'knip'

const config: KnipConfig = {
  ignore: ['src/components/ui/**', 'src/components/layout/app-title.tsx'],
  // topology.ts exports the per-view block and link arrays and also joins
  // them into `blocks` and `links` in the same file.
  ignoreExportsUsedInFile: true,
}

export default config
