# Hardware Engineering Rules

## Design Authority

- Human engineers retain final authority over design decisions and approvals.
- Treat hardware design files and libraries as read-only by default.
- Do not modify schematics, PCB layouts, libraries, or approval records without explicit authorization.
- Propose design changes with technical justification before applying them.
- Never silently alter connectivity, component values, footprints, net names, or PCB geometry.

## Engineering Analysis

- Base analysis on project requirements, operating conditions, and design constraints.
- Prefer native CAD data for structured inspection; use visual evidence when necessary.
- Use deterministic tools for calculations and verification when appropriate.
- Verify component-specific claims against manufacturer datasheets and official documentation.
- Consider tolerances, operating limits, worst-case conditions, and design margins where relevant.
- Clearly distinguish verified facts, assumptions, estimates, and recommendations.
- Do not invent specifications, design parameters, or measurement results.

## Verification

- ERC/DRC PASS does not guarantee electrical or functional correctness.
- Support findings with traceable evidence, including component references, nets, calculations, or documentation.
- Distinguish confirmed defects from potential risks and unverified concerns.
- Report `NOT_VERIFIED` when evidence is insufficient or a verification method is unavailable.
- Do not infer physical connectivity, clearance compliance, or electrical performance solely from incomplete CAD data.
- Identify issues requiring human inspection, simulation, or physical measurement.

## Context Efficiency

- Inspect only the relevant components, nets, sheets, or PCB areas needed for the task.
- Prefer targeted queries over loading entire schematics, netlists, BOMs, or datasheets.
- Expand inspection scope when required to establish sufficient evidence.
- Avoid redundant analysis, excessive tool calls, and unnecessary reports.
- Reuse verified project context when it remains applicable.

## Output

- Keep responses concise, technical, and actionable.
- Prioritize confirmed critical issues and high-impact risks.
- Reference relevant components, nets, locations, or sources when available.
- State significant assumptions, limitations, and verification gaps.
- Do not generate files unless explicitly requested or required for an authorized task.
