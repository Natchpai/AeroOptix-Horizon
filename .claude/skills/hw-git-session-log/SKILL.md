---
name: hw-git-session-log
description: >-
  Summarizes significant engineering discussions, confirmed design decisions,
  unresolved findings, and follow-up actions into a concise project log.
  Use only when the user explicitly invokes /hw-git-session-log to prepare a log entry.
argument-hint: "[topic]"
disable-model-invocation: true
---

# Engineering Session Log

Create a short, evidence-aware record of meaningful engineering discussions.
This skill is optional and must never run automatically.

## Invocation
- Use `/hw-git-session-log` to summarize the current relevant discussion.
- Use `/hw-git-session-log <topic>` to limit the summary to that topic.
- Do not treat ordinary requests to summarize a conversation as permission to write a log.

## Writing style
- Write simple, direct English, like one engineer talking to another. Use everyday words, short sentences and active voice.
- Avoid fancy words, marketing phrases and AI-style filler. Keep standard engineering terms and exact identifiers.
- Do not use the em dash (`—`). Use a period, comma, colon or parentheses.
- Priority: technical accuracy, then clarity, then brevity, then style.

## Procedure
1. Identify the requested scope using available conversation context only.
2. Extract decisions, supporting rationale, findings, and open items that matter for future design work.
3. Distinguish `ACCEPTED`, `PROPOSED`, and `REJECTED` decisions; do not infer user approval from a suggestion.
4. Exclude routine Q&A, speculative claims, lengthy transcripts, and tool output.
5. Show a concise Markdown entry for review; identify uncertainties and missing context.
6. Ask for explicit approval to append the proposed entry to `ENGINEERING_LOG.md` at the repository root.
7. Only after approval, read the existing file if present and append the approved entry; otherwise create it with the heading `# Engineering Log`.
8. Preserve existing entries and confirm the actual write result. Never overwrite, rewrite, or auto-commit the log.

## Entry Format

```markdown
## YYYY-MM-DD : Topic

**Context:** One-sentence summary.

**Decisions:**
- [ACCEPTED | PROPOSED | REJECTED] Decision and brief rationale.

**Findings / Open Items:**
- Finding or action required (owner if known).

**References:** Relevant schematic file, component, net, document, or commit (only if known).
```

Example:

```markdown
## 2026-03-02 : 3V3 rail regulator choice

**Context:** Compared two LDOs for the 3V3 rail against the 500 mA load estimate.

**Decisions:**
- [PROPOSED] Use the 1 A part for current margin; the engineer has not yet confirmed.

**Findings / Open Items:**
- NOT_VERIFIED: dropout at minimum input voltage; check the datasheet (owner: engineer).

**References:** Sheet `power.kicad_sch`, U3.
```

Omit empty sections. Keep entries typically within 5–10 content lines where practical.
Use a verified session date; do not fabricate citations, references, or decisions.

## Placement and duplicates
- Append new entries at the end of the file, in chronological order.
- Use today's date from the environment; if unavailable, ask rather than guess.
- Read only enough of the existing log to avoid duplicating a decision; if one
  exists, propose an update note instead.
- Record `ACCEPTED` only for decisions the human engineer stated. A log entry
  does not declare a project phase or approve a design.
- Release-facing changes belong in `CHANGELOG.md`; do not copy between them
  unasked.
- Git actions on the log need separate approval. Follow
  `rules/git-workflow.md` if present.

## Boundaries
- Do not edit KiCad files, engineering rules, other logs, or review states.
- Do not load the complete log at session start; read it only when necessary to avoid duplicates or on user request.
- Avoid sensitive credentials, personal information, and unrelated chat content.
- Do not create directories, per-session files, or permanent caches.
- Respect project permissions; a tool permission grant does not replace the explicit content-approval step above.
