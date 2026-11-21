import { ids } from '@/data'
import { IdChip } from '@/components/id-chip'
import { MdText } from '@/components/md-text'
import { TaskText } from '@/components/task-status'

const SPEC_ID = /\b([A-Z]{2,5}-\d{2,3})\b/

/** Evidence labels (engineering rules) and the colour each one shows in. */
const LABEL_COLOR: Record<string, string> = {
  VERIFIED: 'var(--status-decided)',
  ESTIMATED: 'var(--brand)',
  ASSUMED: 'var(--status-candidate)',
  NOT_VERIFIED: 'var(--status-open)',
  TBD: 'var(--muted-foreground)',
}

/** An evidence label as a small coloured badge; the word is always shown. */
function EvidenceLabel({ label }: { label: string }) {
  const color = LABEL_COLOR[label] ?? 'var(--muted-foreground)'
  return (
    <span
      className='inline-flex items-center rounded border px-1 py-px align-baseline font-mono text-[11px] leading-none whitespace-nowrap'
      style={{
        color,
        borderColor: `color-mix(in oklab, ${color} 50%, transparent)`,
      }}
    >
      {label}
    </span>
  )
}

/**
 * Record text with spec IDs (IF-010, DEC-050) and checklist task IDs
 * (P3-007) as chips. Code spans and unknown IDs stay as written. With
 * `labels`, a code span that is an evidence label shows as a badge.
 */
export function SpecText({ text, labels }: { text: string; labels?: boolean }) {
  return text.split(/(`[^`]+`)/).map((chunk, c) => {
    if (!chunk.startsWith('`')) {
      return chunk
        .split(SPEC_ID)
        .map((part, i) =>
          i % 2 && ids[part] ? (
            <IdChip key={`${c}-${i}`} id={part} className='align-baseline' />
          ) : (
            part && <TaskText key={`${c}-${i}`} text={part} />
          )
        )
    }
    const word = chunk.slice(1, -1)
    return labels && word in LABEL_COLOR ? (
      <EvidenceLabel key={c} label={word} />
    ) : (
      <MdText key={c} text={chunk} />
    )
  })
}
