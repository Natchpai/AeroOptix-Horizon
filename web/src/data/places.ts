/**
 * Hand placement for the diagrams, like a datasheet block diagram.
 *
 * The MCU (or the board, on the Overview) is drawn just large enough
 * that every block it talks to sits beside one of its edges, so each link is one
 * straight line. Power rails are wide bars that loads tap with a horizontal
 * line. Block order along an edge is chosen so lines do not cross.
 *
 * Link ends on one side of a block are spaced equally and centred on that
 * side (engineer, 2026-10-26); a `bundles` group counts as one end. A block
 * with one end on a side sits level with the other block's end, so the line
 * meets it in the middle. `npm run check` fails on bent or crossing lines
 * and on unequal or off-centre ends.
 *
 * Positions are top-left corners in px; sizes default to the node size.
 * This is drawing data only; connectivity comes from topology.ts.
 */
import type { Level } from './types'

export type Place = { x: number; y: number; w?: number; h?: number }
export type Side = 'left' | 'right' | 'top' | 'bottom'

export const places: Record<Level, Record<string, Place>> = {
  // Overview (L0), in zones. In board (one zone, the PCB): the FC with its
  // ports, power in and out on the left, normal connectors on the right. Out board: the
  // power chain far left, devices far right, actuators below. Each device
  // line starts at the port it plugs into; the FC itself has no lines.
  system: {
    fc: { x: -100, y: 60, w: 480, h: 580 },

    // power in / out ports, left of the FC; the ESC headers face the ESC
    'o-pm': { x: -460, y: 200, w: 240 },
    'o-vservo1': { x: -460, y: 410, w: 240 },
    'o-vservo2': { x: -460, y: 510, w: 240 },
    'o-esc': { x: -460, y: 610, w: 240 },
    'o-servo': { x: -460, y: 710, w: 240 },

    // normal connectors, right of the FC, 92 apart
    'o-tel1': { x: 480, y: 0, w: 240 },
    'o-tel2': { x: 480, y: 92, w: 240 },
    'o-rcin': { x: 480, y: 184, w: 240 },
    'o-gps': { x: 480, y: 276, w: 240 },
    'o-air': { x: 480, y: 368, w: 240 },
    'o-lidar': { x: 480, y: 460, w: 240 },
    'o-usb': { x: 480, y: 552, w: 240 },
    'o-sd': { x: 480, y: 644, w: 240 },
    'o-dbg': { x: 480, y: 736, w: 240 },

    // power chain, left to right: battery, PM02D (battery down to the ESC),
    // 4in1 ESC (no PDB, DEC-054; tall for three right-side ends 100 apart,
    // centred on 540: UBEC 1 at 440, UBEC 2 at 540, ESC headers at 640),
    // one UBEC per servo rail into its 1x3 header (DEC-114)
    battery: { x: -1540, y: 200 },
    pm02d: { x: -1180, y: 140, h: 180 },
    esc: { x: -1210, y: 380, w: 260, h: 320 },
    ubec: { x: -820, y: 410 },
    ubec2: { x: -820, y: 510 },

    // devices, level with their ports, wide enough for their notes
    sik: { x: 940, y: 0, w: 260 },
    tel2dev: { x: 940, y: 92, w: 260 },
    rx: { x: 940, y: 184, w: 260 },
    gps: { x: 940, y: 276, w: 260 },
    airspeed: { x: 940, y: 368, w: 260 },
    lidar: { x: 940, y: 460, w: 260 },
    pc: { x: 940, y: 552, w: 260 },
    card: { x: 940, y: 644, w: 260 },
    probe: { x: 940, y: 736, w: 260 },

    // servos under their port
    servos: { x: -490, y: 992, w: 300 },
  },

  // System (L1), in zones: on-board I/O on top, sensors and the I2C2 bus
  // left, USB and debug under them, connectors in one column on the right
  board: {
    // main MCU, just large enough for seven blocks on its right side
    h743: { x: 400, y: 200, w: 720, h: 640 },

    // on-board I/O, top: 228 apart, centred on the H743 top
    'j-sd': { x: 432, y: 0 },
    'p-spare': { x: 660, y: 0 },
    leds: { x: 888, y: 0 },

    // H743 left side, 120 apart: the IMUs, the I2C2 trunk, USB-C and the
    // H743 debug port
    imu1: { x: 40, y: 250 },
    imu2: { x: 40, y: 370 },
    'j-usb': { x: 40, y: 610 },
    'j-dbg': { x: 40, y: 730 },

    // I2C2: one line out of the H743, between IMU 2 and USB-C, to a bus
    // bar; the bar taps each sensor further out, 92 apart
    i2c2: { x: -160, y: 380, w: 120, h: 280 },
    baro1: { x: -500, y: 398 },
    baro2: { x: -500, y: 490 },
    mag: { x: -500, y: 582 },

    // IO MCU and buzzer driver under the H743. The H743 bottom has two
    // ends centred on 760: the MCU link at 580 (F100 centre) and the
    // buzzer line at 940 (buzzer centre). The buzzer driver sits level
    // with GPS1's centre (916), so its line to GPS1 is the middle of
    // three GPS1 ends 120 apart (796, 916, 1036). The F100 left side
    // drives the SWD pads, in the USB and debug column.
    // Tall for its four right-side ends (DEC-051, DEC-053): the safety
    // line, RC IN, the ESC group and the surface group, 200 apart, centred
    // on 1336.
    f100: { x: 380, y: 900, w: 400, h: 872 },
    buzzer: { x: 840, y: 886 },
    'p-f100dbg': { x: 40, y: 1306 },

    // connectors, right column, 92 apart. GPS1 is tall, so it faces both
    // the H743 (796) and the F100 (1036). The tilt servo headers (AUX, H743
    // TIM5) sit above it; the ESC and surface headers (MAIN, F100) under it.
    'j-tel1': { x: 1300, y: 214, w: 240 },
    'j-tel2': { x: 1300, y: 306, w: 240 },
    'j-pm': { x: 1300, y: 398, w: 240 },
    'j-air': { x: 1300, y: 490, w: 240 },
    'j-lidar': { x: 1300, y: 582, w: 240 },
    'j-aux': { x: 1300, y: 674, w: 240 },
    'j-gps': { x: 1300, y: 776, w: 240, h: 280 },
    'j-rcin': { x: 1300, y: 1206, w: 240 },
    'j-esc': { x: 1300, y: 1360, w: 240, h: 152 },
    'j-servo': { x: 1300, y: 1538, w: 240, h: 196 },
  },

  // Power (L1): left to right, columns 180 px apart: source, input,
  // protection, +5V bar, converters, +3V3 bar, loads. Rail bars stand
  // upright and are wide enough for their name. The +5V bar is centred on
  // the LDO line (560), the +3V3 bar on the buck line (300), with the
  // H743 and F100 lines 85 px either side. The LDO is tall and centred on
  // 560, so its +3V3A lines to the sensors (515, 605) pass under the
  // +3V3 bar (DEC-043).
  power: {
    'pw-batt': { x: 0, y: 730 },
    'pw-pm02d': { x: 380, y: 460, h: 600 },

    // USB-C feeds the power mux IN2 from above; the mux line sits on the
    // +5V bar centre (560)
    'pw-usb': { x: 760, y: 350 },
    'pw-pmux': { x: 760, y: 530 },
    // 4in1 ESC in the old PDB place (no PDB, DEC-054); the UBEC sits on
    // its battery pads
    'pw-esc': { x: 760, y: 860, w: 260, h: 200 },

    'pw-r5v': { x: 1140, y: 280, w: 120, h: 560 },

    'pw-buck': { x: 1440, y: 270 },
    'pw-ldo': { x: 1440, y: 470, w: 240, h: 180 },
    // one UBEC per servo rail (DEC-114): two rows 88 apart, centred on the
    // ESC (960), clear of the 5 V ports block above
    'pw-ubec': { x: 1440, y: 886, w: 240 },
    'pw-ubec2': { x: 1440, y: 974, w: 240 },

    'pw-r3v3': { x: 1820, y: 130, w: 120, h: 340 },
    'pw-cn804': { x: 1800, y: 886, w: 240 },
    'pw-cn805': { x: 1800, y: 974, w: 240 },

    // loads wide enough for their part numbers in full
    'pw-h743': { x: 2120, y: 145, w: 300, h: 140 },
    'pw-f100': { x: 2120, y: 315, w: 300, h: 140 },
    'pw-baro-mag': { x: 2120, y: 485, w: 300 },
    'pw-imu': { x: 2120, y: 575, w: 300 },
    'pw-ports': { x: 2120, y: 790, w: 300 },
    'pw-servos': { x: 2120, y: 886, w: 300 },
    'pw-servos2': { x: 2120, y: 974, w: 300 },
  },
}

