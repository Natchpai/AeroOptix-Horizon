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

    // power in / out ports, left of the FC
    'o-pm': { x: -460, y: 200, w: 240 },
    'o-xt30': { x: -460, y: 400, w: 240 },
    'o-servo': { x: -460, y: 540, w: 240 },

    // normal connectors, right of the FC, 92 apart; ESC headers last, with
    // their line going down
    'o-tel1': { x: 480, y: 0, w: 240 },
    'o-tel2': { x: 480, y: 92, w: 240 },
    'o-gps': { x: 480, y: 184, w: 240 },
    'o-air': { x: 480, y: 276, w: 240 },
    'o-lidar': { x: 480, y: 368, w: 240 },
    'o-usb': { x: 480, y: 460, w: 240 },
    'o-sd': { x: 480, y: 552, w: 240 },
    'o-dbg': { x: 480, y: 644, w: 240 },
    'o-esc': { x: 480, y: 736, w: 240 },

    // power chain, left to right: battery, PM02D (battery down to the PDB),
    // PDB (tall: UBEC at 430, ESCs at 1020), UBEC into the XT30
    battery: { x: -1540, y: 200 },
    pm02d: { x: -1180, y: 140, h: 180 },
    pdb: { x: -1180, y: 380, h: 690 },
    ubec: { x: -820, y: 400 },

    // devices, level with their ports, wide enough for their notes
    elrs: { x: 940, y: 0, w: 260 },
    tel2dev: { x: 940, y: 92, w: 260 },
    gps: { x: 940, y: 184, w: 260 },
    airspeed: { x: 940, y: 276, w: 260 },
    lidar: { x: 940, y: 368, w: 260 },
    pc: { x: 940, y: 460, w: 260 },
    card: { x: 940, y: 552, w: 260 },
    probe: { x: 940, y: 644, w: 260 },

    // actuators under their ports; the ESC line from the PDB runs under
    // the servos
    servos: { x: -490, y: 900, w: 300 },
    esc: { x: 470, y: 990, w: 260 },
  },

  // System (L1), in zones: on-board I/O on top, sensors and the I2C2 bus
  // left, USB and debug under them, connectors in one column on the right
  board: {
    // main MCU, just large enough for seven blocks on its right side
    h743: { x: 400, y: 200, w: 720, h: 640 },

    // on-board I/O, top: 228 apart, centred on the H743 top
    'j-sd': { x: 318, y: 0 },
    'p-spare': { x: 546, y: 0 },
    leds: { x: 774, y: 0 },
    buzzer: { x: 1002, y: 0 },

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

    // IO MCU under the H743, centred on it. Its right side drives the
    // safety line to GPS1 and the servo group, centred on 1130; its left
    // side the SWD pads, in the USB and debug column.
    f100: { x: 560, y: 900, w: 400, h: 460 },
    'p-f100dbg': { x: 40, y: 1100 },

    // connectors, right column, 92 apart. GPS1 is tall, so it faces both
    // the H743 (796) and the F100 (1036); the servo headers sit under it.
    'j-tel1': { x: 1300, y: 214, w: 240 },
    'j-tel2': { x: 1300, y: 306, w: 240 },
    'j-pm': { x: 1300, y: 398, w: 240 },
    'j-air': { x: 1300, y: 490, w: 240 },
    'j-lidar': { x: 1300, y: 582, w: 240 },
    'j-esc': { x: 1300, y: 674, w: 240 },
    'j-gps': { x: 1300, y: 776, w: 240, h: 280 },
    'j-servo': { x: 1300, y: 1084, w: 240, h: 280 },
  },

  // Power (L1): left to right, columns 180 px apart: source, input,
  // protection, +5V bar, converters, +3V3 bar, loads. Rail bars stand
  // upright and are wide enough for their name. The +5V bar is centred on
  // the LDO line (560), the +3V3 bar on the buck line (300).
  power: {
    'pw-batt': { x: 0, y: 670 },
    'pw-pm02d': { x: 380, y: 400, h: 600 },

    'pw-efuse': { x: 760, y: 410 },
    'pw-usb': { x: 760, y: 650 },
    'pw-pdb': { x: 760, y: 860, h: 200 },

    'pw-r5v': { x: 1140, y: 280, w: 120, h: 560 },

    'pw-buck': { x: 1440, y: 270 },
    'pw-ldo': { x: 1440, y: 530, w: 240 },
    'pw-ubec': { x: 1440, y: 880 },

    'pw-r3v3': { x: 1820, y: 90, w: 120, h: 420 },
    'pw-xt30': { x: 1800, y: 880 },

    // loads wide enough for their part numbers in full
    'pw-h743': { x: 2120, y: 60, w: 300, h: 140 },
    'pw-f100': { x: 2120, y: 230, w: 300, h: 140 },
    'pw-baro-mag': { x: 2120, y: 440, w: 300 },
    'pw-imu': { x: 2120, y: 530, w: 300 },
    'pw-ports': { x: 2120, y: 790, w: 300 },
    'pw-servos': { x: 2120, y: 880, w: 300 },
    'pw-esc': { x: 2120, y: 980, w: 300 },
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
        'o-xt30',
        'o-servo',
        'o-tel1',
        'o-tel2',
        'o-gps',
        'o-air',
        'o-lidar',
        'o-usb',
        'o-sd',
        'o-dbg',
        'o-esc',
      ],
    },
    {
      id: 'z-out-pwr',
      label: 'Out board: power',
      blocks: ['battery', 'pm02d', 'pdb', 'ubec'],
    },
    {
      id: 'z-out-dev',
      label: 'Out board: devices',
      blocks: [
        'elrs',
        'tel2dev',
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
      // centred: the servo and ESC lines pass the left and right ends
      title: 'center',
      blocks: ['servos', 'esc'],
    },
  ],
  board: [
    {
      id: 'z-io',
      label: 'On-board I/O',
      blocks: ['j-sd', 'p-spare', 'leds', 'buzzer'],
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
        'j-esc',
        'j-gps',
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
  // servo PWM lines, with the rail sense line set apart (engineer's rule)
  [...Array.from({ length: 8 }, (_, i) => `b-servo-${i + 1}`), 'b-servo-sense'],
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
  // PDB right side: UBEC and ESC lines, centred on the PDB (725)
  's-pdb-ubec': 430,
  's-pdb-esc': 1020,
  // servo headers to servos pair, centred on both (-340)
  's-fc-servo': -354,
  's-fc-servo-pwr': -326,
  // H743 top: the outer two lines through the middle of their blocks
  'b-sd': 418,
  'b-buzzer': 1102,
  // GPS1: the H743 line on the 92 px pitch of the right column
  'b-gps': 796,
  // F100 right side: the safety line and the servo group, centred
  'b-safety': 1036,
  // Power view: lines that would otherwise sit at the middle of a partial
  // overlap
  'pw-pm-pdb': 960,
  'pw-5v-buck': 300,
  'pw-5v-ports': 820,
  'pw-3v3-h743': 130,
  // servo PWM lines 28 px apart, then the rail sense line set apart; the
  // group is centred on 1224, the safety line's mirror on the F100 right side
  ...Object.fromEntries(
    Array.from({ length: 8 }, (_, i) => [`b-servo-${i + 1}`, 1104 + i * 28])
  ),
  'b-servo-sense': 1344,
}
