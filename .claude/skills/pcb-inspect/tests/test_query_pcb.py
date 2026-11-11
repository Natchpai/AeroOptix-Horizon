"""Standalone PCB synthetic regression tests (v0.1 through v1.1)."""
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

# Back-side footprints as saved by KiCad 10 (file version 20260206), from a
# real routed board: one at 0 degrees and one at 90 degrees. The expected pad
# centres in the tests are the ends of the saved B.Cu tracks on the same net
# (+5V), not values computed by query_pcb.py.
KICAD10_BACK_SIDE_BOARD = '''(kicad_pcb (version 20260206) (generator "pcbnew")
 (layers (0 "F.Cu" signal) (2 "B.Cu" signal))
 (footprint "0_net_tie:NetTie-2_SMD_Pad0.15mm" (layer "B.Cu") (at 156.2 87.45)
  (property "Reference" "NT304") (property "Value" "EN")
  (pad "1" smd circle (at -0.2 0) (size 0.15 0.15) (layers "B.Cu") (net "+5V"))
  (pad "2" smd circle (at 0.2 0) (size 0.15 0.15) (layers "B.Cu") (net "EN_3V3_S")))
 (footprint "0_SOT:SOT-23-5" (layer "B.Cu") (at 158.1125 86.2 90)
  (property "Reference" "U304") (property "Value" "SPX3819M5-L-3-3/TR")
  (pad "1" smd roundrect (at -1.25 0.95 90) (size 1.1 0.55) (layers "B.Cu" "B.Mask" "B.Paste") (net "+5V"))
  (pad "2" smd roundrect (at -1.25 0 90) (size 1.1 0.55) (layers "B.Cu" "B.Mask" "B.Paste") (net "GND")))
 (segment (start 156 87.45) (end 159.0625 87.45) (width 0.3) (layer "B.Cu") (net "+5V")))'''

NET_TABLE_MISSING_ENTRY_BOARD = '''(kicad_pcb (version 20241229) (generator "pcbnew")
 (layers (0 "F.Cu" signal))
 (nets (net 0 "") (net 1 "GND"))
 (footprint "Test:One" (layer "F.Cu") (at 1 2)
  (property "Reference" "J1") (property "Value" "test")
  (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu") (net 1 "GND"))
  (pad "2" smd rect (at 1 0) (size 1 1) (layers "F.Cu") (net "NOT_IN_TABLE"))
  (pad "3" smd rect (at 2 0) (size 1 1) (layers "F.Cu") (net "")))
 (segment (start 0 0) (end 1 0) (width 0.2) (layer "F.Cu") (net "NOT_IN_TABLE")))'''

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

