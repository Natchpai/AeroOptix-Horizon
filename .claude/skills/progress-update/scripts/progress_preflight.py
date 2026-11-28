#!/usr/bin/env python3
"""Deterministic preflight for progress-update: one compact JSON for the model.

Read-only. Python 3.10+ standard library only. Works on any git repo with a
KiCad 6 or later project. Covers the steps whose inputs decide the output:
baseline since a ref, schematic part checks, library symbol, footprint and 3D
checks, an optional datasheet pin-text check, and doc checks (em dashes, spec
IDs, tracker rows or, with no tracker table, a checklist task named in each
open spec row, relative links), and a review of open items, task status
and the summary lists (`review:*` findings, INFO only; review_items()).
The change tier (0 cosmetic, 1 fields, 2 connectivity) comes from the sibling
sch-inspect `diff` against --since, with ERC when the tier asks for it.
Parts whose schematic `STATUS` field is `CHECKED` were checked by the human
(symbol pins, footprint, 3D model): their library checks are skipped.
Judgement (what changed, DECISION vs DRAWN, doc text, whether to close an
item) stays with the model and the human. Connectivity is out of scope: use
sch-inspect for nets and power sources.

Usage:
    python -I progress_preflight.py [--project <file.kicad_pro>] [--since <ref>]
        [--spec <md>] [--checklist <md>] [--id-prefixes DEC,OPEN,...]
        [--open-prefix OPEN] [--dec-prefix DEC] [--tracker-prefix OI]
        [--pin-text SYMBOL=fulltext.txt ...] [--findings-only] [--tier-only]
        [--no-tier] [--verbose]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from list_symbols import LCSC_KEYS, children, first, head, parse  # noqa: E402
import register  # noqa: E402

EM_DASH = "\u2014"
MPN_KEYS = ("MFR.P/N", "MPN", "Manufacturer Part Number", "Manufacturer_Part_Number", "MFR Part #", "Part Number")
LINK_RE = re.compile(r"\]\(<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\)")
VAR_RE = re.compile(r"\$\{([A-Za-z0-9_]+)\}")
STOCK_VAR_RE = re.compile(r"KICAD(\d+)_(3DMODEL|FOOTPRINT|SYMBOL|TEMPLATE)_DIR")
STOCK_SUBDIR = {"3DMODEL": "3dmodels", "FOOTPRINT": "footprints", "SYMBOL": "symbols", "TEMPLATE": "template"}
MAX_LIBRARY_ENTRIES = 50
FIELD_NAMES = ("MFR", "MFR.P/N", "LCSC", "Footprint")
# .claude/ holds tool files and fixtures, -backups/ holds KiCad backups: not project docs.
MD_EXCLUDE = (":(exclude).claude/**", ":(exclude)**/*-backups/**", ":(exclude)*-backups/**")


def git(root: Path, *args: str) -> str:
    out = subprocess.run(["git", "-c", "core.quotePath=false", "-C", str(root), *args],
                         capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout


def load(path: Path) -> list:
    return parse(path.read_text(encoding="utf-8"))


def walk(node, name: str):
    if head(node) == name:
        yield node
    if isinstance(node, list):
        for c in node[1:]:
            yield from walk(c, name)


def props_of(node) -> dict:
    return {p[1]: p[2] for p in children(node, "property") if len(p) > 2}


def pick(p: dict, keys: tuple) -> str:
    return next((p[k] for k in keys if p.get(k)), "")


def kicad_share(major: str) -> Path:
    if os.name == "nt":
        return Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "KiCad" / f"{major}.0" / "share" / "kicad"
    if sys.platform == "darwin":
        return Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport")
    return Path("/usr/share/kicad")


def kicad_config() -> tuple[Path | None, str]:
    """Newest KiCad user config folder and its major version."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", "")) / "kicad"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Preferences" / "kicad"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "kicad"
    vers = sorted((d for d in base.glob("*") if re.fullmatch(r"\d+\.\d+", d.name)),
                  key=lambda d: tuple(int(x) for x in d.name.split(".")))
    return (vers[-1], vers[-1].name.split(".")[0]) if vers else (None, "")


def expand(uri: str, proj: Path, major: str) -> Path | None:
    """Resolve ${VAR} like KiCad: KIPRJMOD, the environment, then stock install dirs."""
    def sub(m: re.Match) -> str:
        var = m.group(1)
        if var == "KIPRJMOD":
            return str(proj)
        if var in os.environ:
            return os.environ[var]
        stock = STOCK_VAR_RE.fullmatch(var)
        if stock:
            return str(kicad_share(stock.group(1)) / STOCK_SUBDIR[stock.group(2)])
        if var == "KISYS3DMOD" and major:
            return str(kicad_share(major) / "3dmodels")
        return m.group(0)
    out = VAR_RE.sub(sub, uri)
    return None if "${" in out else Path(out)


def lib_table(path: Path | None, proj: Path, major: str, depth: int = 0) -> dict:
    """{nickname: uri}; follows KiCad 10 nested "Table" entries."""
    if path is None or not path.exists() or depth > 3:
        return {}
    root = next((n for n in load(path) if isinstance(n, list)), [])
    libs = {}
    for lib in children(root, "lib"):
        name, uri, typ = first(lib, "name"), first(lib, "uri"), first(lib, "type")
        if not (name and uri):
            continue
        if typ and typ[1] == "Table":
            libs.update(lib_table(expand(uri[1], proj, major), proj, major, depth + 1))
        else:
            libs[name[1]] = uri[1]
    return libs


