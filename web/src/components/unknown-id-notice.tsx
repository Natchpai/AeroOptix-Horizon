/**
 * One muted line above a table when the linked `?id=` (or `?rev=`) names no
 * record. `known` must hold every record of the page, before any filter, so
 * a filter that hides a real row never shows the notice.
 */
export function UnknownIdNotice({
  id,
  known,
  prefix,
  children,
}: {
  /** The ID or revision from the URL. */
  id: string | undefined
  /** Every record ID of the page. */
  known: ReadonlySet<string>
  /** A word before the ID, e.g. "Revision". */
  prefix?: string
  /** The rest of the line, e.g. "is not in the spec." */
  children: string
}) {
  if (!id || known.has(id)) return null
  return (
    <p
      role='status'
      data-unknown-id={id}
      className='px-6 pb-2 text-sm text-muted-foreground'
    >
      {prefix && `${prefix} `}
      <span className='font-mono'>{id}</span> {children}
    </p>
  )
}
