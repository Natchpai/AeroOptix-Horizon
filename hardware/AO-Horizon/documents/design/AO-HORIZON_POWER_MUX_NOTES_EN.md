# AeroOptix-Horizon: TPS2121 Power Mux Notes

**Revision:** 0.6
**Updated:** 2026-11-03
**Status:** Design note for reading and re-calculation. Not a requirement or verification record. Decisions live in the spec (DEC-029 to DEC-037, PWR-015; references as in the 17:11 save, 2026-11-03; OPEN-024 closed; OPEN-025 open).
**Source:** TI TPS212x datasheet SLVSEA3F (August 2020), NotebookLM notebook `TPS212x 2.8-V to 22-V Priority Power MUX with Seamless Switchover`, read as source fulltext. TI values are `VERIFIED`; calculated values are `ESTIMATED`, before resistor tolerance.

## 1. What the mux does on this board

```text
PM02D 5 V  (PM02_5V) --> IN1 --+
                               +--> TPS2121 U101 --> OUT --> +5V bus
USB VBUS   (VBUS)    --> IN2 --+
```

- It picks one input and connects it to `+5V`. The other input is blocked, so USB never back-feeds the PM02D and the PM02D never back-feeds USB (reverse current blocking on both channels, TI 9.3.6).
- Which input it picks depends on two pins, PR1 and CP2. Each has a resistor divider or is tied to `GND`.
- An input is "valid" only when it is above UV (2.65 V typ) and below its OV divider trip. If only one input is valid, that one is used, whatever PR1 and CP2 say.

## 2. TI numbers used in every calculation

| Item | Value | TI source |
| ---- | ----- | --------- |
| VREF (PR1, CP2, OV1, OV2), rising | 1.01 / 1.06 / 1.10 V (min / typ / max) | Electrical Characteristics |
| VREF, falling | 0.99 / 1.04 / 1.09 V | Electrical Characteristics |
| Comparator offset PR1 vs CP2 (TPS2121) | 5 / 20 / 40 mV | Electrical Characteristics |
| Switchover time, CP2 below VREF | up to 100 µs | Electrical Characteristics |
| Fast switchover time, CP2 at or above VREF | 5 µs | Electrical Characteristics |
| VCOMP (IN2 vs IN1) | 0 / 280 / 600 mV | Electrical Characteristics |
| RILM range | 18 to 100 kΩ | Recommended Operating Conditions |
| OV1, OV2, PR1, CP2, ST pin voltage | 5.5 V recommended, 6 V absolute maximum | 7.1, 7.3 |

## 3. The four modes (TI Table 9-3)

| Mode | PR1 | CP2 | Who wins when both inputs are valid | Switchover |
| ---- | --- | --- | ----------------------------------- | ---------- |
| VCOMP | `GND` | `GND` | The higher input. IN2 wins at equal voltage or within VCOMP of IN1 | 100 µs |
| VREF | Divider from IN1 | `GND` | IN1 while PR1 is above VREF; IN2 when PR1 falls below VREF | 100 µs |
| XCOMP | Divider from IN1 | Divider from IN2 | IN1 while PR1 is above CP2; IN2 when CP2 is above PR1 | 5 µs |
| XREF | Divider from IN1 | Fixed reference (TI: REF3325, 2.5 V) | IN1 while PR1 is above the reference | 5 µs |

Rule of thumb: CP2 below VREF means "ignore CP2" (slow). CP2 at or above VREF means "compare PR1 with CP2" (fast).

## 4. Divider basics

A divider with `Rtop` from the input to the pin and `Rbot` from the pin to `GND`:

```text
Vpin = Vin × Rbot / (Rtop + Rbot)
k    = (Rtop + Rbot) / Rbot          (the divider ratio)
Vin at the switch point = Vpin threshold × k
Rtop = Rbot × (k − 1)
```

Pick `Rbot` first (TI uses 5 kΩ in all examples), find `k`, then `Rtop`, then round to an E96 value and re-check.

## 5. How to calculate each mode

### 5.1 VCOMP (no resistors)

Tie PR1 and CP2 to `GND`. Nothing to calculate. On this board it is a bad fit: USB usually wins when both are plugged in, because USB is at or near the PM02D voltage.

### 5.2 VREF (PR1 divider, CP2 to `GND`)

Goal: switch to USB when the PM02D falls to `Vsw`.

1. `k1 = Vsw / VREF_typ` (use 1.04 V falling).
2. `Rtop = 5 kΩ × (k1 − 1)`, round to E96.
3. Check the worst case: `Vsw_max = 1.09 V × k1` (falling). It must stay below the 4.5 V input minimum (PWR-010).

