#!/usr/bin/env python3
"""Boost BJT topology — Vin—L—SW—D—Vout / C∥R; BJT SW→GND labeled b."""
import cairo
from pathlib import Path
import symbols as S
from symbols import hx, wire, junction, text, npn, gnd, coil, diode, capacitor, resistor

OUT = Path(__file__).resolve().parent / "boost_topology.png"
W, H = 1920, 1080
BG = (0xF6 / 255, 0xF8 / 255, 0xFA / 255)
INK = hx("#1f2328")
LW = 5.0


def layout(compact=False):
    """Boost geometry. compact=True fits left schematic panel (~900 px)."""
    if compact:
        Xvin = 140
        Ysw, Ygnd = 360, 800
        Xl0, Xl1 = 260, 430
        Xsw = 500
        Xvout = 720
        Xr_off = 130
        s_bjt = 1.0
    else:
        Xvin = 200
        Ysw, Ygnd = 400, 880
        Xl0, Xl1 = 380, 620
        Xsw = 760
        Xvout = 1120
        Xr_off = 200
        s_bjt = 1.25
    # Vin rail height = L / SW rail (straight horizontal)
    Yvin = Ysw
    Xr = Xvout + Xr_off
    Sx = Xsw - 22 * s_bjt
    # BJT lower toward vertical center between SW and GND
    Sy = Ysw + 0.58 * (Ygnd - Ysw)
    return dict(Sx=Sx, Sy=Sy, s_bjt=s_bjt, Ysw=Ysw, Ygnd=Ygnd,
                Xvout=Xvout, Xvin=Xvin, Yvin=Yvin, Xsw=Xsw,
                Xl0=Xl0, Xl1=Xl1, Xr=Xr)


def draw_schematic(ctx, on=False, oncol=None, compact=False):
    L = layout(compact=compact)
    Sx, Sy, s = L['Sx'], L['Sy'], L['s_bjt']
    Ysw, Ygnd = L['Ysw'], L['Ygnd']
    Xvout, Xvin, Yvin = L['Xvout'], L['Xvin'], L['Yvin']
    Xl0, Xl1, Xr, Xsw = L['Xl0'], L['Xl1'], L['Xr'], L['Xsw']

    C, E, B, ce = npn(ctx, Sx, Sy, s=s, c=INK, lw=LW, on=on, oncol=oncol)
    Xsw = C[0]

    # Vin —— straight horizontal into L (aligned with L / SW rail)
    wire(ctx, [(Xvin, Ysw), (Xl0, Ysw)], INK, LW)
    junction(ctx, Xvin, Ysw, 7)
    text(ctx, "Vin", Xvin + 48, Ysw - 40, 34, INK, "l", True)

    coil_pts = coil(ctx, (Xl0, Ysw), (Xl1, Ysw), INK, LW, n=4, bulge=1.15)
    wire(ctx, [(Xl1, Ysw), (Xsw, Ysw)], INK, LW)
    junction(ctx, Xsw, Ysw, 8)
    text(ctx, "L", (Xl0 + Xl1) / 2, Ysw - 52, 36, INK, "c", True)

    # BJT SW → GND (lowered body)
    wire(ctx, [(Xsw, Ysw), C], INK, LW)
    wire(ctx, [E, (E[0], Ygnd)], INK, LW)
    junction(ctx, E[0], Ygnd, 7)
    text(ctx, "b", B[0] - 42, B[1] + 48, 36, INK, "r", True)

    # Diode SW → Vout
    diode(ctx, (Xsw, Ysw), (Xvout, Ysw), INK, LW, size=30)
    junction(ctx, Xvout, Ysw, 8)
    text(ctx, "D", (Xsw + Xvout) / 2, Ysw + 52, 34, INK, "c", True)
    text(ctx, "Vout", Xvout + 64, Ysw - 40, 32, INK, "l", True)

    capacitor(ctx, (Xvout, Ysw), (Xvout, Ygnd), INK, LW, plate=40, gap=12)
    text(ctx, "C", Xvout - 48, (Ysw + Ygnd) / 2, 36, INK, "r", True)

    wire(ctx, [(Xvout, Ysw), (Xr, Ysw)], INK, LW)
    junction(ctx, Xr, Ysw, 7)
    r_pts = resistor(ctx, (Xr, Ysw), (Xr, Ygnd), INK, LW, zig=8, amp=18)
    text(ctx, "R", Xr + 50, (Ysw + Ygnd) / 2 - 14, 34, INK, "l", True)
    text(ctx, "load", Xr + 50, (Ysw + Ygnd) / 2 + 18, 24, hx("#6e7781"), "l", False)

    wire(ctx, [(Xvin, Ygnd), (Xr, Ygnd)], INK, LW)
    junction(ctx, Xvin, Ygnd, 7)
    junction(ctx, Xvout, Ygnd, 7)
    junction(ctx, Xr, Ygnd, 7)
    gnd(ctx, Xvin, Ygnd, INK, LW)
    text(ctx, "GND", Xvin + 48, Ygnd + 46, 30, INK, "l", True)

    # ON: Vin → L → BJT → GND
    path_on = (
        [(Xvin, Ysw)] + list(coil_pts) + [(Xsw, Ysw)] + list(ce) +
        [(E[0], Ygnd), (Xvin, Ygnd)]
    )
    # ON secondary: capacitor supplies load (C top → R zig → GND → back under C)
    path_on_cap = (
        [(Xvout, Ysw)] + list(r_pts) + [(Xvout, Ygnd), (Xvout, Ysw)]
    )
    # OFF: Vin → L → D → load R zig → GND
    path_off = (
        [(Xvin, Ysw)] + list(coil_pts) + [(Xsw, Ysw), (Xvout, Ysw)] +
        list(r_pts) + [(Xvin, Ygnd)]
    )
    probes = {
        'Vb': (B[0], B[1]),
        'iL': (Xl1, Ysw),
        'Vsw': (Xsw, Ysw),
        'Vout': (Xvout, Ysw),
    }
    return dict(L=L, C=C, E=E, B=B, ce=ce, coil_pts=coil_pts, r_pts=r_pts,
                Xsw=Xsw, path_on=path_on, path_on_cap=path_on_cap,
                path_off=path_off, probes=probes)


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