# KiCad 10 style board (no net table) with zones and a board outline.
V11_BOARD = '''(kicad_pcb (version 20260206) (generator "pcbnew")
 (layers (0 "F.Cu" signal) (2 "B.Cu" signal))
 (footprint "Test:One" (layer "F.Cu") (at 10 10)
  (property "Reference" "U1") (property "Value" "ic")
  (pad "1" smd rect (at -1 0) (size 1 1) (layers "F.Cu") (net "GND"))
  (pad "2" smd rect (at 1 0) (size 1 1) (layers "F.Cu") (net "/Top/Power/+5VUSB"))
  (pad "3" smd rect (at 0 1) (size 1 1) (layers "F.Cu")))
 (footprint "Test:Two" (layer "F.Cu") (at 13 14)
  (property "Reference" "C1") (property "Value" "100n")
  (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu") (net "GND")))
 (footprint "Test:Two" (layer "B.Cu") (at 10 12)
  (property "Reference" "C2") (property "Value" "100n")
  (pad "1" smd rect (at 0 0) (size 1 1) (layers "B.Cu") (net "GND")))
 (footprint "Test:Two" (layer "F.Cu") (at 40 10)
  (property "Reference" "C3") (property "Value" "far")
  (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu") (net "GND")))
 (gr_line (start 0 0) (end 50 0) (stroke (width 0.1) (type default)) (layer "Edge.Cuts"))
 (gr_rect (start 0 0) (end 50 30) (stroke (width 0.1) (type default)) (fill no) (layer "Edge.Cuts"))
 (gr_line (start 0 0) (end 99 99) (stroke (width 0.1) (type default)) (layer "F.SilkS"))
 (segment (start 0 0) (end 3 4) (width 0.25) (layer "F.Cu") (net "GND"))
 (segment (start 3 4) (end 3 6) (width 0.25) (layer "F.Cu") (net "GND"))
 (segment (start 3 6) (end 6 10) (width 0.4) (layer "B.Cu") (net "GND"))
 (arc (start 0 0) (mid 1 1) (end 2 0) (width 0.2) (layer "B.Cu") (net "GND"))
 (segment (start 9 9) (width 0.4) (layer "F.Cu") (net "GND"))
 (segment (start 20 0) (end 21 0) (width 0.3) (layer "F.Cu") (net "/Top/Power/+5VUSB"))
 (via (at 3 6) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "GND"))
 (via (at 4 6) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "GND"))
 (via (at 5 6) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net "GND"))
 (zone (net "GND") (layer "F.Cu") (uuid "z1") (name "GND pour") (hatch edge 0.5) (priority 2)
  (connect_pads yes (clearance 0.2)) (min_thickness 0.25)
  (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))
  (polygon (pts (xy 1 2) (xy 11 2) (xy 11 8) (xy 1 8)))
  (filled_polygon (layer "F.Cu") (pts (xy 1 2) (xy 11 2) (xy 11 8))))
 (zone (net "GND") (layers "F.Cu" "B.Cu") (uuid "z2") (hatch edge 0.5)
  (connect_pads (clearance 0.5)) (min_thickness 0.25) (fill (thermal_gap 0.5) (thermal_bridge_width 0.5))
  (polygon (pts (xy 0 0) (xy 50 0) (xy 50 30) (xy 0 30))))
 (zone (net "GND") (layer "F.Cu") (hatch none 0.1) (priority 30000) (attr (teardrop (type padvia)))
  (connect_pads yes (clearance 0)) (min_thickness 0.0254) (fill yes)
  (polygon (pts (xy 1 1) (xy 2 1) (xy 2 2)))
  (filled_polygon (layer "F.Cu") (pts (xy 1 1) (xy 2 1) (xy 2 2))))
 (zone (layer "F.Cu") (uuid "z4") (hatch edge 0.5) (connect_pads (clearance 0)) (min_thickness 0.25)
  (keepout (tracks not_allowed) (vias not_allowed) (pads allowed) (copperpour not_allowed) (footprints allowed))
  (fill (thermal_gap 0.5) (thermal_bridge_width 0.5))
  (polygon (pts (xy 20 20) (xy 22 20) (xy 22 22)))))'''

