#!/usr/bin/env python3
"""Read-only KiCad schematic discovery and conservative local and parent-interface tracing (v1.0.1).

Python 3.10+ standard library only. Never modifies project files.
"""
from __future__ import annotations

import argparse
import json
import sys
import math
from pathlib import Path


class QueryError(Exception):
    pass


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
            'unit': val(expr, 'unit'), 'instances': instances}


def sheet_info(expr, file):
    p = properties(expr)
    return {'parent_file': str(file), 'name': p.get('Sheetname'),
            'file': p.get('Sheetfile'), 'uuid': val(expr, 'uuid'),
            'pins': [pin[1] for pin in children(expr, 'pin') if len(pin)>1]}


def read_sheet(path: Path):
    try:
        source = path.read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError) as exc:
        raise QueryError(f'cannot read {path}: {exc}') from exc
    if not source.lstrip().startswith('(kicad_sch'):
        raise QueryError(f'not a KiCad schematic: {path}')
    symbols, sheets = [], []
    file_uuid = None
    for tag, fragment in forms(source):
        if tag == 'symbol':
            symbols.append(symbol_info(parse(fragment), path))
        elif tag == 'sheet':
            sheets.append(sheet_info(parse(fragment), path))
        elif tag == 'uuid':
            file_uuid = val(parse(fragment), 'uuid')  # root UUID form is (uuid VALUE)
            if file_uuid is None:
                file_uuid = parse(fragment)[1]
    return {'file': str(path), 'uuid': file_uuid, 'symbols': symbols, 'sheets': sheets}



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


def local_geometry(path):
    """Load selected file geometry only. No netlist export or flattened connectivity."""
    source = path.read_text(encoding='utf-8-sig')
    lib = {}
    wires, buses, labels, junctions, no_connects = [], [], [], [], []
    for tag, fragment in forms(source):
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
    labels = [label for label in labels if not (
        label['point'] and any(is_on_segment(label['point'], a, b) for a, b in buses)
    )]
    return lib, wires, labels, junctions, no_connects


def pins_from_symbol(symbol, lib):
    """Return placed pin positions for common native KiCad symbols.

    Complex inheritance, unsupported pin transforms, or missing libraries are
    explicitly surfaced as limitations rather than silently marked connected.
    """
    libid = val(symbol, 'lib_id')
    libsym = lib.get(libid)
    if not libsym:
        return [], [f'embedded lib symbol unavailable: {libid}']
    origins = xy(symbol)
    if not origins:
        return [], ['symbol placement missing']
    at = first(symbol, 'at')
    try:
        rotation = float(at[3]) if at and len(at) > 3 else 0.0
    except (ValueError, TypeError):
        return [], ['symbol rotation invalid']
    unit = str(val(symbol, 'unit', '1'))
    mirror = first(symbol, 'mirror')
    mirrored = mirror[1] if mirror and len(mirror)>1 else None
    if mirrored not in (None, 'x', 'y'):
        return [], [f'unsupported mirror mode: {mirrored}']
    if first(libsym, 'extends'):
        return [], ['inherited lib symbol pins are not resolved']
    pins=[]
    for subsym in children(libsym, 'symbol'):
        subname = subsym[1] if len(subsym)>1 else ''
        # KiCad sub-symbol naming convention: NAME_<unit>_<convert>
        bits = subname.rsplit('_', 2)
        if len(bits) != 3 or bits[1] not in ('0', unit):
            continue
        for kind in ('pin',):
            for pin in children(subsym, kind):
                atpin = xy(pin)
                if not atpin:
                    continue
                px,py = atpin
                if mirrored == 'x':
                    py=-py
                elif mirrored == 'y':
                    px=-px
                angle = math.radians(rotation)
                x = origins[0]+px*math.cos(angle)-py*math.sin(angle)
                # Local Y positive up; schematic canvas Y positive down.
                y = origins[1]-(px*math.sin(angle)+py*math.cos(angle))
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
    source = path.read_text(encoding='utf-8-sig')
    for tag, fragment in forms(source):
        if tag != 'symbol':
            continue
        expr = parse(fragment)
        lib_id = val(expr, 'lib_id')
        definition = lib.get(lib_id)
        if definition is None or first(definition, 'power') is None:
            continue
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
                           'symbol_uuid': info['uuid'],
                           'position_mm': pin['position_mm']})
    return result, warnings


