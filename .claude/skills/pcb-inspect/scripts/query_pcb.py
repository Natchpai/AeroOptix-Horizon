#!/usr/bin/env python3
"""Targeted, read-only KiCad PCB inspection (v1.1.1). Python 3.10+ stdlib."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path


VERSION = "1.1.1"  # keep the docstring above and SKILL.md in step


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
        # With a net table, code 0 is "no net". Without one (KiCad 10) the
        # token is a name, and a net can be named "0".
        if code == "0" and declared_nets:
            return {"net_code": code, "net_name": None, "net_status": "UNCONNECTED"}
        if code == "":
            return {"net_code": None, "net_name": None, "net_status": "UNCONNECTED"}
        # KiCad 10 boards have no net table and store (net "name") on each
        # item. That is the normal format, not a missing declaration.
        status = "ASSIGNED_WITHOUT_DECLARATION" if declared_nets else "ASSIGNED"
        return {"net_code": None, "net_name": code, "net_status": status}
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


VIA_TYPES = ("blind", "buried", "micro")


def via_data(expr, declared_nets, source_index):
    # KiCad saves the type as a bare word, (via blind ...), and saves no word
    # for a through via.
    via_type = next((part for part in expr[1:] if isinstance(part, str) and part in VIA_TYPES), "through")
    result = {
        "position": point_value(expr, "at"),
        "size_mm": scalar_value(expr, "size"),
        "drill_mm": scalar_value(expr, "drill"),
        "layer_span": layer_values(expr),
        "via_type": via_type,
        "via_type_status": "STRUCTURAL_EVIDENCE",
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

    KiCad PCB coordinates use a downward-positive Y axis. The saved file
    already stores flipped local coordinates for a footprint on B.Cu, so the
    same rotation applies on both sides and no extra mirror is added.
    This reports only the pad centre; it does not construct pad outlines.
    """
    if footprint_at is None or pad_at is None:
        return None
    local_x = pad_at["x_mm"]
    local_y = pad_at["y_mm"]
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
    # re.split with one group alternates text and digit runs, so the index
    # tells them apart. str.isdigit() is also true for "²", which int() rejects.
    return [int(part) if index % 2 else part.casefold() for index, part in enumerate(re.split(r"(\d+)", value))]


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


def bounding_box(points):
    if not points:
        return None
    xs = [point["x_mm"] for point in points]
    ys = [point["y_mm"] for point in points]
    return {
        "min": {"x_mm": clean_number(min(xs)), "y_mm": clean_number(min(ys))},
        "max": {"x_mm": clean_number(max(xs)), "y_mm": clean_number(max(ys))},
        "width_mm": clean_number(max(xs) - min(xs)),
        "height_mm": clean_number(max(ys) - min(ys)),
    }


def xy_points(expr):
    """Return the (xy x y) points of a (pts ...) child, and whether every entry was a plain point."""
    node = first(expr, "pts")
    if not node:
        return [], False
    points = []
    plain = True
    for item in node[1:]:
        if isinstance(item, list) and item and item[0] == "xy" and len(item) >= 3:
            x_mm = optional_number(item[1])
            y_mm = optional_number(item[2])
            if x_mm is None or y_mm is None:
                plain = False
            else:
                points.append({"x_mm": x_mm, "y_mm": y_mm})
        else:
            plain = False
    return points, plain


def track_totals(records):
    """Totals over every matching track primitive, not only the listed ones."""
    by_layer = {}
    widths = {}
    total = 0.0
    unresolved = 0
    for record in records:
        if record["length_mm"] is None:
            unresolved += 1
        else:
            total += record["length_mm"]
            layer = record["layer"] or "UNKNOWN"
            by_layer[layer] = by_layer.get(layer, 0.0) + record["length_mm"]
        widths[record["width_mm"]] = widths.get(record["width_mm"], 0) + 1
    return {
        "segment_count": sum(1 for record in records if record["geometry_type"] == "segment"),
        "arc_count": sum(1 for record in records if record["geometry_type"] == "arc"),
        "total_length_mm": clean_number(total),
        "length_by_layer_mm": {layer: clean_number(length) for layer, length in sorted(by_layer.items())},
        "length_not_verified_count": unresolved,
        "widths": [
            {"width_mm": width, "count": count}
            for width, count in sorted(widths.items(), key=lambda item: (item[0] is None, item[0] or 0))
        ],
    }


