#!/usr/bin/env python3
"""Read-only KiCad schematic discovery and conservative local, hierarchical, project net and bus evidence (v1.4.0).

Python 3.10+ standard library only. Never modifies project files. The
netlist commands run kicad-cli (or read an export the user made) and write
the export to a temporary folder only.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import math
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


class QueryError(Exception):
    pass


_STRUCTURAL_LIMITS = [
    'No electrical connectivity or pin-net verification',
    'Shared sheet files are not expanded into unique hierarchical instances',
    'Symbol reference properties can differ from instance references']
_INTERFACE_LIMITS = [
    'Parent sheet pins, other connected sheet pins, and wire/label paths are geometric/interface evidence only',
    'Destination child pins and labels are sheet-local evidence only; global labels, cross-sheet power nets, reused instances, buses and inherited symbols are not fully resolved',
    'Not a KiCad-equivalent full-project net resolver']
_BUS_LIMIT = ('Bus members join by name as in KiCad 10: a label with the member name on the bus sheet, '
              'a sheet pin to the hierarchical label of the same name, or a global bus label; bus entries are not needed. '
              'Bus-to-bus entries and member names held only by power symbols or sheet pins are not resolved')
PROJECT_NET_LIMITS = [
    'Conservative geometry and declared labels only; not KiCad netlist parity',
    'Complex symbol inheritance, hidden connectivity, and ambiguous unit instances may be unresolved',
    _BUS_LIMIT,
    'Starting reference with pins on multiple separate nets needs a pin-specific query']

_NETLIST_LIMITS = [
    "Read from KiCad's own netlist export of the saved files; unsaved editor changes are not included",
    'kicad-cli runs only for the netlist commands, which the user asks for; --netlist reads an export the user made',
    'Power and flag symbols (#PWR, #FLG) are not netlist nodes']

# One entry per command: the top-level `verification` value and `limitations`
# it prints. SKILL.md documents these values; a test keeps the two in sync.
MODES = {
    'summary': {'verification': 'STRUCTURAL_DISCOVERY_ONLY', 'limitations': _STRUCTURAL_LIMITS},
    'component': {'verification': 'STRUCTURAL_DISCOVERY_ONLY', 'limitations': _STRUCTURAL_LIMITS},
    'sheet': {'verification': 'STRUCTURAL_DISCOVERY_ONLY', 'limitations': _STRUCTURAL_LIMITS},
    'pins': {'verification': 'LOCAL_GEOMETRY_EVIDENCE_ONLY', 'limitations': [
        'Pin positions and direct wires are geometric evidence, not resolved electrical nets',
        'Labels on connected multi-segment paths may not be reported',
        'Hierarchical, global and power connectivity are not resolved']},
    'local-net': {'verification': 'SHEET_LOCAL_ONLY', 'limitations': [
        'Local wire paths and local-label names do not prove entire project connectivity',
        'Cross-sheet/global power-net connectivity, buses, inherited symbols and reused sheet instances are not resolved',
        'Geometric connectivity may differ from KiCad in complex edge cases']},
    'hier-net': {'verification': 'HIERARCHICAL_INTERFACE_EVIDENCE_ONLY', 'limitations': _INTERFACE_LIMITS},
    'connected-pins': {'verification': 'PARENT_CONNECTED_PINS_GEOMETRY_ONLY', 'limitations': _INTERFACE_LIMITS},
    'project-net': {'verification': 'INSTANCE_AWARE_PROJECT_EVIDENCE_ONLY', 'limitations': PROJECT_NET_LIMITS},
    'net': {'verification': 'INSTANCE_AWARE_PROJECT_EVIDENCE_ONLY', 'limitations': PROJECT_NET_LIMITS[:3] + [
        'The name is matched exactly against label and power symbol text, not against KiCad full net paths',
        'A local label repeated in several sheet instances gives one result per separate net',
        'Bus names are not net names; use the bus command for them']},
    'bus': {'verification': 'INSTANCE_AWARE_PROJECT_EVIDENCE_ONLY', 'limitations': [
        'Conservative geometry and declared labels only; not KiCad netlist parity',
        _BUS_LIMIT,
        'Members match by name inside a sheet, by short name (groups) or index (vectors) across a sheet pin, and by name across global bus labels',
        'Bus aliases come from the project file and from bus_alias forms in the sheets']},
    'components': {'verification': 'STRUCTURAL_DISCOVERY_ONLY', 'limitations': [
        'Structural list only; no electrical connectivity or pin-net verification',
        'A reference is resolved per sheet instance only when the symbol has exactly one matching instance path; otherwise the Reference property is shown',
        'References that start with # (power symbols, flags) are left out unless --prefix starts with #']},
    'instances': {'verification': 'HIERARCHICAL_INSTANCE_DISCOVERY_ONLY', 'limitations': [
        'Hierarchical sheet instance discovery only; no electrical connectivity or pin-net verification',
        'Lists sheet instances, not the components or references inside each instance',
        'Sheets that are missing or outside the project directory are not expanded']},
    'netlist': {'verification': 'KICAD_NETLIST_EVIDENCE', 'limitations': _NETLIST_LIMITS},
    'netlist-compare': {'verification': 'KICAD_NETLIST_COMPARISON', 'limitations': _NETLIST_LIMITS + [
        'Compares component pin sets only; net names differ by design (KiCad uses full sheet paths)',
        'Nets with one component pin (unconnected pins) are not compared',
        'A difference is a finding to read in KiCad, not proof that either tool is wrong']},
}


def forms(source: str):
    """Yield (form_name, source_slice) for direct children of an S-expression root.

    Strings, escapes and nested parentheses are recognized. Nested children are
    skipped without materializing the whole KiCad library-symbol tree.
    """
    n = len(source)
    depth = 0
    start = None
    quoted = False
    escaped = False
    i = 0
    while i < n:
        ch = source[i]
        if quoted:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                quoted = False
        elif ch == '"':
            quoted = True
        elif ch == '(':
            if depth == 1:
                start = i
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth < 0:
                raise QueryError('invalid S-expression: extra closing parenthesis')
            if depth == 1 and start is not None:
                j = start + 1
                while j < i and source[j].isspace():
                    j += 1
                k = j
                while k < i and not source[k].isspace() and source[k] not in '()':
                    k += 1
                yield source[j:k], source[start:i+1]
                start = None
        i += 1
    if quoted or depth != 0:
        raise QueryError('invalid or incomplete S-expression')


def parse(form: str):
    """Parse a selected, small S-expression, preserving quoted strings."""
    stack = []
    root = None
    i = 0
    n = len(form)
    while i < n:
        c = form[i]
        if c.isspace():
            i += 1
            continue
        if c == '(':
            new = []
            if stack:
                stack[-1].append(new)
            stack.append(new)
            if root is None:
                root = new
            i += 1
        elif c == ')':
            if not stack:
                raise QueryError('unbalanced expression')
            stack.pop()
            i += 1
        elif c == '"':
            i += 1
            out = []
            while i < n:
                if form[i] == '"':
                    i += 1
                    break
                if form[i] == '\\' and i+1 < n:
                    i += 1
                    mapping = {'n': '\n', 'r': '\r', 't': '\t', '"': '"', '\\': '\\'}
                    out.append(mapping.get(form[i], '\\'+form[i]))
                else:
                    out.append(form[i])
                i += 1
            else:
                raise QueryError('unterminated string')
            if not stack:
                raise QueryError('atom outside expression')
            stack[-1].append(''.join(out))
        else:
            j = i
            while j < n and not form[j].isspace() and form[j] not in '()':
                j += 1
            if not stack:
                raise QueryError('atom outside expression')
            stack[-1].append(form[i:j])
            i = j
    if stack or not isinstance(root, list):
        raise QueryError('invalid expression')
    return root


def children(expr, tag):
    return [x for x in expr[1:] if isinstance(x, list) and x and x[0] == tag]


def first(expr, tag):
    return next(iter(children(expr, tag)), None)


def val(expr, tag, default=None):
    x = first(expr, tag)
    return x[1] if x and len(x) > 1 else default


def properties(expr):
    return {p[1]: p[2] for p in children(expr, 'property') if len(p) > 2}


# Project name of the current query (the .kicad_pro stem); main() sets it.
# A copied project keeps old (project "...") instance entries; this one wins.
_PROJECT = {'name': None}


def instance_entry(instances, path):
    """The one instance entry for a sheet instance path, or None.

    When several entries share the path (a copied project), the entry of the
    current project wins.
    """
    matches = [x for x in instances if x.get('path') == path]
    if len(matches) > 1 and _PROJECT['name'] is not None:
        matches = [x for x in matches if x.get('project') == _PROJECT['name']]
    return matches[0] if len(matches) == 1 else None


def symbol_info(expr, file):
    p = properties(expr)
    instances = []
    inst = first(expr, 'instances')
    if inst:
        for project in children(inst, 'project'):
            project_name = project[1] if len(project) > 1 else None
            for path in children(project, 'path'):
                instances.append({'project': project_name, 'path': path[1] if len(path)>1 else None,
                                  'reference': val(path, 'reference'), 'unit': val(path, 'unit')})
    return {'file': str(file), 'reference_property': p.get('Reference'),
            'value': p.get('Value'), 'footprint': p.get('Footprint'),
            'lib_id': val(expr, 'lib_id'), 'uuid': val(expr, 'uuid'),
            'position': first(expr, 'at')[1:] if first(expr,'at') else None,
            'unit': val(expr, 'unit'), 'instances': instances, 'properties': p}


def sheet_info(expr, file):
    p = properties(expr)
    return {'parent_file': str(file), 'name': p.get('Sheetname'),
            'file': p.get('Sheetfile'), 'uuid': val(expr, 'uuid'),
            'pins': [pin[1] for pin in children(expr, 'pin') if len(pin)>1]}


# One entry per schematic file for the whole run: the file is read and
# scanned once. main() clears it, so a new query never sees old data.
_FILES = {}
_GEOMETRY_TAGS = ('lib_symbols', 'wire', 'bus', 'label', 'global_label',
                  'hierarchical_label', 'junction', 'no_connect')


def load_file(path: Path):
    """Read and scan a schematic once; return its parsed top-level forms.

    Symbols and sheets are parsed here. Geometry forms are kept as text and
    parsed on the first local_geometry() call, so a structural query does not
    parse the embedded library symbols.
    """
    key = str(path)
    cached = _FILES.get(key)
    if cached is not None:
        return cached
    try:
        source = path.read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError) as exc:
        raise QueryError(f'cannot read {path}: {exc}') from exc
    if not source.lstrip().startswith('(kicad_sch'):
        raise QueryError(f'not a KiCad schematic: {path}')
    symbols, sheets, geometry, aliases = [], [], [], []
    file_uuid = None
    for tag, fragment in forms(source):
        if tag == 'symbol':
            symbols.append(parse(fragment))
        elif tag == 'sheet':
            sheets.append(parse(fragment))
        elif tag == 'uuid':
            file_uuid = parse(fragment)[1]  # root UUID form is (uuid VALUE)
        elif tag in _GEOMETRY_TAGS:
            geometry.append((tag, fragment))
        elif tag == 'bus_alias':
            aliases.append(parse(fragment))
    cached = {'uuid': file_uuid, 'symbols': symbols, 'sheets': sheets,
              'geometry_forms': geometry, 'geometry': None, 'bus': None,
              'bus_aliases': aliases}
    _FILES[key] = cached
    return cached


def read_sheet(path: Path):
    loaded = load_file(path)
    return {'file': str(path), 'uuid': loaded['uuid'],
            'symbols': [symbol_info(expr, path) for expr in loaded['symbols']],
            'sheets': [sheet_info(expr, path) for expr in loaded['sheets']]}



def xy(expr, tag='at'):
    item = first(expr, tag)
    if item and len(item) >= 3:
        try:
            return (float(item[1]), float(item[2]))
        except (TypeError, ValueError):
            pass
    return None


def is_on_segment(point, a, b, tol=0.002):
    """Geometry proximity in schematic millimeters, not proof of net membership."""
    if not point or not a or not b:
        return False
    vx, vy = b[0] - a[0], b[1] - a[1]
    squared = vx * vx + vy * vy
    if squared < tol * tol:
        return math.dist(point, a) <= tol
    t = ((point[0]-a[0])*vx + (point[1]-a[1])*vy) / squared
    if t < -1e-7 or t > 1+1e-7:
        return False
    closest = (a[0]+max(0,min(1,t))*vx, a[1]+max(0,min(1,t))*vy)
    return math.dist(point, closest) <= tol


def at_segment_end(point, a, b, tol=0.002):
    """True when point is an end of segment a-b.

    KiCad joins a symbol pin or another segment's end to a segment only at
    the segment's ends; on the middle of a segment they stay apart unless a
    junction is there. Labels, junctions and sheet pins join anywhere on it.
    """
    return bool(point) and (math.dist(point, a) <= tol or math.dist(point, b) <= tol)


def pin_segments(point, wires, junctions):
    """Indexes of the wire segments a symbol pin connects to.

    A pin connects at a segment end, or on the middle of a segment only
    where a junction sits.
    """
    at_junction = bool(point) and any(j and math.dist(point, j) <= 0.002 for j in junctions)
    return [i for i, (a, b) in enumerate(wires)
            if at_segment_end(point, a, b) or (at_junction and is_on_segment(point, a, b))]


def local_geometry(path):
    """Load selected file geometry only. No netlist export or flattened connectivity."""
    loaded = load_file(path)
    if loaded['geometry'] is not None:
        return loaded['geometry']
    lib = {}
    wires, buses, labels, junctions, no_connects = [], [], [], [], []
    for tag, fragment in loaded['geometry_forms']:
        if tag == 'lib_symbols':
            tree = parse(fragment)
            for sym in children(tree, 'symbol'):
                if len(sym) > 1:
                    lib[sym[1]] = sym
        elif tag == 'wire':
            node = parse(fragment)
            pts = first(node, 'pts')
            p = [tuple(map(float, x[1:3])) for x in children(pts, 'xy')] if pts else []
            if len(p) >= 2:
                for a,b in zip(p, p[1:]):
                    wires.append((a,b))
        elif tag == 'bus':
            node = parse(fragment)
            pts = first(node, 'pts')
            p = [tuple(map(float, x[1:3])) for x in children(pts, 'xy')] if pts else []
            if len(p) >= 2:
                for a,b in zip(p, p[1:]):
                    buses.append((a,b))
        elif tag in ('label', 'global_label', 'hierarchical_label'):
            node = parse(fragment)
            labels.append({'kind':tag, 'name':node[1] if len(node)>1 else None, 'point':xy(node)})
        elif tag == 'junction':
            junctions.append(xy(parse(fragment)))
        elif tag == 'no_connect':
            no_connects.append(xy(parse(fragment)))
    # A label drawn on a bus is not a scalar-net label.  Bus expansion and
    # bus entries are deliberately unsupported, so excluding these labels is
    # safer than letting identical bus names union scalar local-net groups.
    on_bus = [bool(label['point']) and any(is_on_segment(label['point'], a, b) for a, b in buses)
              for label in labels]
    loaded['bus'] = (buses, [l for l, b in zip(labels, on_bus) if b])
    labels = [l for l, b in zip(labels, on_bus) if not b]
    loaded['geometry'] = (lib, wires, labels, junctions, no_connects)
    return loaded['geometry']


def bus_geometry(path):
    """Return (bus segments, labels on bus segments) of one schematic file."""
    local_geometry(path)
    return load_file(path)['bus']


# KiCad text escapes such as {slash} look like a one-member group.
_ESCAPE_TEXT = {'slash': '/', 'backslash': '\\', 'lt': '<', 'gt': '>', 'colon': ':',
                'dblquote': '"', 'quote': "'", 'comma': ',', 'tab': '\t', 'return': '\n',
                'brace': '{', 'space': ' ', 'pipe': '|', 'bar': '|', 'dollar': '$'}
_ESCAPES = set(_ESCAPE_TEXT)
_VECTOR = re.compile(r'^([^\[\]{}\s]*)\[(\d+)\.\.(\d+)\]$')
_GROUP = re.compile(r'^([^\[\]{}\s]*)\{([^{}]+)\}$')
# Text markup: ~{overbar}, _{subscript}, ^{superscript}. Part of a plain name.
_MARKUP = re.compile(r'([~_^])\{([^{}]*)\}')
_OPEN, _CLOSE = '\x01', '\x02'


def unescape(name):
    """Name with KiCad escapes ({slash}, {lt}, ...) decoded, for matching."""
    if not name or '{' not in name:
        return name
    return re.sub(r'\{([a-z]+)\}', lambda m: _ESCAPE_TEXT.get(m.group(1), m.group(0)), name)


def _hide_markup(name):
    """Replace markup braces so the bus patterns do not read them as groups."""
    while True:
        new = _MARKUP.sub(lambda m: m.group(1) + _OPEN + m.group(2) + _CLOSE, name)
        if new == name:
            return name
        name = new


def _show_markup(name):
    return name.replace(_OPEN, '{').replace(_CLOSE, '}')


def bus_members(name, aliases, _depth=0, _stack=()):
    """Expand a bus name into an ordered list of (key, member net name).

    Returns None for a scalar name. A vector P[a..b] gives Pa..Pb with key
    ('v', index). A group P{m1 m2} gives P.m1 (or m1 without a prefix) with
    key ('g', m1); a member may be a vector or an alias. An alias expands
    only inside braces: a bare alias name is a plain net name in KiCad 10.
    Keys match members across a sheet pin, as in KiCad: vectors by index,
    groups by short name. Text markup (~{X}, _{X}, ^{X}) is part of a name.
    """
    if not name or _depth > 8:
        return None
    hidden = _hide_markup(name)
    if hidden != name:
        found = bus_members(hidden, aliases, _depth, _stack)
        return [((k[0], _show_markup(k[1]) if isinstance(k[1], str) else k[1]), _show_markup(n))
                for k, n in found] if found else None
    m = _VECTOR.match(name)
    if m:
        prefix, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        if abs(a - b) > 4096:
            return None
        step = 1 if b >= a else -1
        return [(('v', i), f'{prefix}{i}') for i in range(a, b + step, step)]
    m = _GROUP.match(name)
    if not m or m.group(2).strip() in _ESCAPES:
        return None
    prefix, items = m.group(1), [x for x in re.split(r'[\s,]+', m.group(2)) if x]
    out = []
    for item in items:
        if item in aliases and item not in _stack:
            names = []
            for member in aliases[item]:
                sub = bus_members(member, aliases, _depth + 1, (*_stack, item))
                names += [n for _, n in sub] if sub else [member]
        else:
            sub = _VECTOR.match(item) and bus_members(item, aliases, _depth + 1)
            names = [n for _, n in sub] if sub else [item]
        for short in names:
            member = (('g', short), f'{prefix}.{short}' if prefix else short)
            if member not in out:
                out.append(member)
    return out or None


def load_bus_aliases(root, files):
    """Bus aliases: the project file first, then bus_alias forms in sheets.

    KiCad 10 keeps aliases in <project>.kicad_pro (schematic.bus_aliases).
    Older files keep (bus_alias "NAME" (members ...)) in a schematic; KiCad
    applies those to the whole project.
    """
    aliases = {}
    pro = root.with_suffix('.kicad_pro')
    if pro.is_file():
        try:
            data = json.loads(pro.read_text(encoding='utf-8-sig'))
        except (OSError, UnicodeError, ValueError) as exc:
            raise QueryError(f'cannot read bus aliases from {pro}: {exc}') from exc
        schematic = data.get('schematic') if isinstance(data, dict) else None
        raw = schematic.get('bus_aliases', {}) if isinstance(schematic, dict) else {}
        raw = {} if raw is None else raw
        if not isinstance(raw, dict):
            raise QueryError(f'bus_aliases in {pro} is not an object')
        for key, members in raw.items():
            if isinstance(members, list):
                aliases[str(key)] = [str(x) for x in members]
    for file in files:
        for form in load_file(file)['bus_aliases']:
            members = first(form, 'members')
            if len(form) > 1 and isinstance(form[1], str) and members:
                aliases.setdefault(form[1], [x for x in members[1:] if isinstance(x, str)])
    return aliases


def lib_definition(symbol, lib):
    """Return the embedded library symbol of a placed symbol, or None.

    KiCad writes (lib_name NAME) when placed symbols share a lib_id but
    differ, and stores that definition under the lib_name.
    """
    name = val(symbol, 'lib_name')
    if name is not None and name in lib:
        return lib[name]
    return lib.get(val(symbol, 'lib_id'))


def pins_from_symbol(symbol, lib, unit=None):
    """Return placed pin positions for common native KiCad symbols.

    Complex inheritance, unsupported pin transforms, or missing libraries are
    explicitly surfaced as limitations rather than silently marked connected.
    """
    libsym = lib_definition(symbol, lib)
    if not libsym:
        return [], [f"embedded lib symbol unavailable: {val(symbol, 'lib_name') or val(symbol, 'lib_id')}"]
    origins = xy(symbol)
    if not origins:
        return [], ['symbol placement missing']
    at = first(symbol, 'at')
    try:
        rotation = float(at[3]) if at and len(at) > 3 else 0.0
    except (ValueError, TypeError):
        return [], ['symbol rotation invalid']
    unit = str(unit) if unit is not None else str(val(symbol, 'unit', '1'))
    # (convert N) is the legacy name of (body_style N).
    style = str(val(symbol, 'body_style', val(symbol, 'convert', '1')))
    mirror = first(symbol, 'mirror')
    mirrored = mirror[1] if mirror and len(mirror)>1 else None
    if mirrored not in (None, 'x', 'y'):
        return [], [f'unsupported mirror mode: {mirrored}']
    if first(libsym, 'extends'):
        return [], ['inherited lib symbol pins are not resolved']
    pins=[]
    for subsym in children(libsym, 'symbol'):
        subname = subsym[1] if len(subsym)>1 else ''
        # KiCad sub-symbol naming convention: NAME_<unit>_<body style>.
        # 0 means shared by all units, or by all body styles.
        bits = subname.rsplit('_', 2)
        if len(bits) != 3 or bits[1] not in ('0', unit) or bits[2] not in ('0', style):
            continue
        for kind in ('pin',):
            for pin in children(subsym, kind):
                atpin = xy(pin)
                if not atpin:
                    continue
                px,py = atpin
                angle = math.radians(rotation)
                dx = px*math.cos(angle)-py*math.sin(angle)
                # Local Y positive up; schematic canvas Y positive down.
                dy = -(px*math.sin(angle)+py*math.cos(angle))
                # KiCad rotates first, then mirrors on the canvas axis. The
                # two orders only agree at 0 and 180 degrees.
                if mirrored == 'x':
                    dy=-dy
                elif mirrored == 'y':
                    dx=-dx
                x = origins[0]+dx
                y = origins[1]+dy
                num=first(pin, 'number')
                name=first(pin, 'name')
                pins.append({'number':num[1] if num and len(num)>1 else None,
                             'name':name[1] if name and len(name)>1 else None,
                             'position_mm':[round(x,4),round(y,4)]})
    return pins, ([] if pins else ['no pin definitions found for placed symbol unit'])


def power_symbol_anchors(path, lib):
    """Identify placed KiCad power symbols and their local pin anchors.

    Power is identified from the embedded library symbol's (power) marker,
    not from a name prefix or arbitrary symbol Value. This intentionally
    does not implement global power-net propagation across sheets.
    """
    result, warnings = [], []
    for expr in load_file(path)['symbols']:
        lib_id = val(expr, 'lib_id')
        definition = lib_definition(expr, lib)
        if definition is None or first(definition, 'power') is None:
            continue
        flag = first(definition, 'power')
        info = symbol_info(expr, path)
        pins, problems = pins_from_symbol(expr, lib)
        for problem in problems:
            warnings.append({'symbol_uuid': info['uuid'], 'reason': problem})
        name = info['value']
        if not name:
            warnings.append({'symbol_uuid': info['uuid'], 'reason': 'power symbol Value missing'})
            continue
        for pin in pins:
            result.append({'name': name, 'lib_id': lib_id,
                           'local': len(flag) > 1 and flag[1] == 'local',
                           'symbol_uuid': info['uuid'],
                           'position_mm': pin['position_mm']})
    return result, warnings


def resolve_local_networks(wires, labels, junctions, pin_points=(), mid_points=()):
    """Build sheet-local conductive groups as KiCad 10 does.

    A segment joins its two ends and every junction, label and mid point
    (sheet pin) on it. A symbol pin (pin_points) or another segment's end
    joins a segment only at that segment's end; on its middle they stay
    apart (checked with a KiCad 10.0.8 netlist). Crossings never join.
    Labels of any kind with the same name join on this sheet; global and
    hierarchical connections to other sheets are not resolved here.
    """
    precision = 4  # KiCad coordinates normally use 4 decimals, mm
    def key(p):
        return (round(p[0], precision), round(p[1], precision))
    parent = {}
    def add(p):
        k=key(p)
        if k not in parent:
            parent[k]=k
        return k
    def find(k):
        while parent[k]!=k:
            parent[k]=parent[parent[k]]
            k=parent[k]
        return k
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:
            parent[b]=a
    joiners = [p for p in junctions if p]
    joiners += [l['point'] for l in labels if l['point']]
    joiners += [p for p in mid_points if p]
    for p in [*joiners, *pin_points]:
        add(p)
    for a,b in wires:
        end=add(a)
        union(end, add(b))
        for p in joiners:
            if is_on_segment(p,a,b):
                union(end, add(p))
    names={}
    for label in labels:
        if label['point'] and label['name']:
            k=add(label['point'])
            if label['name'] in names:
                union(k,names[label['name']])
            else:
                names[label['name']]=k
    groups={}
    for label in labels:
        if label['point']:
            groups.setdefault(find(add(label['point'])),[]).append(label)
    return add,find,groups


def symbol_units(info):
    """Every unit a placed symbol uses: its own and each instance entry's."""
    own = str(info['unit'] or '1')
    return sorted({own} | {str(x['unit']) for x in info['instances'] if x.get('unit') is not None})