def sheet_files(root_sch: Path) -> list[Path]:
    seen, todo = [], [root_sch.resolve()]
    while todo:
        f = todo.pop(0)
        if f in seen or not f.exists():
            continue
        seen.append(f)
        root = next((n for n in load(f) if head(n) == "kicad_sch"), [])
        for sh in children(root, "sheet"):
            sf = props_of(sh).get("Sheetfile")
            if sf:
                todo.append((f.parent / sf).resolve())
    return seen


class Ctx:
    def __init__(self, repo: Path, proj: Path, major: str, fp_libs: dict, sym_libs: dict,
                 global_tables: bool, finds: list):
        self.repo, self.proj, self.major = repo, proj, major
        self.fp_libs, self.sym_libs, self.global_tables = fp_libs, sym_libs, global_tables
        self.finds = finds
        self.refs: set = set()       # every placed reference (no "#" power symbols)
        self.fields: dict = {}       # BOM ref -> filled fields among FIELD_NAMES
        self.part_text: set = set()  # Value and MPN strings of placed parts
        self.status: dict = defaultdict(set)  # "sym:<nick:name>", "symname:<name>", "fp:<nick:name>" -> STATUS
        self.status_mtime: dict = {}  # same keys -> oldest save time of a sheet that holds them
        self.verbose = False

    def nickname(self, path: Path, libs: dict) -> str | None:
        """Library table nickname whose URI is this file or a folder that holds it."""
        path = path.resolve()
        for nick, uri in libs.items():
            lib = expand(uri, self.proj, self.major)
            if lib is not None and (lib.resolve() == path or lib.resolve() in path.parents):
                return nick
        return None

    def human_checked(self, key: str, lib_file: Path | None = None) -> bool:
        """Every placed part that uses this library item has STATUS CHECKED, and the
        library file was not saved after the sheet that holds the check."""
        vals = self.status.get(key)
        if not (vals and all(v.upper() == "CHECKED" for v in vals)):
            return False
        if lib_file is not None and lib_file.exists() and key in self.status_mtime:
            return lib_file.stat().st_mtime <= self.status_mtime[key]
        return True

    def footprint_file(self, fp: str) -> tuple[str, Path | None]:
        """("ok"|"no_nickname"|"unknown"|"unresolved"|"missing", path)."""
        nick, _, name = fp.partition(":")
        if nick not in self.fp_libs:
            return ("no_nickname" if self.global_tables else "unknown"), None
        lib = expand(self.fp_libs[nick], self.proj, self.major)
        if lib is None:
            return "unresolved", None
        mod = lib / f"{name}.kicad_mod"
        return ("ok" if mod.exists() else "missing"), mod

    def models(self, mod: Path, owner: str, quiet: bool = False) -> tuple[set, list]:
        fpt = next((n for n in load(mod) if isinstance(n, list)), [])
        missing = []
        for m in children(fpt, "model"):
            if len(m) < 2:
                continue
            path = expand(m[1], self.proj, self.major)
            if path is None:
                if not quiet:
                    self.finds.append(["INFO", "model_var_unset", owner, m[1]])
            elif not path.exists():
                missing.append(m[1])
                if not quiet:
                    self.finds.append(["MINOR", "model_missing", owner, m[1]])
        pads = {p[1] for p in children(fpt, "pad") if len(p) > 1 and p[1]}
        return pads, missing


def check_sheets(files: list[Path], changed: set, ctx: Ctx) -> list[dict]:
    out, lcsc, pwr_flag = [], defaultdict(set), False
    single_counts = {}
    links = defaultdict(list)  # (severity, check, item, detail) -> refs
    for path in files:
        root = next((n for n in load(path) if head(n) == "kicad_sch"), [])
        parts, unannotated, power_nets, no_fp = [], Counter(), set(), []
        for sym in children(root, "symbol"):
            lib_id = first(sym, "lib_id")
            if lib_id is None:
                continue
            lib_id, p = lib_id[1], props_of(sym)
            ref = p.get("Reference", "")
            if ref.startswith("#"):
                if lib_id.endswith(":PWR_FLAG") or p.get("Value") == "PWR_FLAG":
                    pwr_flag = True
                else:
                    power_nets.add(p.get("Value", ""))
                continue
            parts.append(ref)
            ctx.refs.add(ref)
            ctx.part_text |= {v for v in (p.get("Value", ""), pick(p, MPN_KEYS)) if v}
            status = p.get("STATUS", "").strip()
            keys = [f"sym:{lib_id}", f"symname:{lib_id.split(':', 1)[-1]}"]
            if p.get("Footprint"):
                keys.append(f"fp:{p['Footprint']}")
            saved = path.stat().st_mtime
            for k in keys:
                ctx.status[k].add(status)
                ctx.status_mtime[k] = min(saved, ctx.status_mtime.get(k, saved))
            in_bom = first(sym, "in_bom")
            bare_pad = "TestPoint" in lib_id or lib_id.endswith(":SolderPad")
            if not (in_bom and in_bom[1] == "no") and not bare_pad:
                filled = {k for k in FIELD_NAMES if p.get(k, "").strip() not in ("", "~")}
                ctx.fields[ref] = ctx.fields.get(ref, set()) | filled
            if ref.endswith("?"):
                unannotated[ref.rstrip("?")] += 1
            code = pick(p, LCSC_KEYS)
            if code:
                lcsc[code].add((p.get("Value", ""), pick(p, MPN_KEYS), path.name))
            nick = lib_id.split(":", 1)[0]
            if ctx.global_tables and nick not in ctx.sym_libs:
                links[("MINOR", "sym_nickname", nick, "nickname is in no symbol library table")].append(f"{path.name}:{ref}")
            fp = p.get("Footprint", "")
            board = first(sym, "on_board")
            if not fp:
                if not (board and board[1] == "no"):
                    no_fp.append(ref)
            elif ":" in fp:
                state, _ = ctx.footprint_file(fp)
                if state == "no_nickname":
                    links[("MAJOR", "footprint_unresolved", fp, "nickname is in no footprint library table")].append(f"{path.name}:{ref}")
                elif state == "missing":
                    links[("MAJOR", "footprint_missing", fp, "footprint file not found")].append(f"{path.name}:{ref}")
        labels = Counter(lb[1] for lb in children(root, "label") if len(lb) > 1)
        single = sorted(n for n, c in labels.items() if c == 1)
        if single and ctx.verbose:
            ctx.finds.append(["INFO", "single_use_labels", path.name, f"local labels used once (check with sch-inspect): {single}"])
        elif single:
            single_counts[path.name] = len(single)
        if unannotated:
            ctx.finds.append(["MINOR", "unannotated", path.name, dict(unannotated)])
        if no_fp:
            ctx.finds.append(["MINOR", "no_footprint_placed", path.name, f"board parts with an empty Footprint: {sorted(no_fp)}"])
        try:
            sheet = path.relative_to(ctx.proj).as_posix()
        except ValueError:  # a sheet stored outside the project folder
            sheet = path.as_posix()
        out.append({"sheet": sheet, "changed": path in changed,
                    "parts": len(parts), "unannotated": dict(unannotated),
                    "power_nets": sorted(power_nets)})
    if single_counts:
        # Mostly stub labels on spare pins: one count line unless --verbose asks for names.
        ctx.finds.append(["INFO", "single_use_labels", f"{len(single_counts)} sheets",
                          f"{sum(single_counts.values())} local labels used once; names with --verbose"])
    for (sev, check, item, detail), refs in links.items():
        ctx.finds.append([sev, check, item, f"{detail}; used by {refs}"])
    for code, vals in lcsc.items():
        if len({v[:2] for v in vals}) > 1:
            ctx.finds.append(["MAJOR", "lcsc_conflict", code, f"one LCSC code on {sorted(vals)}"])
    if any(s["parts"] for s in out) and not pwr_flag:
        ctx.finds.append(["INFO", "no_pwr_flag", "project", "no PWR_FLAG on any sheet; ERC may flag undriven power nets"])
    return out


