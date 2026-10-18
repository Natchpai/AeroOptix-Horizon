#!/usr/bin/env python3
"""List placed symbols and labels in one KiCad 10 .kicad_sch file.

Read-only. Python 3.10+ standard library only. Prints reference, lib_id,
Value, Footprint, LCSC, DNP and instance references for every placed symbol,
plus every local, global and hierarchical label. Connectivity is out of scope:
use sch-inspect for that.

Usage:
    python -I list_symbols.py <sheet.kicad_sch> [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LCSC_KEYS = ("LCSC", "LCSC Part", "LCSC Part #", "JLCPCB Part #")
LABEL_KINDS = ("label", "global_label", "hierarchical_label")


def tokenize(text: str):
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c in "()":
            yield c
            i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            j, buf = i + 1, []
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n:
                    j += 1
                buf.append(text[j])
                j += 1
            yield ("str", "".join(buf))
            i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in '()"':
                j += 1
            yield ("atom", text[i:j])
            i = j


def parse(text: str) -> list:
    stack: list[list] = [[]]
    for tok in tokenize(text):
        if tok == "(":
            stack.append([])
        elif tok == ")":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(tok[1])
    if len(stack) != 1:
        raise ValueError("unbalanced parentheses")
    return stack[0]


def head(node) -> str | None:
    return node[0] if isinstance(node, list) and node and isinstance(node[0], str) else None


def children(node, name: str):
    return [c for c in node[1:] if head(c) == name]


def first(node, name: str):
    found = children(node, name)
    return found[0] if found else None


def collect(path: Path) -> dict:
    tree = parse(path.read_text(encoding="utf-8"))
    root = next((n for n in tree if head(n) == "kicad_sch"), None)
    if root is None:
        raise ValueError("not a kicad_sch file")

    symbols = []
    for sym in children(root, "symbol"):
        lib_id = first(sym, "lib_id")
        if lib_id is None:
            continue
        props = {p[1]: p[2] for p in children(sym, "property") if len(p) > 2}
        dnp = first(sym, "dnp")
        refs = []
        inst = first(sym, "instances")
        if inst is not None:
            for proj in children(inst, "project"):
                for p in children(proj, "path"):
                    r = first(p, "reference")
                    if r is not None and len(r) > 1:
                        refs.append(r[1])
        symbols.append({
            "reference": props.get("Reference", ""),
            "instance_refs": sorted(set(refs)),
            "lib_id": lib_id[1] if len(lib_id) > 1 else "",
            "value": props.get("Value", ""),
            "footprint": props.get("Footprint", ""),
            "lcsc": next((props[k] for k in LCSC_KEYS if props.get(k)), ""),
            "dnp": bool(dnp is not None and len(dnp) > 1 and dnp[1] == "yes"),
            "power": props.get("Reference", "").startswith("#"),
        })

    labels = [{"kind": kind, "name": lbl[1]}
              for kind in LABEL_KINDS
              for lbl in children(root, kind) if len(lbl) > 1]

    return {
        "file": str(path),
        "verification": "STRUCTURAL_LISTING_ONLY",
        "limitations": [
            "Saved file only; the editor may hold unsaved changes",
            "No connectivity; use sch-inspect local-net for pin nets",
        ],
        "symbol_count": sum(not s["power"] for s in symbols),
        "power_symbol_count": sum(s["power"] for s in symbols),
        "symbols": symbols,
        "labels": labels,
    }


def print_table(data: dict) -> None:
    print(f"# {data['file']}")
    print(f"# {data['symbol_count']} symbols, {data['power_symbol_count']} power symbols, "
          f"{len(data['labels'])} labels ({data['verification']})")
    for s in sorted(data["symbols"], key=lambda s: (s["power"], s["lib_id"], s["value"])):
        refs = ",".join(s["instance_refs"]) or s["reference"]
        flags = " DNP" if s["dnp"] else ""
        print(f"{refs:8} | {s['lib_id']} | {s['value']} | {s['footprint']} | {s['lcsc']}{flags}")
    for lbl in data["labels"]:
        print(f"{lbl['kind']:18} | {lbl['name']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("sheet", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        data = collect(args.sheet)
    except (OSError, ValueError) as exc:
        print(json.dumps({"file": str(args.sheet), "verification": "NOT_VERIFIED",
                          "error": str(exc)}))
        return 1
    if args.json:
        print(json.dumps(data, indent=1, ensure_ascii=False))
    else:
        print_table(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