def queried_pins(expr, lib, info, reference):
    """Pins of the units the queried reference uses.

    In a reused sheet one placed symbol can be unit 1 as UM1 and unit 2 as UM2.
    Without an instance entry for the reference, the symbol's own unit.
    """
    units = sorted({str(x['unit']) for x in info['instances']
                    if x.get('reference') == reference and x.get('unit') is not None})
    pins, warnings, seen = [], [], set()
    for unit in units or [None]:
        found, problems = pins_from_symbol(expr, lib, unit)
        warnings += [p for p in problems if p not in warnings]
        for pin in found:
            key = (pin['number'], tuple(pin['position_mm']))
            if key not in seen:
                seen.add(key)
                pins.append(pin)
    return pins, warnings if not pins else [w for w in warnings if 'no pin definitions' not in w]


def pin_anchors(path, lib):
    """(position, symbol uuid) of every pin of every placed symbol on a sheet."""
    anchors = []
    for expr in load_file(path)['symbols']:
        info = symbol_info(expr, path)
        for unit in symbol_units(info):
            for pin in pins_from_symbol(expr, lib, unit)[0]:
                anchors.append((tuple(pin['position_mm']), info['uuid']))
    return anchors


def touches(point, anchors, owner):
    """True when a pin of another symbol sits on point (direct pin contact)."""
    return any(other != owner and math.dist(point, p) < .002 for p, other in anchors)


