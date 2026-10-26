import { useEffect, useMemo } from 'react'
import { type Level, blocksAt, linksAt, linksOf } from '@/data'
import { lineAt, places, sideOverrides, zones } from '@/data/places'
import {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useTheme } from '@/context/theme-provider'
import { BlockNode, type BlockNodeType } from './block-node'
import { blockColor } from './kinds'
import { placedLayout, zoneBoxes } from './layout'
import { LinkEdge, type LinkEdgeType } from './link-edge'
import { ZoneNode, type ZoneNodeType } from './zone-node'

const nodeTypes = { block: BlockNode, zone: ZoneNode }
const edgeTypes = { link: LinkEdge }

type CanvasProps = {
  level: Level
  selectedBlock?: string
  selectedLink?: string
  onBlock: (id: string) => void
  onLink: (id: string) => void
  onPane: () => void
}

export function DiagramCanvas(props: CanvasProps) {
  return (
    <ReactFlowProvider>
      <CanvasInner {...props} />
    </ReactFlowProvider>
  )
}

function CanvasInner({
  level,
  selectedBlock,
  selectedLink,
  onBlock,
  onLink,
  onPane,
}: CanvasProps) {
  const { resolvedTheme } = useTheme()
  const { fitView } = useReactFlow()
  const laid = useMemo(
    () =>
      placedLayout(
        blocksAt(level),
        linksAt(level),
        places[level],
        sideOverrides,
        lineAt
      ),
    [level]
  )

  // Fit once per level, after the new layout is on screen.
  useEffect(() => {
    const t = setTimeout(
      () => fitView({ padding: 0.05, maxZoom: 1, duration: 300 }),
      30
    )
    return () => clearTimeout(t)
  }, [laid, fitView])

  // Neighbours of the selected block stay bright; the rest dims.
  const focus = useMemo(() => {
    if (!selectedBlock) return null
    const ls = linksOf(selectedBlock)
    return {
      links: new Set(ls.map((l) => l.id)),
      blocks: new Set([selectedBlock, ...ls.flatMap((l) => [l.from, l.to])]),
    }
  }, [selectedBlock])

  // zones sit under the lines (zIndex -1) and take no clicks
  const zoneNodes: ZoneNodeType[] = useMemo(
    () =>
      zoneBoxes(zones[level] ?? [], laid.nodes).map((z) => ({
        id: z.zone.id,
        type: 'zone',
        position: { x: z.x, y: z.y },
        data: { label: z.zone.label, w: z.w, h: z.h },
        width: z.w,
        height: z.h,
        zIndex: -1,
        draggable: false,
        selectable: false,
        focusable: false,
      })),
    [laid, level]
  )

  const nodes: (BlockNodeType | ZoneNodeType)[] = useMemo(
    () => [
      ...zoneNodes,
      ...laid.nodes.map((n): BlockNodeType => ({
        id: n.block.id,
        type: 'block',
        position: { x: n.x, y: n.y },
        data: {
          block: n.block,
          w: n.w,
          h: n.h,
          handles: n.handles,
          dim: !!focus && !focus.blocks.has(n.block.id),
        },
        width: n.w,
        height: n.h,
        selected: n.block.id === selectedBlock,
        draggable: false,
      })),
    ],
    [zoneNodes, laid, focus, selectedBlock]
  )

  const edges: LinkEdgeType[] = useMemo(
    () =>
      laid.edges.map((e) => ({
        id: e.link.id,
        type: 'link',
        source: e.link.from,
        target: e.link.to,
        sourceHandle: e.sourceHandle,
        targetHandle: e.targetHandle,
        selected: e.link.id === selectedLink,
        data: {
          link: e.link,
          labelAt: e.labelAt,
          labelSide: e.labelSide,
          dim: !!focus && !focus.links.has(e.link.id),
          hot: !!focus && focus.links.has(e.link.id),
          onPick: onLink,
        },
      })),
    [laid, focus, selectedLink, onLink]
  )

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      edgeTypes={edgeTypes}
      colorMode={resolvedTheme}
      onNodeClick={(_, n) => n.type === 'block' && onBlock(n.id)}
      onEdgeClick={(_, e) => onLink(e.id)}
      onPaneClick={onPane}
      nodesConnectable={false}
      elementsSelectable
      minZoom={0.15}
      maxZoom={2.5}
      proOptions={{ hideAttribution: true }}
      className='!bg-transparent'
    >
      <Background
        variant={BackgroundVariant.Dots}
        gap={22}
        size={1.2}
        color='color-mix(in oklab, var(--brand) 22%, transparent)'
      />
      <Controls showInteractive={false} position='top-right' />
      <MiniMap
        pannable
        zoomable
        position='bottom-right'
        style={{ width: 170, height: 110 }}
        className='!hidden !rounded-md !border !bg-card lg:!block'
        maskColor='color-mix(in oklab, var(--background) 70%, transparent)'
        nodeColor={(n) =>
          n.type === 'block'
            ? blockColor((n as BlockNodeType).data.block)
            : 'transparent'
        }
        nodeStrokeWidth={0}
      />
    </ReactFlow>
  )
}
