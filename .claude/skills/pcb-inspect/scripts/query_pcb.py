#!/usr/bin/env python3
"""Targeted, read-only KiCad PCB inspection (v0.4). Python 3.10+ stdlib."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path


class QueryError(Exception):
    pass


def forms(source):
    """Yield direct child forms; correctly skip quoted parentheses and escapes."""
    depth = 0
    start = None
    quoted = False
    escaped = False
    for i, ch in enumerate(source):
        if quoted:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                quoted = False
        elif ch == '"':
            quoted = True
        elif ch == "(":
            if depth == 1:
                start = i
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise QueryError("invalid S-expression: extra closing parenthesis")
            if depth == 1 and start is not None:
                fragment = source[start : i + 1]
                body = fragment[1:].lstrip()
                if not body or body.startswith(")"):
                    raise QueryError("empty S-expression")
                head = body.split(None, 1)[0].split(")", 1)[0]
                if not head:
                    raise QueryError("empty S-expression head")
                yield head, fragment
                start = None
    if quoted or depth != 0:
        raise QueryError("invalid or incomplete S-expression")


def parse(form):
    stack = []
    root = None
    i = 0
    while i < len(form):
        char = form[i]
        if char.isspace():
            i += 1
            continue
        if char == "(":
            node = []
            if stack:
                stack[-1].append(node)
            stack.append(node)
            if root is None:
                root = node
            i += 1
        elif char == ")":
            if not stack:
                raise QueryError("extra closing parenthesis")
            stack.pop()
            i += 1
        elif char == '"':
            i += 1
            out = []
            while i < len(form):
                char = form[i]
                if char == '"':
                    i += 1
                    break
                if char == "\\" and i + 1 < len(form):
                    i += 1
                    out.append({"n": "\n", "r": "\r", "t": "\t", '"': '"', "\\": "\\"}.get(form[i], "\\" + form[i]))
                else:
                    out.append(char)
                i += 1
            else:
                raise QueryError("unterminated quoted string")
            stack[-1].append("".join(out))
        else:
            j = i
            while j < len(form) and not form[j].isspace() and form[j] not in "()":
                j += 1
            if j == i:
                raise QueryError("invalid token")
            stack[-1].append(form[i:j])
            i = j
    if stack or root is None:
        raise QueryError("invalid S-expression")
    return root


def children(expr, tag):
    return [part for part in expr[1:] if isinstance(part, list) and part and part[0] == tag]


def first(expr, tag):
    return next(iter(children(expr, tag)), None)


def value(expr, tag, default=None):
    node = first(expr, tag)
    return node[1] if node and len(node) > 1 else default


def props(expr):
    return {part[1]: part[2] for part in children(expr, "property") if len(part) > 2}


def number(raw, description):
    try:
        result = float(raw)
    except (TypeError, ValueError) as exc:
        raise QueryError(f"invalid numeric {description}") from exc
    if not math.isfinite(result):
        raise QueryError(f"non-finite {description}")
    return result


def clean_number(value):
    """KiCad board coordinates are written to no more than six decimal places."""
    rounded = round(value, 6)
    return 0.0 if rounded == 0 else rounded


def at_value(expr, description="footprint placement"):
    node = first(expr, "at")
    if not node:
        return None
    if len(node) < 3:
        raise QueryError(f"invalid {description}")
    return {
        "x_mm": number(node[1], description),
        "y_mm": number(node[2], description),
        "rotation_deg": number(node[3], description) if len(node) > 3 else 0.0,
    }


def size_value(expr):
    node = first(expr, "size")
    if not node or len(node) < 3:
        return None
    return {"x_mm": number(node[1], "pad size"), "y_mm": number(node[2], "pad size")}


def layer_values(expr):
    node = first(expr, "layers")
    if not node or len(node) < 2:
        return None
    return [str(layer) for layer in node[1:]]


def net_value(expr, declared_nets):
    node = first(expr, "net")
    if not node:
        return {"net_code": None, "net_name": None, "net_status": "UNCONNECTED"}
    if len(node) < 2:
        return {"net_code": None, "net_name": None, "net_status": "NOT_VERIFIED"}
    code = str(node[1])
    declared_name = declared_nets.get(code)
    if len(node) == 2 and declared_name is None:
        if code == "0":
            return {"net_code": code, "net_name": None, "net_status": "UNCONNECTED"}
        return {"net_code": None, "net_name": code, "net_status": "ASSIGNED_WITHOUT_DECLARATION"}
    name = str(node[2]) if len(node) > 2 else declared_name
    if code == "0" or name == "":
        return {"net_code": code, "net_name": None, "net_status": "UNCONNECTED"}
    if declared_name is None:
        return {"net_code": code, "net_name": name, "net_status": "ASSIGNED_WITHOUT_DECLARATION" if name else "NOT_VERIFIED"}
    if declared_name != name:
        return {"net_code": code, "net_name": name, "net_status": "NOT_VERIFIED"}
    return {"net_code": code, "net_name": name, "net_status": "ASSIGNED"}


def optional_number(raw):
    """Return a finite number, or None when a saved geometry field is unusable."""
    try:
        return number(raw, "geometry")
    except QueryError:
        return None


def point_value(expr, tag):
    node = first(expr, tag)
    if not node or len(node) < 3:
        return None
    x_mm = optional_number(node[1])
    y_mm = optional_number(node[2])
    if x_mm is None or y_mm is None:
        return None
    return {"x_mm": x_mm, "y_mm": y_mm}


def scalar_value(expr, tag):
    node = first(expr, tag)
    if not node or len(node) != 2:
        return None
    return optional_number(node[1])


def arc_length(start, mid, end):
    """Return the circular arc through three points, or None if it is unresolved.

    KiCad track arcs encode a point on the intended sweep as ``mid``.  The
    three points define a circle, while whether ``mid`` lies on the clockwise
    or counter-clockwise sweep selects the correct minor or major arc.
    """
    if start is None or mid is None or end is None:
        return None
    x1, y1 = start["x_mm"], start["y_mm"]
    x2, y2 = mid["x_mm"], mid["y_mm"]
    x3, y3 = end["x_mm"], end["y_mm"]
    determinant = 2.0 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    if abs(determinant) <= 1e-12:
        return None
    x1_sq_y1_sq = x1 * x1 + y1 * y1
    x2_sq_y2_sq = x2 * x2 + y2 * y2
    x3_sq_y3_sq = x3 * x3 + y3 * y3
    center_x = (
        x1_sq_y1_sq * (y2 - y3)
        + x2_sq_y2_sq * (y3 - y1)
        + x3_sq_y3_sq * (y1 - y2)
    ) / determinant
    center_y = (
        x1_sq_y1_sq * (x3 - x2)
        + x2_sq_y2_sq * (x1 - x3)
        + x3_sq_y3_sq * (x2 - x1)
    ) / determinant
    radius = math.hypot(x1 - center_x, y1 - center_y)
    if radius <= 1e-12 or not math.isfinite(radius):
        return None

    def ccw_delta(first_angle, second_angle):
        return (second_angle - first_angle) % (2.0 * math.pi)

    start_angle = math.atan2(y1 - center_y, x1 - center_x)
    mid_angle = math.atan2(y2 - center_y, x2 - center_x)
    end_angle = math.atan2(y3 - center_y, x3 - center_x)
    start_to_end = ccw_delta(start_angle, end_angle)
    start_to_mid = ccw_delta(start_angle, mid_angle)
    if start_to_end <= 1e-12 or start_to_mid <= 1e-12:
        return None
    sweep = start_to_end if start_to_mid < start_to_end else (2.0 * math.pi - start_to_end)
    if sweep <= 1e-12 or not math.isfinite(sweep):
        return None
    return clean_number(radius * sweep)


def track_data(expr, declared_nets, source_index):
    geometry_type = str(expr[0]) if expr else "UNKNOWN"
    start = point_value(expr, "start")
    end = point_value(expr, "end")
    mid = point_value(expr, "mid") if geometry_type == "arc" else None
    width = scalar_value(expr, "width")
    layer = value(expr, "layer")
    if geometry_type == "segment":
        length = clean_number(math.hypot(end["x_mm"] - start["x_mm"], end["y_mm"] - start["y_mm"])) if start and end else None
    elif geometry_type == "arc":
        length = arc_length(start, mid, end)
    else:
        length = None
    result = {
        "geometry_type": geometry_type,
        "start": start,
        "end": end,
        "width_mm": width,
        "layer": layer,
        "length_mm": length,
        "length_status": "STRUCTURAL_EVIDENCE" if length is not None else "NOT_VERIFIED",
        "geometry_status": "STRUCTURAL_EVIDENCE" if start and end and width is not None and layer and (geometry_type != "arc" or mid and length is not None) else "NOT_VERIFIED",
        "verification": "STRUCTURAL_EVIDENCE",
        "_source_index": source_index,
    }
    if geometry_type == "arc":
        result["mid"] = mid
    result.update(net_value(expr, declared_nets))
    return result


def via_data(expr, declared_nets, source_index):
    via_type = value(expr, "type")
    result = {
        "position": point_value(expr, "at"),
        "size_mm": scalar_value(expr, "size"),
        "drill_mm": scalar_value(expr, "drill"),
        "layer_span": layer_values(expr),
        "via_type": via_type,
        "via_type_status": "STRUCTURAL_EVIDENCE" if via_type is not None else "NOT_VERIFIED",
        "verification": "STRUCTURAL_EVIDENCE",
        "_source_index": source_index,
    }
    result["geometry_status"] = (
        "STRUCTURAL_EVIDENCE"
        if result["position"] is not None
        and result["size_mm"] is not None
        and result["drill_mm"] is not None
        and result["layer_span"] is not None
        else "NOT_VERIFIED"
    )
    result.update(net_value(expr, declared_nets))
    return result


def board_position(footprint_at, pad_at, footprint_layer):
    """Transform a footprint-local pad centre into board coordinates.

    KiCad PCB coordinates use a downward-positive Y axis. On B.Cu, the
    footprint local X axis is mirrored before the parent rotation is applied.
    This reports only the pad centre; it does not construct pad outlines.
    """
    if footprint_at is None or pad_at is None:
        return None
    local_x = pad_at["x_mm"]
    local_y = pad_at["y_mm"]
    if footprint_layer == "B.Cu":
        local_x = -local_x
    radians = math.radians(footprint_at["rotation_deg"])
    cosine = math.cos(radians)
    sine = math.sin(radians)
    return {
        "x_mm": clean_number(footprint_at["x_mm"] + local_x * cosine + local_y * sine),
        "y_mm": clean_number(footprint_at["y_mm"] - local_x * sine + local_y * cosine),
    }


def footprint_data(expr):
    footprint_props = props(expr)
    return {
        "reference": footprint_props.get("Reference") or value(expr, "reference"),
        "value": footprint_props.get("Value"),
        "library_id": expr[1] if len(expr) > 1 else None,
        "layer": value(expr, "layer"),
        "position": at_value(expr),
        "uuid": value(expr, "uuid"),
        "attributes": [item[1:] for item in children(expr, "attr")],
        "verification": "STRUCTURAL_EVIDENCE",
    }


def geometry_status(pad_type, shape, pad_at, size, layers):
    if pad_type not in {"smd", "thru_hole", "connect", "np_thru_hole"}:
        return "NOT_VERIFIED"
    if shape not in {"circle", "rect", "oval", "trapezoid", "roundrect"}:
        return "NOT_VERIFIED"
    if pad_at is None or size is None or layers is None:
        return "NOT_VERIFIED"
    return "STRUCTURAL_EVIDENCE"


def pad_data(expr, footprint, declared_nets, source_index):
    if len(expr) < 4:
        raise QueryError("invalid pad definition")
    pad_at = at_value(expr, "pad placement")
    size = size_value(expr)
    layers = layer_values(expr)
    pad_type = str(expr[2])
    shape = str(expr[3])
    result = {
        "number": str(expr[1]),
        "type": pad_type,
        "shape": shape,
        "layers": layers,
        "size_mm": size,
        "position": board_position(footprint["position"], pad_at, footprint["layer"]),
        "geometry_status": geometry_status(pad_type, shape, pad_at, size, layers),
        "verification": "STRUCTURAL_EVIDENCE",
        "_source_index": source_index,
    }
    result.update(net_value(expr, declared_nets))
    return result


def natural_key(value):
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value)]


def pad_sort_key(pad):
    return natural_key(pad["number"]), pad["_source_index"]


def public_pad(pad):
    return {key: value for key, value in pad.items() if key != "_source_index"}


def point_distance(first_point, second_point):
    """Return the Euclidean distance between two saved board-space points."""
    if first_point is None or second_point is None:
        return None
    return clean_number(math.hypot(
        second_point["x_mm"] - first_point["x_mm"],
        second_point["y_mm"] - first_point["y_mm"],
    ))


def footprint_origin(footprint):
    position = footprint["position"]
    if position is None:
        return None
    return {"x_mm": position["x_mm"], "y_mm": position["y_mm"]}


def spatial_limit_data(records, limit, count_key, list_key):
    return {
        count_key: len(records),
        list_key: records[:limit],
        f"{list_key}_truncated": len(records) > limit,
    }


def scan_board(file):
    source = file.read_text(encoding="utf-8-sig")
    metadata = {}
    layers = []
    declared_nets = {}
    footprints = []
    tracks = []
    vias = []
    def add_net(expr):
        if len(expr) < 3:
            return
        code = str(expr[1])
        name = str(expr[2])
        if code in declared_nets and declared_nets[code] != name:
            raise QueryError(f"conflicting net declarations for code {code}")
        declared_nets[code] = name

    for tag, fragment in forms(source):
        if tag == "version":
            metadata["version"] = str(fragment[1:-1].strip().split(maxsplit=1)[-1])
        elif tag == "generator":
            metadata["generator"] = str(fragment[1:-1].strip().split(maxsplit=1)[-1]).strip('"')
        elif tag == "layers":
            expr = parse(fragment)
            for item in expr[1:]:
                if isinstance(item, list) and len(item) >= 3:
                    layers.append({"id": item[0], "name": item[1], "type": item[2]})
        elif tag == "net":
            add_net(parse(fragment))
        elif tag == "nets":
            for net in children(parse(fragment), "net"):
                add_net(net)
        elif tag == "footprint":
            expr = parse(fragment)
            footprints.append((footprint_data(expr), expr))
        elif tag in {"segment", "arc"}:
            tracks.append((parse(fragment), len(tracks)))
        elif tag == "via":
            vias.append((parse(fragment), len(vias)))
    return metadata, layers, declared_nets, footprints, tracks, vias


def base_data(file):
    return {"file": str(file), "verification": "STRUCTURAL_EVIDENCE", "scope": "saved_board_only"}


def summarize(file, target, limit):
    metadata, layers, _declared_nets, footprints, _tracks, _vias = scan_board(file)
    data = base_data(file)
    by_layer = {}
    matches = []
    for footprint, _expr in footprints:
        layer = footprint["layer"] or "UNKNOWN"
        by_layer[layer] = by_layer.get(layer, 0) + 1
        if target is None or footprint["reference"] == target:
            matches.append(footprint)
    if target is not None:
        if not matches:
            return {
                **data,
                "status": "NOT_FOUND",
                "reference": target,
                "limitations": ["No footprint with this Reference in the saved PCB; not a schematic/BOM validation."],
            }
        return {
            **data,
            "status": "FOUND" if len(matches) == 1 else "AMBIGUOUS_REFERENCE",
            "reference": target,
            "total_matches": len(matches),
            "footprints": matches[:limit],
            "truncated": len(matches) > limit,
            "limitations": [
                "Footprint placement and properties only; pad, routing, copper and DRC are NOT_VERIFIED.",
                "Saved PCB may differ from unsaved editor state.",
            ],
        }
    return {
        **data,
        "status": "BOARD_SUMMARY",
        "metadata": metadata,
        "layer_count": len(layers),
        "layers": layers[:limit],
        "layers_truncated": len(layers) > limit,
        "footprint_count": len(footprints),
        "footprints_by_layer": by_layer,
        "footprints": [footprint for footprint, _expr in footprints[:limit]],
        "footprints_truncated": len(footprints) > limit,
        "limitations": ["No copper connectivity, clearance, ERC/DRC, pad-to-net, or zone-fill verification."],
    }


def inspect_pads(file, reference, limit):
    _metadata, _layers, declared_nets, footprints, _tracks, _vias = scan_board(file)
    data = base_data(file)
    matches = [(footprint, expr) for footprint, expr in footprints if footprint["reference"] == reference]
    if not matches:
        return {
            **data,
            "status": "NOT_FOUND",
            "reference": reference,
            "limitations": ["No footprint with this Reference in the saved PCB; not a schematic/BOM validation."],
        }
    if len(matches) > 1:
        return {
            **data,
            "status": "AMBIGUOUS_REFERENCE",
            "reference": reference,
            "total_matches": len(matches),
            "footprints": [footprint for footprint, _expr in matches[:limit]],
            "truncated": len(matches) > limit,
            "limitations": ["Pads are not returned for an ambiguous Reference."],
        }
    footprint, expr = matches[0]
    pads = [pad_data(pad, footprint, declared_nets, index) for index, pad in enumerate(children(expr, "pad"))]
    pads.sort(key=pad_sort_key)
    unresolved_geometry = any(pad["geometry_status"] == "NOT_VERIFIED" for pad in pads)
    return {
        **data,
        "status": "FOUND",
        "reference": reference,
        "footprint": footprint,
        "pad_count": len(pads),
        "pads": [public_pad(pad) for pad in pads[:limit]],
        "pads_truncated": len(pads) > limit,
        "limitations": [
            "Net assignment is saved PCB structural data and does not prove copper connectivity.",
            "Pad centres include the saved footprint translation, rotation, and B.Cu mirror transform.",
            "Custom or unsupported pad outlines are NOT_VERIFIED; reported size is only the saved nominal pad size.",
            "Saved PCB may differ from unsaved editor state.",
        ] + (["One or more pad geometries are NOT_VERIFIED."] if unresolved_geometry else []),
    }


def inspect_net(file, net_name, limit):
    _metadata, _layers, declared_nets, footprints, _tracks, _vias = scan_board(file)
    data = base_data(file)
    matching_codes = sorted(code for code, name in declared_nets.items() if name == net_name)
    if len(matching_codes) != 1:
        if len(matching_codes) > 1:
            return {
                **data,
                "status": "NOT_VERIFIED",
                "net": net_name,
                "net_status": "NOT_VERIFIED",
                "net_codes": matching_codes,
                "limitations": ["Multiple declared net codes share this name; assignments cannot be resolved safely."],
            }
    assignments = []
    for footprint, expr in footprints:
        for index, pad in enumerate(children(expr, "pad")):
            pad_record = pad_data(pad, footprint, declared_nets, index)
            if pad_record["net_name"] == net_name:
                assignments.append((footprint, pad_record))
    if not assignments:
        return {
            **data,
            "status": "NOT_FOUND",
            "net": net_name,
            "net_status": "MISSING",
            "footprint_count": 0,
            "pad_count": 0,
            "footprints": [],
            "pads": [],
            "limitations": ["No saved pad assignment with this exact net name exists in the saved PCB."],
        }
    unresolved = [pad for _footprint, pad in assignments if pad["net_status"] not in {"ASSIGNED", "ASSIGNED_WITHOUT_DECLARATION"}]
    if unresolved:
        return {
            **data,
            "status": "NOT_VERIFIED",
            "net": net_name,
            "net_status": "NOT_VERIFIED",
            "net_code": matching_codes[0],
            "limitations": ["At least one pad has an inconsistent or unresolved saved net assignment."],
        }
    assignments.sort(key=lambda item: (natural_key(item[0]["reference"] or ""), pad_sort_key(item[1])))
    footprint_rows = {}
    for footprint, _pad in assignments:
        footprint_rows.setdefault(
            footprint["reference"],
            {"reference": footprint["reference"], "value": footprint["value"], "layer": footprint["layer"]},
        )
    pads = [{"reference": footprint["reference"], **public_pad(pad)} for footprint, pad in assignments]
    ordered_footprints = [footprint_rows[key] for key in sorted(footprint_rows, key=natural_key)]
    return {
        **data,
        "status": "FOUND",
        "net": net_name,
        "net_status": "DECLARED" if matching_codes else "ASSIGNED_WITHOUT_DECLARATION",
        "net_code": matching_codes[0] if matching_codes else None,
        "net_declaration_status": "STRUCTURAL_EVIDENCE" if matching_codes else "NOT_VERIFIED",
        "footprint_count": len(ordered_footprints),
        "pad_count": len(pads),
        "footprints": ordered_footprints[:limit],
        "footprints_truncated": len(ordered_footprints) > limit,
        "pads": pads[:limit],
        "pads_truncated": len(pads) > limit,
        "limitations": [
            "Shared saved net names do not prove copper connectivity, routing, zone fill, or electrical intent.",
            "Unconnected pads are excluded because they have no assigned net.",
            "A name-only net assignment without a declared net table has NOT_VERIFIED net declaration semantics.",
            "Saved PCB may differ from unsaved editor state.",
        ],
    }


def public_routing(record):
    return {key: value for key, value in record.items() if key != "_source_index"}


def inspect_routing(file, net_name, limit, kind):
    """Return saved tracks or vias assigned to one exact net name.

    This is deliberately an assignment query.  The returned items are not
    joined into paths and do not establish any physical copper connection.
    """
    _metadata, _layers, declared_nets, _footprints, raw_tracks, raw_vias = scan_board(file)
    data = base_data(file)
    if kind == "tracks":
        records = [track_data(expr, declared_nets, source_index) for expr, source_index in raw_tracks]
        count_key, list_key = "track_count", "tracks"
    else:
        records = [via_data(expr, declared_nets, source_index) for expr, source_index in raw_vias]
        count_key, list_key = "via_count", "vias"

    matching_codes = sorted(code for code, name in declared_nets.items() if name == net_name)
    if len(matching_codes) > 1:
        return {
            **data,
            "status": "NOT_VERIFIED",
            "net": net_name,
            "net_status": "NOT_VERIFIED",
            "net_codes": matching_codes,
            count_key: 0,
            list_key: [],
            f"{list_key}_truncated": False,
            "limitations": ["Multiple declared net codes share this name; assignments cannot be resolved safely."],
        }

    if net_name == "":
        matching = [record for record in records if record["net_status"] == "UNCONNECTED"]
        reported_net_status = "UNCONNECTED"
        declaration_status = "NOT_APPLICABLE"
    elif matching_codes:
        matching = [
            record
            for record in records
            if record["net_code"] in matching_codes or record["net_name"] == net_name
        ]
        reported_net_status = "DECLARED"
        declaration_status = "STRUCTURAL_EVIDENCE"
    else:
        matching = [record for record in records if record["net_name"] == net_name]
        reported_net_status = "ASSIGNED_WITHOUT_DECLARATION" if matching else "MISSING"
        declaration_status = "NOT_VERIFIED"

    if matching and any(record["net_status"] not in {"ASSIGNED", "ASSIGNED_WITHOUT_DECLARATION", "UNCONNECTED"} for record in matching):
        return {
            **data,
            "status": "NOT_VERIFIED",
            "net": net_name,
            "net_status": "NOT_VERIFIED",
            "net_declaration_status": declaration_status,
            count_key: len(matching),
            list_key: [public_routing(record) for record in matching[:limit]],
            f"{list_key}_truncated": len(matching) > limit,
            "limitations": ["At least one matching saved routing item has an inconsistent or unresolved net assignment."],
        }

    matching.sort(key=lambda record: record["_source_index"])
    if not matching:
        if net_name == "":
            absent_message = "No unconnected saved routing items exist in the saved PCB."
        elif matching_codes:
            absent_message = "The net is declared, but no saved routing items are assigned to it."
        else:
            absent_message = "No saved routing item has this exact net assignment."
        return {
            **data,
            "status": "NOT_FOUND",
            "net": net_name,
            "net_status": reported_net_status,
            "net_code": matching_codes[0] if matching_codes else None,
            "net_declaration_status": declaration_status,
            count_key: 0,
            list_key: [],
            f"{list_key}_truncated": False,
            "limitations": [absent_message],
        }

    return {
        **data,
        "status": "FOUND",
        "net": net_name,
        "net_status": reported_net_status,
        "net_code": matching_codes[0] if matching_codes else None,
        "net_declaration_status": declaration_status,
        count_key: len(matching),
        list_key: [public_routing(record) for record in matching[:limit]],
        f"{list_key}_truncated": len(matching) > limit,
        "limitations": [
            "Saved net assignment and geometry do not prove physical copper connectivity, clearance, route completeness, or signal-path length.",
            "A NOT_VERIFIED length is returned as null rather than estimated from malformed or unsupported geometry.",
            "Saved PCB may differ from unsaved editor state.",
        ],
    }


def inspect_tracks(file, net_name, limit):
    return inspect_routing(file, net_name, limit, "tracks")


def inspect_vias(file, net_name, limit):
    return inspect_routing(file, net_name, limit, "vias")


def inspect_nearby(file, reference, limit):
    """Find footprint origins near one uniquely identified saved footprint."""
    _metadata, _layers, _declared_nets, footprints, _tracks, _vias = scan_board(file)
    data = base_data(file)
    matches = [(index, footprint) for index, (footprint, _expr) in enumerate(footprints) if footprint["reference"] == reference]
    if not matches:
        return {
            **data,
            "status": "NOT_FOUND",
            "reference": reference,
            "limitations": ["No footprint with this Reference in the saved PCB; not a schematic/BOM validation."],
        }
    if len(matches) > 1:
        return {
            **data,
            "status": "AMBIGUOUS_REFERENCE",
            "reference": reference,
            "total_matches": len(matches),
            "footprints": [footprint for _index, footprint in matches[:limit]],
            "truncated": len(matches) > limit,
            "limitations": ["Nearby footprints are not returned for an ambiguous Reference."],
        }

    target_index, target = matches[0]
    origin = footprint_origin(target)
    if origin is None:
        return {
            **data,
            "status": "NOT_VERIFIED",
            "reference": reference,
            "error": "target footprint has no resolvable saved board-space origin",
            "measurement_point": "saved footprint origin in board coordinates",
        }

    neighbors = []
    unresolved = False
    for index, (footprint, _expr) in enumerate(footprints):
        if index == target_index:
            continue
        neighbor_origin = footprint_origin(footprint)
        distance = point_distance(origin, neighbor_origin)
        row = {
            "reference": footprint["reference"],
            "value": footprint["value"],
            "layer": footprint["layer"],
            "origin": neighbor_origin,
            "distance_mm": distance,
            "distance_status": "STRUCTURAL_EVIDENCE" if distance is not None else "NOT_VERIFIED",
            "verification": "STRUCTURAL_EVIDENCE",
            "_source_index": index,
        }
        unresolved = unresolved or distance is None
        neighbors.append(row)
    neighbors.sort(key=lambda row: (
        row["distance_mm"] is None,
        row["distance_mm"] if row["distance_mm"] is not None else math.inf,
        natural_key(row["reference"] or ""),
        row["_source_index"],
    ))
    public_neighbors = [{key: value for key, value in row.items() if key != "_source_index"} for row in neighbors]
    result = {
        **data,
        "status": "NOT_VERIFIED" if unresolved else "FOUND",
        "reference": reference,
        "origin": origin,
        "measurement_point": "Euclidean distance between saved footprint origins in board coordinates, in millimeters.",
        **spatial_limit_data(public_neighbors, limit, "neighbor_count", "neighbors"),
        "limitations": [
            "Distance between footprint origins does not prove copper clearance, body-to-body clearance, connectivity, routing quality, or electrical correctness.",
            "Saved PCB may differ from unsaved editor state.",
        ],
    }
    if unresolved:
        result["error"] = "One or more saved footprint origins cannot be resolved; their distances are NOT_VERIFIED."
    return result


def pad_identifier_matches(identifier, footprints):
    """Resolve ref.pin by matching complete saved references before pad numbers.

    The reference is not split on a fixed character position.  Every saved
    reference that is a complete prefix ending at a dot is considered, which
    safely supports references and pad numbers that themselves contain dots.
    """
    matches = []
    reference_matches = []
    for footprint_index, (footprint, expr) in enumerate(footprints):
        reference = footprint["reference"]
        if reference is None:
            continue
        prefix = f"{reference}."
        if not identifier.startswith(prefix):
            continue
        pad_number = identifier[len(prefix):]
        reference_matches.append((footprint_index, footprint, expr, pad_number))
        if not pad_number:
            continue
        for pad_index, pad_expr in enumerate(children(expr, "pad")):
            if len(pad_expr) > 1 and str(pad_expr[1]) == pad_number:
                matches.append((footprint_index, footprint, pad_expr, pad_index))
    return matches, reference_matches


def resolve_pad_identifier(identifier, footprints, declared_nets, limit):
    matches, reference_matches = pad_identifier_matches(identifier, footprints)
    if not matches:
        if "." not in identifier:
            message = "pad identifier must use the complete saved reference followed by a dot and exact saved pad number"
        elif not reference_matches:
            message = "no saved footprint reference matches this pad identifier"
        elif any(not pad_number for _index, _footprint, _expr, pad_number in reference_matches):
            message = "pad identifier has no pad number after its saved reference"
        else:
            message = "no saved pad with this exact number exists on the matching saved footprint reference"
        return {"status": "NOT_FOUND", "identifier": identifier, "error": message}
    if len(matches) > 1:
        candidates = []
        for footprint_index, footprint, pad_expr, pad_index in matches:
            try:
                pad = pad_data(pad_expr, footprint, declared_nets, pad_index)
                position = pad["position"]
            except QueryError:
                position = None
            candidates.append({
                "reference": footprint["reference"],
                "pad_number": str(pad_expr[1]),
                "position": position,
                "_footprint_index": footprint_index,
                "_pad_index": pad_index,
            })
        candidates.sort(key=lambda item: (natural_key(item["reference"] or ""), item["_footprint_index"], item["_pad_index"]))
        public_candidates = [
            {key: value for key, value in item.items() if not key.startswith("_")}
            for item in candidates
        ]
        return {
            "status": "AMBIGUOUS",
            "identifier": identifier,
            "error": "requested pad number identifies multiple saved pads",
            **spatial_limit_data(public_candidates, limit, "total_matches", "matches"),
        }

    _footprint_index, footprint, pad_expr, pad_index = matches[0]
    try:
        pad = pad_data(pad_expr, footprint, declared_nets, pad_index)
    except QueryError as exc:
        return {"status": "NOT_VERIFIED", "identifier": identifier, "error": str(exc)}
    if pad["position"] is None:
        return {
            "status": "NOT_VERIFIED",
            "identifier": identifier,
            "error": "requested pad has no resolvable saved board-space centre",
        }
    return {
        "status": "FOUND",
        "identifier": identifier,
        "reference": footprint["reference"],
        "pad_number": pad["number"],
        "position": pad["position"],
    }


def inspect_pad_distance(file, first_identifier, second_identifier, limit):
    _metadata, _layers, declared_nets, footprints, _tracks, _vias = scan_board(file)
    data = base_data(file)
    first_pad = resolve_pad_identifier(first_identifier, footprints, declared_nets, limit)
    second_pad = resolve_pad_identifier(second_identifier, footprints, declared_nets, limit)
    unresolved = [item for item in (first_pad, second_pad) if item["status"] != "FOUND"]
    if unresolved:
        status = "AMBIGUOUS" if any(item["status"] == "AMBIGUOUS" for item in unresolved) else unresolved[0]["status"]
        return {
            **data,
            "status": status,
            "first_identifier": first_identifier,
            "second_identifier": second_identifier,
            "first": first_pad,
            "second": second_pad,
            "measurement_point": "saved pad centres in board coordinates after saved footprint rotation and B.Cu mirror transforms",
            "limitations": ["No distance is calculated until both requested pad identifiers resolve to exactly one saved pad centre."],
        }
    return {
        **data,
        "status": "FOUND",
        "first": first_pad,
        "second": second_pad,
        "distance_mm": point_distance(first_pad["position"], second_pad["position"]),
        "distance_status": "STRUCTURAL_EVIDENCE",
        "measurement_point": "Euclidean distance between saved pad centres in board coordinates after saved footprint rotation and B.Cu mirror transforms, in millimeters.",
        "limitations": [
            "Pad-centre distance does not prove copper clearance, physical clearance, connectivity, routing quality, or electrical correctness.",
            "Saved PCB may differ from unsaved editor state.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["summary", "footprint", "pads", "net", "tracks", "vias", "nearby", "pad-distance"])
    parser.add_argument("target", nargs="?")
    parser.add_argument("target2", nargs="?")
    parser.add_argument("--board", required=True, help="Path to saved .kicad_pcb")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)
    try:
        if args.limit < 1 or args.limit > 1000:
            raise QueryError("--limit must be from 1 to 1000")
        if args.command in {"footprint", "pads", "net"} and not args.target:
            raise QueryError(f"{args.command} requires a target")
        if args.command in {"nearby", "pad-distance"} and not args.target:
            raise QueryError(f"{args.command} requires a target")
        if args.command in {"tracks", "vias"} and args.target is None:
            raise QueryError(f"{args.command} requires a target")
        if args.command == "pad-distance" and not args.target2:
            raise QueryError("pad-distance requires two pad identifiers")
        if args.command != "pad-distance" and args.target2 is not None:
            raise QueryError(f"{args.command} takes no second target")
        if args.command == "summary" and args.target:
            raise QueryError("summary takes no target")
        path = Path(args.board).expanduser().resolve()
        if path.suffix.lower() != ".kicad_pcb" or not path.is_file():
            raise QueryError("board must be an existing .kicad_pcb file")
        if args.command == "summary":
            result = summarize(path, None, args.limit)
        elif args.command == "footprint":
            result = summarize(path, args.target, args.limit)
        elif args.command == "pads":
            result = inspect_pads(path, args.target, args.limit)
        elif args.command == "net":
            result = inspect_net(path, args.target, args.limit)
        elif args.command == "tracks":
            result = inspect_tracks(path, args.target, args.limit)
        elif args.command == "vias":
            result = inspect_vias(path, args.target, args.limit)
        elif args.command == "nearby":
            result = inspect_nearby(path, args.target, args.limit)
        else:
            result = inspect_pad_distance(path, args.target, args.target2, args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (QueryError, OSError, UnicodeError, RecursionError, IndexError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "NOT_VERIFIED", "verification": "NOT_VERIFIED", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
