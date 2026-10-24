/**
 * Hand placement for the diagrams, like a datasheet block diagram.
 *
 * The MCU (or the board, on the system view) is drawn large, and every
 * block it talks to sits beside one of its edges, so each link is one
 * straight line. Power rails are wide bars that loads tap with a vertical
 * line. Block order along an edge is chosen so lines do not cross;
 * `npm run check` fails on bent or crossing lines.
 *
 * Positions are top-left corners in px; sizes default to the node size.
 * This is drawing data only; connectivity comes from topology.ts.
 */
import type { Level } from './types'

export type Place = { x: number; y: number; w?: number; h?: number }
export type Side = 'left' | 'right' | 'top' | 'bottom'

export const places: Record<Level, Record<string, Place>> = {
  system: {
    fc: { x: 400, y: 150, w: 600, h: 660 },

    // power path, left
    battery: { x: 40, y: 20 },
    pm02d: { x: 40, y: 200, h: 84 },
    pdb: { x: -300, y: 200, h: 820 },
    ubec: { x: 40, y: 420 },
    probe: { x: 40, y: 640 },

    // devices on the FC I/O, right
    elrs: { x: 1160, y: 170 },
    tel2dev: { x: 1160, y: 260 },
    gps: { x: 1160, y: 350 },
    airspeed: { x: 1160, y: 440 },
    lidar: { x: 1160, y: 530 },
    pc: { x: 1160, y: 620 },
    card: { x: 1160, y: 710 },

    // actuators, below
    esc: { x: 440, y: 950 },
    servos: { x: 760, y: 950 },
  },

  board: {
    // main MCU, large so every link reaches it straight
    h743: { x: 400, y: 200, w: 900, h: 700 },

    // H743 I/O on the top
    'j-sd': { x: 440, y: 0 },
    'j-dbg': { x: 660, y: 0 },
    buzzer: { x: 880, y: 0 },
    leds: { x: 1100, y: 0 },

    // sensors and the power module port, left
    imu1: { x: 40, y: 220 },
    imu2: { x: 40, y: 310 },
    baro1: { x: 40, y: 430 },
    baro2: { x: 40, y: 520 },
    mag: { x: 40, y: 610 },
    'j-pm': { x: 40, y: 780 },

    // H743 connectors, right
    'j-tel1': { x: 1440, y: 220 },
    'j-tel2': { x: 1440, y: 310 },
    'j-air': { x: 1440, y: 400 },
    'j-lidar': { x: 1440, y: 490 },
    'j-esc': { x: 1440, y: 580 },
    'p-spare': { x: 1440, y: 670 },
    'j-gps': { x: 1440, y: 790 },

    // IO MCU under the H743, wide enough to reach GPS1 straight up
    f100: { x: 900, y: 1040, w: 740, h: 200 },
    'j-servo': { x: 1780, y: 1050, h: 84 },
    'p-f100dbg': { x: 1780, y: 1170 },
    xt30: { x: 2060, y: 1060 },

    // power chain, lower left; rails are wide bars
    efuse: { x: 40, y: 1040 },
    'j-usb': { x: 440, y: 1040 },
    'r-5v': { x: 40, y: 1200, w: 584, h: 40 },
    ldo: { x: 40, y: 1320 },
    buck: { x: 260, y: 1320 },
    'r-3v3': { x: 260, y: 1480, w: 1380, h: 40 },
  },
}

/** Sides to use instead of the facing sides, as [source side, target side]. */
export const sideOverrides: Record<string, [Side, Side]> = {}

/**
 * Where a straight link runs, in absolute px (x for a vertical link, y for
 * a horizontal one), when the middle of the overlap would pass too close
 * to another block.
 */
export const lineAt: Record<string, number> = {
  'b-3v3-h743': 760,
}