V11_ARC_OUTLINE_BOARD = '''(kicad_pcb (version 20260206) (generator "pcbnew")
 (layers (0 "F.Cu" signal))
 (gr_line (start 0 0) (end 10 0) (stroke (width 0.1) (type default)) (layer "Edge.Cuts"))
 (gr_arc (start 10 0) (mid 12 2) (end 10 4) (stroke (width 0.1) (type default)) (layer "Edge.Cuts")))'''

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
        # Results are JSON on stdout; errors are JSON on stderr.
        proc = self.run_cli_raw(*args)
        return proc.returncode, json.loads(proc.stdout if proc.returncode == 0 else proc.stderr)

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

    def test_pads_back_layer_centres_match_kicad10_saved_track_ends(self):
        # The saved file already stores flipped local coordinates for a
        # back-side footprint, so no extra B.Cu mirror is applied.
        self.board.write_text(KICAD10_BACK_SIDE_BOARD, encoding="utf-8")
        rc, zero = self.run_cli("pads", "NT304")
        self.assertEqual(rc, 0)
        pads = {pad["number"]: pad for pad in zero["pads"]}
        self.assertEqual(pads["1"]["layers"], ["B.Cu"])
        self.assertEqual(pads["1"]["position"], {"x_mm": 156.0, "y_mm": 87.45})
        self.assertEqual(pads["2"]["position"], {"x_mm": 156.4, "y_mm": 87.45})
        rc, ninety = self.run_cli("pads", "U304")
        self.assertEqual(rc, 0)
        pads = {pad["number"]: pad for pad in ninety["pads"]}
        self.assertEqual(pads["1"]["position"], {"x_mm": 159.0625, "y_mm": 87.45})
        rc, tracks = self.run_cli("tracks", "+5V")
        self.assertEqual(rc, 0)
        self.assertEqual(tracks["tracks"][0]["start"], {"x_mm": 156.0, "y_mm": 87.45})
        self.assertEqual(tracks["tracks"][0]["end"], {"x_mm": 159.0625, "y_mm": 87.45})

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

    def test_name_only_net_is_assigned_on_a_board_without_a_net_table(self):
        # KiCad 10 boards have no net table and store (net "name") per item.
        self.write_name_only_net_board()
        rc, pad_data = self.run_cli("pads", "J1")
        self.assertEqual(rc, 0)
        self.assertEqual(pad_data["pads"][0]["net_name"], "NAME_ONLY")
        self.assertEqual(pad_data["pads"][0]["net_status"], "ASSIGNED")
        rc, net_data = self.run_cli("net", "NAME_ONLY")
        self.assertEqual(rc, 0)
        self.assertEqual(net_data["status"], "FOUND")
        self.assertEqual(net_data["net_status"], "ASSIGNED")
        self.assertEqual(net_data["net_declaration_status"], "NOT_APPLICABLE")
        rc, missing = self.run_cli("net", "MISSING")
        self.assertEqual(rc, 0)
        self.assertEqual(missing["status"], "NOT_FOUND")
        self.assertEqual(missing["net_status"], "MISSING")
        self.assertEqual(missing["net_declaration_status"], "NOT_APPLICABLE")
        self.board.write_text(KICAD10_BACK_SIDE_BOARD, encoding="utf-8")
        rc, tracks = self.run_cli("tracks", "+5V")
        self.assertEqual(rc, 0)
        self.assertEqual(tracks["net_status"], "ASSIGNED")
        self.assertEqual(tracks["net_declaration_status"], "NOT_APPLICABLE")
        self.assertEqual(tracks["tracks"][0]["net_status"], "ASSIGNED")

    def test_net_missing_from_an_existing_net_table_stays_without_declaration(self):
        self.board.write_text(NET_TABLE_MISSING_ENTRY_BOARD, encoding="utf-8")
        rc, pad_data = self.run_cli("pads", "J1")
        self.assertEqual(rc, 0)
        pads = {pad["number"]: pad for pad in pad_data["pads"]}
        self.assertEqual(pads["1"]["net_status"], "ASSIGNED")
        self.assertEqual(pads["2"]["net_status"], "ASSIGNED_WITHOUT_DECLARATION")
        self.assertEqual(pads["3"]["net_status"], "UNCONNECTED")
        self.assertIsNone(pads["3"]["net_name"])
        rc, net_data = self.run_cli("net", "NOT_IN_TABLE")
        self.assertEqual(rc, 0)
        self.assertEqual(net_data["net_status"], "ASSIGNED_WITHOUT_DECLARATION")
        self.assertEqual(net_data["net_declaration_status"], "NOT_VERIFIED")
        rc, tracks = self.run_cli("tracks", "NOT_IN_TABLE")
        self.assertEqual(rc, 0)
        self.assertEqual(tracks["net_status"], "ASSIGNED_WITHOUT_DECLARATION")
        self.assertEqual(tracks["net_declaration_status"], "NOT_VERIFIED")

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

    def test_pad_distance_uses_rotation_back_layer_and_unusual_references(self):
        self.board.write_text(KICAD10_BACK_SIDE_BOARD, encoding="utf-8")
        rc, back = self.run_cli("pad-distance", "NT304.1", "U304.1")
        self.assertEqual(rc, 0)
        self.assertEqual(back["status"], "FOUND")
        self.assertEqual(back["first"]["position"], {"x_mm": 156.0, "y_mm": 87.45})
        self.assertEqual(back["second"]["position"], {"x_mm": 159.0625, "y_mm": 87.45})
        self.assertEqual(back["distance_mm"], 3.0625)
        self.write_v04_board()
        rc, data = self.run_cli("pad-distance", "R.1.A.1", "J[1].A.P.1")
        self.assertEqual(rc, 0)
        self.assertEqual(data["status"], "FOUND")
        self.assertEqual(data["first"]["position"], {"x_mm": 12.0, "y_mm": 19.0})
        self.assertEqual(data["second"]["position"], {"x_mm": 16.0, "y_mm": 20.0})
        self.assertAlmostEqual(data["distance_mm"], 4.123106, places=6)
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
    # --- v1.1: totals, zones, nets, summary counts, nearby filters

    def write_v11_board(self):
        self.board.write_text(V11_BOARD, encoding="utf-8")

    def test_tracks_totals_cover_all_matches_beyond_the_limit(self):
        self.write_v11_board()
        rc, data = self.run_cli("tracks", "GND", "--limit", "1")
        self.assertEqual(rc, 0)
        self.assertEqual(data["track_count"], 5)
        self.assertEqual(len(data["tracks"]), 1)
        self.assertTrue(data["tracks_truncated"])
        totals = data["totals"]
        self.assertEqual(totals["segment_count"], 4)
        self.assertEqual(totals["arc_count"], 1)
        self.assertEqual(totals["length_not_verified_count"], 1)
        # 5 + 2 on F.Cu, 5 + a half circle of radius 1 on B.Cu.
        self.assertEqual(totals["length_by_layer_mm"]["F.Cu"], 7.0)
        self.assertAlmostEqual(totals["length_by_layer_mm"]["B.Cu"], 5 + 3.141593, places=5)
        self.assertAlmostEqual(totals["total_length_mm"], 12 + 3.141593, places=5)
        self.assertEqual(totals["widths"], [
            {"width_mm": 0.2, "count": 1},
            {"width_mm": 0.25, "count": 2},
            {"width_mm": 0.4, "count": 2},
        ])
        self.assertTrue(any("path length" in line or "signal-path" in line for line in data["limitations"]))

    def test_vias_totals_group_by_size_drill_span_and_type(self):
        self.write_v11_board()
        rc, data = self.run_cli("vias", "GND", "--limit", "1")
        self.assertEqual(rc, 0)
        self.assertEqual(data["via_count"], 3)
        self.assertEqual(len(data["vias"]), 1)
        self.assertEqual(data["totals"]["groups"], [
            {"size_mm": 0.6, "drill_mm": 0.3, "layer_span": ["F.Cu", "B.Cu"], "via_type": None, "count": 2},
            {"size_mm": 0.8, "drill_mm": 0.4, "layer_span": ["F.Cu", "B.Cu"], "via_type": None, "count": 1},
        ])

    def test_zones_report_settings_outline_and_unverified_fill(self):
        self.write_v11_board()
        rc, data = self.run_cli("zones", "GND")
        self.assertEqual(rc, 0)
        self.assertEqual(data["status"], "FOUND")
        self.assertEqual(data["zone_count"], 3)
        self.assertEqual(data["board_zone_count"], 4)
        pour, multi, teardrop = data["zones"]
        self.assertEqual(pour["name"], "GND pour")
        self.assertEqual(pour["layers"], ["F.Cu"])
        self.assertEqual(pour["priority"], 2)
        self.assertEqual(pour["net_name"], "GND")
        self.assertEqual(pour["outline_bbox"]["min"], {"x_mm": 1.0, "y_mm": 2.0})
        self.assertEqual(pour["outline_bbox"]["max"], {"x_mm": 11.0, "y_mm": 8.0})
        self.assertEqual(pour["outline_point_count"], 4)
        self.assertEqual(pour["connect_pads"], {"mode": "yes", "clearance_mm": 0.2})
        self.assertTrue(pour["saved_fill_present"])
        self.assertEqual(pour["fill_status"], "NOT_VERIFIED")
        self.assertEqual(multi["layers"], ["F.Cu", "B.Cu"])
        self.assertIsNone(multi["priority"])
        self.assertIsNone(multi["name"])
        self.assertEqual(multi["connect_pads"], {"mode": None, "clearance_mm": 0.5})
        self.assertFalse(multi["saved_fill_present"])
        self.assertEqual(multi["fill_status"], "NOT_VERIFIED")
        self.assertTrue(teardrop["teardrop"])
        self.assertEqual(data["totals"]["zones_by_layer"], {"B.Cu": 1, "F.Cu": 3})
        self.assertEqual(data["totals"]["teardrop_count"], 1)
        self.assertEqual(data["totals"]["with_saved_fill_count"], 2)

    def test_zones_limit_missing_net_and_rule_areas(self):
        self.write_v11_board()
        rc, limited = self.run_cli("zones", "GND", "--limit", "1")
        self.assertEqual(rc, 0)
        self.assertEqual(limited["zone_count"], 3)
        self.assertEqual(len(limited["zones"]), 1)
        self.assertTrue(limited["zones_truncated"])
        rc, missing = self.run_cli("zones", "MISSING")
        self.assertEqual(rc, 0)
        self.assertEqual(missing["status"], "NOT_FOUND")
        self.assertEqual(missing["zone_count"], 0)
        rc, no_net = self.run_cli("zones", "")
        self.assertEqual(rc, 0)
        self.assertEqual(no_net["zone_count"], 1)
        self.assertTrue(no_net["zones"][0]["rule_area"])
        self.assertEqual(no_net["zones"][0]["net_status"], "UNCONNECTED")
        proc = self.run_cli_raw("zones")
        self.assertEqual(proc.returncode, 2)

    def test_nets_lists_names_with_counts_and_substring_match(self):
        self.write_v11_board()
        rc, data = self.run_cli("nets")
        self.assertEqual(rc, 0)
        self.assertEqual(data["status"], "FOUND")
        self.assertEqual(data["net_count"], 2)
        self.assertFalse(data["has_net_table"])
        self.assertEqual(data["nets"], [
            {"name": "/Top/Power/+5VUSB", "pad_count": 1, "track_count": 1, "via_count": 0, "zone_count": 0},
            {"name": "GND", "pad_count": 4, "track_count": 5, "via_count": 3, "zone_count": 3},
        ])
        rc, matched = self.run_cli("nets", "--match", "5vusb")
        self.assertEqual(rc, 0)
        self.assertEqual(matched["net_count"], 1)
        self.assertEqual(matched["board_net_count"], 2)
        self.assertEqual(matched["nets"][0]["name"], "/Top/Power/+5VUSB")
        rc, none = self.run_cli("nets", "--match", "nothing")
        self.assertEqual(rc, 0)
        self.assertEqual(none["status"], "NOT_FOUND")
        self.assertEqual(none["nets"], [])
        rc, limited = self.run_cli("nets", "--limit", "1")
        self.assertTrue(limited["nets_truncated"])
        self.assertEqual(self.run_cli_raw("nets", "GND").returncode, 2)
        self.assertEqual(self.run_cli_raw("net", "GND", "--match", "G").returncode, 2)

    def test_summary_reports_board_totals_and_outline_box(self):
        self.write_v11_board()
        rc, data = self.run_cli("summary")
        self.assertEqual(rc, 0)
        self.assertEqual(data["net_count"], 2)
        self.assertEqual(data["track_count"], 6)
        self.assertEqual(data["via_count"], 3)
        self.assertEqual(data["zone_count"], 4)
        self.assertEqual(data["edge_cuts_bbox"]["min"], {"x_mm": 0.0, "y_mm": 0.0})
        self.assertEqual(data["edge_cuts_bbox"]["max"], {"x_mm": 50.0, "y_mm": 30.0})
        self.assertEqual(data["edge_cuts_bbox"]["width_mm"], 50.0)
        self.assertEqual(data["edge_cuts_bbox_status"], "STRUCTURAL_EVIDENCE")
        self.assertEqual(data["edge_cuts_primitives"], {"gr_line": 1, "gr_rect": 1})

    def test_summary_outline_box_is_not_verified_with_arcs_or_no_outline(self):
        self.board.write_text(V11_ARC_OUTLINE_BOARD, encoding="utf-8")
        rc, arcs = self.run_cli("summary")
        self.assertEqual(rc, 0)
        self.assertEqual(arcs["edge_cuts_bbox_status"], "NOT_VERIFIED")
        self.assertIsNotNone(arcs["edge_cuts_bbox"])
        self.board.write_text(BOARD, encoding="utf-8")
        rc, none = self.run_cli("summary")
        self.assertEqual(rc, 0)
        self.assertIsNone(none["edge_cuts_bbox"])
        self.assertEqual(none["edge_cuts_bbox_status"], "NOT_VERIFIED")
        self.assertEqual(none["zone_count"], 0)

    def test_nearby_layer_and_radius_filters_are_reported(self):
        self.write_v11_board()
        rc, plain = self.run_cli("nearby", "U1")
        self.assertEqual(rc, 0)
        self.assertEqual(plain["neighbor_count"], 3)
        self.assertEqual(plain["filters_applied"], {"layer": None, "radius_mm": None})
        rc, layer = self.run_cli("nearby", "U1", "--layer", "F.Cu")
        self.assertEqual(rc, 0)
        self.assertEqual([row["reference"] for row in layer["neighbors"]], ["C1", "C3"])
        self.assertEqual(layer["filters_applied"], {"layer": "F.Cu", "radius_mm": None})
        self.assertEqual(layer["unfiltered_neighbor_count"], 3)
        rc, radius = self.run_cli("nearby", "U1", "--radius", "5")
        self.assertEqual(rc, 0)
        self.assertEqual([row["reference"] for row in radius["neighbors"]], ["C2", "C1"])
        rc, both = self.run_cli("nearby", "U1", "--layer", "B.Cu", "--radius", "5")
        self.assertEqual(rc, 0)
        self.assertEqual([row["reference"] for row in both["neighbors"]], ["C2"])
        self.assertEqual(both["filters_applied"], {"layer": "B.Cu", "radius_mm": 5.0})
        self.assertEqual(self.run_cli_raw("nearby", "U1", "--radius", "0").returncode, 2)
        self.assertEqual(self.run_cli_raw("pads", "U1", "--layer", "F.Cu").returncode, 2)

    def test_v11_read_only(self):
        self.write_v11_board()
        before = self.board.read_bytes()
        for args in (("zones", "GND"), ("nets",), ("summary",), ("nearby", "U1", "--radius", "5")):
            self.run_cli(*args)
        self.assertEqual(self.board.read_bytes(), before)

    def test_errors_are_json_on_stderr_with_empty_stdout(self):
        for args in (("pads",), ("summary", "--limit", "0"), ("nets", "GND")):
            proc = self.run_cli_raw(*args)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(proc.stdout, "")
            error = json.loads(proc.stderr)
            self.assertEqual(error["status"], "NOT_VERIFIED")
            self.assertEqual(error["verification"], "NOT_VERIFIED")
            self.assertTrue(error["error"])
        ok = self.run_cli_raw("summary")
        self.assertEqual(ok.returncode, 0)
        self.assertEqual(ok.stderr, "")

    def test_version_is_the_same_in_script_and_skill(self):
        source = SCRIPT.read_text(encoding="utf-8")
        skill = (SCRIPT.parents[1] / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn('VERSION = "1.1"', source)
        self.assertIn("(v1.1)", source.split("\n", 2)[1])
        self.assertIn("## Commands (v1.1", skill)
        self.assertNotIn("v0.4", source)
        self.assertNotIn("v1.0", skill)

    def test_output_is_utf8_json_for_non_ascii_names(self):
        self.board.write_text(NAME_ONLY_NET_BOARD.replace("NAME_ONLY", "Ω_SENSE_µ"), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "net", "Ω_SENSE_µ", "--board", str(self.board)],
            capture_output=True, env={**__import__("os").environ, "PYTHONIOENCODING": "ascii"},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout.decode("utf-8"))["net"], "Ω_SENSE_µ")

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