def lib_symbols(sym_file: Path):
    lib = next((n for n in load(sym_file) if head(n) == "kicad_symbol_lib"), [])
    for top in children(lib, "symbol"):
        pins = []
        for pin in walk(top, "pin"):
            name, num = first(pin, "name"), first(pin, "number")
            if name and num and len(pin) > 2:
                pins.append({"number": num[1], "name": name[1]})
        yield top[1], pins, props_of(top).get("Footprint", ""), first(top, "extends") is not None


def pin_row_found(number: str, name: str, text: str) -> bool:
    """A text line that starts with the pin number, then the first word of its name.

    KiCad markup (overbar ~{RESET}, subscript _{x}, superscript ^{x}) is dropped
    first, so the datasheet text may say ~RESET or RESET.
    """
    plain = re.sub(r"[~_^]\{([^}]*)\}", r"\1", name)
    token = re.escape(re.split(r"[/ ]", plain)[0])
    return bool(re.search(rf"(?im)^\W*{re.escape(number)}\W+{token}(?!\w)", text))


def check_library(sym_files: list[Path], mod_files: list[Path], pin_text: dict, ctx: Ctx) -> dict:
    out, no_fp = [], []
    for f in sym_files:
        for name, pins, fp, derived in lib_symbols(f):
            entry = {"symbol": name, "file": f.relative_to(ctx.repo).as_posix(), "pins": len(pins), "footprint": fp}
            nums = {p["number"] for p in pins}
            nick = ctx.nickname(f, ctx.sym_libs)
            # By nickname when the table names the file; else every placed part with this symbol name.
            key = f"sym:{nick}:{name}" if nick else f"symname:{name}"
            checked = ctx.human_checked(key, f)
            if checked:
                entry["human_checked"] = True
            elif ctx.human_checked(key):
                entry["human_check_older_than_file"] = True  # edited after the check: check again
            if derived:
                entry["derived"] = True
            elif fp and ":" in fp:
                state, mod = ctx.footprint_file(fp)
                if state == "ok":
                    pads, missing = ctx.models(mod, name, quiet=checked)
                    entry.update(pads=len(pads), models_missing=missing)
                    if pins and pads != nums and not checked:
                        ctx.finds.append(["MAJOR", "pin_pad_mismatch", name,
                                          {"pins_only": sorted(nums - pads), "pads_only": sorted(pads - nums)}])
                elif state != "unknown" and not checked:
                    ctx.finds.append(["MAJOR", "footprint_unresolved", name, f"{fp}: {state}"])
            else:
                no_fp.append(name)
            if name in pin_text and not checked:
                miss = []
                for p in pins:
                    if not pin_row_found(p["number"], p["name"], pin_text[name]):
                        miss.append(f"{p['number']}:{p['name']}")
                entry["pin_text_missing"] = miss
                if miss:
                    ctx.finds.append(["MINOR", "pin_text_mismatch", name, f"pin rows not found in datasheet text (heuristic): {miss}"])
            out.append(entry)
    for mod in mod_files:
        nick = ctx.nickname(mod, ctx.fp_libs) or mod.parent.name.removesuffix(".pretty")
        checked = ctx.human_checked(f"fp:{nick}:{mod.stem}", mod)
        _, missing = ctx.models(mod, mod.stem, quiet=checked)
        entry = {"footprint_file": mod.relative_to(ctx.repo).as_posix(), "models_missing": missing}
        if checked:
            entry["human_checked"] = True
        elif ctx.human_checked(f"fp:{nick}:{mod.stem}"):
            entry["human_check_older_than_file"] = True
        out.append(entry)
    if no_fp:
        ctx.finds.append(["INFO", "no_footprint", f"{len(no_fp)} symbols", f"Footprint property empty (generic parts?): {no_fp}"])
    unmatched = sorted(set(pin_text) - {e.get("symbol") for e in out})
    if unmatched:
        ctx.finds.append(["INFO", "pin_text_unused", ", ".join(unmatched), "no changed symbol has this name"])
    return {"checked": len(out), "entries": out[:MAX_LIBRARY_ENTRIES], "truncated": len(out) > MAX_LIBRARY_ENTRIES}