def via_totals(records):
    """Count matching vias per size, drill, layer span and type."""
    groups = {}
    for record in records:
        key = (record["size_mm"], record["drill_mm"], tuple(record["layer_span"] or ()), record["via_type"])
        groups[key] = groups.get(key, 0) + 1
    ordered = sorted(groups.items(), key=lambda item: (
        item[0][0] is None, item[0][0] or 0, item[0][1] is None, item[0][1] or 0, item[0][2], item[0][3] or "",
    ))
    return {
        "groups": [
            {"size_mm": size, "drill_mm": drill, "layer_span": list(span) or None, "via_type": via_type, "count": count}
            for (size, drill, span, via_type), count in ordered
        ],
    }


def zone_data(expr, declared_nets, source_index):
    layers = layer_values(expr)
    if layers is None:
        layer = value(expr, "layer")
        layers = [str(layer)] if layer is not None else None
    outline_points = []
    outline_plain = True
    outlines = children(expr, "polygon")
    for outline in outlines:
        points, plain = xy_points(outline)
        outline_points.extend(points)
        outline_plain = outline_plain and plain
    fills = children(expr, "filled_polygon")
    connect = first(expr, "connect_pads")
    fill = first(expr, "fill")
    priority = optional_number(value(expr, "priority"))
    result = {
        "layers": layers,
        "name": value(expr, "name"),
        "priority": int(priority) if priority is not None else None,
        "rule_area": first(expr, "keepout") is not None,
        "teardrop": any(isinstance(item, list) and item and item[0] == "teardrop" for attr in children(expr, "attr") for item in attr[1:]),
        "outline_count": len(outlines),
        "outline_point_count": len(outline_points),
        "outline_bbox": bounding_box(outline_points),
        "outline_status": "STRUCTURAL_EVIDENCE" if outline_points and outline_plain else "NOT_VERIFIED",
        "connect_pads": {
            "mode": str(connect[1]) if connect and len(connect) > 1 and not isinstance(connect[1], list) else None,
            "clearance_mm": scalar_value(connect, "clearance") if connect else None,
        },
        "min_thickness_mm": scalar_value(expr, "min_thickness"),
        "fill_setting": str(fill[1]) if fill and len(fill) > 1 and not isinstance(fill[1], list) else None,
        "thermal_gap_mm": scalar_value(fill, "thermal_gap") if fill else None,
        "thermal_bridge_width_mm": scalar_value(fill, "thermal_bridge_width") if fill else None,
        "saved_fill_present": bool(fills),
        "saved_fill_polygon_count": len(fills),
        "saved_fill_layers": sorted({str(value(item, "layer")) for item in fills if value(item, "layer") is not None}),
        "fill_status": "NOT_VERIFIED",
        "verification": "STRUCTURAL_EVIDENCE",
        "_source_index": source_index,
    }
    result.update(net_value(expr, declared_nets))
    return result


def zone_records(extras, declared_nets):
    return [zone_data(parse(fragment), declared_nets, index) for index, fragment in enumerate(extras["zones"])]


