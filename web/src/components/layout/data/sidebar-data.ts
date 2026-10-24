import { REPO_URL, meta, sourceUrl } from '@/data'
import {
  BookOpen,
  Boxes,
  Cpu,
  FileText,
  GitBranch,
  LayoutDashboard,
  Network,
  Sparkles,
} from 'lucide-react'
import { type SidebarData } from '../types'

export const sidebarData: SidebarData = {
  navGroups: [
    {
      title: 'Project',
      items: [{ title: 'Overview', url: '/', icon: LayoutDashboard }],
    },
    {
      title: 'Design',
      items: [
        {
          title: 'Block Diagram',
          icon: Network,
          items: [
            { title: 'System', url: '/diagram', search: { level: 'system' } },
            { title: 'Board', url: '/diagram', search: { level: 'board' } },
          ],
        },
        {
          title: 'Pinout',
          icon: Cpu,
          items: [
            { title: 'STM32H743', url: '/pinout', search: { mcu: 'h743' } },
            { title: 'STM32F100', url: '/pinout', search: { mcu: 'f100' } },
          ],
        },
      ],
    },
    {
      title: 'Output',
      items: [
        { title: 'Showcase', url: '/showcase', icon: Sparkles, badge: 'soon' },
      ],
    },
    {
      title: 'Links',
      items: [
        {
          title: 'Specification',
          url: sourceUrl(meta.sources.spec),
          icon: FileText,
        },
        {
          title: 'Design records',
          url: `${REPO_URL}/tree/main/hardware/AO-Horizon/documents/design`,
          icon: BookOpen,
        },
        {
          title: 'KiCad project',
          url: `${REPO_URL}/tree/main/hardware/AO-Horizon`,
          icon: Boxes,
        },
        { title: 'Repository', url: REPO_URL, icon: GitBranch },
      ],
    },
  ],
}
