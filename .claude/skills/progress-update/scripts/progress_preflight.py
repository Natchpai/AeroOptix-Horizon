#!/usr/bin/env python3
"""Deterministic preflight for progress-update: one compact JSON for the model.

Read-only. Python 3.10+ standard library only. Works on any git repo with a
KiCad 6 or later project. Covers the steps whose inputs decide the output:
baseline since a ref, schematic part checks, library symbol, footprint and 3D
checks, an optional datasheet pin-text check, and doc checks (em dashes, spec
IDs, tracker rows, relative links). Judgement (what changed, DECISION vs
DRAWN, doc text) stays with the model. Connectivity is out of scope: use
sch-inspect for nets and power sources.

Usage:
    python -I progress_preflight.py [--project <file.kicad_pro>] [--since <ref>]
        [--spec <md>] [--checklist <md>] [--id-prefixes DEC,OPEN,...]
        [--open-prefix OPEN] [--tracker-prefix OI]
        [--pin-text SYMBOL=fulltext.txt ...] [--findings-only]
"""
from __future__ import annotations

import argparse
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

EM_DASH = "\u2014"
MPN_KEYS = ("MPN", "Manufacturer Part Number", "Manufacturer_Part_Number", "MFR Part #", "Part Number")
ROW_ID_RE = re.compile(r"(?m)^\|\s*([A-Z][A-Z0-9]*-\d+)\s*\|")
LINK_RE = re.compile(r"\]\(<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\)")
VAR_RE = re.compile(r"\$\{([A-Za-z0-9_]+)\}")
STOCK_VAR_RE = re.compile(r"KICAD(\d+)_(3DMODEL|FOOTPRINT|SYMBOL|TEMPLATE)_DIR")
STOCK_SUBDIR = {"3DMODEL": "3dmodels", "FOOTPRINT": "footprints", "SYMBOL": "symbols", "TEMPLATE": "template"}
MAX_LIBRARY_ENTRIES = 50


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

    def models(self, mod: Path, owner: str) -> tuple[set, list]:
        fpt = next((n for n in load(mod) if isinstance(n, list)), [])
        missing = []
        for m in children(fpt, "model"):
            if len(m) < 2:
                continue
            path = expand(m[1], self.proj, self.major)
            if path is None:
                self.finds.append(["INFO", "model_var_unset", owner, m[1]])
            elif not path.exists():
                missing.append(m[1])
                self.finds.append(["MINOR", "model_missing", owner, m[1]])
        pads = {p[1] for p in children(fpt, "pad") if len(p) > 1 and p[1]}
        return pads, missing


def check_sheets(files: list[Path], changed: set, ctx: Ctx) -> list[dict]:
    out, lcsc, pwr_flag = [], defaultdict(set), False
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
        if single:
            ctx.finds.append(["INFO", "single_use_labels", path.name, f"local labels used once (check with sch-inspect): {single}"])
        if unannotated:
            ctx.finds.append(["MINOR", "unannotated", path.name, dict(unannotated)])
        if no_fp:
            ctx.finds.append(["MINOR", "no_footprint_placed", path.name, f"board parts with an empty Footprint: {sorted(no_fp)}"])
        out.append({"sheet": path.relative_to(ctx.proj).as_posix(), "changed": path in changed,
                    "parts": len(parts), "unannotated": dict(unannotated),
                    "power_nets": sorted(power_nets)})
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