Examples:

| PR1 Rtop / Rbot | k1 | To USB at (min / typ / max) | Back to PM02D at |
| --------------- | -- | --------------------------- | ---------------- |
| 13.7 kΩ / 5 kΩ | 3.74 | 3.70 / 3.89 / 4.08 V | 3.78 / 3.96 / 4.11 V |
| 12.4 kΩ / 5 kΩ | 3.48 | 3.45 / 3.62 / 3.79 V | 3.51 / 3.69 / 3.83 V |
| 12.1 kΩ / 5 kΩ (as drawn) | 3.42 | 3.39 / 3.56 / 3.73 V | 3.45 / 3.63 / 3.76 V |

### 5.3 XCOMP (PR1 divider from IN1, CP2 divider from IN2)

Here PR1 is compared with CP2, not with VREF. So the CP2 voltage sets the switch point, and it moves with the USB voltage.

1. **CP2 floor.** CP2 must be at or above VREF max (1.10 V) at the lowest USB voltage, or fast mode does not turn on.
   `k2 ≤ VBUS_min / 1.10 V = 4.75 / 1.10 = 4.32`. With 5 kΩ: `Rtop ≤ 16.6 kΩ`, so 16.5 kΩ (k2 = 4.3).
2. **Highest CP2.** `VCP2_max = VBUS_max / k2 = 5.25 / 4.3 = 1.221 V`.
3. **PR1.** At the lowest valid PM02D (4.5 V), PR1 must stay above the highest CP2 plus the offset:
   `4.5 V / k1 > 1.221 V + 0.040 V`, so `k1 < 3.57`. With 5 kΩ: `Rtop < 12.85 kΩ`. 12.7 kΩ leaves only 40 mV. 12.4 kΩ (k1 = 3.48) looked fine before resistor tolerance but fails step 5, so the board uses 12.1 kΩ (k1 = 3.42, DEC-034).
4. **Check.** Switch point `= VCP2 × k1`: 3.78 / 3.98 / 4.18 V for `VBUS` 4.75 / 5.0 / 5.25 V, plus up to 0.14 V offset, so 4.31 V before resistor tolerance.
5. **Resistor tolerance.** Worst case at `VBUS` 5.25 V, each 1 % resistor in the bad direction:
   - CP2 high: R105 16.335 kΩ, R106 5.05 kΩ, so `VCP2 = 5.25 × 5.05 / 21.385 = 1.24 V`.
   - PR1 ratio low: R101 12.221 kΩ, R102 4.95 kΩ, so `4.95 / 17.171 = 0.2883`.
   - Switch point `= 1.24 / 0.2883 = 4.30 V`, plus the offset `0.040 / 0.2883 = 0.14 V`, so **4.44 V**: 0.06 V below the 4.5 V minimum.
   - With the old 12.4 kΩ the same case gave 4.52 V, 0.02 V above the minimum. 0.5 % resistors would also have fixed it (4.45 V); R101 12.1 kΩ with 1 % parts was chosen (DEC-034).
   - It only matters on the bench: in flight there is no `VBUS`, so CP2 is 0 V.
6. **Check the fallback.** If CP2 is not fitted, the same PR1 works in VREF mode (5.2): 3.39 to 3.76 V.

Why not other values:

| Change | Result |
| ------ | ------ |
| Keep PR1 at 13.7 kΩ in XCOMP | Worst case 4.72 V: a PM02D at 4.5 V would hand over to USB |
| Keep PR1 at 12.4 kΩ in XCOMP | Worst case 4.52 V with 1 % resistors (5.3 step 5): just above 4.5 V |
| CP2 top 15.8 kΩ (with PR1 12.4 kΩ) | More fast-mode margin, but worst-case switch point about 4.53 V before resistor tolerance |
| CP2 top 10.2 kΩ (TI 5 V example, 1.64 V) | Switch point about 6 V: USB always wins |

Weak point: at `VBUS` 4.75 V, CP2 is about 1.10 V, the same as VREF max. A part may then stay in VREF mode. That is safe: the PM02D still has priority, only the switchover is slow.

### 5.4 XREF (PR1 divider, CP2 from a fixed reference)

The switch point no longer depends on the USB voltage.

