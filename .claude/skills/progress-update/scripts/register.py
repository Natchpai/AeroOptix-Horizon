#!/usr/bin/env python3
"""Shared reader for the ID tables of a hardware spec and checklist.

Read-only. Python 3.10+ standard library only. The Markdown files stay the
source; this module only reads them, the same way for every caller:

- parse_tables(text): every pipe table with its nearest heading, header,
  rows and line numbers (fenced code is skipped).
- records(text): the ID rows grouped by kind (open, dec, ref, task, gate,
  note, other). Columns are found by header name first (HEADER_ALIASES) and
  by position second, so a table with extra or renamed columns still reads.
- doc_revision(text) and lint(...): header revisions and structure checks.

CLI:
    python -I register.py lint --spec S.md --checklist C.md [--open-prefix OPEN]
        [--dec-prefix DEC] [--ref-prefix REF]
prints one JSON object with a "findings" list of [severity, check, item, detail].
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ID_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")
SEP_CELL_RE = re.compile(r"^:?-+:?$")  # GFM: one or more hyphens
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# Table detection is loose (bold or any case), so a non-canonical status still
# makes a task table and bad_status can flag it. TASK_STATUS_RE is the strict form.
STATUS_WORD_RE = re.compile(r"^(OPEN|IN_PROGRESS|DONE|N/A|DEFERRED|BLOCKED)", re.IGNORECASE)
TASK_STATUS_RE = re.compile(r"^(OPEN|IN_PROGRESS|DONE|N/A|DEFERRED|BLOCKED BY \S+)(?:\s|$|\()")
REV_RE = re.compile(r"\d+(?:\.\d+)+")
CLOSED_DATE_RE = re.compile(r"^Closed\s+20\d\d-\d\d-\d\d")
# Documented closed forms: description "Closed <date>: ..." (or "Closed: ..."),
# owner cell "Closed". "Closed-loop ..." is not a closed row.
CLOSED_DESC_RE = re.compile(r"^Closed(?:\s+20\d\d-\d\d-\d\d|\s*:)")
CLOSED_OWNER_RE = re.compile(r"^Closed(?![-\w])")
# Header revision: "**Revision:** 0.1" or a table row "| Revision | 0.1 |" /
# "| Document revision | 0.1 |" (cell names may be bold).
REV_HEADER_RE = re.compile(r"(?mi)^(?:\*\*Revision:\*\*\s*|\|\s*\**(?:Document\s+)?revision\**\s*\|\s*)(\d+(?:\.\d+)+)")
MD_NAME_RE = re.compile(r"([A-Za-z0-9_.\-]+\.md)\b")
LONG_TASK = 600

# Role -> header names that mean it (lower case, compared after stripping
# backticks and '*'). Position is the fallback when no header matches.
HEADER_ALIASES = {
    "open": {"desc": ("description", "item"), "impact": ("impact",),
             "owner": ("owner / next action", "owner")},
    "dec": {"topic": ("topic",), "choice": ("selected option", "decision"),
            "notes": ("notes", "alternatives / reasoning", "basis"),
            "date": ("date", "date / owner")},
    "ref": {"doc": ("source", "document / url", "document"),
            "rev": ("revision / date", "revision"), "purpose": ("purpose",)},
    "task": {"task": ("task",), "req": ("req",), "owner": ("owner",), "status": ("status",),
             "evidence": ("evidence required / link", "evidence")},
    "gate": {"name": ("name",), "exit": ("exit criterion", "exit"), "status": ("status",)},
    "note": {"rev": ("revision",), "date": ("date",), "desc": ("description",),
             "approved": ("approved by", "human-approved by (if applicable)", "human-approved by")},
}
# Roles of columns 1.. when the header names do not match (column 0 is the ID).
POSITION = {
    "open": ("desc", "impact", "owner"),
    "dec": ("topic", "choice", "notes", "date"),
    "ref": ("doc", "rev", "purpose"),
    "task": ("task", "req", "owner", "status", "evidence"),
    "gate": ("name", "exit", "status"),
    "note": ("date", "desc", "approved"),
}


@dataclass
class Table:
    heading: str
    header: list[str]
    rows: list[tuple[int, list[str]]]
    line: int


@dataclass
class Record:
    id: str
    kind: str
    cells: dict[str, str]
    raw: list[str]
    line: int
    heading: str

    @property
    def text(self) -> str:
        return " | ".join(self.raw)


@dataclass
class Register:
    by_kind: dict[str, dict[str, Record]] = field(default_factory=dict)
    duplicates: list[tuple[str, str, int, int]] = field(default_factory=list)  # kind, id, first, again

    def kind(self, k: str) -> dict[str, Record]:
        return self.by_kind.get(k, {})

    def ids(self) -> set[str]:
        """Every row ID of the form PREFIX-n (gates and change-note revisions excluded)."""
        return {i for recs in self.by_kind.values() for i in recs if ID_RE.match(i)}


def split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, cur, i = [], [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if s[i] == "|":
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(s[i])
        i += 1
    cells.append("".join(cur).strip())
    return cells


def _is_sep(line: str) -> bool:
    cells = split_row(line)
    return bool(cells) and all(SEP_CELL_RE.match(c.replace(" ", "")) for c in cells if c) and any(cells)


def parse_tables(text: str) -> list[Table]:
    lines = text.splitlines()
    tables, heading, fence, i = [], "", False, 0
    while i < len(lines):
        ln = lines[i]
        if ln.lstrip().startswith("```"):
            fence = not fence
            i += 1
            continue
        if fence:
            i += 1
            continue
        m = HEADING_RE.match(ln)
        if m:
            heading = m.group(2)
        if ln.lstrip().startswith("|") and i + 1 < len(lines) and _is_sep(lines[i + 1]):
            t = Table(heading, split_row(ln), [], i + 1)
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                t.rows.append((j + 1, split_row(lines[j])))
                j += 1
            tables.append(t)
            i = j
            continue
        i += 1
    return tables


def _norm(h: str) -> str:
    return re.sub(r"[`*_]", "", h).strip().lower()


def cell_id(c: str) -> str:
    """First-column ID without backticks or bold."""
    return c.strip("`* ")


def status_text(c: str) -> str:
    return c.strip("`* ")


def is_closed(desc: str, owner: str) -> bool:
    """True for an open-item row in a documented closed form."""
    return bool(CLOSED_DESC_RE.match(desc.strip()) or CLOSED_OWNER_RE.match(status_text(owner)))


def column_map(kind: str, header: list[str]) -> dict[str, int]:
    names = [_norm(h) for h in header]
    roles = POSITION[kind]
    cols = {r: n + 1 for n, r in enumerate(roles) if n + 1 < len(header)}
    taken = set()
    for role, aliases in HEADER_ALIASES[kind].items():
        hit = next((k for a in aliases for k, n in enumerate(names) if k > 0 and n == a and k not in taken), None)
        if hit is not None:
            cols[role] = hit
            taken.add(hit)
    return cols


def table_kind(t: Table, open_prefix: str, dec_prefix: str, ref_prefix: str) -> str:
    first = _norm(t.header[0]) if t.header else ""
    if first == "gate":
        return "gate"
    if first == "revision":
        return "note"
    ids = [cell_id(c[0]) for _, c in t.rows if c and ID_RE.match(cell_id(c[0]))]
    if not ids:
        return ""
    pre = {i.rsplit("-", 1)[0] for i in ids}
    if pre == {open_prefix}:
        return "open"
    if pre == {dec_prefix}:
        return "dec"
    if pre == {ref_prefix}:
        return "ref"
    names = [_norm(h) for h in t.header]
    if "status" in names:
        k = names.index("status")
        if any(len(c) > k and STATUS_WORD_RE.match(status_text(c[k])) for _, c in t.rows):
            return "task"
    return "other"


def records(text: str, open_prefix: str = "OPEN", dec_prefix: str = "DEC", ref_prefix: str = "REF") -> Register:
    reg = Register()
    for t in parse_tables(text):
        kind = table_kind(t, open_prefix, dec_prefix, ref_prefix)
        if not kind:
            continue
        cols = column_map(kind, t.header) if kind in POSITION else {}
        for line, cells in t.rows:
            if not cells or not cells[0]:
                continue
            rid = cell_id(cells[0])
            if kind == "gate":
                if not re.match(r"^[A-Z][A-Z0-9]*$", rid):
                    continue
            elif kind == "note":
                if not REV_RE.fullmatch(rid):
                    continue
            elif not ID_RE.match(rid):
                continue
            rec = Record(rid, kind, {r: (cells[k] if k < len(cells) else "") for r, k in cols.items()},
                         cells, line, t.heading)
            bucket = reg.by_kind.setdefault(kind, {})
            if rid in bucket:
                reg.duplicates.append((kind, rid, bucket[rid].line, line))
                continue
            bucket[rid] = rec
    return reg


def doc_revision(text: str) -> str | None:
    m = REV_HEADER_RE.search(text)
    return m.group(1) if m else None


def _rev_key(rev: str) -> tuple:
    return tuple(int(x) for x in rev.split("."))


def ref_doc_name(cell: str) -> str | None:
    m = MD_NAME_RE.search(cell)
    return Path(m.group(1)).name if m else None


def lint(spec_text: str, checklist_text: str | None, rev_of=None,
         open_prefix: str = "OPEN", dec_prefix: str = "DEC", ref_prefix: str = "REF") -> list[list]:
    """Structure findings. rev_of(name) returns a record's header revision or None."""
    finds = []
    spec = records(spec_text, open_prefix, dec_prefix, ref_prefix)
    cl = records(checklist_text, open_prefix, dec_prefix, ref_prefix) if checklist_text else Register()
    for reg in (spec, cl):
        # Only defining tables; requirement IDs also appear in plan and trace tables.
        for kind, rid, a, b in reg.duplicates:
            if kind in ("open", "dec", "ref", "task", "gate"):
                finds.append(["INFO", "duplicate_id", rid, f"{kind} row defined again at line {b} (first at line {a})"])
            elif kind == "note" and reg is spec:
                finds.append(["MINOR", "rev_order", rid, f"change-note revision {rid} again at line {b} (first at line {a})"])
    for rid, r in cl.kind("task").items():
        st = r.cells.get("status", "").strip("` ")
        if not TASK_STATUS_RE.match(st):
            finds.append(["MINOR", "bad_status", rid, f"status {st!r} is not one of OPEN, IN_PROGRESS, "
                                                       "BLOCKED BY <ID>, DEFERRED, DONE, N/A"])
    for rid, r in spec.kind("open").items():
        desc, owner = r.cells.get("desc", ""), r.cells.get("owner", "")
        if is_closed(desc, owner) and not CLOSED_DATE_RE.match(desc.strip()):
            finds.append(["INFO", "closed_no_date", rid, "closed row does not start with 'Closed <YYYY-MM-DD>:'"])
    notes = list(spec.kind("note"))
    for a, b in zip(notes, notes[1:]):
        if _rev_key(b) <= _rev_key(a):
            finds.append(["MINOR", "rev_order", b, f"change-note revision {b} follows {a}"])
    head = doc_revision(spec_text)
    if notes and head and _rev_key(max(notes, key=_rev_key)) != _rev_key(head):
        finds.append(["MINOR", "rev_order", "spec header",
                      f"Document revision {head}, newest change-note row {max(notes, key=_rev_key)}"])
    if rev_of:
        for rid, r in spec.kind("ref").items():
            name = ref_doc_name(r.cells.get("doc", ""))
            m = REV_RE.search(r.cells.get("rev", ""))
            now = rev_of(name) if name else None
            if name and m and now and _rev_key(m.group(0)) != _rev_key(now):
                finds.append(["INFO", "review:rev_drift", rid, f"cites {name} rev {m.group(0)}; the file is rev {now}"])
    long = [rid for rid, r in cl.kind("task").items() if len(r.cells.get("task", "")) > LONG_TASK]
    if long:
        finds.append(["INFO", "long_task", f"{len(long)} tasks",
                      f"task text over {LONG_TASK} characters (keep the statement, 'Left:' and the current "
                      f"state; history goes to the spec change-note): {', '.join(long)}"])
    return finds


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    lp = sub.add_parser("lint", help="structure checks of the spec and checklist tables")
    lp.add_argument("--spec", required=True)
    lp.add_argument("--checklist")
    lp.add_argument("--open-prefix", default="OPEN")
    lp.add_argument("--dec-prefix", default="DEC")
    lp.add_argument("--ref-prefix", default="REF")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        spec = Path(args.spec)
        cl = Path(args.checklist) if args.checklist else None
        here = spec.resolve().parent

        def rev_of(name: str) -> str | None:
            f = here / name
            return doc_revision(f.read_text(encoding="utf-8")) if f.exists() else None
        finds = lint(spec.read_text(encoding="utf-8"), cl.read_text(encoding="utf-8") if cl else None,
                     rev_of, args.open_prefix, args.dec_prefix, args.ref_prefix)
    except (OSError, ValueError) as exc:
        print(json.dumps({"verification": "NOT_VERIFIED", "error": str(exc)}), file=sys.stderr)
        return 2
    out = {"verification": "STRUCTURAL_CHECKS_ONLY",
           "findings": [dict(zip(("severity", "check", "item", "detail"), f)) for f in finds]}
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