/**
 * Zones: a titled box drawn behind a group of blocks, sized to fit them.
 * No other block may sit inside a zone (`npm run check`).
 */
export type Zone = {
  id: string
  label: string
  blocks: string[]
  /** Title place; left unless a line passes there. */
  title?: 'center'
}

export const zones: Partial<Record<Level, Zone[]>> = {
  system: [
    {
      // the PCB: the FC and every port on it. Power ports sit left of the
      // FC, normal connectors right of it.
      id: 'z-in',
      label: 'In board (PCB)',
      blocks: [
        'fc',
        'o-pm',
        'o-vservo1',
        'o-vservo2',
        'o-esc',
        'o-servo',
        'o-tel1',
        'o-tel2',
        'o-rcin',
        'o-gps',
        'o-air',
        'o-lidar',
        'o-usb',
        'o-sd',
        'o-dbg',
      ],
    },
    {
      id: 'z-out-pwr',
      label: 'Out board: power and ESC',
      blocks: ['battery', 'pm02d', 'esc', 'ubec', 'ubec2'],
    },
    {
      id: 'z-out-dev',
      label: 'Out board: devices',
      blocks: [
        'sik',
        'tel2dev',
        'rx',
        'gps',
        'airspeed',
        'lidar',
        'pc',
        'card',
        'probe',
      ],
    },
    {
      id: 'z-out-act',
      label: 'Out board: actuators',
      // centred: the servo lines pass the left end
      title: 'center',
      blocks: ['servos'],
    },
  ],
  board: [
    {
      id: 'z-io',
      label: 'On-board I/O',
      blocks: ['j-sd', 'p-spare', 'leds'],
    },
    {
      id: 'z-usb-dbg',
      label: 'USB and debug',
      blocks: ['j-usb', 'j-dbg', 'p-f100dbg'],
    },
    {
      id: 'z-conn',
      label: 'Connectors',
      blocks: [
        'j-tel1',
        'j-tel2',
        'j-pm',
        'j-air',
        'j-lidar',
        'j-aux',
        'j-gps',
        'j-rcin',
        'j-esc',
        'j-servo',
      ],
    },
  ],
}