def strip_code(text: str) -> str:
    return re.sub(r"`[^`\n]*`", "", re.sub(r"(?ms)^```.*?^```", "", text))


def check_docs(repo: Path, since: str, mds: list[str], untracked: set, spec: Path | None,
               checklist: Path | None, id_prefixes: list, open_prefix: str, tracker_prefix: str,
               finds: list) -> dict:
    added = [ln for ln in git(repo, "diff", "-U0", since, "--", "*.md", *MD_EXCLUDE).splitlines()
             if ln.startswith("+") and not ln.startswith("+++")]
    mds = [p for p in mds if (repo / p).is_file()]  # a tracked file may be deleted
    for p in mds:
        if p in untracked:
            added += (repo / p).read_text(encoding="utf-8").splitlines()
    em = sum(EM_DASH in ln for ln in added)
    if em:
        finds.append(["MINOR", "em_dash", "*.md", f"{em} added lines contain an em dash"])
    defined = set()
    if spec and spec.exists():
        defined = register.records(spec.read_text(encoding="utf-8"), open_prefix).ids()
    if id_prefixes:
        prefixes = sorted(id_prefixes)
    else:
        # A requirement-style ID is short or zero-padded (DEC-001); part numbers
        # in a table's first column (ICM-45686) are not.
        num = defaultdict(list)
        for i in defined:
            pre, _, n = i.partition("-")
            num[pre].append(n)
        prefixes = sorted(k for k, ns in num.items() if any(len(n) <= 3 or n.startswith("0") for n in ns))
    defined = {i for i in defined if i.split("-")[0] in prefixes}
    id_re = re.compile(rf"\b(?:{'|'.join(map(re.escape, prefixes))})-\d+\b") if prefixes else None
    undefined, broken = set(), []
    for p in mds:
        md = repo / p
        text = strip_code(md.read_text(encoding="utf-8"))
        if id_re:
            undefined |= {(md.name, i) for i in id_re.findall(text) if i not in defined}
        for link in LINK_RE.findall(text):
            link = unquote(link)
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", link) or link.startswith(("/", "#")):
                continue
            if not (md.parent / link.split("#", 1)[0]).exists():
                broken.append(f"{p} -> {link}")
    for f, i in sorted(undefined):
        finds.append(["MINOR", "undefined_id", i, f"cited in {f}, not defined in the spec"])
    for b in broken:
        finds.append(["MINOR", "broken_link", b, ""])
    tracker, no_tracker = "skipped: no checklist", []
    if checklist and checklist.exists():
        rows = re.findall(rf"(?m)^\|\s*{re.escape(tracker_prefix)}-\d+\s*\|.*$", checklist.read_text(encoding="utf-8"))
        if rows:
            tracker = f"{len(rows)} {tracker_prefix} rows"
            opens = sorted(i for i in defined if i.startswith(f"{open_prefix}-"))
            no_tracker = [o for o in opens if not any(re.search(rf"\b{o}\b", r) for r in rows)]
            for o in no_tracker:
                finds.append(["MINOR", "no_tracker_row", o, f"open item has no checklist {tracker_prefix} row"])
        elif spec and spec.exists():
            # No tracker table: the spec's open-item table is the register, and
            # each open row must name a checklist task (first-column ID there).
            cl_reg = register.records(checklist.read_text(encoding="utf-8"), open_prefix)
            # Only active tasks count: a DONE or N/A (merged, retired) row closes nothing.
            tasks = {i for i, r in cl_reg.kind("task").items()
                     if not register.status_text(r.cells.get("status", "")).upper().startswith(("DONE", "N/A"))}
            open_rows = 0
            for oid, r in register.records(spec.read_text(encoding="utf-8"), open_prefix).kind("open").items():
                if register.is_closed(r.cells.get("desc", ""), r.cells.get("owner", "")):
                    continue
                open_rows += 1
                body = " | ".join(r.raw[1:])
                if not any(re.search(rf"\b{re.escape(t)}\b", body) for t in tasks):
                    no_tracker.append(oid)
                    finds.append(["MINOR", "open_without_task", oid,
                                  "open item names no checklist task, and the checklist has no "
                                  f"{tracker_prefix} table"])
            tracker = f"no {tracker_prefix} table; {open_rows} open spec rows checked for a checklist task"
        else:
            tracker = f"skipped: no {tracker_prefix}-n rows in the checklist and no spec"
    return {"md_files": len(mds), "em_dash_lines": em, "spec_ids": len(defined), "id_prefixes": prefixes,
            "undefined_ids": len(undefined), "broken_links": len(broken), "tracker_check": tracker,
            "open_without_tracker": no_tracker}


# ---------------------------------------------------------------------------
# Review of open items, task status and summary lists
# ---------------------------------------------------------------------------

