#!/usr/bin/env python3
"""Buck BJT topology still — continuous L centered between D and C."""
import cairo
from pathlib import Path
import symbols as S
from symbols import hx, wire, junction, text, npn, gnd, coil, diode, capacitor, resistor

OUT = Path(__file__).resolve().parent / "buck_topology.png"
W, H = 1920, 1080
BG = (0xF6 / 255, 0xF8 / 255, 0xFA / 255)
INK = hx("#1f2328")
LW = 5.0


def layout():
    """Shared geometry for topology + animation."""
    Sx, Sy = 560, 360
    s_bjt = 1.25
    Ysw, Ygnd = 540, 880
    Xvout = 1100
    Xvin, Yvin = 220, 150
    # BJT collector x offset ≈ 22*s
    Xsw = Sx + 22 * s_bjt
    # L centered in open span between SW/D and Vout/C
    gap = 36
    mid = (Xsw + Xvout) / 2
    half = 90  # ~180 px continuous coil, centered D↔C
    Xl0, Xl1 = mid - half, mid + half
    Xr = Xvout + 200
    return dict(Sx=Sx, Sy=Sy, s_bjt=s_bjt, Ysw=Ysw, Ygnd=Ygnd,
                Xvout=Xvout, Xvin=Xvin, Yvin=Yvin, Xsw=Xsw,
                Xl0=Xl0, Xl1=Xl1, Xr=Xr, gap=gap)


def draw_schematic(ctx, on=False, oncol=None):
    """Draw Buck schematic; returns path dict for animation."""
    L = layout()
    Sx, Sy, s = L['Sx'], L['Sy'], L['s_bjt']
    Ysw, Ygnd = L['Ysw'], L['Ygnd']
    Xvout, Xvin, Yvin = L['Xvout'], L['Xvin'], L['Yvin']
    Xl0, Xl1, Xr = L['Xl0'], L['Xl1'], L['Xr']

    C, E, B, ce = npn(ctx, Sx, Sy, s=s, c=INK, lw=LW, on=on, oncol=oncol)
    Xsw = E[0]

    wire(ctx, [(Xvin, Yvin), (C[0], Yvin), C], INK, LW)
    junction(ctx, C[0], Yvin, 7)
    junction(ctx, Xvin, Yvin, 7)
    text(ctx, "Vin", Xvin - 70, Yvin, 44, INK, "r", True)
    text(ctx, "S", B[0] - 50, B[1], 44, INK, "r", True)

    wire(ctx, [E, (Xsw, Ysw)], INK, LW)
    junction(ctx, Xsw, Ysw, 8)

    diode(ctx, (Xsw, Ygnd - 70), (Xsw, Ysw), INK, LW, size=32)
    wire(ctx, [(Xsw, Ygnd - 70), (Xsw, Ygnd)], INK, LW)
    text(ctx, "D", Xsw + 55, (Ysw + Ygnd - 70) / 2, 40, INK, "l", True)

    coil_pts = coil(ctx, (Xl0, Ysw), (Xl1, Ysw), INK, LW, n=4, bulge=1.15)
    wire(ctx, [(Xsw, Ysw), (Xl0, Ysw)], INK, LW)
    wire(ctx, [(Xl1, Ysw), (Xvout, Ysw)], INK, LW)
    junction(ctx, Xvout, Ysw, 8)
    text(ctx, "L", (Xl0 + Xl1) / 2, Ysw - 58, 40, INK, "c", True)
    text(ctx, "Vout", Xvout + 90, Ysw - 48, 36, INK, "l", True)

    capacitor(ctx, (Xvout, Ysw), (Xvout, Ygnd), INK, LW, plate=44, gap=12)
    text(ctx, "C", Xvout - 55, (Ysw + Ygnd) / 2, 40, INK, "r", True)

    wire(ctx, [(Xvout, Ysw), (Xr, Ysw)], INK, LW)
    junction(ctx, Xr, Ysw, 7)
    resistor(ctx, (Xr, Ysw), (Xr, Ygnd), INK, LW, zig=8, amp=16)
    text(ctx, "R", Xr + 58, (Ysw + Ygnd) / 2 - 18, 40, INK, "l", True)
    text(ctx, "load", Xr + 58, (Ysw + Ygnd) / 2 + 24, 28, hx("#6e7781"), "l", False)

    wire(ctx, [(Xvin, Ygnd), (Xr, Ygnd)], INK, LW)
    junction(ctx, Xsw, Ygnd, 7)
    junction(ctx, Xvout, Ygnd, 7)
    junction(ctx, Xr, Ygnd, 7)
    junction(ctx, Xvin, Ygnd, 7)
    gnd(ctx, Xvin, Ygnd, INK, LW)
    text(ctx, "GND", Xvin - 70, Ygnd + 50, 36, INK, "r", True)

    # Current paths
    path_on = (
        [(Xvin, Yvin), (C[0], Yvin)] + list(ce) +
        [(Xsw, Ysw)] + list(coil_pts) +
        [(Xvout, Ysw), (Xr, Ysw), (Xr, Ygnd)]
    )
    # diode anode@GND → cathode@SW, then wavy L to load
    path_off = (
        [(Xsw, Ygnd), (Xsw, Ysw)] + list(coil_pts) +
        [(Xvout, Ysw), (Xr, Ysw), (Xr, Ygnd)]
    )
    return dict(L=L, C=C, E=E, B=B, ce=ce, coil_pts=coil_pts,
                Xsw=Xsw, path_on=path_on, path_off=path_off)


def draw(ctx):
    S.col(ctx, (*BG, 1)); ctx.paint()
    draw_schematic(ctx)


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    draw(ctx)
    surf.write_to_png(str(OUT))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