def inspect_pins(root, data, reference, limit, resolved=False):
    results=[]
    issues=[]
    geometry_cache={}
    for item in data:
        path=Path(item['file'])
        matches=[sym for sym in item['symbols'] if reference in ({sym['reference_property']} | {x['reference'] for x in sym['instances']})]
        if not matches:
            continue
        if path not in geometry_cache:
            geometry_cache[path]=local_geometry(path)
        lib,wires,labels,junctions,nc=geometry_cache[path]
        power_anchors, power_warnings = power_symbol_anchors(path, lib) if resolved else ([], [])
        wanted={m['uuid'] for m in matches}
        placed={}
        for expr in load_file(path)['symbols']:
            uid=val(expr,'uuid')
            if uid in wanted:
                placed[uid]=expr
        pins_by_uuid={}
        warnings_by_uuid={}
        all_positions=[]
        for m in matches:
            expr=placed.get(m['uuid'])
            if expr is None:
                issues.append('target symbol could not be resolved')
                continue
            pins, warnings=queried_pins(expr,lib,m,reference)
            pins_by_uuid[m['uuid']]=pins
            warnings_by_uuid[m['uuid']]=warnings
            issues.extend(warnings)
            all_positions.extend(tuple(p['position_mm']) for p in pins)
        power_positions = [tuple(p["position_mm"]) for p in power_anchors]
        anchors = pin_anchors(path, lib) if resolved else []
        add,find,groups=resolve_local_networks(wires,labels,junctions,
                                               all_positions+power_positions+[a for a, _ in anchors])
        for m in matches:
            if m['uuid'] not in pins_by_uuid:
                continue
            annotated=[]
            for pin in pins_by_uuid[m['uuid']]:
                pos=tuple(pin['position_mm'])
                attached=pin_segments(pos,wires,junctions)
                near_labels=[{'kind':l['kind'],'name':l['name']} for l in labels if l['point'] and (math.dist(pos,l['point']) < .002 or any(is_on_segment(l['point'], *wires[i]) for i in attached))]
                pin['local_wire_segments_at_pin']=len(attached)
                pin['candidate_labels_on_same_segment']=near_labels[:limit]
                pin['candidate_labels_truncated']=len(near_labels)>limit
                pin['no_connect_marker']=any(p and math.dist(pos,p)<.002 for p in nc)
                pin['connection_evidence']='DIRECT_GEOMETRY_ONLY'
                if resolved:
                    on_label = any(l['point'] and math.dist(pos,l['point']) < .002 for l in labels)
                    # A pin of another symbol (a power symbol too) placed on
                    # this pin joins it with no wire, as in KiCad.
                    contact = touches(pos, anchors, m['uuid'])
                    attached_network = bool(attached or on_label or contact)
                    connected_labels=groups.get(find(add(pos)),[]) if attached_network else []
                    local=sorted({l['name'] for l in connected_labels if l['kind']=='label' and l['name']})
                    interfaces=sorted({(l['kind'],l['name']) for l in connected_labels if l['kind']!='label' and l['name']})
                    pin['local_net_labels']=local[:limit]
                    pin['local_net_labels_truncated']=len(local)>limit
                    pin['interface_labels']=[{'kind':k,'name':n} for k,n in interfaces][:limit]
                    pin['interface_labels_truncated']=len(interfaces)>limit
                    pin['local_connection_status']=('NO_CONNECT_MARKER' if pin['no_connect_marker'] and not attached_network
                        else 'CONFLICTING_NO_CONNECT' if pin['no_connect_marker'] and attached_network
                        else 'LOCAL_WIRE_PATH' if attached else 'LABEL_ANCHOR_ONLY' if on_label
                        else 'PIN_CONTACT_ONLY' if contact
                        else 'NO_LOCAL_CONNECTION_FOUND')
                    pin['local_net_verified']=bool(local) and len(local)==1 and not interfaces and not pin['no_connect_marker']
                    # Power symbols are net-name evidence only on this sheet.
                    # Do not infer full global power-net resolution.
                    power_matches = []
                    if attached_network:
                        target_group = find(add(pos))
                        for power in power_anchors:
                            at_power = tuple(power['position_mm'])
                            if find(add(at_power)) == target_group and (
                                pin_segments(at_power, wires, junctions)
                                or math.dist(pos, at_power) < .002
                            ):
                                power_matches.append({
                                    'name': power['name'], 'source': power['lib_id'],
                                    'symbol_uuid': power['symbol_uuid'],
                                    'evidence': 'POWER_SYMBOL_ON_LOCAL_GRAPH'
                                })
                    power_matches.sort(key=lambda p: (p['name'], p['symbol_uuid'] or ''))
                    pin['power_nets'] = power_matches[:limit]
                    pin['power_nets_truncated'] = len(power_matches) > limit
                    pin['power_net_status'] = (
                        'LOCAL_POWER_SYMBOL_FOUND' if power_matches else 'NO_LOCAL_POWER_SYMBOL_FOUND'
                    )
                    pin['power_net_verified'] = False
                    pin['connection_evidence']='SHEET_LOCAL_GRAPH_ONLY'
                annotated.append(pin)
            results.append({'file':str(path),'symbol_uuid':m['uuid'],
                            'reference_property':m['reference_property'],
                            'instances':m['instances'][:limit],
                            'instances_truncated':len(m['instances'])>limit,
                            'pins':annotated[:limit],
                            'total_pins':len(annotated), 'pins_truncated':len(annotated)>limit,
                            'limitations':warnings_by_uuid[m['uuid']] + [x['reason'] for x in power_warnings]})
    return results,issues