ANY_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*-\d+\b")
DATE_RE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
MARKER_RE = re.compile(r"(?:Still open|Open|Left|left)\s*:")
CLOSED_STATUS = ("DONE", "N/A", "DEFERRED")
STATUS_RE = re.compile(r"^(OPEN|IN_PROGRESS|DONE|N/A|DEFERRED|BLOCKED)")
PENDING_RE = re.compile(r"(?i)\b(later|TBD|open|fill|not decided|not chosen|missing|empty|not filled)\b")
CLOSED_WORD_RE = re.compile(r"(?i)\b(closed?|closes|done|accepted|settled|resolved|replaced|was|were|cleared)\b")
REV_HEADER_RE = register.REV_HEADER_RE
REF_RANGE_RE = re.compile(r"\b([A-Z]{1,3})(\d+)\s+(?:to|-)\s+(?:\1)?(\d+)\b")
REF_RE = re.compile(r"\b([A-Z]{1,3})(\d{1,4})\b")
UNANNOTATED_RE = re.compile(r"\b([A-Z]{1,3})\?")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.;])\s+|\n")


def section(text: str, heading: str) -> str:
    """Body of the first '##' or '###' <heading> section, up to the next heading
    of the same or a higher level. Case-insensitive; a number such as '8.' or
    '8.2' before the heading text is allowed."""
    m = re.search(rf"(?mi)^(#{{2,3}})\s+(?:\d+(?:\.\d+)*\.?\s+)?{re.escape(heading)}\s*$", text)
    if not m:
        return ""
    level = len(m.group(1))
    nxt = re.search(rf"(?m)^#{{1,{level}}}\s", text[m.end():])
    return text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():]


def still_open(text: str) -> str:
    """Text after the last 'Still open:' / 'Open:' / 'Left:' marker, else all of it."""
    hits = list(MARKER_RE.finditer(text))
    return text[hits[-1].end():] if hits else text


def newest_date(text: str) -> str | None:
    dates = DATE_RE.findall(text)
    return max(dates) if dates else None


def field_words(clause: str) -> set:
    found = set()
    if "MFR.P/N" in clause:
        found.add("MFR.P/N")
    if re.search(r"\bMFR\b(?!\.P/N)", clause):
        found.add("MFR")
    if re.search(r"\bLCSC\b(?!\s*:?\s*C\d)", clause):  # "LCSC C7519" is a filled value
        found.add("LCSC")
    if re.search(r"(?i)\bfootprints?\b", clause) and re.search(r"(?i)\bfields?\b", clause):
        found.add("Footprint")
    return found


def named_refs(clause: str, refs: set) -> set:
    out = set()
    for pre, a, b in REF_RANGE_RE.findall(clause):
        lo, hi = int(a), int(b)
        if 0 < hi - lo <= 200:
            width = len(a)
            out |= {f"{pre}{n:0{width}d}" for n in range(lo, hi + 1)} & refs
    out |= {f"{p}{n}" for p, n in REF_RE.findall(clause)} & refs
    return out


ITEM_CITE_RE = re.compile(r"\b([A-Z][A-Z0-9]*-\d+)(\s+items?\s+\d+(?:\s*(?:,|and|to)\s*\d+)*)?")
ROW_ITEM_RE = re.compile(r"\bitems?\s+(\d+(?:\s*(?:,|and|to)\s*\d+)*)|\((\d{1,2})\)")


def item_cites(text: str) -> dict:
    """{id: item numbers} for each ID whose every cite in text names items."""
    seen: dict = {}
    for m in ITEM_CITE_RE.finditer(text):
        nums = set(re.findall(r"\d+", m.group(2))) if m.group(2) else None
        prev = seen.get(m.group(1), set())
        seen[m.group(1)] = None if nums is None or prev is None else prev | nums
    return {i: n for i, n in seen.items() if n}


def row_items(text: str) -> set:
    out = set()
    for a, b in ROW_ITEM_RE.findall(text):
        out |= set(re.findall(r"\d+", a or b))
    return out