1. Pick a reference `Vx` at or above 1.10 V (TI uses 2.5 V).
2. `k1 = Vsw / Vx`, then `Rtop = 5 kΩ × (k1 − 1)`.
3. Example for `Vsw` = 4.0 V with a 2.5 V reference: `k1` = 1.6, `Rtop` = 3.0 kΩ (E96 3.01 kΩ).
4. Before the reference is up, CP2 is low, so the mux runs VREF mode with the same PR1: `Vsw = 1.04 V × 1.6 ≈ 1.7 V`. Check that this start-up case is acceptable.

Not used on this board: it needs a reference part. Not checked further.

### 5.5 OV dividers (OV1, OV2)

The channel turns off when its OV pin reaches VREF.

- `Vov = 1.06 V × k`. With 23.2 kΩ / 5 kΩ (k = 5.64, DEC-036): 5.98 V typ, 5.70 to 6.20 V over the VREF range, 5.60 to 6.31 V with 1 % resistors. The channel turns back on below `1.04 V × k` = 5.87 V typ (VREF falling 0.99 / 1.04 / 1.09 V).
- Window: the lowest trip must stay above the 5.5 V input maximum (PWR-010). `+5V` stays below 5.5 V in normal operation (PWR-015); the OV trip is a fault guard. 23.2 kΩ is the lowest E96 value that meets 5.5 V in the worst case (22.6 kΩ gives 5.48 V).
- Was 23.7 kΩ (6.08 V typ) until 2026-11-02, then 21.5 kΩ, which could trip at 5.27 V.

### 5.6 Current limit (ILIM)

- TI table: RILM 80 kΩ gives 1.0 / 1.5 / 2.0 A (use the table for min and max).
- Equation for the typical value, RILM in kΩ: `ILM = 65.2 / RILM^0.861`, so `RILM = (65.2 / ILM)^(1/0.861)`. For 1.5 A: about 80 kΩ, so 80.6 kΩ (E96). The equation form was read from flattened text; it matches TI's 59 kΩ to 1.95 A example.

### 5.7 Soft-start (SS) and switchover dip

- TI Table 9-1: 100 nF gives 780 V/s at 5 V. Slew scales about as `1 / CSS`, so 10 nF gives about 7.8 kV/s (extrapolated, below the table range).
- Inrush current `= C_load × slew`. With about 60 µF on `+5V` and `+5V_BUCK`: about 0.47 A.
- Output dip during a switchover: `VDIP = IOUT × tSW / COUT`. At 1 A, 100 µs, 60 µF: about 1.7 V. At 5 µs: about 0.08 V.

## 6. As drawn (saved file, 2026-11-02 00:32)

| Pin | Parts | Value | Decision |
| --- | ----- | ----- | -------- |
| PR1 | R101 from `PM02_5V`, R102 to `GND` | 12.1 kΩ / 5 kΩ | DEC-031, DEC-034 |
| CP2 | R105 from `VBUS`, R106 to `GND` | 16.5 kΩ / 5 kΩ (R105 fitted) | DEC-032, DEC-033 |
| OV1 | R103 from `PM02_5V`, R104 to `GND` | 23.2 kΩ / 5 kΩ | DEC-036 |
| OV2 | R107 from `VBUS`, R108 to `GND` | 23.2 kΩ / 5 kΩ | DEC-036 |
| ILIM | R112 to `GND` | 80.6 kΩ (1.5 A) | DEC-030 |
| SS | C108 to `GND` | 10 nF | Drawn |
| ST | R109 from `+5V`, R110 to `GND`; drives the Q101 gate (2SK3018W), which switches the D103 status LED (lit for IN1, off for IN2) | 10 kΩ / 10 kΩ: ST 2.23 to 3.19 V when high; R109 is the 6 to 20 kΩ pull-up TI asks for | DEC-035, DEC-036 |

**Switching between modes on the board:** fit R105 for XCOMP (5 µs). Leave R105 off for VREF mode (100 µs): R106 then pulls CP2 to `GND`. No other part changes. R105 is fitted in the saved file, so the default build is XCOMP (DEC-033).

## 7. Checklist when changing any value

- [ ] CP2 at or above 1.10 V at the lowest USB voltage (XCOMP).
- [ ] Worst-case switch point below 4.5 V (PWR-010), with resistor tolerance and the 40 mV offset × k1 (5.3 step 5).
- [ ] Use 1 % resistors in the PR1 and CP2 dividers.
- [ ] Every pin below 5.5 V at the highest input (OV trip 6.31 V max: PR1 1.85 V, CP2 1.47 V, OV 1.10 V).
- [ ] RILM between 18 and 100 kΩ.
- [ ] Update DEC-031 to DEC-034 and spec 4.7 if a value changes.