def parent_sheet_interfaces(parent_file: Path, child_uuid: str):
    """Read only the named sheet object; its sheet pins are in parent coordinates."""
    for expr in load_file(parent_file)['sheets']:
        if val(expr, 'uuid') == child_uuid:
            result = []
            for pin in children(expr, 'pin'):
                if len(pin) > 1:
                    result.append({'name': pin[1], 'position': xy(pin),
                                   'uuid': val(pin, 'uuid')})
            return result
    return []


def connected_parent_pins(parent_file, wires, labels, junctions, origin, limit, instance_path=None):
    """Find other symbol pins in the same parent-side local wire network.

    With instance_path, each symbol gives the reference and unit of that
    sheet instance; without it, the Reference property and its own unit.
    Conservative sheet-local geometry only; never marks full electrical verification.
    """
    lib, _, _, _, _ = local_geometry(parent_file)
    candidates = []
    warnings = []
    for expr in load_file(parent_file)['symbols']:
        info = symbol_info(expr, parent_file)
        one = instance_entry(info['instances'], instance_path) if instance_path else None
        pins, pin_warnings = pins_from_symbol(expr, lib, one.get('unit') if one else None)
        for warning in pin_warnings:
            warnings.append({'symbol_uuid': info['uuid'], 'reason': warning})
        for pin in pins:
            candidates.append({'reference': one['reference'] if one else info['reference_property'],
                               'symbol_uuid': info['uuid'],
                               'pin_number': pin['number'], 'pin_name': pin['name'],
                               'position_mm': pin['position_mm'],
                               'instances': info['instances']})
    # Include other pins as graph anchors, but avoid connecting to a pin that
    # merely occupies a crossing of two unrelated segments.
    positions = [tuple(c['position_mm']) for c in candidates]
    anchors = [(tuple(c['position_mm']), c['symbol_uuid']) for c in candidates] + [(origin, None)]
    add, find, _ = resolve_local_networks(wires, labels, junctions, positions, [origin])
    connected = []
    network = find(add(origin))
    for c in candidates:
        pos = tuple(c['position_mm'])
        # A pin joins at a wire end or junction, on a label anchor, or on
        # another pin (or the origin) placed directly on it.
        joined = (pin_segments(pos, wires, junctions)
                  or any(l['point'] and math.dist(pos, l['point']) < .002 for l in labels)
                  or touches(pos, anchors, c['symbol_uuid']))
        if joined and find(add(pos)) == network:
            connected.append(c)
    connected.sort(key=lambda c: (c['reference'] or '', c['pin_number'] or '', c['symbol_uuid'] or ''))
    return {'connected_component_pins': connected[:limit],
            'total_connected_component_pins': len(connected),
            'connected_pins_truncated': len(connected) > limit,
            'unresolved_symbol_warnings': warnings[:limit],
            'unresolved_symbol_warning_count': len(warnings),
            'connectivity_evidence': 'PARENT_SHEET_LOCAL_GRAPH_ONLY',
            'connected_pins_verified': False}



def connected_parent_sheet_pins(parent_file, wires, labels, junctions, origin, source_sheet_uuid, source_pin_uuid, limit):
    """Identify OTHER sheet-symbol pins on the origin's parent-side wire graph.

    Reports local geometric evidence, not verified project connectivity.
    Source sheet/pin is excluded by UUID, not by label name.
    """
    candidates = []
    for sheet in load_file(parent_file)['sheets']:
        sheet_uuid = val(sheet, 'uuid')
        meta = properties(sheet)
        for pin in children(sheet, 'pin'):
            point = xy(pin)
            if point is None:
                continue
            pin_uuid = val(pin, 'uuid')
            if sheet_uuid == source_sheet_uuid and pin_uuid == source_pin_uuid:
                continue
            candidates.append({
                'sheet_name': meta.get('Sheetname'),
                'sheet_file': meta.get('Sheetfile'),
                'sheet_uuid': sheet_uuid,
                'pin_name': pin[1] if len(pin) > 1 else None,
                'pin_uuid': pin_uuid,
                'position_mm': [round(v, 4) for v in point],
            })
    positions = [tuple(item['position_mm']) for item in candidates]
    add, find, _ = resolve_local_networks(wires, labels, junctions, (), [origin, *positions])
    connected = []
    if any(is_on_segment(origin, a, b) for a, b in wires):
        network = find(add(origin))
        for item in candidates:
            point = tuple(item['position_mm'])
            if any(is_on_segment(point, a, b) for a, b in wires) and find(add(point)) == network:
                connected.append(item)
    connected.sort(key=lambda x: (x['sheet_name'] or '', x['pin_name'] or '', x['sheet_uuid'] or ''))
    return {
        'connected_sheet_pins': connected[:limit],
        'total_connected_sheet_pins': len(connected),
        'connected_sheet_pins_truncated': len(connected) > limit,
        'connected_sheet_pins_verified': False,
    }


def inspect_destination_sheet_pin(parent_file, endpoint, limit, root_dir, instance_path=None):
    """Trace a parent sheet pin to a SAME-NAMED hierarchical label in its child.

    Stops at one destination child level. A physical wire path is evidence,
    not a complete KiCad-equivalent net or electrical verification.
    """
    raw = endpoint.get('sheet_file')
    if not raw:
        return {'destination_status': 'SHEET_FILE_MISSING', 'destination_verified': False}
    child = (parent_file.parent / raw).resolve()
    try:
        child.relative_to(root_dir.resolve())
    except ValueError:
        return {'destination_status': 'OUTSIDE_PROJECT', 'destination_verified': False}
    if not child.is_file():
        return {'destination_status': 'SHEET_FILE_NOT_FOUND', 'destination_verified': False}
    lib, wires, labels, junctions, _ = local_geometry(child)
    matching = [label for label in labels if label['kind'] == 'hierarchical_label'
                and label['name'] == endpoint.get('pin_name') and label['point']]
    if not matching:
        return {'destination_status': 'HIERARCHICAL_LABEL_NOT_FOUND',
                'destination_file': str(child), 'destination_verified': False}
    results = []
    for label in matching[:limit]:
        point = label['point']
        hits = connected_parent_pins(child, wires, labels, junctions, point, limit, instance_path)
        add, find, groups = resolve_local_networks(wires, labels, junctions, (), [point])
        anchored = any(is_on_segment(point, a, b) for a, b in wires)
        same_network = groups.get(find(add(point)), []) if anchored else []
        global_names = sorted({x['name'] for x in same_network if x['kind'] == 'global_label' and x['name']})
        local_names = sorted({x['name'] for x in same_network if x['kind'] == 'label' and x['name']})
        results.append({
            'hierarchical_label': label['name'],
            'position_mm': list(point),
            'wire_at_label': anchored,
            'connected_component_pins': hits['connected_component_pins'],
            'total_connected_component_pins': hits['total_connected_component_pins'],
            'connected_pins_truncated': hits['connected_pins_truncated'],
            'unresolved_symbol_warnings': hits['unresolved_symbol_warnings'],
            'global_labels_on_local_path': global_names[:limit],
            'local_labels_on_path': local_names[:limit],
            'labels_on_path_truncated': len(global_names) > limit or len(local_names) > limit,
            'verification': 'DESTINATION_SHEET_LOCAL_GEOMETRY_ONLY',
        })
    return {'destination_status': 'CHILD_LOCAL_PATH_INSPECTED',
            'destination_file': str(child),
            'destination_paths': results,
            'destination_paths_truncated': len(matching) > limit,
            'destination_verified': False}


def hierarchical_trace(root: Path, data, reference: str, limit: int, discover_pins=False, max_instances=1000):
    """Trace child hierarchical-label anchors to matching parent sheet pins.

    This is *interface evidence*, not a KiCad-equivalent net resolver.
    Reused file instances are surfaced as ambiguous and never certified.
    """
    records, issues = inspect_pins(root, data, reference, limit, resolved=True)
    # Instance path of each file used exactly once, so that pins found on a
    # parent or destination sheet get the reference of that sheet instance.
    paths_of = {}
    if discover_pins:
        for node in build_instance_tree(root, data, max_instances):
            paths_of.setdefault(Path(node['file']), []).append(node['path'])
    def only_path(file):
        found = paths_of.get(Path(file).resolve(), [])
        return found[0] if len(found) == 1 else None
    parent_links = {}
    for item in data:
        parent = Path(item['file'])
        for sheet in item['sheets']:
            raw = sheet['file']
            if raw:
                child = (parent.parent / raw).resolve()
                parent_links.setdefault(child, []).append((parent, sheet))
    parent_cache = {}
    for record in records:
        file = Path(record['file']).resolve()
        links = parent_links.get(file, [])
        for pin in record['pins']:
            traces = []
            hier_names = [x['name'] for x in pin.get('interface_labels', [])
                          if x['kind'] == 'hierarchical_label']
            for name in sorted(set(hier_names)):
                if len(links) != 1:
                    traces.append({'hierarchical_label': name,
                                   'status': 'AMBIGUOUS_INSTANCE' if links else 'PARENT_NOT_FOUND',
                                   'possible_parent_count': len(links)})
                    continue
                parent, sheet = links[0]
                matching = [p for p in parent_sheet_interfaces(parent, sheet['uuid'])
                            if p['name'] == name]
                if len(matching) != 1 or matching[0]['position'] is None:
                    traces.append({'hierarchical_label': name,
                                   'status': 'PARENT_PIN_AMBIGUOUS_OR_MISSING',
                                   'matching_sheet_pins': len(matching)})
                    continue
                if parent not in parent_cache:
                    parent_cache[parent] = local_geometry(parent)
                _, wires, labels, junctions, _ = parent_cache[parent]
                at = matching[0]['position']
                add, find, groups = resolve_local_networks(wires, labels, junctions, (), [at])
                attached = any(is_on_segment(at, a, b) for a, b in wires)
                attached = attached or any(l['point'] and math.dist(l['point'], at) < .002 for l in labels)
                connected_labels = groups.get(find(add(at)), []) if attached else []
                trace = {'hierarchical_label': name,
                               'status': 'PARENT_LOCAL_PATH_FOUND' if attached else 'PARENT_PIN_UNCONNECTED_OR_UNRESOLVED',
                               'parent_file': str(parent),
                               'parent_sheet_name': sheet['name'],
                               'parent_sheet_uuid': sheet['uuid'],
                               'parent_pin_position_mm': [round(v,4) for v in at],
                               'parent_wire_segments_at_pin': sum(is_on_segment(at,a,b) for a,b in wires),
                               'parent_labels_on_path': [
                                   {'kind': l['kind'], 'name': l['name']}
                                   for l in connected_labels[:limit]],
                               'parent_labels_truncated': len(connected_labels) > limit,
                               'project_net_verified': False}
                if discover_pins:
                    parent_path = only_path(parent)
                    trace.update(connected_parent_pins(parent, wires, labels, junctions, at, limit, parent_path))
                    trace.update(connected_parent_sheet_pins(
                        parent, wires, labels, junctions, at,
                        sheet['uuid'], matching[0]['uuid'], limit))
                    for endpoint in trace['connected_sheet_pins']:
                        dest_path = (parent_path.rstrip('/') + '/' + endpoint['sheet_uuid']
                                     if parent_path and endpoint.get('sheet_uuid') else None)
                        endpoint.update(inspect_destination_sheet_pin(
                            parent, endpoint, limit, root.parent, dest_path))
                traces.append(trace)
            pin['hierarchical_traces'] = traces[:limit]
            pin['hierarchical_traces_truncated'] = len(traces) > limit
            pin['hierarchical_net_verified'] = False
        record['hierarchical_instance_status'] = (
            'UNIQUE_PARENT_FILE_LINK' if len(links)==1 else
            'REUSED_OR_MULTIPLE_PARENT_LINKS' if links else 'ROOT_OR_UNRESOLVED')
    return records, issues