def review_items(spec_text: str, checklist_text: str, readme_text: str | None,
                 refs: set | None, fields: dict | None, rev_of,
                 open_prefix: str = "OPEN", dec_prefix: str = "DEC",
                 part_text: set | None = None) -> tuple[list, int]:
    """Findings that an open item, a task status or a summary line may be stale.

    Pure: text and data in, rows out. rev_of(name) returns the header revision of
    a Markdown record by file name, or None. refs/fields None skips the CAD rules.
    Every row is INFO and only a question for the human; nothing is changed here.
    """
    finds = []

    def add(rule, item, reason):
        finds.append(["INFO", f"review:{rule}", item, reason])

    # --- parse (register.py reads columns by header name, then by position)
    spec_reg = register.records(spec_text, open_prefix, dec_prefix)
    cl_reg = register.records(checklist_text, open_prefix, dec_prefix)
    opens = {}  # id -> (desc, owner, full row text, closed)
    for i, r in spec_reg.kind("open").items():
        desc, owner = r.cells.get("desc", ""), r.cells.get("owner", "")
        opens[i] = (desc, owner, r.text, register.is_closed(desc, owner))
    decs = {}  # id -> (date, cited ids, {cited id: item numbers, when every cite names items})
    for i, r in spec_reg.kind("dec").items():
        body = " | ".join(r.raw[1:])
        decs[i] = (newest_date(r.cells.get("date", "")) or newest_date(r.text),
                   set(ANY_ID_RE.findall(body)), item_cites(body))
    tasks = {}  # id -> (task text, status, evidence, full row)
    for i, r in cl_reg.kind("task").items():
        st = register.status_text(r.cells.get("status", "")).upper()
        if STATUS_RE.match(st):
            tasks[i] = (r.cells.get("task", ""), st, r.cells.get("evidence", ""), r.text)
    gates = {i: r.cells.get("status", "") for i, r in cl_reg.kind("gate").items()}

    def task_closed(tid):
        return tid in tasks and tasks[tid][1].startswith(CLOSED_STATUS)

    def task_done(tid):
        return tid in tasks and tasks[tid][1].startswith(("DONE", "N/A"))

    open_ids = [i for i, v in opens.items() if not v[3]]
    active = [t for t in tasks if not task_closed(t)]
    checked = len(open_ids) + len(tasks)

    # --- tasks_closed: every task an open item names is DONE or N/A
    # (a DEFERRED task parks the item; it does not settle it)
    for oid in open_ids:
        named = [t for t in ANY_ID_RE.findall(opens[oid][1]) if t in tasks]
        if named and all(task_done(t) for t in named):
            add("tasks_closed", oid, "owner tasks all closed: " + ", ".join(f"{t} {tasks[t][1].split()[0]}" for t in named))

    # --- newer_dec: a DEC on or after the row's newest date cites it, and the row does not cite the DEC
    def newer_decs(row_text, targets):
        nd = newest_date(row_text)
        if not nd:
            return []
        cited = set(ANY_ID_RE.findall(row_text))
        named = row_items(row_text)

        def hits(ids, items):
            # a cite that names items ("OPEN-031 item 5") only counts for a row that names one of them
            return any(t not in items or items[t] & named for t in ids & targets)
        return sorted(d for d, (date, ids, items) in decs.items()
                      if date and date >= nd and d not in cited and hits(ids, items))
    for oid in open_ids:
        for d in newer_decs(opens[oid][2], {oid}):
            add("newer_dec", oid, f"{d} ({decs[d][0]}) cites {oid}; the row does not cite {d}")
    for t in active:
        # the task itself, and the open items its still-open text waits on
        text = tasks[t][0]
        waits = {i for i in ANY_ID_RE.findall(still_open(text)) if i in opens} if MARKER_RE.search(text) else set()
        targets = {t} | waits
        for d in newer_decs(tasks[t][3], targets):
            via = sorted(decs[d][1] & targets)
            add("newer_dec", t, f"{d} ({decs[d][0]}) cites {', '.join(via)}; {t} does not cite {d}")

    # --- field_filled: text waits for a part field that is filled
    if fields:
        def check_fields(item, text):
            for clause in SENTENCE_SPLIT_RE.split(text):
                wanted = field_words(clause)
                if not wanted or not PENDING_RE.search(ANY_ID_RE.sub("", clause)):
                    continue
                scope = named_refs(clause, set(fields)) or set(fields)
                if all(wanted <= fields[r] for r in scope):
                    where = f"{len(scope)} named parts" if scope != set(fields) else f"all {len(scope)} BOM parts"
                    add("field_filled", item, f"{', '.join(sorted(wanted))} filled on {where}: \"{clause.strip()[:120]}\"")
                    return
        for oid in open_ids:
            check_fields(oid, still_open(opens[oid][0]))
        for t in active:
            check_fields(t, still_open(tasks[t][0]))

    # --- ref_missing: still-open text names a reference that is not drawn
    if refs:
        prefixes, blocks = defaultdict(list), defaultdict(set)
        for r in refs:
            m = re.fullmatch(r"([A-Z]{1,3})(\d+)", r)
            if m:
                prefixes[m.group(1)].append(len(m.group(2)))
                blocks[m.group(1)].add(int(m.group(2)) // 100)
        for oid in open_ids:
            text = ANY_ID_RE.sub("", still_open(opens[oid][0]))
            text = re.sub(r"`[^`]*`", "", text)
            bad = set()
            for pre, num in REF_RE.findall(text):
                # same digit count as drawn refs of that prefix: "Q10" (a question) and
                # "C7519" (an LCSC code) are not references when every Q or C ref has 3 digits
                # "H743" in the value "STM32H743VIT6" is a part name when no H ref is in the
                # 700s; "C104" in "GRM155R71C104KA88D" stays a ref when C101 is drawn
                part_name = (int(num) // 100 not in blocks[pre]
                             and any(f"{pre}{num}" in v for v in (part_text or ())))
                if (pre in prefixes and min(prefixes[pre]) <= len(num) <= max(prefixes[pre])
                        and f"{pre}{num}" not in refs and not part_name):
                    bad.add(f"{pre}{num}")
            bad |= {f"{pre}?" for pre in UNANNOTATED_RE.findall(text) if pre in prefixes}
            if bad:
                add("ref_missing", oid, f"not in the saved schematic: {sorted(bad)}")

    # --- rev_drift: a cited record revision differs from the record's header
    spec_rev = (REV_HEADER_RE.search(spec_text) or [None, None])[1]
    mention_re = re.compile(r"(?:\[([^\]]+\.md)\]\([^)]*\)|`([^`]+\.md)`)\s+rev\s+(\d+(?:\.\d+)+)")

    def check_revs(item, text):
        for a, b, rev in mention_re.findall(text):
            name = Path(a or b).name
            now = rev_of(name)
            if now and now != rev:
                add("rev_drift", item, f"cites {name} rev {rev}; the file is rev {now}")
    for t in active:
        check_revs(t, tasks[t][3])
    for oid in open_ids:
        check_revs(oid, opens[oid][0])
    head = "\n".join(checklist_text.splitlines()[:15])
    check_revs("checklist header", head)
    if readme_text and spec_rev:
        m = re.search(r"(?i)specification \(rev (\d+(?:\.\d+)+)", readme_text)
        if m and m.group(1) != spec_rev:
            add("rev_drift", "README", f"names spec rev {m.group(1)}; the spec is rev {spec_rev}")

    # --- status_mismatch: DONE without evidence; gate status against its tasks
    for t, (_, status, evidence, _) in tasks.items():
        if status.startswith("DONE") and evidence.strip() in ("", "-", "TBD"):
            add("status_mismatch", t, "DONE with no evidence record")
    for g, gstatus in gates.items():
        mine = [t for t in tasks if t.startswith(f"{g}-")]
        if not mine:
            continue
        if gstatus.startswith("OPEN") and all(task_closed(t) for t in mine):
            add("status_mismatch", g, f"gate OPEN but all {len(mine)} tasks are DONE, N/A or DEFERRED")
        if gstatus.startswith("DONE"):
            still = [t for t in mine if not task_closed(t)]
            if still:
                add("status_mismatch", g, f"gate DONE but tasks still active: {still}")

    # --- summary_cites_closed: a summary list calls a closed item open
    summaries = [("spec verdict", section(spec_text, "Current verdict")),
                 ("checklist next action", section(checklist_text, "Current next action"))]
    if readme_text:
        summaries.append(("README open items", section(readme_text, "Open Items")))
    for where, body in summaries:
        hits = set()
        for clause in SENTENCE_SPLIT_RE.split(body):
            if CLOSED_WORD_RE.search(ANY_ID_RE.sub("", clause)):
                continue
            for i in ANY_ID_RE.findall(clause):
                if (i in opens and opens[i][3]) or task_done(i):
                    hits.add(i)
        if hits:
            add("summary_cites_closed", where, f"cites closed items as open: {sorted(hits)}")

    return finds, checked


def find_doc(repo: Path, mds: list[str], name_key: str, heading_key: str | None) -> Path | None:
    mds = [p for p in mds if (repo / p).is_file()]
    hit = next((p for p in mds if name_key in Path(p).name.upper()), None)
    if hit is None and heading_key:
        for p in mds:
            h1 = next((ln for ln in (repo / p).read_text(encoding="utf-8").splitlines() if ln.startswith("# ")), "")
            if heading_key in h1.lower():
                hit = p
                break
    return repo / hit if hit else None


def pick_project(repo: Path, arg: str | None) -> Path:
    if arg:
        pro = Path(arg).resolve()
        if pro.is_dir():
            found = list(pro.glob("*.kicad_pro"))
            if len(found) != 1:
                raise RuntimeError(f"expected one .kicad_pro in {pro}, found {[f.name for f in found]}")
            pro = found[0]
        if not pro.exists():
            raise RuntimeError(f"project not found: {pro}")
        return pro
    listed = git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "*.kicad_pro").splitlines()
    # .claude/ holds tool fixtures (sch-inspect ships a test project), not the design
    pros = [repo / p for p in listed if "-backups/" not in p and not p.startswith(".claude/")]
    if not pros:
        raise RuntimeError("no .kicad_pro file in this git repo; pass --project")
    if len(pros) == 1:
        return pros[0]
    cwd = Path.cwd().resolve()
    here = [p for p in pros if p.parent in (cwd, *cwd.parents) and p.parent != repo]
    if len(here) == 1:
        return here[0]
    raise RuntimeError(f"expected one .kicad_pro, found {[p.relative_to(repo).as_posix() for p in pros]}; pass --project")