/** Sides to use instead of the facing sides, as [source side, target side]. */
export const sideOverrides: Record<string, [Side, Side]> = {}

/**
 * Links drawn as one group, 28 px apart. A group counts as one end when
 * `npm run check` tests that the ends on a side are equally spaced.
 */
export const bundles: string[][] = [
  // ESC PWM lines (MAIN 1 to 4)
  Array.from({ length: 4 }, (_, i) => `b-esc-${i + 1}`),
  // surface servo PWM lines (MAIN 5 to 8), with the rail sense line set
  // apart (engineer's rule)
  [...Array.from({ length: 4 }, (_, i) => `b-servo-${i + 1}`), 'b-servo-sense'],
  // servo headers to servos: PWM and the 6 V bus side by side
  ['s-fc-servo', 's-fc-servo-pwr'],
]

/**
 * Where a straight link runs, in absolute px (x for a vertical link, y for
 * a horizontal one), when the middle of the overlap is not where the
 * equal-spacing rule needs it.
 */
export const lineAt: Record<string, number> = {
  // Overview: PM02D to its port, two lines 28 apart, centred on both
  's-pm-fc-pwr': 216,
  's-pm-fc-i2c': 244,
  // ESC right side: two UBEC lines and the ESC header line, centred on
  // the ESC (540)
  's-esc-ubec': 440,
  's-esc-ubec2': 540,
  's-fc-esc': 640,
  // servo headers to servos pair, centred on both (-340)
  's-fc-servo': -354,
  's-fc-servo-pwr': -326,
  // H743 bottom: the MCU link through the F100 centre (the buzzer line
  // meets the middle of its block without help)
  'b-link': 580,
  // GPS1: the H743 line on the 92 px pitch of the right column
  'b-gps': 796,
  // F100 right side: the safety line and the servo group, centred
  'b-safety': 1036,
  // Power view: lines that would otherwise sit at the middle of a partial
  // overlap
  'pw-pm-esc': 960,
  'pw-5v-buck': 300,
  'pw-5v-ports': 820,
  // F100 right side, four ends 200 apart centred on 1336: the safety line
  // (1036), RC IN (1236), the ESC group (centred on 1436) and the surface
  // group with the rail sense line set apart (centred on 1636). Lines 28 px
  // apart.
  'b-rcin': 1236,
  ...Object.fromEntries(
    Array.from({ length: 4 }, (_, i) => [`b-esc-${i + 1}`, 1394 + i * 28])
  ),
  ...Object.fromEntries(
    Array.from({ length: 4 }, (_, i) => [`b-servo-${i + 1}`, 1572 + i * 28])
  ),
  'b-servo-sense': 1700,
}
