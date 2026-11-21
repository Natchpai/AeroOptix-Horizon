import { ids } from '@/data'
import { IdChip } from '@/components/id-chip'
import { MdText } from '@/components/md-text'
import { TaskText } from '@/components/task-status'

const SPEC_ID = /\b([A-Z]{2,5}-\d{2,3})\b/

/**
 * Record text with spec IDs (IF-010, DEC-050) and checklist task IDs
 * (P3-007) as chips. Code spans and unknown IDs stay as written.
 */
export function SpecText({ text }: { text: string }) {
  return text
    .split(/(`[^`]+`)/)
    .map((chunk, c) =>
      chunk.startsWith('`') ? (
        <MdText key={c} text={chunk} />
      ) : (
        chunk
          .split(SPEC_ID)
          .map((part, i) =>
            i % 2 && ids[part] ? (
              <IdChip key={`${c}-${i}`} id={part} className='align-baseline' />
            ) : (
              part && <TaskText key={`${c}-${i}`} text={part} />
            )
          )
      )
    )
}
