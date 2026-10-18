"""Standalone PCB v0.1 through v0.4 synthetic regression tests."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "query_pcb.py"
BOARD = '''(kicad_pcb (version 20241229) (generator "pcbnew")
 (layers (0 "F.Cu" signal) (31 "B.Cu" signal))
 (footprint "Resistor_SMD:R_0603" (layer "F.Cu") (at 10.5 20.25 90)
 (uuid "some-uuid") (property "Reference" "R1") (property "Value" "10k")
 (fp_text user "text (and) \\"quoted\\"")
 (pad "1" smd roundrect (at -1 0) (size 1 1) (layers "F.Cu")))
 (footprint "Capacitor_SMD:C_0402" (layer "B.Cu") (at 5 7)
 (property "Reference" "C1") (property "Value" "100n")))'''

V02_BOARD = '''(kicad_pcb (version 20260206) (generator "pcbnew")
 (layers (0 "F.Cu" signal) (31 "B.Cu" signal))
 (nets (net 0 "") (net 1 "GND") (net 2 "+3V3"))
 (footprint "Resistor_SMD:R_0603" (layer "F.Cu") (at 10 20 90)
  (property "Reference" "R1") (property "Value" "10k")
  (pad "1" smd roundrect (at 1 2) (size 1.2 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (net 1 "GND"))
  (pad "2" thru_hole circle (at -1 0) (size 2 2) (drill 1) (layers "*.Cu" "*.Mask") (net 0 ""))
  (pad "3" smd custom (at 0 0) (size 1 1) (layers "F.Cu") (net 2 "+3V3")
   (options (clearance outline) (anchor rect))
   (primitives (gr_poly (pts (xy -1 -1) (xy 1 -1) (xy 1 1) (xy -1 1)) (width 0) (fill yes)))))
 (footprint "Capacitor_SMD:C_0402" (layer "B.Cu") (at 50 60 90)
  (property "Reference" "C1") (property "Value" "100n")
  (pad "1" smd rect (at 2 3) (size 0.8 0.8) (layers "B.Cu" "B.Paste" "B.Mask") (net 1 "GND"))))'''

NAME_ONLY_NET_BOARD = '''(kicad_pcb (version 20260206) (generator "pcbnew")
 (layers (0 "F.Cu" signal))
 (footprint "Test:One" (layer "F.Cu") (at 1 2)
  (property "Reference" "J1") (property "Value" "test")
  (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu") (net "NAME_ONLY"))))'''

V03_BOARD = '''(kicad_pcb (version 20260206) (generator "pcbnew")
 (layers (0 "F.Cu" signal) (2 "In1.Cu" power) (31 "B.Cu" signal))
 (nets (net 0 "") (net 1 "GND") (net 2 "ISO"))
 (segment (start 0 0) (end 3 4) (width 0.25) (layer "F.Cu") (net 1))
 (arc (start 0 0) (mid 1 1) (end 2 0) (width 0.2) (layer "B.Cu") (net 1))
 (segment (start 5 5) (end 5 5) (width 0.15) (layer "F.Cu") (net 1))
 (segment (start 9 9) (width 0.15) (layer "F.Cu") (net 1))
 (segment (start 10 0) (end 10 1) (width 0.3) (layer "F.Cu") (net 2))
 (segment (start 11 0) (end 11 1) (width 0.3) (layer "F.Cu") (net "FLOATING"))
 (segment (start 12 0) (end 12 1) (width 0.3) (layer "F.Cu") (net 0 ""))
 (via (at 1 2) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net 1))
 (via (at 3 4) (size 0.6) (drill 0.3) (layers "F.Cu" "In1.Cu") (type blind) (net 2))
 (via (at 5 6) (size 0.7) (drill 0.35) (layers "In1.Cu" "B.Cu") (type buried) (net 2))
 (via (at 7 8) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net 0 "")))'''

V04_BOARD = '''(kicad_pcb (version 20260206) (generator "pcbnew")
 (layers (0 "F.Cu" signal) (31 "B.Cu" signal))
 (footprint "Test:One" (layer "F.Cu") (at 10 20 90)
  (property "Reference" "R.1") (property "Value" "rotated")
  (pad "A.1" smd rect (at 1 2) (size 1 1) (layers "F.Cu")))
 (footprint "Test:Two" (layer "B.Cu") (at 50 60 90)
  (property "Reference" "C@2") (property "Value" "back")
  (pad "2" smd rect (at 2 3) (size 1 1) (layers "B.Cu")))
 (footprint "Test:Three" (layer "F.Cu") (at 10 20)
  (property "Reference" "U#3") (property "Value" "same-origin")
  (pad "1" smd rect (at 2 -1) (size 1 1) (layers "F.Cu")))
 (footprint "Test:Four" (layer "F.Cu") (at 15 20)
  (property "Reference" "DUP") (property "Value" "duplicate-pad")
  (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu"))
  (pad "1" smd rect (at 1 0) (size 1 1) (layers "F.Cu")))
 (footprint "Test:Five" (layer "F.Cu") (at 16 20)
  (property "Reference" "J[1].A") (property "Value" "unusual-reference")
  (pad "P.1" smd rect (at 0 0) (size 1 1) (layers "F.Cu"))))'''

V04_INVALID_SPATIAL_BOARD = '''(kicad_pcb (version 20260206) (generator "pcbnew")
 (layers (0 "F.Cu" signal))
 (footprint "Test:Bad" (layer "F.Cu")
  (property "Reference" "BAD") (property "Value" "no-origin")
  (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu")))
 (footprint "Test:Good" (layer "F.Cu") (at 1 2)
  (property "Reference" "GOOD") (property "Value" "good")
  (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu"))))'''

V04_INVALID_PAD_BOARD = '''(kicad_pcb (version 20260206) (generator "pcbnew")
 (layers (0 "F.Cu" signal))
 (footprint "Test:BadPad" (layer "F.Cu") (at 1 2)
  (property "Reference" "BADPAD") (property "Value" "bad-pad")
  (pad "1" smd rect (at not-a-number 0) (size 1 1) (layers "F.Cu")))
 (footprint "Test:Good" (layer "F.Cu") (at 3 4)
  (property "Reference" "GOOD") (property "Value" "good")
  (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu"))))'''

DUPLICATE_REFERENCE_BOARD = '''(kicad_pcb (version 20260206) (generator "pcbnew")
 (layers (0 "F.Cu" signal))
 (footprint "Test:One" (layer "F.Cu") (at 1 1)
  (property "Reference" "U1") (property "Value" "first")
  (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu")))
 (footprint "Test:Two" (layer "F.Cu") (at 2 2)
  (property "Reference" "U1") (property "Value" "second")
  (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu")))
 (footprint "Test:Three" (layer "F.Cu") (at 3 3)
  (property "Reference" "R1") (property "Value" "other")
  (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu"))))'''

CONFLICTING_NET_BOARD = '''(kicad_pcb (version 20260206) (generator "pcbnew")
 (layers (0 "F.Cu" signal))
 (nets (net 1 "NET_A") (net 1 "NET_B")))'''

EMPTY_FORM_BOARD = '''(kicad_pcb (version 20260206) ())'''


class PCBTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.addCleanup(self.tmp.cleanup)
        self.board = Path(self.tmp.name) / "fixture.kicad_pcb"
        self.board.write_text(BOARD, encoding="utf-8")
        self.before = self.board.read_bytes()

    def run_cli_raw(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--board", str(self.board)],
            capture_output=True,
            text=True,
        )

    def run_cli(self, *args):
        proc = self.run_cli_raw(*args)
        return proc.returncode, json.loads(proc.stdout)

    def write_v02_board(self):
        self.board.write_text(V02_BOARD, encoding="utf-8")

    def write_name_only_net_board(self):
        self.board.write_text(NAME_ONLY_NET_BOARD, encoding="utf-8")

    def write_v03_board(self):
        self.board.write_text(V03_BOARD, encoding="utf-8")

    def write_v04_board(self):
        self.board.write_text(V04_BOARD, encoding="utf-8")

    def write_v04_invalid_spatial_board(self):
        self.board.write_text(V04_INVALID_SPATIAL_BOARD, encoding="utf-8")

    def write_v04_invalid_pad_board(self):
        self.board.write_text(V04_INVALID_PAD_BOARD, encoding="utf-8")

    def write_duplicate_reference_board(self):
        self.board.write_text(DUPLICATE_REFERENCE_BOARD, encoding="utf-8")

    # v0.1 regression coverage: retain existing commands and their fields.
    def test_summary(self):
        rc, data = self.run_cli("summary")
        self.assertEqual(rc, 0)
        self.assertEqual(data["footprint_count"], 2)
        self.assertEqual(data["layer_count"], 2)
        self.assertEqual(data["footprints_by_layer"], {"B.Cu": 1, "F.Cu": 1})

    def test_footprint(self):
        rc, data = self.run_cli("footprint", "R1")
        self.assertEqual(rc, 0)
        self.assertEqual(data["footprints"][0]["position"]["rotation_deg"], 90)
        self.assertEqual(data["footprints"][0]["library_id"], "Resistor_SMD:R_0603")

    def test_missing(self):
        rc, data = self.run_cli("footprint", "U999")
        self.assertEqual(rc, 0)
        self.assertEqual(data["status"], "NOT_FOUND")

    def test_limit(self):
        rc, data = self.run_cli("summary", "--limit", "1")
        self.assertEqual(rc, 0)
        self.assertTrue(data["footprints_truncated"])

    def test_bad_limit(self):
        rc, data = self.run_cli("summary", "--limit", "0")
        self.assertEqual(rc, 2)
        self.assertEqual(data["verification"], "NOT_VERIFIED")

    def test_malformed(self):
        self.board.write_text("(kicad_pcb (footprint", encoding="utf-8")
        rc, data = self.run_cli("summary")
        self.assertEqual(rc, 2)
        self.assertEqual(data["status"], "NOT_VERIFIED")

    def test_read_only(self):
        self.run_cli("summary")
        self.assertEqual(self.board.read_bytes(), self.before)

    # v0.2 coverage: pads, nets, transforms, limits, and unresolved geometry.
    def test_pads_reports_smd_through_hole_and_unconnected(self):
        self.write_v02_board()
        rc, data = self.run_cli("pads", "R1")
        self.assertEqual(rc, 0)
        self.assertEqual(data["status"], "FOUND")
        self.assertEqual(data["pad_count"], 3)
        pads = {pad["number"]: pad for pad in data["pads"]}
        self.assertEqual(pads["1"]["type"], "smd")
        self.assertEqual(pads["1"]["shape"], "roundrect")
        self.assertEqual(pads["1"]["net_name"], "GND")
        self.assertEqual(pads["1"]["net_status"], "ASSIGNED")
        self.assertEqual(pads["1"]["layers"], ["F.Cu", "F.Paste", "F.Mask"])
        self.assertEqual(pads["1"]["size_mm"], {"x_mm": 1.2, "y_mm": 0.8})
        self.assertEqual(pads["1"]["position"], {"x_mm": 12.0, "y_mm": 19.0})
        self.assertEqual(pads["2"]["type"], "thru_hole")
        self.assertEqual(pads["2"]["net_status"], "UNCONNECTED")
        self.assertIsNone(pads["2"]["net_name"])
        self.assertEqual(pads["3"]["geometry_status"], "NOT_VERIFIED")

    def test_pads_applies_back_layer_mirror_and_rotation(self):
        self.write_v02_board()
        rc, data = self.run_cli("pads", "C1")
        self.assertEqual(rc, 0)
        pad = data["pads"][0]
        self.assertEqual(pad["layers"], ["B.Cu", "B.Paste", "B.Mask"])
        self.assertEqual(pad["position"], {"x_mm": 53.0, "y_mm": 62.0})

    def test_net_reports_declared_assignments_without_connectivity_claim(self):
        self.write_v02_board()
        rc, data = self.run_cli("net", "GND")
        self.assertEqual(rc, 0)
        self.assertEqual(data["status"], "FOUND")
        self.assertEqual(data["net_status"], "DECLARED")
        self.assertEqual(data["net_code"], "1")
        self.assertEqual(data["footprint_count"], 2)
        self.assertEqual(data["pad_count"], 2)
        self.assertEqual([row["reference"] for row in data["footprints"]], ["C1", "R1"])
        self.assertEqual([row["reference"] for row in data["pads"]], ["C1", "R1"])

    def test_missing_net_is_distinct_from_unconnected_pad(self):
        self.write_v02_board()
        rc, data = self.run_cli("net", "MISSING")
        self.assertEqual(rc, 0)
        self.assertEqual(data["status"], "NOT_FOUND")
        self.assertEqual(data["net_status"], "MISSING")
        self.assertEqual(data["pad_count"], 0)

    def test_name_only_net_assignment_is_reported_with_unverified_declaration(self):
        self.write_name_only_net_board()
        rc, pad_data = self.run_cli("pads", "J1")
        self.assertEqual(rc, 0)
        self.assertEqual(pad_data["pads"][0]["net_name"], "NAME_ONLY")
        self.assertEqual(pad_data["pads"][0]["net_status"], "ASSIGNED_WITHOUT_DECLARATION")
        rc, net_data = self.run_cli("net", "NAME_ONLY")
        self.assertEqual(rc, 0)
        self.assertEqual(net_data["status"], "FOUND")
        self.assertEqual(net_data["net_status"], "ASSIGNED_WITHOUT_DECLARATION")
        self.assertEqual(net_data["net_declaration_status"], "NOT_VERIFIED")

    def test_v02_limits_and_json_order_are_deterministic(self):
        self.write_v02_board()
        first = self.run_cli_raw("pads", "R1", "--limit", "1")
        second = self.run_cli_raw("pads", "R1", "--limit", "1")
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        data = json.loads(first.stdout)
        self.assertTrue(data["pads_truncated"])
        self.assertEqual(data["pads"][0]["number"], "1")

    def test_v02_read_only(self):
        self.write_v02_board()
        before = self.board.read_bytes()
        self.run_cli("pads", "R1")
        self.run_cli("net", "GND")
        self.assertEqual(self.board.read_bytes(), before)

    # v0.3 coverage: targeted tracks and vias are assignment/geometry evidence only.
    def test_tracks_reports_straight_arc_zero_length_and_malformed_geometry(self):
        self.write_v03_board()
        rc, data = self.run_cli("tracks", "GND")
        self.assertEqual(rc, 0)
        self.assertEqual(data["status"], "FOUND")
        self.assertEqual(data["net_status"], "DECLARED")
        self.assertEqual(data["track_count"], 4)
        tracks = data["tracks"]
        self.assertEqual(tracks[0]["geometry_type"], "segment")
        self.assertEqual(tracks[0]["length_mm"], 5.0)
        self.assertEqual(tracks[1]["geometry_type"], "arc")
        self.assertEqual(tracks[1]["mid"], {"x_mm": 1.0, "y_mm": 1.0})
        self.assertAlmostEqual(tracks[1]["length_mm"], 3.141593, places=6)
        self.assertEqual(tracks[2]["length_mm"], 0.0)
        self.assertEqual(tracks[2]["length_status"], "STRUCTURAL_EVIDENCE")
        self.assertIsNone(tracks[3]["length_mm"])
        self.assertEqual(tracks[3]["geometry_status"], "NOT_VERIFIED")
        self.assertEqual(tracks[3]["length_status"], "NOT_VERIFIED")

    def test_tracks_isolate_net_and_distinguish_missing_unconnected_and_undeclared(self):
        self.write_v03_board()
        rc, isolated = self.run_cli("tracks", "ISO")
        self.assertEqual(rc, 0)
        self.assertEqual(isolated["track_count"], 1)
        self.assertEqual(isolated["tracks"][0]["net_name"], "ISO")
        self.assertEqual(isolated["tracks"][0]["start"], {"x_mm": 10.0, "y_mm": 0.0})
        rc, unconnected = self.run_cli("tracks", "")
        self.assertEqual(rc, 0)
        self.assertEqual(unconnected["net_status"], "UNCONNECTED")
        self.assertEqual(unconnected["track_count"], 1)
        rc, undeclared = self.run_cli("tracks", "FLOATING")
        self.assertEqual(rc, 0)
        self.assertEqual(undeclared["net_status"], "ASSIGNED_WITHOUT_DECLARATION")
        self.assertEqual(undeclared["net_declaration_status"], "NOT_VERIFIED")
        rc, missing = self.run_cli("tracks", "MISSING")
        self.assertEqual(rc, 0)
        self.assertEqual(missing["status"], "NOT_FOUND")
        self.assertEqual(missing["net_status"], "MISSING")

    def test_tracks_limit_and_order_are_deterministic(self):
        self.write_v03_board()
        first = self.run_cli_raw("tracks", "GND", "--limit", "1")
        second = self.run_cli_raw("tracks", "GND", "--limit", "1")
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        data = json.loads(first.stdout)
        self.assertEqual(data["track_count"], 4)
        self.assertTrue(data["tracks_truncated"])
        self.assertEqual(data["tracks"][0]["start"], {"x_mm": 0.0, "y_mm": 0.0})

    def test_vias_report_geometry_and_blind_buried_types(self):
        self.write_v03_board()
        rc, gnd = self.run_cli("vias", "GND")
        self.assertEqual(rc, 0)
        self.assertEqual(gnd["via_count"], 1)
        via = gnd["vias"][0]
        self.assertEqual(via["position"], {"x_mm": 1.0, "y_mm": 2.0})
        self.assertEqual(via["size_mm"], 0.8)
        self.assertEqual(via["drill_mm"], 0.4)
        self.assertEqual(via["layer_span"], ["F.Cu", "B.Cu"])
        self.assertIsNone(via["via_type"])
        self.assertEqual(via["via_type_status"], "NOT_VERIFIED")
        rc, iso = self.run_cli("vias", "ISO")
        self.assertEqual(rc, 0)
        self.assertEqual(iso["via_count"], 2)
        self.assertEqual([via["via_type"] for via in iso["vias"]], ["blind", "buried"])
        rc, unconnected = self.run_cli("vias", "")
        self.assertEqual(rc, 0)
        self.assertEqual(unconnected["net_status"], "UNCONNECTED")
        self.assertEqual(unconnected["via_count"], 1)

    def test_v03_read_only(self):
        self.write_v03_board()
        before = self.board.read_bytes()
        self.run_cli("tracks", "GND")
        self.run_cli("vias", "ISO", "--limit", "1")
        self.assertEqual(self.board.read_bytes(), before)

    # v0.4 coverage: spatial origin and pad-centre measurement only.
    def test_nearby_reports_origin_distances_with_deterministic_limit(self):
        self.write_v04_board()
        first = self.run_cli_raw("nearby", "R.1", "--limit", "1")
        second = self.run_cli_raw("nearby", "R.1", "--limit", "1")
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        data = json.loads(first.stdout)
        self.assertEqual(data["status"], "FOUND")
        self.assertEqual(data["origin"], {"x_mm": 10.0, "y_mm": 20.0})
        self.assertEqual(data["neighbor_count"], 4)
        self.assertTrue(data["neighbors_truncated"])
        self.assertEqual(data["neighbors"][0]["reference"], "U#3")
        self.assertEqual(data["neighbors"][0]["distance_mm"], 0.0)
        self.assertEqual(data["neighbors"][0]["distance_status"], "STRUCTURAL_EVIDENCE")

    def test_nearby_missing_and_invalid_origin_return_structured_statuses(self):
        self.write_v04_board()
        rc, missing = self.run_cli("nearby", "NO_SUCH_REFERENCE")
        self.assertEqual(rc, 0)
        self.assertEqual(missing["status"], "NOT_FOUND")
        self.write_v04_invalid_spatial_board()
        rc, invalid = self.run_cli("nearby", "BAD")
        self.assertEqual(rc, 0)
        self.assertEqual(invalid["status"], "NOT_VERIFIED")
        self.assertIn("origin", invalid["error"])

    def test_pad_distance_uses_rotated_back_layer_and_unusual_reference_transforms(self):
        self.write_v04_board()
        rc, data = self.run_cli("pad-distance", "R.1.A.1", "C@2.2")
        self.assertEqual(rc, 0)
        self.assertEqual(data["status"], "FOUND")
        self.assertEqual(data["first"]["position"], {"x_mm": 12.0, "y_mm": 19.0})
        self.assertEqual(data["second"]["position"], {"x_mm": 53.0, "y_mm": 62.0})
        self.assertAlmostEqual(data["distance_mm"], 59.413803, places=6)
        rc, unusual = self.run_cli("pad-distance", "J[1].A.P.1", "J[1].A.P.1")
        self.assertEqual(rc, 0)
        self.assertEqual(unusual["status"], "FOUND")
        self.assertEqual(unusual["distance_mm"], 0.0)

    def test_pad_distance_returns_ambiguous_for_duplicate_pad_numbers(self):
        self.write_v04_board()
        rc, data = self.run_cli("pad-distance", "DUP.1", "R.1.A.1", "--limit", "1")
        self.assertEqual(rc, 0)
        self.assertEqual(data["status"], "AMBIGUOUS")
        self.assertEqual(data["first"]["total_matches"], 2)
        self.assertTrue(data["first"]["matches_truncated"])
        self.assertEqual(data["first"]["matches"][0]["reference"], "DUP")

    def test_pad_distance_missing_and_invalid_pad_geometry_are_structured(self):
        self.write_v04_board()
        rc, missing = self.run_cli("pad-distance", "NO_SUCH.1", "R.1.A.1")
        self.assertEqual(rc, 0)
        self.assertEqual(missing["status"], "NOT_FOUND")
        self.assertEqual(missing["first"]["identifier"], "NO_SUCH.1")
        self.write_v04_invalid_spatial_board()
        rc, invalid = self.run_cli("pad-distance", "BAD.1", "GOOD.1")
        self.assertEqual(rc, 0)
        self.assertEqual(invalid["status"], "NOT_VERIFIED")
        self.assertIn("centre", invalid["first"]["error"])

    def test_pad_distance_invalid_coordinate_returns_structured_not_verified(self):
        self.write_v04_invalid_pad_board()
        rc, invalid = self.run_cli("pad-distance", "BADPAD.1", "GOOD.1")
        self.assertEqual(rc, 0)
        self.assertEqual(invalid["status"], "NOT_VERIFIED")
        self.assertIn("invalid numeric", invalid["first"]["error"])

    def test_v04_read_only(self):
        self.write_v04_board()
        before = self.board.read_bytes()
        self.run_cli("nearby", "R.1")
        self.run_cli("pad-distance", "R.1.A.1", "C@2.2")
        self.assertEqual(self.board.read_bytes(), before)

    # v1.0 hardening coverage: malformed forms, ambiguity, declarations, and bounds.
    def test_empty_sexpression_returns_structured_not_verified(self):
        self.board.write_text(EMPTY_FORM_BOARD, encoding="utf-8")
        rc, data = self.run_cli("summary")
        self.assertEqual(rc, 2)
        self.assertEqual(data["status"], "NOT_VERIFIED")
        self.assertIn("empty S-expression", data["error"])

    def test_conflicting_net_declarations_return_structured_not_verified(self):
        self.board.write_text(CONFLICTING_NET_BOARD, encoding="utf-8")
        rc, data = self.run_cli("summary")
        self.assertEqual(rc, 2)
        self.assertEqual(data["status"], "NOT_VERIFIED")
        self.assertIn("conflicting net declarations", data["error"])

    def test_duplicate_references_and_pads_remain_ambiguous(self):
        self.write_duplicate_reference_board()
        rc, nearby = self.run_cli("nearby", "U1")
        self.assertEqual(rc, 0)
        self.assertEqual(nearby["status"], "AMBIGUOUS_REFERENCE")
        self.assertEqual(nearby["total_matches"], 2)
        rc, distance = self.run_cli("pad-distance", "U1.1", "R1.1")
        self.assertEqual(rc, 0)
        self.assertEqual(distance["status"], "AMBIGUOUS")
        self.assertEqual(distance["first"]["total_matches"], 2)

    def test_net_and_via_result_limits_are_explicit(self):
        self.write_v02_board()
        rc, net = self.run_cli("net", "GND", "--limit", "1")
        self.assertEqual(rc, 0)
        self.assertTrue(net["footprints_truncated"])
        self.assertTrue(net["pads_truncated"])
        self.write_v03_board()
        rc, vias = self.run_cli("vias", "ISO", "--limit", "1")
        self.assertEqual(rc, 0)
        self.assertEqual(vias["via_count"], 2)
        self.assertTrue(vias["vias_truncated"])

    def test_malformed_via_geometry_is_not_verified_not_invented(self):
        self.board.write_text('''(kicad_pcb (version 20260206) (generator "pcbnew")
 (layers (0 "F.Cu" signal) (31 "B.Cu" signal))
 (nets (net 1 "GND"))
 (via (at 1 2) (size 0.8) (layers "F.Cu" "B.Cu") (net 1)))''', encoding="utf-8")
        rc, data = self.run_cli("vias", "GND")
        self.assertEqual(rc, 0)
        self.assertEqual(data["status"], "FOUND")
        self.assertIsNone(data["vias"][0]["drill_mm"])
        self.assertEqual(data["vias"][0]["geometry_status"], "NOT_VERIFIED")


if __name__ == "__main__":
    unittest.main()