def compact(rec: dict) -> dict:
    """Drop empty lists, false flags and all-zero counts from a tier record."""
    out = {k: v for k, v in rec.items() if not (v is None or v is False or v == [])}  # keep tier 0
    if isinstance(out.get("counts"), dict) and not any(out["counts"].values()):
        out.pop("counts")
    return out


def change_tier(root_sch: Path, base: str, sheets: list[Path]) -> dict:
    """Tier from the sibling sch-inspect `diff` (saved files against `base`), with ERC when it asks."""
    script = Path(__file__).resolve().parents[2] / "sch-inspect" / "scripts" / "query_sch.py"
    if not script.is_file():
        return {"tier": "NOT_VERIFIED", "reason": "sch-inspect skill not installed"}
    try:
        spec = importlib.util.spec_from_file_location("_sch_inspect_query", script)
        q = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(q)
        outside = q.outside_sheets(root_sch, sheets)
        if outside:
            return {"tier": "NOT_VERIFIED", "reason": f"sheets outside the project folder: {outside[:5]}"}
        cli = q.find_kicad_cli()
        work = q.export_netlist(root_sch, cli, sheets)
        old = q.export_netlist_at(root_sch, base, cli)
        rec = q.diff_netlists(q.parse_netlist(old)[1], q.parse_netlist_parts(old),
                              q.parse_netlist(work)[1], q.parse_netlist_parts(work), 20)
        if rec["erc_recommended"]:
            rec["erc"] = q.run_erc(root_sch, cli, sheets)
        rec["base"] = base
        return compact(rec)
    except Exception as exc:  # any failure leaves the tier open, never blocks the doc checks
        return {"tier": "NOT_VERIFIED", "reason": f"{type(exc).__name__}: {exc}"[:300]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", help=".kicad_pro file or its folder; default: the only project in the repo")
    ap.add_argument("--since", help="git ref; default: last commit that touched the spec, else HEAD")
    ap.add_argument("--spec", help="spec Markdown; default: name contains SPEC, or H1 says Specification")
    ap.add_argument("--checklist", help="checklist Markdown; default: name contains CHECKLIST")
    ap.add_argument("--id-prefixes", type=lambda s: [x for x in s.split(",") if x], default=[],
                    help="spec ID prefixes, comma-separated; default: short or zero-padded IDs in table rows")
    ap.add_argument("--open-prefix", default="OPEN", help="spec ID prefix of open items (default OPEN)")
    ap.add_argument("--dec-prefix", default="DEC", help="spec ID prefix of decisions (default DEC)")
    ap.add_argument("--tracker-prefix", default="OI", help="checklist row prefix that tracks open items (default OI)")
    ap.add_argument("--pin-text", action="append", default=[], metavar="SYMBOL=FILE",
                    help="datasheet fulltext (e.g. NotebookLM source fulltext) to match pin rows against")
    ap.add_argument("--findings-only", action="store_true")
    ap.add_argument("--tier-only", action="store_true", help="print only the change tier and stop")
    ap.add_argument("--no-tier", action="store_true", help="skip the netlist diff (no kicad-cli run)")
    ap.add_argument("--verbose", action="store_true", help="full lists in INFO findings")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        repo = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip()).resolve()
        pro = pick_project(repo, args.project)
        proj, root_sch = pro.parent, pro.with_suffix(".kicad_sch")
        if not root_sch.exists():
            raise RuntimeError(f"root schematic not found: {root_sch.name}")
        untracked = set(git(repo, "ls-files", "--others", "--exclude-standard").splitlines())
        mds = sorted(p for p in git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "*.md").splitlines()
                     if not p.startswith(".claude/") and "-backups/" not in p and (repo / p).is_file())
        spec = Path(args.spec).resolve() if args.spec else find_doc(repo, mds, "SPEC", "specification")
        checklist = Path(args.checklist).resolve() if args.checklist else find_doc(repo, mds, "CHECKLIST", None)
        since = args.since
        if not since and spec and spec.relative_to(repo).as_posix() not in untracked:
            since = git(repo, "log", "-1", "--format=%h", "--", str(spec)).strip()
        since = since or "HEAD"
        git(repo, "rev-parse", "--verify", f"{since}^{{commit}}")
        rel = proj.relative_to(repo).as_posix()
        changed = [ln.split("\t") for ln in git(repo, "diff", "--name-status", since, "--", rel).splitlines()]
        changed_paths = [c[-1] for c in changed if not c[0].startswith("D")]
        changed_paths += [p for p in untracked if rel == "." or p.startswith(f"{rel}/")]
        changed_set = {(repo / p).resolve() for p in changed_paths}
        status = git(repo, "status", "--short", "--", rel).splitlines()
        tier = {"tier": "NOT_VERIFIED", "reason": "--no-tier"} if args.no_tier else \
            change_tier(root_sch, since, sheet_files(root_sch))
        if args.tier_only:
            print(json.dumps({"since": since, "uncommitted": status, "tier": tier}, indent=1, ensure_ascii=False))
            return 0
        pin_text = {}
        for item in args.pin_text:
            sym, _, f = item.partition("=")
            pin_text[sym] = Path(f).read_text(encoding="utf-8", errors="replace")

        cfg, major = kicad_config()
        fp_libs = lib_table(cfg / "fp-lib-table" if cfg else None, proj, major)
        sym_libs = lib_table(cfg / "sym-lib-table" if cfg else None, proj, major)
        global_tables = bool(fp_libs or sym_libs)
        fp_libs.update(lib_table(proj / "fp-lib-table", proj, major))
        sym_libs.update(lib_table(proj / "sym-lib-table", proj, major))
        finds: list = []
        ctx = Ctx(repo, proj, major, fp_libs, sym_libs, global_tables, finds)
        ctx.verbose = args.verbose
        sheets = check_sheets(sheet_files(root_sch), changed_set, ctx)
        live = [p for p in sorted(changed_set) if p.exists() and "-backups" not in p.as_posix()]
        library = check_library([p for p in live if p.suffix == ".kicad_sym"],
                                [p for p in live if p.suffix == ".kicad_mod"], pin_text, ctx)
        docs = check_docs(repo, since, mds, untracked, spec, checklist,
                          args.id_prefixes, args.open_prefix, args.tracker_prefix, finds)
        review = {"items_checked": 0, "findings": 0, "readme": "MISSING"}
        if spec and spec.exists() and checklist and checklist.exists():
            by_name = {Path(p).name: repo / p for p in mds}

            def rev_of(name: str) -> str | None:
                f = by_name.get(name)
                m = REV_HEADER_RE.search(f.read_text(encoding="utf-8")) if f and f.exists() else None
                return m.group(1) if m else None
            readme = repo / "README.md"
            spec_text, cl_text = spec.read_text(encoding="utf-8"), checklist.read_text(encoding="utf-8")
            rows, checked = review_items(
                spec_text, cl_text, readme.read_text(encoding="utf-8") if readme.exists() else None,
                ctx.refs, ctx.fields, rev_of, args.open_prefix, args.dec_prefix, ctx.part_text)
            rows += register.lint(spec_text, cl_text, rev_of, args.open_prefix, args.dec_prefix)
            finds.extend(rows)
            review = {"items_checked": checked, "findings": len(rows),
                      "readme": "README.md" if readme.exists() else "MISSING"}
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"verification": "NOT_VERIFIED", "error": str(exc)}))
        return 1

    limitations = ["Saved files only; the editor may hold unsaved changes",
                   "No connectivity or power-source tracing; use sch-inspect",
                   "pin_text check is a regex heuristic, not a datasheet review"]
    if not global_tables:
        limitations.append("No global KiCad library tables found: stock nicknames and footprints not checked")
    kinds = Counter(Path(p).suffix or Path(p).name for p in changed_paths)
    data = {
        "verification": "STRUCTURAL_CHECKS_ONLY",
        "limitations": limitations,
        "project": pro.relative_to(repo).as_posix(),
        "kicad_config_version": major or None,
        "kicad_open": any(proj.glob("~*.lck")),
        "spec": spec.relative_to(repo).as_posix() if spec else "MISSING",
        "checklist": checklist.relative_to(repo).as_posix() if checklist else "MISSING",
        "since": since,
        "tier": tier,
        "commits": git(repo, "log", "--oneline", f"{since}..HEAD").splitlines(),
        "changed_by_kind": dict(kinds),
        "uncommitted": status,
        "sheets": sheets,
        "library": library,
        "docs": docs,
        "review": review,
        "findings": [dict(zip(("severity", "check", "item", "detail"), f)) for f in finds],
    }
    if args.findings_only:
        data = {k: data[k] for k in ("since", "tier", "kicad_open", "findings")}
    print(json.dumps(data, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