def build_instance_tree(root, data, max_instances=1000):
    """Build physical hierarchical occurrences, not just distinct schematic files."""
    indexed = {Path(d['file']).resolve(): d for d in data}
    # KiCad's symbol instance paths start with the root schematic UUID.
    # Preserve it so references in reused sheet files resolve per instance.
    root_uuid = indexed[root.resolve()].get('uuid')
    root_path = '/' + root_uuid if root_uuid else '/'
    nodes = [{'path': root_path, 'file': str(root.resolve()), 'parent': None,
              'parent_sheet_uuid': None, 'parent_sheet_name': None}]
    queue = [0]
    while queue:
        idx = queue.pop(0)
        node = nodes[idx]
        for sh in indexed[Path(node['file'])]['sheets']:
            if not sh['file']:
                continue
            child = (Path(node['file']).parent / sh['file']).resolve()
            if child not in indexed:
                continue
            # Path IDs are based on the instantiated sheet-symbol UUID.
            segment = sh['uuid'] or ''
            chain = node['path'].strip('/').split('/') if node['path'] != '/' else []
            if segment in chain:
                raise QueryError('cyclic schematic hierarchy detected')
            if len(nodes) >= max_instances:
                raise QueryError('instance expansion exceeded --max-files')
            new = {'path': node['path'].rstrip('/') + '/' + segment,
                   'file': str(child), 'parent': idx,
                   'parent_sheet_uuid': segment, 'parent_sheet_name': sh['name']}
            nodes.append(new)
            queue.append(len(nodes)-1)
    return nodes


def build_project_graph(root, data, max_instances):
    """Build the instance-aware graph of schematic net evidence.

    Local paths are grouped by wire geometry/labels. An edge is added only
    for an explicitly matched hierarchical interface or equal global/power
    names. This is NOT a KiCad-equivalent ERC/netlist computation.

    Bus members are graph nodes (instance index, ('bus', bus group, key)).
    KiCad 10 joins a member to every net on that sheet with a label of the
    member name (no bus entry needed), joins a parent sheet pin on a bus to
    the child hierarchical label of the same name (vectors by index, groups
    by short name), and joins global bus labels of one name.

    Returns (instances, cached, graph, details, buses). A graph node is
    (instance index, local group) or a bus member node. `buses` holds the
    bus-group edges, the aliases and the parsed bus names.
    """
    from collections import defaultdict
    instances = build_instance_tree(root, data, max_instances)
    aliases = load_bus_aliases(root, [Path(d['file']) for d in data])
    parsed = {}

    def members_of(name):
        if name not in parsed:
            parsed[name] = bus_members(name, aliases)
        return parsed[name]

    cached = {}
    for node in instances:
        file = Path(node['file'])
        if file in cached:
            continue
        lib, wires, labels, junctions, no_conn = local_geometry(file)
        loaded = load_file(file)
        component_pins = []
        sheet_pins = []
        for expr in loaded['symbols']:
            info = symbol_info(expr, file)
            # A reused sheet can place another unit of the symbol in each
            # instance: give the pins of every unit an instance uses.
            own = str(info['unit'] or '1')
            units = {own} | {str(x['unit']) for x in info['instances'] if x.get('unit') is not None}
            # Same test as power_symbol_anchors: the (power) flag of the
            # embedded library symbol, not the library name.
            definition = lib_definition(expr, lib)
            is_power = definition is not None and first(definition, 'power') is not None
            for unit in sorted(units):
                pins, _ = pins_from_symbol(expr, lib, unit)
                for pin in pins:
                    component_pins.append({**pin, 'reference': info['reference_property'],
                                           'instances': info['instances'], 'symbol_uuid': info['uuid'],
                                           'lib_id': info['lib_id'], 'is_power': is_power,
                                           'unit': unit, 'own_unit': own})
        for expr in loaded['sheets']:
            for pin in children(expr, 'pin'):
                point = xy(pin)
                if point:
                    sheet_pins.append({'name': pin[1], 'point': point,
                                       'sheet_uuid': val(expr, 'uuid')})
        powers, warnings = power_symbol_anchors(file, lib)
        pin_points = [tuple(p['position_mm']) for p in component_pins]
        pin_points += [tuple(p['position_mm']) for p in powers]
        anchors = pin_points + [x['point'] for x in sheet_pins]
        add, find, groups = resolve_local_networks(
            wires, labels, junctions, pin_points, [x['point'] for x in sheet_pins])
        # Only an electrically anchored node is admitted; a coincident crossing
        # without a junction is never proof of connectivity.
        # Capture THIS file's graph and geometry; otherwise the cached closure
        # would read values rebound by later iterations of the file loop.
        def group(point, mid=False, _find=find, _add=add, _wires=wires,
                  _labels=labels, _anchors=anchors, _junctions=junctions):
            # A label or sheet pin (mid) joins anywhere on a wire; a symbol
            # pin at a wire end or at a junction on a wire.
            on_wire = (any(is_on_segment(point, a, b) for a, b in _wires) if mid
                       else bool(pin_segments(point, _wires, _junctions)))
            if on_wire or any(
                    l['point'] and math.dist(l['point'], point) < 0.002 for l in _labels):
                return _find(_add(point))
            # Direct physical pin overlap is an endpoint, but no validation.
            if sum(math.dist(point, x) < 0.002 for x in _anchors) > 1:
                return _find(_add(point))
            return None
        for p in component_pins:
            p['_group'] = group(tuple(p['position_mm']))
        for p in sheet_pins:
            p['_group'] = group(p['point'], mid=True)
        for p in powers:
            p['_group'] = group(tuple(p['position_mm']))
        # Buses: segments are grouped like wires. Labels and sheet pins on a
        # segment name the bus and give its members.
        buses, bus_labels = bus_geometry(file)
        bus_pins = [x for x in sheet_pins
                    if any(is_on_segment(x['point'], a, b) for a, b in buses)]
        badd, bfind, _ = resolve_local_networks(
            buses, bus_labels, junctions, (), [x['point'] for x in bus_pins])
        bus_groups, bus_hier, bus_global, bus_warnings = {}, [], [], []

        def name_bus(point, name, kind, _find=bfind, _add=badd,
                     _groups=bus_groups, _warnings=bus_warnings, _file=file):
            key = _find(_add(point))
            item = _groups.setdefault(key, {'names': set(), 'keys': {}, 'conflict': False})
            item['names'].add(name)
            members = members_of(name)
            if members is None:
                # KiCad gives such a bus no members (bus to net conflict).
                item['conflict'] = True
                _warnings.append({'file': str(_file), 'name': name, 'kind': kind,
                                  'reason': 'name on a bus is not a bus name; the bus is not expanded'})
                return key
            for member_key, full in members:
                item['keys'].setdefault(member_key, set()).add(full)
            return key
        for l in bus_labels:
            key = name_bus(l['point'], l['name'], l['kind'])
            if key is not None and l['kind'] == 'hierarchical_label':
                bus_hier.append((l['name'], key))
            elif key is not None and l['kind'] == 'global_label':
                bus_global.append((l['name'], key))
        for x in bus_pins:
            x['_bus'] = name_bus(x['point'], x['name'], 'sheet_pin')
        for item in bus_groups.values():
            if item['conflict']:
                item['keys'] = {}
        # Every label name on this sheet and the local groups that carry it.
        label_groups = defaultdict(set)
        for l in labels:
            if l['point'] and l['name']:
                found = group(l['point'], mid=True)
                if found is not None:
                    label_groups[l['name']].add(found)
        cached[file] = {'labels': labels, 'components': component_pins,
                        'sheet_pins': sheet_pins, 'powers': powers,
                        'group': group, 'warnings': warnings,
                        'bus_groups': bus_groups, 'bus_hier': bus_hier,
                        'bus_global': bus_global, 'bus_pins': bus_pins,
                        'bus_warnings': bus_warnings, 'label_groups': label_groups}

    graph = defaultdict(set)
    details = defaultdict(lambda: {'components': [], 'global': set(), 'power': set(), 'hier': [], 'labels': set(),
                                   'bus_links': []})
    bus_edges = defaultdict(set)
    bus_named = defaultdict(list)

    def link(a, b):
        graph[a].add(b)
        graph[b].add(a)
    # Group keys per global name. KiCad joins a global label and a power
    # symbol that share a name, so both kinds go into one table.
    named_nodes = defaultdict(list)
    for i, node in enumerate(instances):
        file = Path(node['file'])
        d = cached[file]
        def key(g): return (i, g)
        for p in d['components']:
            if p['_group'] is not None and p['lib_id'] and not p['is_power'] \
                    and p['unit'] == instance_unit(p, node['path']):
                one = instance_entry(p['instances'], node['path'])
                ref = one['reference'] if one else p['reference']
                details[key(p['_group'])]['components'].append({
                    'reference': ref, 'pin_number': p['number'],
                    'pin_name': p['name'], 'file': str(file), 'instance_path': node['path']})
        for l in d['labels']:
            if not l['point']:
                continue
            group = d['group'](l['point'], mid=True)
            if group is None: continue
            item = details[key(group)]
            if l['kind'] == 'global_label':
                item['global'].add(l['name'])
                named_nodes[l['name']].append(key(group))
            elif l['kind'] == 'hierarchical_label':
                item['hier'].append(l['name'])
            else: item['labels'].add(l['name'])
        for p in d['powers']:
            if p['_group'] is not None:
                details[key(p['_group'])]['power'].add(p['name'])
                # PWR_FLAG is an ERC power-driver marker, not an electrical
                # net name. Unioning it globally bridges otherwise unrelated
                # nets that merely contain a PWR_FLAG symbol.
                # A local power symbol is one net per sheet instance.
                if p['name'] != 'PWR_FLAG':
                    name = ('local', i, p['name']) if p['local'] else p['name']
                    named_nodes[name].append(key(p['_group']))
        global_buses = {bus_key for _, bus_key in d['bus_global']}
        member_nodes = defaultdict(list)
        for bus_key, item in d['bus_groups'].items():
            names = sorted(item['names'])
            for member_key, fulls in item['keys'].items():
                member_node = (i, ('bus', bus_key, member_key))
                graph[member_node]  # a member with no net is still a node
                attached = False
                for full in fulls:
                    # Members of one name on this sheet are one net, and the
                    # members of a global bus are global names.
                    member_nodes[full].append(member_node)
                    if bus_key in global_buses:
                        named_nodes[full].append(member_node)
                    for local in d['label_groups'].get(full, ()):
                        link(member_node, key(local))
                        attached = True
                details[member_node]['bus_links'].append({
                    'bus_names': names, 'members': sorted(fulls),
                    'instance_path': node['path'], 'file': str(file),
                    'member_net_on_sheet': attached})
        for nodes in member_nodes.values():
            for other in nodes[1:]:
                link(nodes[0], other)
        for name, bus_key in d['bus_global']:
            if not d['bus_groups'][bus_key]['conflict']:
                bus_named[name].append((i, bus_key))
        if node['parent'] is None: continue
        parent_idx = node['parent']
        parent_file = Path(instances[parent_idx]['file'])
        pd = cached[parent_file]
        sheet_uuid = node['parent_sheet_uuid']
        for p in pd['sheet_pins']:
            if p['sheet_uuid'] != sheet_uuid or p['_group'] is None:
                continue
            origin = (parent_idx, p['_group'])
            child_matches = [l for l in d['labels'] if l['kind'] == 'hierarchical_label'
                             and l['name'] == p['name'] and l['point']]
            for l in child_matches:
                child_group = d['group'](l['point'], mid=True)
                if child_group is not None:
                    # This is the CHILD instance, not the last loop iteration.
                    target = (i, child_group)
                    graph[origin].add(target)
                    graph[target].add(origin)
        # A parent sheet pin on a bus meets the child bus with the
        # hierarchical label of the same name.
        for p in pd['bus_pins']:
            if p['sheet_uuid'] != sheet_uuid or p['_bus'] is None:
                continue
            if pd['bus_groups'][p['_bus']]['conflict']:
                continue
            for name, child_bus in d['bus_hier']:
                if name != p['name'] or d['bus_groups'][child_bus]['conflict']:
                    continue
                bus_edges[(parent_idx, p['_bus'])].add((i, child_bus))
                bus_edges[(i, child_bus)].add((parent_idx, p['_bus']))
                for member_key, _ in members_of(name):
                    link((parent_idx, ('bus', p['_bus'], member_key)),
                         (i, ('bus', child_bus, member_key)))
    # Global labels and power symbols are global *by KiCad semantics*.
    for keys in named_nodes.values():
        first_key = keys[0]
        for other in keys[1:]:
            graph[first_key].add(other)
            graph[other].add(first_key)
    for name, found in bus_named.items():
        for other in found[1:]:
            bus_edges[found[0]].add(other)
            bus_edges[other].add(found[0])
            for member_key, _ in members_of(name):
                link((found[0][0], ('bus', found[0][1], member_key)),
                     (other[0], ('bus', other[1], member_key)))

    buses = {'edges': bus_edges, 'aliases': aliases, 'members_of': members_of}
    return instances, cached, graph, details, buses