def edge_cuts_data(extras):
    """Bounding box of top-level Edge.Cuts graphics.

    Lines, rectangles, circles and plain polygons are exact. For arcs and
    curves only the saved start, mid, end or control points are used, so the
    box is reported as NOT_VERIFIED when any of them is present.
    """
    points = []
    counts = {}
    exact = True
    for fragment in extras["edge_cuts"]:
        expr = parse(fragment)
        if value(expr, "layer") != "Edge.Cuts":
            continue
        kind = str(expr[0])
        counts[kind] = counts.get(kind, 0) + 1
        if kind in {"gr_line", "gr_rect"}:
            found = [point_value(expr, "start"), point_value(expr, "end")]
        elif kind == "gr_arc":
            found = [point_value(expr, "start"), point_value(expr, "mid"), point_value(expr, "end")]
            exact = False
        elif kind == "gr_circle":
            center, edge = point_value(expr, "center"), point_value(expr, "end")
            if center and edge:
                radius = math.hypot(edge["x_mm"] - center["x_mm"], edge["y_mm"] - center["y_mm"])
                found = [
                    {"x_mm": center["x_mm"] - radius, "y_mm": center["y_mm"] - radius},
                    {"x_mm": center["x_mm"] + radius, "y_mm": center["y_mm"] + radius},
                ]
            else:
                found = [None]
        elif kind in {"gr_poly", "gr_curve"}:
            found, plain = xy_points(expr)
            exact = exact and plain and kind == "gr_poly"
            if not found:
                found = [None]
        else:
            found = [None]
        if any(point is None for point in found):
            exact = False
        points.extend(point for point in found if point is not None)
    return {
        "edge_cuts_bbox": bounding_box(points),
        "edge_cuts_bbox_status": "STRUCTURAL_EVIDENCE" if points and exact else "NOT_VERIFIED",
        "edge_cuts_primitives": dict(sorted(counts.items())),
    }


def net_usage(declared_nets, footprints, raw_tracks, raw_vias, extras):
    """Count pads, tracks, vias and zones per assigned net name."""
    usage = {}
    def add(record, key):
        name = record["net_name"]
        if name is None or record["net_status"] not in {"ASSIGNED", "ASSIGNED_WITHOUT_DECLARATION"}:
            return
        row = usage.setdefault(name, {"name": name, "pad_count": 0, "track_count": 0, "via_count": 0, "zone_count": 0})
        row[key] += 1
    for _footprint, expr in footprints:
        for pad in children(expr, "pad"):
            add(net_value(pad, declared_nets), "pad_count")
    for expr, _index in raw_tracks:
        add(net_value(expr, declared_nets), "track_count")
    for expr, _index in raw_vias:
        add(net_value(expr, declared_nets), "via_count")
    for fragment in extras["zones"]:
        add(net_value(parse(fragment), declared_nets), "zone_count")
    return usage


def scan_board(file):
    source = file.read_text(encoding="utf-8-sig")
    if not source.lstrip().startswith("(kicad_pcb"):
        raise QueryError(f"not a KiCad PCB file: {file}")
    metadata = {}
    layers = []
    declared_nets = {}
    footprints = []
    tracks = []
    vias = []
    # Zones and board-outline graphics are kept as raw text and parsed only
    # by the commands that need them.
    extras = {"zones": [], "edge_cuts": []}
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
        elif tag == "zone":
            extras["zones"].append(fragment)
        elif tag.startswith("gr_") and "Edge.Cuts" in fragment:
            extras["edge_cuts"].append(fragment)
    return metadata, layers, declared_nets, footprints, tracks, vias, extras


def base_data(file):
    return {"file": str(file), "verification": "STRUCTURAL_EVIDENCE", "scope": "saved_board_only"}


def summarize(file, target, limit):
    metadata, layers, declared_nets, footprints, raw_tracks, raw_vias, extras = scan_board(file)
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
        "net_count": len(net_usage(declared_nets, footprints, raw_tracks, raw_vias, extras)),
        "has_net_table": bool(declared_nets),
        "track_count": len(raw_tracks),
        "via_count": len(raw_vias),
        "zone_count": len(extras["zones"]),
        **edge_cuts_data(extras),
        "limitations": [
            "No copper connectivity, clearance, ERC/DRC, pad-to-net, or zone-fill verification.",
            "net_count is the number of distinct net names assigned to saved pads, tracks, vias and zones.",
            "edge_cuts_bbox uses top-level Edge.Cuts graphics only; outline graphics inside footprints are not included.",
        ],
    }