def check_library(sym_files: list[Path], mod_files: list[Path], pin_text: dict, ctx: Ctx) -> dict:
    out, no_fp = [], []
    for f in sym_files:
        for name, pins, fp, derived in lib_symbols(f):
            entry = {"symbol": name, "file": f.relative_to(ctx.repo).as_posix(), "pins": len(pins), "footprint": fp}
            nums = {p["number"] for p in pins}
            if derived:
                entry["derived"] = True
            elif fp and ":" in fp:
                state, mod = ctx.footprint_file(fp)
                if state == "ok":
                    pads, missing = ctx.models(mod, name)
                    entry.update(pads=len(pads), models_missing=missing)
                    if pins and pads != nums:
                        ctx.finds.append(["MAJOR", "pin_pad_mismatch", name,
                                          {"pins_only": sorted(nums - pads), "pads_only": sorted(pads - nums)}])
                elif state != "unknown":
                    ctx.finds.append(["MAJOR", "footprint_unresolved", name, f"{fp}: {state}"])
            else:
                no_fp.append(name)
            if name in pin_text:
                miss = []
                for p in pins:
                    token = re.escape(re.split(r"[/ ]", p["name"])[0])
                    if not re.search(rf"(?im)^\W*{re.escape(p['number'])}\W+{token}\b", pin_text[name]):
                        miss.append(f"{p['number']}:{p['name']}")
                entry["pin_text_missing"] = miss
                if miss:
                    ctx.finds.append(["MINOR", "pin_text_mismatch", name, f"pin rows not found in datasheet text (heuristic): {miss}"])
            out.append(entry)
    for mod in mod_files:
        _, missing = ctx.models(mod, mod.stem)
        out.append({"footprint_file": mod.relative_to(ctx.repo).as_posix(), "models_missing": missing})
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
    added = [ln for ln in git(repo, "diff", "-U0", since, "--", "*.md").splitlines()
             if ln.startswith("+") and not ln.startswith("+++")]
    for p in mds:
        if p in untracked:
            added += (repo / p).read_text(encoding="utf-8").splitlines()
    em = sum(EM_DASH in ln for ln in added)
    if em:
        finds.append(["MINOR", "em_dash", "*.md", f"{em} added lines contain an em dash"])
    defined = set()
    if spec and spec.exists():
        defined = set(ROW_ID_RE.findall(spec.read_text(encoding="utf-8")))
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
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", link) or link.startswith("/"):
                continue
            if not (md.parent / link).exists():
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
        else:
            tracker = f"skipped: no {tracker_prefix}-n rows in the checklist"
    return {"md_files": len(mds), "em_dash_lines": em, "spec_ids": len(defined), "id_prefixes": prefixes,
            "undefined_ids": len(undefined), "broken_links": len(broken), "tracker_check": tracker,
            "open_without_tracker": no_tracker}


def find_doc(repo: Path, mds: list[str], name_key: str, heading_key: str | None) -> Path | None:
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
    pros = [repo / p for p in listed if "-backups/" not in p]
    if not pros:
        raise RuntimeError("no .kicad_pro file in this git repo; pass --project")
    if len(pros) == 1:
        return pros[0]
    cwd = Path.cwd().resolve()
    here = [p for p in pros if p.parent in (cwd, *cwd.parents) and p.parent != repo]
    if len(here) == 1:
        return here[0]
    raise RuntimeError(f"expected one .kicad_pro, found {[p.relative_to(repo).as_posix() for p in pros]}; pass --project")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", help=".kicad_pro file or its folder; default: the only project in the repo")
    ap.add_argument("--since", help="git ref; default: last commit that touched the spec, else HEAD")
    ap.add_argument("--spec", help="spec Markdown; default: name contains SPEC, or H1 says Specification")
    ap.add_argument("--checklist", help="checklist Markdown; default: name contains CHECKLIST")
    ap.add_argument("--id-prefixes", type=lambda s: [x for x in s.split(",") if x], default=[],
                    help="spec ID prefixes, comma-separated; default: short or zero-padded IDs in table rows")
    ap.add_argument("--open-prefix", default="OPEN", help="spec ID prefix of open items (default OPEN)")
    ap.add_argument("--tracker-prefix", default="OI", help="checklist row prefix that tracks open items (default OI)")
    ap.add_argument("--pin-text", action="append", default=[], metavar="SYMBOL=FILE",
                    help="datasheet fulltext (e.g. NotebookLM source fulltext) to match pin rows against")
    ap.add_argument("--findings-only", action="store_true")
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
                     if not p.startswith(".claude/") and "-backups/" not in p)
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
        sheets = check_sheets(sheet_files(root_sch), changed_set, ctx)
        live = [p for p in sorted(changed_set) if p.exists() and "-backups" not in p.as_posix()]
        library = check_library([p for p in live if p.suffix == ".kicad_sym"],
                                [p for p in live if p.suffix == ".kicad_mod"], pin_text, ctx)
        docs = check_docs(repo, since, mds, untracked, spec, checklist,
                          args.id_prefixes, args.open_prefix, args.tracker_prefix, finds)
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
        "commits": git(repo, "log", "--oneline", f"{since}..HEAD").splitlines(),
        "changed_by_kind": dict(kinds),
        "uncommitted": status,
        "sheets": sheets,
        "library": library,
        "docs": docs,
        "findings": [dict(zip(("severity", "check", "item", "detail"), f)) for f in finds],
    }
    if args.findings_only:
        data = {k: data[k] for k in ("since", "kicad_open", "findings")}
    print(json.dumps(data, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