def instance_unit(pin, path):
    """Unit of a placed symbol in one sheet instance.

    The instance entry for that path wins; without one, the symbol's own unit.
    """
    one = instance_entry(pin['instances'], path)
    if one is not None and one.get('unit') is not None:
        return str(one['unit'])
    return pin['own_unit']


def reach(graph, start):
    """All graph nodes connected to `start`."""
    reached = {start}
    queue = [start]
    while queue:
        current = queue.pop()
        for other in graph[current]:
            if other not in reached:
                reached.add(other)
                queue.append(other)
    return reached


def net_evidence(instances, details, reached, limit):
    """Result fields shared by project-net and net for one set of groups."""
    # One node per pin: each placed unit of a multi-unit symbol carries the
    # shared pins, so the same reference and pin can appear in two groups.
    unique = {(p['instance_path'], p['reference'], p['pin_number']): p
              for group in reached for p in details[group]['components']}
    pins = sorted(unique.values(),
                  key=lambda p: (p['instance_path'], p['reference'] or '', p['pin_number'] or ''))
    globals_found = sorted({x for group in reached for x in details[group]['global']})
    power_found = sorted({x for group in reached for x in details[group]['power']})
    links = sorted((x for group in reached for x in details[group]['bus_links']),
                   key=lambda x: (x['instance_path'], x['bus_names'], x['members']))
    return {'connected_component_pins': pins[:limit],
            'total_connected_component_pins': len(pins),
            'connected_pins_truncated': len(pins) > limit,
            'global_labels': globals_found[:limit], 'power_net_names': power_found[:limit],
            'names_truncated': len(globals_found)>limit or len(power_found)>limit,
            'bus_links': links[:limit], 'bus_links_truncated': len(links) > limit,
            'groups_visited': len(reached), 'instance_count': len(instances),
            'project_net_verified': False,
            'limitations': list(PROJECT_NET_LIMITS)}


def project_connections(root, data, reference, limit, max_instances, pin_filter=None):
    """Connectivity evidence for the net on one component pin."""
    instances, cached, graph, details, _ = build_project_graph(root, data, max_instances)
    starts = []
    for i, node in enumerate(instances):
        for p in cached[Path(node['file'])]['components']:
            if p['_group'] is None or p['unit'] != instance_unit(p, node['path']): continue
            one = instance_entry(p['instances'], node['path'])
            ref = one['reference'] if one else p['reference']
            if ref == reference and (pin_filter is None or str(p["number"]) == pin_filter):
                starts.append((i, p['_group'], p['number']))
    if not starts:
        return {'status': 'TARGET_NOT_FOUND_OR_UNRESOLVED', 'reference': reference,
                'project_net_verified': False, 'instance_count': len(instances)}
    # Several starts are one net when they reach each other, for example the
    # shared power pin of each placed unit of a multi-unit symbol.
    reached = reach(graph, (starts[0][0], starts[0][1]))
    if any((i, g) not in reached for i, g, _ in starts):
        return {'status': 'AMBIGUOUS_TARGET_NETS', 'reference': reference,
                'starting_pins': [{'instance_path': instances[i]['path'], 'pin': n}
                                  for i,g,n in starts][:limit],
                'starting_pins_truncated': len(starts) > limit,
                'project_net_verified': False, 'instance_count': len(instances)}
    return {'status': 'PROJECT_CONNECTIVITY_EVIDENCE', 'reference': reference,
            'source_instance_path': instances[starts[0][0]]['path'],
            'source_pin_number': starts[0][2],
            **net_evidence(instances, details, reached, limit)}


def net_connections(root, data, name, limit, max_instances):
    """Connectivity evidence for every net that carries `name`.

    A start is any group holding a local label, global label, hierarchical
    label or power symbol with that exact name. Starts that reach each other
    are one result; a local label repeated in separate sheet instances gives
    one result per instance.
    """
    instances, _, graph, details, _ = build_project_graph(root, data, max_instances)
    kinds = (('label', 'labels'), ('global_label', 'global'),
             ('hierarchical_label', 'hier'), ('power_symbol', 'power'))
    # Saved text keeps KiCad escapes (SS{slash}TR for SS/TR); match either form.
    wanted = unescape(name)
    starts, saved = {}, {}
    for key, item in details.items():
        hits = [(kind, n) for kind, field in kinds for n in item[field]
                if n == name or unescape(n) == wanted]
        if hits:
            starts[key] = sorted({kind for kind, _ in hits})
            saved[key] = {n for _, n in hits}
    if not starts:
        return [{'status': 'NET_NAME_NOT_FOUND', 'net_name': name,
                 'project_net_verified': False, 'instance_count': len(instances)}]
    results, seen = [], set()
    for key in sorted(starts, key=lambda k: (instances[k[0]]['path'], k[1])):
        if key in seen:
            continue
        reached = reach(graph, key)
        seen |= reached
        matched_by = sorted(
            ({'kind': kind, 'instance_path': instances[k[0]]['path'], 'file': instances[k[0]]['file']}
             for k in reached if k in starts for kind in starts[k]),
            key=lambda m: (m['instance_path'], m['kind']))
        unique = [m for n, m in enumerate(matched_by) if m not in matched_by[:n]]
        results.append({'status': 'PROJECT_CONNECTIVITY_EVIDENCE', 'net_name': name,
                        'saved_names': sorted({n for k in reached if k in saved for n in saved[k]}),
                        'matched_by': unique[:limit],
                        'matched_by_truncated': len(unique) > limit,
                        **net_evidence(instances, details, reached, limit)})
    return results


