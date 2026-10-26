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
  // Overview (L0). FC left side ends at 300, 420, 540, 660: 120 apart,
  // centred on 150..810.
  system: {
    fc: { x: 400, y: 150, w: 600, h: 660 },

    // power path, left to right: battery, PM02D (5 V and I2C4 out to the
    // FC, battery down to the PDB), PDB, then the UBEC into the FC and the
    // ESCs
    battery: { x: -1040, y: 330 },
    pm02d: { x: -720, y: 270, h: 180 },
    pdb: { x: -720, y: 510, h: 560 },
    ubec: { x: 40, y: 510 },
    probe: { x: 40, y: 630 },

    // devices on the FC I/O, right: 90 apart, centred on the FC side
    elrs: { x: 1200, y: 180 },
    tel2dev: { x: 1200, y: 270 },
    gps: { x: 1200, y: 360 },
    airspeed: { x: 1200, y: 450 },
    lidar: { x: 1200, y: 540 },
    pc: { x: 1200, y: 630 },
    card: { x: 1200, y: 720 },

    // actuators, below: ESC line at 540 and the servo pair centred at 860,
    // both 160 from the FC bottom centre (700)
    esc: { x: 440, y: 1010 },
    servos: { x: 760, y: 1010 },
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
export type Zone = { id: string; label: string; blocks: string[] }

export const zones: Partial<Record<Level, Zone[]>> = {
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
  // FC to servos: PWM and the 6 V bus side by side
  ['s-fc-servo', 's-fc-servo-pwr'],
]

/**
 * Where a straight link runs, in absolute px (x for a vertical link, y for
 * a horizontal one), when the middle of the overlap is not where the
 * equal-spacing rule needs it.
 */
export const lineAt: Record<string, number> = {
  // PM02D (y 270 to 450) right side: two ends, 120 apart, centred
  's-pm-fc-pwr': 300,
  's-pm-fc-i2c': 420,
  // FC to servos pair, centred on the servos block (860)
  's-fc-servo': 846,
  's-fc-servo-pwr': 874,
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