def resolve_local_networks(wires, labels, junctions, pin_points=()):
    """Build sheet-local conductive wire groups; crossings alone do not join.

    Endpoints, explicit junctions, label anchor points and pin attachment points
    split segments. Local labels with the same name unify groups within this
    sheet; global/hierarchical labels are evidence, not cross-sheet resolved.
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
    anchors = [p for a,b in wires for p in (a,b)]
    anchors += [p for p in junctions if p]
    anchors += [l['point'] for l in labels if l['point']]
    anchors += list(pin_points)
    for p in anchors:
        add(p)
    # Union all anchored points on each conductive segment. Crossing
    # segments without an endpoint/junction remain separate networks.
    for a,b in wires:
        on=[add(p) for p in anchors if is_on_segment(p,a,b)]
        for k in on[1:]:
            union(on[0],k)
    # Only local label scope can be resolved without sheet hierarchy.
    local_names={}
    for label in labels:
        if label['kind']=='label' and label['point']:
            k=add(label['point'])
            if label['name'] in local_names:
                union(k,local_names[label['name']])
            else:
                local_names[label['name']]=k
    groups={}
    for label in labels:
        if label['point']:
            groups.setdefault(find(add(label['point'])),[]).append(label)
    return add,find,groups


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
        source=path.read_text(encoding='utf-8-sig')
        wanted={m['uuid'] for m in matches}
        placed={}
        for tag,fragment in forms(source):
            if tag=='symbol':
                expr=parse(fragment)
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
            pins, warnings=pins_from_symbol(expr,lib)
            pins_by_uuid[m['uuid']]=pins
            warnings_by_uuid[m['uuid']]=warnings
            issues.extend(warnings)
            all_positions.extend(tuple(p['position_mm']) for p in pins)
        power_positions = [tuple(p["position_mm"]) for p in power_anchors]
        add,find,groups=resolve_local_networks(wires,labels,junctions,all_positions+power_positions)
        for m in matches:
            if m['uuid'] not in pins_by_uuid:
                continue
            annotated=[]
            for pin in pins_by_uuid[m['uuid']]:
                pos=tuple(pin['position_mm'])
                attached=[i for i,(a,b) in enumerate(wires) if is_on_segment(pos,a,b)]
                near_labels=[{'kind':l['kind'],'name':l['name']} for l in labels if l['point'] and (math.dist(pos,l['point']) < .002 or any(is_on_segment(l['point'], *wires[i]) for i in attached))]
                pin['local_wire_segments_at_pin']=len(attached)
                pin['candidate_labels_on_same_segment']=near_labels[:10]
                pin['no_connect_marker']=any(p and math.dist(pos,p)<.002 for p in nc)
                pin['connection_evidence']='DIRECT_GEOMETRY_ONLY'
                if resolved:
                    attached_network = bool(attached or any(l['point'] and math.dist(pos,l['point']) < .002 for l in labels))
                    connected_labels=groups.get(find(add(pos)),[]) if attached_network else []
                    local=sorted({l['name'] for l in connected_labels if l['kind']=='label' and l['name']})
                    interfaces=sorted({(l['kind'],l['name']) for l in connected_labels if l['kind']!='label' and l['name']})
                    pin['local_net_labels']=local
                    pin['interface_labels']=[{'kind':k,'name':n} for k,n in interfaces]
                    pin['local_connection_status']=('NO_CONNECT_MARKER' if pin['no_connect_marker'] and not attached_network
                        else 'CONFLICTING_NO_CONNECT' if pin['no_connect_marker'] and attached_network
                        else 'LOCAL_WIRE_PATH' if attached else 'LABEL_ANCHOR_ONLY' if attached_network
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
                                any(is_on_segment(at_power, a, b) for a, b in wires)
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
                            'instances':m['instances'], 'pins':annotated[:limit],
                            'total_pins':len(annotated), 'pins_truncated':len(annotated)>limit,
                            'limitations':warnings_by_uuid[m['uuid']] + [x['reason'] for x in power_warnings]})
    return results,issues


def parent_sheet_interfaces(parent_file: Path, child_uuid: str):
    """Read only the named sheet object; its sheet pins are in parent coordinates."""
    text = parent_file.read_text(encoding='utf-8-sig')
    for tag, fragment in forms(text):
        if tag != 'sheet':
            continue
        expr = parse(fragment)
        if val(expr, 'uuid') == child_uuid:
            result = []
            for pin in children(expr, 'pin'):
                if len(pin) > 1:
                    result.append({'name': pin[1], 'position': xy(pin),
                                   'uuid': val(pin, 'uuid')})
            return result
    return []


def connected_parent_pins(parent_file, wires, labels, junctions, origin, limit):
    """Find other symbol pins in the same parent-side local wire network.

    Conservative sheet-local geometry only; never marks full electrical verification.
    """
    source = parent_file.read_text(encoding='utf-8-sig')
    lib, _, _, _, _ = local_geometry(parent_file)
    candidates = []
    warnings = []
    for tag, fragment in forms(source):
        if tag != 'symbol':
            continue
        expr = parse(fragment)
        info = symbol_info(expr, parent_file)
        pins, pin_warnings = pins_from_symbol(expr, lib)
        for warning in pin_warnings:
            warnings.append({'symbol_uuid': info['uuid'], 'reason': warning})
        for pin in pins:
            candidates.append({'reference': info['reference_property'],
                               'symbol_uuid': info['uuid'],
                               'pin_number': pin['number'], 'pin_name': pin['name'],
                               'position_mm': pin['position_mm'],
                               'instances': info['instances']})
    # Include other pins as graph anchors, but avoid connecting to a pin that
    # merely occupies a crossing of two unrelated segments.
    positions = [tuple(c['position_mm']) for c in candidates]
    add, find, _ = resolve_local_networks(wires, labels, junctions, [origin, *positions])
    connected = []
    origin_is_attached = any(is_on_segment(origin, a, b) for a, b in wires)
    if origin_is_attached:
        network = find(add(origin))
        for c in candidates:
            pos = tuple(c['position_mm'])
            if not any(is_on_segment(pos, a, b) for a, b in wires):
                continue
            if find(add(pos)) == network:
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
    source = parent_file.read_text(encoding='utf-8-sig')
    for tag, fragment in forms(source):
        if tag != 'sheet':
            continue
        sheet = parse(fragment)
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
    add, find, _ = resolve_local_networks(wires, labels, junctions, [origin, *positions])
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


def inspect_destination_sheet_pin(parent_file, endpoint, limit, root_dir):
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
        hits = connected_parent_pins(child, wires, labels, junctions, point, limit)
        add, find, groups = resolve_local_networks(wires, labels, junctions, [point])
        anchored = any(is_on_segment(point, a, b) for a, b in wires)
        same_network = groups.get(find(add(point)), []) if anchored else []
        results.append({
            'hierarchical_label': label['name'],
            'position_mm': list(point),
            'wire_at_label': anchored,
            'connected_component_pins': hits['connected_component_pins'],
            'total_connected_component_pins': hits['total_connected_component_pins'],
            'connected_pins_truncated': hits['connected_pins_truncated'],
            'unresolved_symbol_warnings': hits['unresolved_symbol_warnings'],
            'global_labels_on_local_path': sorted(set(
                x['name'] for x in same_network
                if x['kind'] == 'global_label' and x['name'])),
            'local_labels_on_path': sorted(set(
                x['name'] for x in same_network
                if x['kind'] == 'label' and x['name'])),
            'verification': 'DESTINATION_SHEET_LOCAL_GEOMETRY_ONLY',
        })
    return {'destination_status': 'CHILD_LOCAL_PATH_INSPECTED',
            'destination_file': str(child),
            'destination_paths': results,
            'destination_paths_truncated': len(matching) > limit,
            'destination_verified': False}


def hierarchical_trace(root: Path, data, reference: str, limit: int, discover_pins=False):
    """Trace child hierarchical-label anchors to matching parent sheet pins.

    This is *interface evidence*, not a KiCad-equivalent net resolver.
    Reused file instances are surfaced as ambiguous and never certified.
    """
    records, issues = inspect_pins(root, data, reference, limit, resolved=True)
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
                add, find, groups = resolve_local_networks(wires, labels, junctions, [at])
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
                               'project_net_verified': False}
                if discover_pins:
                    trace.update(connected_parent_pins(parent, wires, labels, junctions, at, limit))
                    trace.update(connected_parent_sheet_pins(
                        parent, wires, labels, junctions, at,
                        sheet['uuid'], matching[0]['uuid'], limit))
                    for endpoint in trace['connected_sheet_pins']:
                        endpoint.update(inspect_destination_sheet_pin(
                            parent, endpoint, limit, root.parent))
                traces.append(trace)
            pin['hierarchical_traces'] = traces
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


def project_connections(root, data, reference, limit, max_instances, pin_filter=None):
    """Conservative instance-aware traversal of schematic net evidence.

    Local paths are grouped by wire geometry/labels. An edge is added only
    for an explicitly matched hierarchical interface or equal global/power
    names. This is NOT a KiCad-equivalent ERC/netlist computation.
    """
    from collections import defaultdict, deque
    instances = build_instance_tree(root, data, max_instances)
    cached = {}
    for node in instances:
        file = Path(node['file'])
        if file in cached:
            continue
        lib, wires, labels, junctions, no_conn = local_geometry(file)
        source = file.read_text(encoding='utf-8-sig')
        component_pins = []
        sheet_pins = []
        for tag, frag in forms(source):
            if tag == 'symbol':
                expr = parse(frag)
                info = symbol_info(expr, file)
                pins, warnings = pins_from_symbol(expr, lib)
                for pin in pins:
                    component_pins.append({**pin, 'reference': info['reference_property'],
                                           'instances': info['instances'], 'symbol_uuid': info['uuid'],
                                           'lib_id': info['lib_id']})
            elif tag == 'sheet':
                expr = parse(frag)
                for pin in children(expr, 'pin'):
                    point = xy(pin)
                    if point:
                        sheet_pins.append({'name': pin[1], 'point': point,
                                           'sheet_uuid': val(expr, 'uuid')})
        powers, warnings = power_symbol_anchors(file, lib)
        anchors = [tuple(p['position_mm']) for p in component_pins]
        anchors += [x['point'] for x in sheet_pins]
        anchors += [tuple(p['position_mm']) for p in powers]
        add, find, groups = resolve_local_networks(wires, labels, junctions, anchors)
        # Only an electrically anchored node is admitted; a coincident crossing
        # without a junction is never proof of connectivity.
        # Capture THIS file's graph and geometry; otherwise the cached closure
        # would read values rebound by later iterations of the file loop.
        def group(point, _find=find, _add=add, _wires=wires,
                  _labels=labels, _anchors=anchors):
            if any(is_on_segment(point, a, b) for a, b in _wires) or any(
                    l['point'] and math.dist(l['point'], point) < 0.002 for l in _labels):
                return _find(_add(point))
            # Direct physical pin overlap is an endpoint, but no validation.
            if sum(math.dist(point, x) < 0.002 for x in _anchors) > 1:
                return _find(_add(point))
            return None
        for p in component_pins:
            p['_group'] = group(tuple(p['position_mm']))
        for p in sheet_pins:
            p['_group'] = group(p['point'])
        for p in powers:
            p['_group'] = group(tuple(p['position_mm']))
        cached[file] = {'labels': labels, 'components': component_pins,
                        'sheet_pins': sheet_pins, 'powers': powers,
                        'group': group, 'warnings': warnings}

    graph = defaultdict(set)
    details = defaultdict(lambda: {'components': [], 'global': set(), 'power': set(), 'hier': [], 'labels': set()})
    global_nodes, power_nodes = defaultdict(list), defaultdict(list)
    for i, node in enumerate(instances):
        file = Path(node['file'])
        d = cached[file]
        def key(g): return (i, g)
        for p in d['components']:
            if p['_group'] is not None and p['lib_id'] and not p['lib_id'].startswith('power:'):
                matches = [x for x in p['instances'] if x.get('path') == node['path']]
                ref = matches[0]['reference'] if len(matches) == 1 else p['reference']
                details[key(p['_group'])]['components'].append({
                    'reference': ref, 'pin_number': p['number'],
                    'pin_name': p['name'], 'file': str(file), 'instance_path': node['path']})
        for l in d['labels']:
            if not l['point']:
                continue
            group = d['group'](l['point'])
            if group is None: continue
            item = details[key(group)]
            if l['kind'] == 'global_label':
                item['global'].add(l['name'])
                global_nodes[l['name']].append(key(group))
            elif l['kind'] == 'hierarchical_label':
                item['hier'].append(l['name'])
            else: item['labels'].add(l['name'])
        for p in d['powers']:
            if p['_group'] is not None:
                details[key(p['_group'])]['power'].add(p['name'])
                # PWR_FLAG is an ERC power-driver marker, not an electrical
                # net name. Unioning it globally bridges otherwise unrelated
                # nets that merely contain a PWR_FLAG symbol.
                if p['name'] != 'PWR_FLAG':
                    power_nodes[p['name']].append(key(p['_group']))
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
                child_group = d['group'](l['point'])
                if child_group is not None:
                    # This is the CHILD instance, not the last loop iteration.
                    target = (i, child_group)
                    graph[origin].add(target)
                    graph[target].add(origin)
    # Global labels and power symbols are global *by KiCad semantics*.
    for collection in (global_nodes, power_nodes):
        for _, keys in collection.items():
            if keys:
                first_key = keys[0]
                for other in keys[1:]:
                    graph[first_key].add(other)
                    graph[other].add(first_key)

    starts = []
    for i, node in enumerate(instances):
        for p in cached[Path(node['file'])]['components']:
            if p['_group'] is None: continue
            matches = [x for x in p['instances'] if x.get('path') == node['path']]
            ref = matches[0]['reference'] if len(matches)==1 else p['reference']
            if ref == reference and (pin_filter is None or str(p["number"]) == pin_filter):
                starts.append((i, p['_group'], p['number']))
    if not starts:
        return {'status': 'TARGET_NOT_FOUND_OR_UNRESOLVED', 'reference': reference,
                'project_net_verified': False, 'instance_count': len(instances)}
    if len({(i,g) for i,g,_ in starts}) != 1:
        return {'status': 'AMBIGUOUS_TARGET_NETS', 'reference': reference,
                'starting_pins': [{'instance_path': instances[i]['path'], 'pin': n}
                                  for i,g,n in starts][:limit],
                'project_net_verified': False, 'instance_count': len(instances)}
    start = (starts[0][0], starts[0][1])
    reached = {start}
    q = deque([start])
    while q:
        current = q.popleft()
        for other in graph[current]:
            if other not in reached:
                reached.add(other)
                q.append(other)
    pins = sorted([p for group in reached for p in details[group]['components']],
                  key=lambda p: (p['instance_path'], p['reference'] or '', p['pin_number'] or ''))
    globals_found = sorted({x for group in reached for x in details[group]['global']})
    power_found = sorted({x for group in reached for x in details[group]['power']})
    return {'status': 'PROJECT_CONNECTIVITY_EVIDENCE', 'reference': reference,
            'source_instance_path': instances[starts[0][0]]['path'],
            'source_pin_number': starts[0][2],
            'connected_component_pins': pins[:limit],
            'total_connected_component_pins': len(pins),
            'connected_pins_truncated': len(pins) > limit,
            'global_labels': globals_found[:limit], 'power_net_names': power_found[:limit],
            'names_truncated': len(globals_found)>limit or len(power_found)>limit,
            'groups_visited': len(reached), 'instance_count': len(instances),
            'project_net_verified': False,
            'limitations': ['Conservative geometry and declared labels only; not KiCad netlist parity',
                            'Complex symbol inheritance, buses, hidden connectivity, and ambiguous unit instances may be unresolved',
                            'Starting reference with pins on multiple separate nets needs a pin-specific query']}


def root_file(raw: str):
    p = Path(raw).expanduser().resolve()
    if p.is_dir():
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode', choices=['summary', 'component', 'sheet', 'pins', 'local-net', 'hier-net', 'connected-pins', 'project-net', 'instances'])
    ap.add_argument('target', nargs='?', help='reference (component/pins) or sheet filename/name (sheet)')
    ap.add_argument('--project', required=True, help='root .kicad_sch (preferred) or its directory')
    ap.add_argument('--limit', type=int, default=20)
    ap.add_argument('--max-files', type=int, default=100)
    ap.add_argument('--pin', help='pin number for project-net; necessary when a component has multiple nets')
    args = ap.parse_args(argv)
    try:
        if not (1 <= args.limit <= 200 and 1 <= args.max_files <= 1000):
            raise QueryError('limit and max-files must be positive and within supported bounds')
        if args.pin and args.mode != 'project-net':
            raise QueryError('--pin is only supported with project-net')
        if args.mode not in ('summary', 'instances') and not args.target:
            raise QueryError(f'{args.mode} requires a target')
        root = root_file(args.project)
        data, missing, outside = discover(root, args.max_files)
        records = []
        if args.mode == 'project-net':
            records = [project_connections(root, data, args.target, args.limit, args.max_files, args.pin)]
        elif args.mode == 'instances':
            records = build_instance_tree(root, data, args.max_files)
        elif args.mode in ('hier-net', 'connected-pins'):
            records, pin_issues = hierarchical_trace(root, data, args.target, args.limit, discover_pins=(args.mode == 'connected-pins'))
        elif args.mode in ('pins','local-net'):
            records, pin_issues = inspect_pins(root, data, args.target, args.limit, resolved=(args.mode == 'local-net'))
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
                    if args.target in (sh['name'], sh['file'], Path(sh['file'] or '').stem):
                        records.append(sh)
        else:
            records = [{'file': d['file'], 'symbol_count': len(d['symbols']),
                        'child_sheet_count': len(d['sheets'])} for d in data]
        out = {'mode': args.mode, 'target': args.target, 'root': str(root),
               'results': records[:args.limit], 'total_matches': len(records),
               'truncated': len(records)>args.limit, 'missing_sheets': missing,
               'skipped_outside_project': outside,
               'verification': 'INSTANCE_AWARE_PROJECT_EVIDENCE_ONLY' if args.mode == 'project-net' else 'HIERARCHICAL_INSTANCE_DISCOVERY_ONLY' if args.mode == 'instances' else 'PARENT_CONNECTED_PINS_GEOMETRY_ONLY' if args.mode == 'connected-pins' else 'HIERARCHICAL_INTERFACE_EVIDENCE_ONLY' if args.mode == 'hier-net' else 'SHEET_LOCAL_ONLY' if args.mode == 'local-net' else 'LOCAL_GEOMETRY_EVIDENCE_ONLY' if args.mode == 'pins' else 'STRUCTURAL_DISCOVERY_ONLY',
               'limitations': (['Parent sheet pins, other connected sheet pins, and wire/label paths are geometric/interface evidence only',
                               'Destination child pins and labels are sheet-local evidence only; global labels, cross-sheet power nets, reused instances, buses and inherited symbols are not fully resolved',
                               'Not a KiCad-equivalent full-project net resolver'] if args.mode in ('hier-net', 'connected-pins') else ['Local wire paths and local-label names do not prove entire project connectivity',
                               'Cross-sheet/global power-net connectivity, buses, inherited symbols and reused sheet instances are not resolved',
                               'Geometric connectivity may differ from KiCad in complex edge cases'] if args.mode == 'local-net' else ['Pin positions and direct wires are geometric evidence, not resolved electrical nets',
                               'Labels on connected multi-segment paths may not be reported',
                               'Hierarchical, global and power connectivity are not resolved'] if args.mode == 'pins' else ['No electrical connectivity or pin-net verification',
                               'Shared sheet files are not expanded into unique hierarchical instances',
                               'Symbol reference properties can differ from instance references']),
               'warnings': pin_issues if args.mode in ('pins','local-net','hier-net','connected-pins') else []}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    except (QueryError, OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({'error': str(exc), 'verification': 'NOT_VERIFIED'}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
