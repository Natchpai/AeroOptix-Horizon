/**
 * Hand placement for the diagrams, like a datasheet block diagram.
 *
 * The MCU (or the board, on the system view) is drawn just large enough
 * that every block it talks to sits beside one of its edges, so each link is one
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
    elrs: { x: 1200, y: 170 },
    tel2dev: { x: 1200, y: 260 },
    gps: { x: 1200, y: 350 },
    airspeed: { x: 1200, y: 440 },
    lidar: { x: 1200, y: 530 },
    pc: { x: 1200, y: 620 },
    card: { x: 1200, y: 710 },

    // actuators, below
    esc: { x: 440, y: 950 },
    servos: { x: 760, y: 950 },
  },

  board: {
    // main MCU, just large enough for seven blocks per side
    h743: { x: 400, y: 200, w: 720, h: 640 },

    // H743 I/O on the top
    'j-sd': { x: 420, y: 0 },
    'j-dbg': { x: 660, y: 0 },
    leds: { x: 900, y: 0 },

    // sensors, buzzer and the power module port, left
    imu1: { x: 40, y: 214 },
    imu2: { x: 40, y: 306 },
    baro1: { x: 40, y: 398 },
    baro2: { x: 40, y: 490 },
    mag: { x: 40, y: 582 },
    buzzer: { x: 40, y: 674 },
    'j-pm': { x: 40, y: 766 },

    // H743 connectors, right
    'j-tel1': { x: 1260, y: 214 },
    'j-tel2': { x: 1260, y: 306 },
    'j-air': { x: 1260, y: 398 },
    'j-lidar': { x: 1260, y: 490 },
    'j-esc': { x: 1260, y: 582 },
    'p-spare': { x: 1260, y: 674 },
    'j-gps': { x: 1260, y: 766 },

    // IO MCU under the H743, wide enough to reach GPS1 straight up;
    // the XT30 input sits above the servo headers
    f100: { x: 760, y: 980, w: 740, h: 200 },
    'j-servo': { x: 1680, y: 990, h: 84 },
    'p-f100dbg': { x: 1680, y: 1110 },
    xt30: { x: 1680, y: 870 },

    // power chain, lower left; rails are wide bars
    efuse: { x: 40, y: 980 },
    'j-usb': { x: 420, y: 980 },
    'r-5v': { x: 40, y: 1140, w: 584, h: 40 },
    ldo: { x: 40, y: 1260 },
    buck: { x: 280, y: 1260 },
    'r-3v3': { x: 280, y: 1420, w: 1220, h: 40 },
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
  'b-3v3-h743': 680,
}
