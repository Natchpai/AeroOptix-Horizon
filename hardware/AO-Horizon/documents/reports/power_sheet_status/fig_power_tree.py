"""Power tree of the saved power_supplies.kicad_sch (2026-10-28). Run from this folder."""
import sys

sys.path.insert(0, "C:/Users/AORUS/.claude/skills/engineering-report-pdf/scripts")
from report_figs import *  # noqa: F401,F403

s = Schematic(1000, 260, inch_w=6.8)
Y = 60  # main rail height
H = 56  # block height


def block(x, y, w, title, sub, decided):
    c = BLUE if decided else GRAY
    s.box(x, y, w, H, c=c, ls="-", lw=1.6 if decided else 1.1)
    s.text(x + w / 2, y + H / 2 - 9, title, size=9, weight="semibold", c=INK)
    s.text(x + w / 2, y + H / 2 + 10, sub, size=7.5, c=MUTED)


# main chain
block(10, Y - H / 2, 130, "PM02D input", "JST-GH 6-pin", False)
block(210, Y - H / 2, 170, "TPS16412DRC", "eFuse, 1.5 A (DEC-024)", True)
block(450, Y - H / 2, 120, "Ferrite bead", "no part number", False)
block(670, Y - H / 2, 160, "TPS62142RGTR", "buck (DEC-012)", True)
s.arrow(140, Y, 210, Y)
s.text(175, Y - 11, "+VIN", size=8, c=INK)
s.wire([(380, Y), (450, Y)])
s.dot(410, Y)
s.text(410, Y - 11, "+5V", size=8, c=INK)
s.arrow(570, Y, 670, Y)
s.text(620, Y - 11, "+5V_BUCK", size=8, c=INK)
s.arrow(830, Y, 870, Y)
s.text(876, Y - 8, "+3V3", size=9, ha="left", weight="semibold", c=INK)
s.text(876, Y + 9, "MCUs, baro, mag", size=7.5, ha="left", c=MUTED)

# eFuse notes
s.text(295, Y + H / 2 + 18, "EN/~SHDN not connected", size=7.5, c=NAVY)
s.text(295, Y + H / 2 + 32, "6 part values still '?'", size=7.5, c=NAVY)

# LDO branch from +5V
Y2 = 200
block(670, Y2 - H / 2, 160, "TPS73533DRBR", "LDO, not decided", False)
s.wire([(410, Y), (410, Y2)])
s.arrow(410, Y2, 670, Y2)
s.text(540, Y2 - 11, "+5V", size=8, c=INK)
s.arrow(830, Y2, 870, Y2)
s.text(876, Y2 - 8, "+3V3A", size=9, ha="left", weight="semibold", c=INK)
s.text(876, Y2 + 9, "2 \u00d7 IMU (DEC-025)", size=7.5, ha="left", c=MUTED)

# fault LED from the eFuse
block(210, Y2 - H / 2, 170, "Red fault LED", "on ~FLT, fed from +VIN", False)
s.wire([(295, Y + H / 2 + 40), (295, Y2 - H / 2)], c=GRAY, ls=(0, (3, 3)))

s.save("fig_power_tree.svg")
