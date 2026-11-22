# Orch log

## Active run

## Knowledge

### Preferences

- The engineer lets Claude decide and build site improvements in web/; look changes and new features are shown to the user first. (from: 2026-11-22-web-improve)
- Keep web/log.md as the change record: one entry per change with what, why and files. (from: 2026-11-22-web-improve, 2026-11-22-handoff-next-idea)
- Phone layout is not critical for the site. (from: 2026-11-22-web-improve)
- The engineer exports the BOM by hand from KiCad (not with the jobset) into hardware/AO-Horizon/documents/manufacturing/Assembly/BOM/. File names vary (e.g. BOM_AO-Horizon_A_2026-11-22.csv), so the site reads the one *.csv there, any name. (from: 2026-11-22-handoff-next-idea)

### Environment

- PRs from dev to main are squash-merged; main needs linear history. After each squash, merge main into dev, or the next PR conflicts in files both sides touched (PR #60 conflicted on web/HANDOFF.md). (from: 2026-11-22-web-improve, 2026-11-22-handoff-next-idea)
- A merge to main that touches web/ deploys the site through .github/workflows/pages.yml; CI web-test.yml runs test:ui on PRs to main. Neither watches the BOM folder, so a BOM-only commit does not rebuild the site. (from: 2026-11-22-web-improve, 2026-11-22-handoff-next-idea)
- Worker scratch files go in web/.run.local/ (gitignored by `*.local`); scripts there must be .mjs or .cjs, because eslint lints .ts files there and no-console is an error. (from: 2026-11-22-web-improve)
- Full `npm run test:ui` takes about 9 to 12 minutes locally with Edge and serves dist on port 4174; build nothing while it runs. (from: 2026-11-22-web-improve)
- The web build needs exactly one CSV in hardware/AO-Horizon/documents/manufacturing/Assembly/BOM/; a fresh sparse clone for a CI-style test needs that folder too. The BOM export has no Footprint column today; the page shows it only if present. (from: 2026-11-22-handoff-next-idea)
- Generating a BOM or other schematic/PCB output is a human step (workflow.md). (from: 2026-11-22-handoff-next-idea)
- sch-inspect does not show the dnp or in_bom flags; read them from the saved .kicad_sch with a targeted grep (the hook allowed it). Saved DNP refs on 2026-11-22: D105, D106, R306. (from: 2026-11-22-handoff-next-idea)

### Lessons

- When a new test:ui check is added, prove it fails on the build before the change (copy the old dist to web/.run.local and run the check's page logic against it). Why: it caught checks that would have passed on broken code. (from: 2026-11-22-web-improve, 2026-11-22-handoff-next-idea)
- When the user grants merge permission with a condition, check the condition literally (mergeable, CI green, PR head equals the tested commit) and stop if it fails. Why: PR #60 was CONFLICTING; the user then approved the fix in one reply. (from: 2026-11-22-web-improve, 2026-11-22-handoff-next-idea)
- When committing, follow the project CLAUDE.md over the attribution reminder: no Co-Authored-By lines. Why: c437c20 got one by mistake. (from: 2026-11-22-web-improve)
- When workers start preview servers for old builds, check ports 4173 to 4177 before the final test:ui and stop leftovers by their command line. Why: three T1 servers were still running after the worker reported them stopped. (from: 2026-11-22-handoff-next-idea)
- When a BOM CSV comes from a schematic with uncommitted edits, ask before committing it alone. Why: the BOM on main could differ from the committed schematic; the user chose to commit both. (from: 2026-11-22-handoff-next-idea)

## Log

### [2026-11-22] run | web-improve

Goal: improve the team website in web/ (fixes, user-picked look changes and features). Outcome: done. Tasks: 11. Fix rounds: 4.
Problems: Co-Authored-By trailer on c437c20 (one-off, kept out of main by an explicit squash body); PR #60 conflicted because PR #59 was never merged back into dev (now an Environment entry); session scratchpad vanished mid-run (workers moved to web/.run.local).
Knowledge: added 3 Preferences, 4 Environment entries, 3 Lessons (reconstructed after the run; this log file did not exist then).

### [2026-11-22] run | handoff-next-idea

Goal: do the next HANDOFF idea (BOM page) and fix two known site gaps; commit, push and merge allowed. Outcome: done. Tasks: 3. Fix rounds: 0.
Problems: the BOM idea was blocked until the engineer exported a CSV (three exports: no delimiters, then no DNP, then usable); the engineer's schematic edits were uncommitted (user chose to commit them, b19c89c); three leftover preview servers from a worker (now a Lesson). PR #61 merged as 416cafc, deployed, main merged into dev.
Knowledge: added 1 Preference (hand BOM export, any file name), 3 Environment entries (BOM folder rule, BOM-only commits do not deploy, DNP flags via grep), 2 Lessons (leftover servers, BOM vs uncommitted schematic); widened 3 entries with this run id.