def bus_connections(root, data, name, limit, max_instances):
    """List bus names, or trace one bus and each of its members.

    Returns (results, warnings). With a name, one result per connected bus:
    every sheet instance it reaches, and per member the sheets where a net
    carries the member name and the component pins on that member net.
    """
    instances, cached, graph, details, buses = build_project_graph(root, data, max_instances)
    members_of, aliases = buses['members_of'], buses['aliases']
    groups = {}
    for i, node in enumerate(instances):
        for bus_key, item in cached[Path(node['file'])]['bus_groups'].items():
            groups[(i, bus_key)] = item
    warnings = []
    for d in cached.values():
        for w in d['bus_warnings']:
            if w not in warnings:
                warnings.append(w)
    if name is None:
        rows = {}
        for (i, _), item in sorted(groups.items(), key=lambda kv: instances[kv[0][0]]['path']):
            for bus_name in sorted(item['names']):
                row = rows.setdefault(bus_name, {
                    'name': bus_name, 'kind': 'bus_name',
                    'members': [full for _, full in members_of(bus_name) or []],
                    'occurrences': []})
                occurrence = {'instance_path': instances[i]['path'], 'file': instances[i]['file']}
                if occurrence not in row['occurrences']:
                    row['occurrences'].append(occurrence)
        bus_names = sorted(rows)
        for alias, members in aliases.items():
            used_by = [n for n in bus_names if alias in re.split(r'[\s,{}]+', n)]
            rows.setdefault(alias, {'name': alias, 'kind': 'alias', 'members': list(members),
                                    'used_by': used_by, 'occurrences': []})
        out = []
        for row in sorted(rows.values(), key=lambda r: (r['kind'], r['name'])):
            row['total_members'] = len(row['members'])
            row['members_truncated'] = len(row['members']) > limit
            row['members'] = row['members'][:limit]
            row['total_occurrences'] = len(row['occurrences'])
            row['occurrences_truncated'] = len(row['occurrences']) > limit
            row['occurrences'] = row['occurrences'][:limit]
            out.append(row)
        return out, warnings
    wanted = {name}
    if name in aliases:
        wanted.add('{' + name + '}')
    if name.startswith('{') and name.endswith('}') and name[1:-1] in aliases:
        wanted.add(name[1:-1])
    starts = [k for k, item in groups.items() if item['names'] & wanted]
    if not starts:
        return [{'status': 'BUS_NAME_NOT_FOUND', 'bus_name': name,
                 'project_net_verified': False, 'instance_count': len(instances)}], warnings
    results, seen = [], set()
    for start in sorted(starts, key=lambda k: (instances[k[0]]['path'], k[1])):
        if start in seen:
            continue
        component, queue = {start}, [start]
        while queue:
            for other in buses['edges'][queue.pop()]:
                if other not in component:
                    component.add(other)
                    queue.append(other)
        seen |= component
        ordered = sorted(component, key=lambda k: (instances[k[0]]['path'], k[1]))
        occurrences = [{'instance_path': instances[i]['path'], 'file': instances[i]['file'],
                        'bus_names': sorted(groups[(i, b)]['names']),
                        'members_resolved': not groups[(i, b)]['conflict']} for i, b in ordered]
        member_keys = []
        for k in ordered:
            for member_key in groups[k]['keys']:
                if member_key not in member_keys:
                    member_keys.append(member_key)
        members = []
        for member_key in member_keys:
            nodes = [(i, ('bus', b, member_key)) for i, b in ordered if member_key in groups[(i, b)]['keys']]
            reached = set()
            for n in nodes:
                if n not in reached:
                    reached |= reach(graph, n)
            sheets = [x for n in nodes for x in details[n]['bus_links']]
            names = sorted({m for x in sheets for m in x['members']})
            evidence = net_evidence(instances, details, reached, limit)
            for unused in ('limitations', 'instance_count', 'bus_links', 'bus_links_truncated', 'project_net_verified'):
                evidence.pop(unused)
            members.append({'member': names[0] if names else None, 'member_names': names,
                            'sheets': [{'instance_path': x['instance_path'], 'file': x['file'],
                                        'member_net_on_sheet': x['member_net_on_sheet']}
                                       for x in sheets][:limit],
                            'sheets_truncated': len(sheets) > limit,
                            **evidence})
        results.append({'status': 'BUS_CONNECTIVITY_EVIDENCE', 'bus_name': name,
                        'occurrences': occurrences[:limit],
                        'occurrences_truncated': len(occurrences) > limit,
                        'members': members[:limit], 'total_members': len(members),
                        'members_truncated': len(members) > limit,
                        'project_net_verified': False,
                        'limitations': list(MODES['bus']['limitations'])})
    return results, warnings


def reference_parts(reference):
    """Split 'R506' into ('R', 506); the number is -1 when there is none."""
    text = reference or ''
    letters = text.rstrip('0123456789?')
    digits = text[len(letters):].strip('?')
    return letters, int(digits) if digits.isdigit() else -1


def list_components(root, data, max_instances, sheet=None, prefix=None):
    """List components per hierarchical sheet instance (structure only)."""
    instances = build_instance_tree(root, data, max_instances)
    indexed = {Path(d['file']).resolve(): d for d in data}
    rows, sheet_found = {}, sheet is None
    for node in instances:
        file = Path(node['file'])
        if sheet is not None:
            names = ((root.name, root.stem) if node['parent'] is None
                     else (node['parent_sheet_name'], file.name, file.stem))
            if sheet not in names:
                continue
            sheet_found = True
        for sym in indexed[file]['symbols']:
            one = instance_entry(sym['instances'], node['path'])
            reference = one['reference'] if one else sym['reference_property']
            if not reference:
                continue
            hidden = reference.startswith('#')
            if prefix is None:
                if hidden:
                    continue
            elif prefix == '#':
                if not hidden:
                    continue
            elif reference_parts(reference)[0] != prefix:
                continue
            row = rows.setdefault((node['path'], reference), {
                'reference': reference, 'value': sym['value'], 'lib_id': sym['lib_id'],
                'sheet_name': node['parent_sheet_name'], 'instance_path': node['path'],
                'file': str(file), 'units': []})
            unit = (one['unit'] if one else None) or sym['unit']
            if unit is not None and unit not in row['units']:
                row['units'].append(unit)
    ordered = sorted(rows.values(), key=lambda r: (r['instance_path'], *reference_parts(r['reference']), r['reference']))
    for row in ordered:
        row['units'].sort(key=lambda u: (0, int(u)) if str(u).isdecimal() else (1, str(u)))
    return ordered, sheet_found


def root_file(raw: str):
    p = Path(raw).expanduser().resolve()
    if p.is_dir():
        # The root sheet has the project file's name.
        pros = sorted(p.glob('*.kicad_pro'))
        if len(pros) == 1 and pros[0].with_suffix('.kicad_sch').is_file():
            return pros[0].with_suffix('.kicad_sch')
        items = sorted(p.glob('*.kicad_sch'))
        if len(items) != 1:
            raise QueryError(f'directory has {len(items)} root candidates; pass the root .kicad_sch explicitly')
        return items[0]
    if not p.is_file() or p.suffix.lower() != '.kicad_sch':
        raise QueryError('pass an existing .kicad_sch file or a directory containing exactly one')
    return p


def discover(root: Path, max_files: int):
    """Follow sheet references from root; read each distinct file at most once.

    This discovers *files*, not unique hierarchical sheet instances.
    """
    pending = [root]
    visited = set()
    data = []
    outside = []
    missing = []
    while pending:
        file = pending.pop(0).resolve()
        if file in visited:
            continue
        if len(visited) >= max_files:
            raise QueryError(f'sheet discovery exceeded --max-files={max_files}')
        visited.add(file)
        if not file.is_file():
            missing.append(str(file))
            continue
        item = read_sheet(file)
        data.append(item)
        for sh in item['sheets']:
            raw = sh['file']
            if not raw:
                continue
            child = (file.parent / raw).resolve()
            try:
                child.relative_to(root.parent.resolve())
            except ValueError:
                outside.append(str(child))
                continue
            if child not in visited:
                pending.append(child)
    return data, missing, outside


# ---------------------------------------------------------------------------
# KiCad netlist (kicad-cli export) and comparison with the project graph
# ---------------------------------------------------------------------------

def _version_key(path):
    """(10, 0) for .../KiCad/10.0/bin/kicad-cli.exe; non-numeric folders sort first."""
    # Split on both separators: Path() on macOS/Linux keeps a Windows path whole.
    bits = re.split(r'[\\/]', str(path))
    folder = bits[-3] if len(bits) >= 3 else ''
    parts = folder.split('.')
    return tuple(int(x) for x in parts) if all(x.isdigit() for x in parts) else (-1,)