def inspect_pads(file, reference, limit):
    _metadata, _layers, declared_nets, footprints, _tracks, _vias, _extras = scan_board(file)
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
            "Pad centres include the saved footprint translation and rotation. Back-side local coordinates are used as saved.",
            "Custom or unsupported pad outlines are NOT_VERIFIED; reported size is only the saved nominal pad size.",
            "Saved PCB may differ from unsaved editor state.",
        ] + (["One or more pad geometries are NOT_VERIFIED."] if unresolved_geometry else []),
    }


def inspect_net(file, net_name, limit):
    _metadata, _layers, declared_nets, footprints, _tracks, _vias, _extras = scan_board(file)
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
    for footprint_index, (footprint, expr) in enumerate(footprints):
        for index, pad in enumerate(children(expr, "pad")):
            pad_record = pad_data(pad, footprint, declared_nets, index)
            if pad_record["net_name"] == net_name:
                assignments.append((footprint, pad_record, footprint_index))
    if not assignments:
        return {
            **data,
            "status": "NOT_FOUND",
            "net": net_name,
            "net_status": "MISSING",
            "net_declaration_status": "NOT_VERIFIED" if declared_nets else "NOT_APPLICABLE",
            "footprint_count": 0,
            "pad_count": 0,
            "footprints": [],
            "pads": [],
            "limitations": ["No saved pad assignment with this exact net name exists in the saved PCB."],
        }
    unresolved = [pad for _footprint, pad, _index in assignments if pad["net_status"] not in {"ASSIGNED", "ASSIGNED_WITHOUT_DECLARATION"}]
    if unresolved:
        return {
            **data,
            "status": "NOT_VERIFIED",
            "net": net_name,
            "net_status": "NOT_VERIFIED",
            "net_code": matching_codes[0] if matching_codes else None,
            "limitations": ["At least one pad has an inconsistent or unresolved saved net assignment."],
        }
    # Order by reference, then by position in the file: references can repeat
    # (REF**) or be missing, and each footprint is still its own row.
    assignments.sort(key=lambda item: (natural_key(item[0]["reference"] or ""), item[2], pad_sort_key(item[1])))
    footprint_rows = {}
    for footprint, _pad, footprint_index in assignments:
        footprint_rows.setdefault(
            footprint_index,
            {"reference": footprint["reference"], "value": footprint["value"], "layer": footprint["layer"]},
        )
    pads = [{"reference": footprint["reference"], **public_pad(pad)} for footprint, pad, _index in assignments]
    ordered_footprints = list(footprint_rows.values())
    return {
        **data,
        "status": "FOUND",
        "net": net_name,
        "net_status": "DECLARED" if matching_codes else "ASSIGNED_WITHOUT_DECLARATION" if declared_nets else "ASSIGNED",
        "net_code": matching_codes[0] if matching_codes else None,
        "net_declaration_status": "STRUCTURAL_EVIDENCE" if matching_codes else "NOT_VERIFIED" if declared_nets else "NOT_APPLICABLE",
        "footprint_count": len(ordered_footprints),
        "pad_count": len(pads),
        "footprints": ordered_footprints[:limit],
        "footprints_truncated": len(ordered_footprints) > limit,
        "pads": pads[:limit],
        "pads_truncated": len(pads) > limit,
        "limitations": [
            "Shared saved net names do not prove copper connectivity, routing, zone fill, or electrical intent.",
            "Unconnected pads are excluded because they have no assigned net.",
            "A board with no net table (KiCad 10) stores net names on each item; ASSIGNED_WITHOUT_DECLARATION is used only when a net table exists and lacks the name.",
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
    _metadata, _layers, declared_nets, _footprints, raw_tracks, raw_vias, _extras = scan_board(file)
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
        if declared_nets:
            reported_net_status = "ASSIGNED_WITHOUT_DECLARATION" if matching else "MISSING"
            declaration_status = "NOT_VERIFIED"
        else:
            reported_net_status = "ASSIGNED" if matching else "MISSING"
            declaration_status = "NOT_APPLICABLE"

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
        "totals": track_totals(matching) if kind == "tracks" else via_totals(matching),
        "limitations": [
            "totals cover every matching saved item, not only the listed ones.",
            "Saved net assignment and geometry do not prove physical copper connectivity, clearance, route completeness, or signal-path length.",
            "A NOT_VERIFIED length is returned as null rather than estimated from malformed or unsupported geometry.",
            "Saved PCB may differ from unsaved editor state.",
        ],
    }


def inspect_tracks(file, net_name, limit):
    return inspect_routing(file, net_name, limit, "tracks")


def inspect_vias(file, net_name, limit):
    return inspect_routing(file, net_name, limit, "vias")


def inspect_zones(file, net_name, limit):
    """Return saved zones assigned to one exact net name ("" for zones with no net)."""
    _metadata, _layers, declared_nets, _footprints, _tracks, _vias, extras = scan_board(file)
    data = base_data(file)
    records = zone_records(extras, declared_nets)
    if net_name == "":
        matching = [record for record in records if record["net_status"] == "UNCONNECTED"]
    else:
        matching = [record for record in records if record["net_name"] == net_name]
    if not matching:
        return {
            **data,
            "status": "NOT_FOUND",
            "net": net_name,
            "zone_count": 0,
            "zones": [],
            "zones_truncated": False,
            "board_zone_count": len(records),
            "limitations": ["No saved zone has this exact net assignment."],
        }
    by_layer = {}
    for record in matching:
        for layer in record["layers"] or ["UNKNOWN"]:
            by_layer[layer] = by_layer.get(layer, 0) + 1
    return {
        **data,
        "status": "FOUND",
        "net": net_name,
        "zone_count": len(matching),
        "zones": [public_routing(record) for record in matching[:limit]],
        "zones_truncated": len(matching) > limit,
        "board_zone_count": len(records),
        "totals": {
            "zones_by_layer": dict(sorted(by_layer.items())),
            "teardrop_count": sum(1 for record in matching if record["teardrop"]),
            "rule_area_count": sum(1 for record in matching if record["rule_area"]),
            "with_saved_fill_count": sum(1 for record in matching if record["saved_fill_present"]),
        },
        "limitations": [
            "A zone outline is not filled copper. fill_status is NOT_VERIFIED: saved fill polygons may be stale and are not checked.",
            "outline_bbox is the bounding box of the saved outline points, not the copper area.",
            "A connect_pads mode of null means the file saves no mode token.",
            "Saved zone net assignment does not prove copper connectivity or clearance.",
            "Saved PCB may differ from unsaved editor state.",
        ],
    }


def inspect_nets(file, match, limit):
    """List assigned net names with pad, track, via and zone counts."""
    _metadata, _layers, declared_nets, footprints, raw_tracks, raw_vias, extras = scan_board(file)
    data = base_data(file)
    usage = net_usage(declared_nets, footprints, raw_tracks, raw_vias, extras)
    rows = sorted(usage.values(), key=lambda row: natural_key(row["name"]))
    if match:
        needle = match.casefold()
        rows = [row for row in rows if needle in row["name"].casefold()]
    return {
        **data,
        "status": "FOUND" if rows else "NOT_FOUND",
        "match": match,
        "net_count": len(rows),
        "board_net_count": len(usage),
        "has_net_table": bool(declared_nets),
        "nets": rows[:limit],
        "nets_truncated": len(rows) > limit,
        "limitations": [
            "Net names are those assigned to saved pads, tracks, vias and zones; unconnected items are not listed.",
            "--match is a case-insensitive substring match on the full saved name, including any sheet path.",
            "Counts are saved assignments, not evidence of copper connectivity.",
            "Saved PCB may differ from unsaved editor state.",
        ],
    }


def inspect_nearby(file, reference, limit, layer=None, radius=None):
    """Find footprint origins near one uniquely identified saved footprint."""
    _metadata, _layers, _declared_nets, footprints, _tracks, _vias, _extras = scan_board(file)
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
    other_count = len(footprints) - 1
    for index, (footprint, _expr) in enumerate(footprints):
        if index == target_index:
            continue
        if layer is not None and footprint["layer"] != layer:
            continue
        neighbor_origin = footprint_origin(footprint)
        distance = point_distance(origin, neighbor_origin)
        if radius is not None and distance is not None and distance > radius:
            continue
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
        "filters_applied": {"layer": layer, "radius_mm": radius},
        "unfiltered_neighbor_count": other_count,
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
    _metadata, _layers, declared_nets, footprints, _tracks, _vias, _extras = scan_board(file)
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
            "measurement_point": "saved pad centres in board coordinates after the saved footprint translation and rotation",
            "limitations": ["No distance is calculated until both requested pad identifiers resolve to exactly one saved pad centre."],
        }
    return {
        **data,
        "status": "FOUND",
        "first": first_pad,
        "second": second_pad,
        "distance_mm": point_distance(first_pad["position"], second_pad["position"]),
        "distance_status": "STRUCTURAL_EVIDENCE",
        "measurement_point": "Euclidean distance between saved pad centres in board coordinates after the saved footprint translation and rotation, in millimeters.",
        "limitations": [
            "Pad-centre distance does not prove copper clearance, physical clearance, connectivity, routing quality, or electrical correctness.",
            "Saved PCB may differ from unsaved editor state.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["summary", "footprint", "pads", "net", "nets", "tracks", "vias", "zones", "nearby", "pad-distance"])
    parser.add_argument("target", nargs="?")
    parser.add_argument("target2", nargs="?")
    parser.add_argument("--board", required=True, help="Path to saved .kicad_pcb")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--match", help="nets only: case-insensitive substring of the net name")
    parser.add_argument("--layer", help="nearby only: keep footprints on this layer, for example F.Cu")
    parser.add_argument("--radius", type=float, help="nearby only: keep footprints within this origin distance in mm")
    args = parser.parse_args(argv)
    # Print UTF-8 JSON whatever the console code page is. A legacy code page
    # (common on Windows) cannot encode some paths and names.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass  # not a text console stream (for example a test buffer)
    try:
        if args.limit < 1 or args.limit > 1000:
            raise QueryError("--limit must be from 1 to 1000")
        if args.command in {"footprint", "pads", "net"} and not args.target:
            raise QueryError(f"{args.command} requires a target")
        if args.command in {"nearby", "pad-distance"} and not args.target:
            raise QueryError(f"{args.command} requires a target")
        if args.command in {"tracks", "vias", "zones"} and args.target is None:
            raise QueryError(f"{args.command} requires a target")
        if args.command == "pad-distance" and not args.target2:
            raise QueryError("pad-distance requires two pad identifiers")
        if args.command != "pad-distance" and args.target2 is not None:
            raise QueryError(f"{args.command} takes no second target")
        if args.command in {"summary", "nets"} and args.target:
            raise QueryError(f"{args.command} takes no target")
        if args.match is not None and args.command != "nets":
            raise QueryError("--match works with nets only")
        if (args.layer is not None or args.radius is not None) and args.command != "nearby":
            raise QueryError("--layer and --radius work with nearby only")
        if args.radius is not None and not (math.isfinite(args.radius) and args.radius > 0):
            raise QueryError("--radius must be a positive number of millimetres")
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
        elif args.command == "zones":
            result = inspect_zones(path, args.target, args.limit)
        elif args.command == "nets":
            result = inspect_nets(path, args.match, args.limit)
        elif args.command == "nearby":
            result = inspect_nearby(path, args.target, args.limit, args.layer, args.radius)
        else:
            result = inspect_pad_distance(path, args.target, args.target2, args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (QueryError, OSError, UnicodeError, RecursionError, IndexError, KeyError, TypeError, ValueError) as exc:
        # Errors are JSON on stderr, as in query_sch.py; stdout stays empty.
        print(json.dumps({"status": "NOT_VERIFIED", "verification": "NOT_VERIFIED", "error": str(exc)}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