def find_kicad_cli(explicit=None):
    """Path of kicad-cli: --kicad-cli, then KICAD_CLI, then PATH, then the usual install folders."""
    candidates = [explicit, os.environ.get('KICAD_CLI'), shutil.which('kicad-cli')]
    if sys.platform == 'win32':
        roots = [os.environ.get('ProgramFiles', r'C:\Program Files'), r'C:\Program Files']
        for r in dict.fromkeys(roots):
            # Newest version first: compare 10.0 and 9.0 as numbers, not text.
            found = glob.glob(os.path.join(r, 'KiCad', '*', 'bin', 'kicad-cli.exe'))
            candidates += sorted(found, key=_version_key, reverse=True)
    elif sys.platform == 'darwin':
        candidates.append('/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
    for c in candidates:
        if c and Path(c).is_file():
            return str(c)
    raise QueryError('kicad-cli not found: pass --kicad-cli PATH, set KICAD_CLI, '
                     'or give an exported KiCad XML netlist with --netlist')


def export_netlist(root, cli, sheets=()):
    """Run kicad-cli on a temp copy of the saved sheets and project file.

    kicad-cli writes a .kicad_prl next to a project that has none, so it never
    runs on the project folder itself. `sheets` are the discovered sheet files;
    each is copied to the same path relative to the root sheet's folder.
    """
    base = Path(root).resolve().parent
    with tempfile.TemporaryDirectory(prefix='sch-inspect-') as tmp:
        work = Path(tmp) / 'project'
        for src in {Path(root).resolve(), *(Path(s).resolve() for s in sheets),
                    Path(root).resolve().with_suffix('.kicad_pro')}:
            try:
                rel = src.relative_to(base)
            except ValueError:
                continue  # outside the project folder: discover() skips it too
            if src.is_file():
                (work / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, work / rel)
        out = Path(tmp) / 'netlist.xml'
        target = work / Path(root).resolve().relative_to(base)
        try:
            proc = subprocess.run([cli, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(out), str(target)],
                                  capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            raise QueryError('kicad-cli netlist export timed out after 120 s')
        if proc.returncode != 0 or not out.is_file():
            raise QueryError(f'kicad-cli netlist export failed (exit {proc.returncode}): '
                             f'{(proc.stderr or proc.stdout).strip()[:300]}')
        return out.read_text(encoding='utf-8')


def parse_netlist(text):
    """(tool, nets) from a KiCad XML netlist (`kicad-cli sch export netlist --format kicadxml`)."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise QueryError(f'not a KiCad XML netlist: {exc}')
    if root.tag != 'export':
        raise QueryError('not a KiCad XML netlist: root element is not <export>')
    nets = []
    for net in root.iter('net'):
        nodes = [{'reference': n.get('ref'), 'pin_number': n.get('pin'),
                  'pin_function': n.get('pinfunction') or '', 'pin_type': n.get('pintype') or ''}
                 for n in net.iter('node')]
        nets.append({'net_name': net.get('name') or '', 'code': net.get('code'), 'nodes': nodes})
    return (root.findtext('design/tool') or '').strip(), nets


def load_netlist(root, data, netlist_file=None, cli=None):
    if netlist_file:
        return parse_netlist(Path(netlist_file).read_text(encoding='utf-8')), f'file {netlist_file}'
    exe = find_kicad_cli(cli)
    return parse_netlist(export_netlist(root, exe, [d['file'] for d in data])), f'kicad-cli {exe}'


def netlist_lookup(nets, target, tool, source, limit):
    """Nets whose name is the target (full or last path part), else every net on a reference."""
    def short(name):
        return name.rsplit('/', 1)[-1]
    named = [n for n in nets if target in (n['net_name'], short(n['net_name']))]
    by_ref = [] if named else [n for n in nets if any(x['reference'] == target for x in n['nodes'])]
    hits = named or by_ref
    if not hits:
        return [{'status': 'NET_OR_REFERENCE_NOT_FOUND', 'target': target,
                 'netlist_tool': tool, 'netlist_source': source}]
    return [{'status': 'KICAD_NETLIST_NET', 'net_name': n['net_name'], 'matched_by': 'net' if named else 'reference',
             'nodes': n['nodes'][:limit], 'node_count': len(n['nodes']), 'nodes_truncated': len(n['nodes']) > limit,
             'netlist_tool': tool, 'netlist_source': source} for n in hits]


def netlist_compare(root, data, nets, tool, source, limit, max_instances):
    """Compare KiCad's nets with the project graph as two partitions of component pins.

    split:  KiCad joins pins that the project graph keeps on separate nets (or misses).
    merged: the project graph joins pins that KiCad keeps on separate nets.
    """
    instances, _, graph, details, _ = build_project_graph(root, data, max_instances)
    graph_net_of, graph_nets, seen = {}, [], set()
    for key in sorted(details, key=lambda k: (instances[k[0]]['path'], str(k[1]))):
        if key in seen:
            continue
        reached = reach(graph, key)
        seen |= reached
        pins = {(p['reference'], str(p['pin_number'])) for g in reached for p in details[g]['components']
                if p['reference'] and not str(p['reference']).startswith('#')}
        if not pins:
            continue
        names = sorted({x for g in reached for f in ('labels', 'global', 'hier', 'power') for x in details[g][f]})
        gid = len(graph_nets)
        graph_nets.append({'pins': pins, 'names': names})
        for pin in pins:
            graph_net_of.setdefault(pin, set()).add(gid)
    kicad_net_of, compared, diffs = {}, [], []
    for n in nets:
        pins = {(x['reference'], str(x['pin_number'])) for x in n['nodes']
                if x['reference'] and not x['reference'].startswith('#')}
        for pin in pins:
            kicad_net_of.setdefault(pin, set()).add(n['net_name'])
        if len(pins) >= 2:
            compared.append((n['net_name'], pins))

    def label(gids):
        return [', '.join(graph_nets[g]['names']) or f'(unnamed net {g})' for g in sorted(gids)]
    for name, pins in compared:
        gids = set().union(*(graph_net_of.get(p, set()) for p in pins))
        missing = sorted(p for p in pins if p not in graph_net_of)
        if len(gids) > 1 or missing:
            diffs.append({'status': 'NETLIST_DIFFERENCE', 'kind': 'split', 'kicad_net': name,
                          'sch_inspect_nets': label(gids),
                          'pins': [f'{r}.{p}' for r, p in sorted(pins)][:limit],
                          'pins_missing_in_sch_inspect': [f'{r}.{p}' for r, p in missing][:limit]})
    for gid, g in enumerate(graph_nets):
        kicad = set().union(*(kicad_net_of.get(p, set()) for p in g['pins']))
        if len(kicad) > 1:
            diffs.append({'status': 'NETLIST_DIFFERENCE', 'kind': 'merged', 'sch_inspect_net': label({gid})[0],
                          'kicad_nets': sorted(kicad)[:limit],
                          'pins': [f'{r}.{p}' for r, p in sorted(g['pins'])][:limit]})
    summary = {'status': 'NETLIST_COMPARISON_SUMMARY', 'netlist_tool': tool, 'netlist_source': source,
               'kicad_nets': len(nets), 'multi_pin_kicad_nets_compared': len(compared),
               'pins_compared': sum(len(p) for _, p in compared), 'sch_inspect_nets': len(graph_nets),
               'differences': len(diffs), 'instance_count': len(instances)}
    return [summary] + diffs


class JsonArgumentParser(argparse.ArgumentParser):
    """Argument errors are JSON on stderr, like every other error."""

    def error(self, message):
        print(json.dumps({'error': message, 'verification': 'NOT_VERIFIED'}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)


def any_truncated(value):
    """True when any nested `*_truncated` flag in the output is true."""
    if isinstance(value, dict):
        return any((k.endswith('_truncated') and v is True) or any_truncated(v) for k, v in value.items())
    if isinstance(value, list):
        return any(any_truncated(v) for v in value)
    return False


def main(argv=None):
    ap = JsonArgumentParser(description=__doc__)
    ap.add_argument('mode', choices=list(MODES))
    ap.add_argument('target', nargs='?', help='reference, sheet filename/name (sheet), net name (net) or bus name (bus)')
    ap.add_argument('--project', required=True, help='root .kicad_sch (preferred) or its directory')
    ap.add_argument('--limit', type=int, default=20, help='bound for every list, 1 to 200; 0 means no bound')
    ap.add_argument('--max-files', type=int, default=100)
    ap.add_argument('--pin', help='pin number for project-net; necessary when a component has multiple nets')
    ap.add_argument('--sheet', help='components only: keep one sheet (name, file name or file stem)')
    ap.add_argument('--prefix', help='components only: keep references with this letter prefix, for example U')
    ap.add_argument('--kicad-cli', help='netlist commands only: path of kicad-cli (default: KICAD_CLI, PATH, install folders)')
    ap.add_argument('--netlist', help='netlist commands only: read this KiCad XML netlist instead of running kicad-cli')
    args = ap.parse_args(argv)
    _FILES.clear()
    _PROJECT['name'] = None
    # Print UTF-8 JSON whatever the console code page is. A legacy code page
    # (common on Windows) cannot encode some paths and names.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass  # not a text console stream (for example a test buffer)
    try:
        if not (0 <= args.limit <= 200 and 1 <= args.max_files <= 1000):
            raise QueryError('limit must be 0 to 200 and max-files 1 to 1000')
        limit = args.limit or sys.maxsize  # 0: no bound
        if args.pin and args.mode != 'project-net':
            raise QueryError('--pin is only supported with project-net')
        if (args.sheet is not None or args.prefix is not None) and args.mode != 'components':
            raise QueryError('--sheet and --prefix are only supported with components')
        if args.mode == 'components' and args.target:
            raise QueryError('components takes --sheet and --prefix, not a target')
        if (args.kicad_cli or args.netlist) and not args.mode.startswith('netlist'):
            raise QueryError('--kicad-cli and --netlist are only supported with netlist and netlist-compare')
        if args.mode == 'netlist-compare' and args.target:
            raise QueryError('netlist-compare compares every net and takes no target')
        if args.mode not in ('summary', 'instances', 'components', 'bus', 'netlist-compare') and not args.target:
            raise QueryError(f'{args.mode} requires a target')
        root = root_file(args.project)
        _PROJECT['name'] = root.stem
        data, missing, outside = discover(root, args.max_files)
        records = []
        warnings = []
        if args.mode in ('netlist', 'netlist-compare'):
            (tool, nets), source = load_netlist(root, data, args.netlist, args.kicad_cli)
            if args.mode == 'netlist':
                records = netlist_lookup(nets, args.target, tool, source, limit)
            else:
                records = netlist_compare(root, data, nets, tool, source, limit, args.max_files)
        elif args.mode == 'net':
            records = net_connections(root, data, args.target, limit, args.max_files)
        elif args.mode == 'bus':
            records, warnings = bus_connections(root, data, args.target, limit, args.max_files)
        elif args.mode == 'components':
            records, sheet_found = list_components(root, data, args.max_files, args.sheet, args.prefix)
            if not sheet_found:
                warnings.append(f'no sheet instance matches --sheet {args.sheet}')
        elif args.mode == 'project-net':
            records = [project_connections(root, data, args.target, limit, args.max_files, args.pin)]
        elif args.mode == 'instances':
            records = build_instance_tree(root, data, args.max_files)
        elif args.mode in ('hier-net', 'connected-pins'):
            records, pin_issues = hierarchical_trace(root, data, args.target, limit,
                                                     discover_pins=(args.mode == 'connected-pins'),
                                                     max_instances=args.max_files)
        elif args.mode in ('pins','local-net'):
            records, pin_issues = inspect_pins(root, data, args.target, limit, resolved=(args.mode == 'local-net'))
        elif args.mode == 'component':
            for item in data:
                for sym in item['symbols']:
                    refs = {sym['reference_property']} | {x['reference'] for x in sym['instances']}
                    if args.target in refs:
                        records.append(sym)
        elif args.mode == 'sheet':
            for item in data:
                if item['file'] == str(root) and args.target in (root.name, root.stem):
                    records.append({'file': item['file'], 'uuid': item['uuid'], 'root': True})
                for sh in item['sheets']:
                    saved = Path(sh['file'] or '')
                    if args.target in (sh['name'], sh['file'], saved.name, saved.stem):
                        records.append({**sh, 'pins': sh['pins'][:limit],
                                        'pins_truncated': len(sh['pins']) > limit})
        else:
            # Counts are per schematic file: a reused sheet is counted once.
            records = [{'file': d['file'], 'symbol_count': len(d['symbols']),
                        'component_count': sum(not (s['reference_property'] or '').startswith('#')
                                               for s in d['symbols']),
                        'child_sheet_count': len(d['sheets'])} for d in data]
        shown = records[:limit]
        out = {'mode': args.mode, 'target': args.target, 'root': str(root),
               'results': shown, 'total_matches': len(records),
               'truncated': len(records) > limit or any_truncated(shown), 'missing_sheets': missing,
               'skipped_outside_project': outside,
               'verification': MODES[args.mode]['verification'],
               'limitations': list(MODES[args.mode]['limitations']),
               'warnings': pin_issues if args.mode in ('pins','local-net','hier-net','connected-pins') else warnings}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    except (QueryError, OSError, UnicodeError, RecursionError, IndexError, KeyError, TypeError, ValueError,
            AttributeError) as exc:
        # Malformed saved data must give JSON on stderr, not a traceback.
        print(json.dumps({'error': str(exc), 'verification': 'NOT_VERIFIED'}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
