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


def layout(compact=False):
    """Shared geometry. compact=True: left of wave panel, roomy Vin/GND margins."""
    if compact:
        # Fit left schematic panel (~940 px wide)
        Sx, Sy = 400, 320
        s_bjt = 1.05
        Ysw, Ygnd = 520, 820
        Xvout = 680
        Xvin, Yvin = 160, 160
        Xr_off = 140
    else:
        Sx, Sy = 560, 360
        s_bjt = 1.25
        Ysw, Ygnd = 540, 880
        Xvout = 1100
        Xvin, Yvin = 220, 150
        Xr_off = 200
    Xsw = Sx + 22 * s_bjt
    span = Xvout - Xsw
    Xl0 = Xsw + span * 0.30
    Xl1 = Xsw + span * 0.70
    Xr = Xvout + Xr_off
    return dict(Sx=Sx, Sy=Sy, s_bjt=s_bjt, Ysw=Ysw, Ygnd=Ygnd,
                Xvout=Xvout, Xvin=Xvin, Yvin=Yvin, Xsw=Xsw,
                Xl0=Xl0, Xl1=Xl1, Xr=Xr)


def draw_schematic(ctx, on=False, oncol=None, compact=False):
    L = layout(compact=compact)
    Sx, Sy, s = L['Sx'], L['Sy'], L['s_bjt']
    Ysw, Ygnd = L['Ysw'], L['Ygnd']
    Xvout, Xvin, Yvin = L['Xvout'], L['Xvin'], L['Yvin']
    Xl0, Xl1, Xr = L['Xl0'], L['Xl1'], L['Xr']

    C, E, B, ce = npn(ctx, Sx, Sy, s=s, c=INK, lw=LW, on=on, oncol=oncol)
    Xsw = E[0]

    wire(ctx, [(Xvin, Yvin), (C[0], Yvin), C], INK, LW)
    junction(ctx, C[0], Yvin, 7)
    junction(ctx, Xvin, Yvin, 7)
    # Labels to the RIGHT of terminals so left crop keeps Vin/GND visible
    text(ctx, "Vin", Xvin + 48, Yvin - 34, 34, INK, "l", True)
    text(ctx, "b", B[0] - 42, B[1] + 48, 36, INK, "r", True)

    wire(ctx, [E, (Xsw, Ysw)], INK, LW)
    junction(ctx, Xsw, Ysw, 8)

    diode(ctx, (Xsw, Ygnd - 65), (Xsw, Ysw), INK, LW, size=28)
    wire(ctx, [(Xsw, Ygnd - 65), (Xsw, Ygnd)], INK, LW)
    text(ctx, "D", Xsw + 48, (Ysw + Ygnd - 65) / 2, 34, INK, "l", True)

    coil_pts = coil(ctx, (Xl0, Ysw), (Xl1, Ysw), INK, LW, n=4, bulge=1.15)
    wire(ctx, [(Xsw, Ysw), (Xl0, Ysw)], INK, LW)
    wire(ctx, [(Xl1, Ysw), (Xvout, Ysw)], INK, LW)
    junction(ctx, Xvout, Ysw, 8)
    text(ctx, "L", (Xl0 + Xl1) / 2, Ysw - 48, 34, INK, "c", True)

    capacitor(ctx, (Xvout, Ysw), (Xvout, Ygnd), INK, LW, plate=38, gap=11)
    text(ctx, "C", Xvout - 44, (Ysw + Ygnd) / 2, 34, INK, "r", True)

    wire(ctx, [(Xvout, Ysw), (Xr, Ysw)], INK, LW)
    junction(ctx, Xr, Ysw, 7)
    r_pts = resistor(ctx, (Xr, Ysw), (Xr, Ygnd), INK, LW, zig=8, amp=20)
    text(ctx, "R", Xr + 48, (Ysw + Ygnd) / 2 - 14, 34, INK, "l", True)
    text(ctx, "load", Xr + 48, (Ysw + Ygnd) / 2 + 18, 24, hx("#6e7781"), "l", False)

    wire(ctx, [(Xvin, Ygnd), (Xr, Ygnd)], INK, LW)
    junction(ctx, Xsw, Ygnd, 7)
    junction(ctx, Xvout, Ygnd, 7)
    junction(ctx, Xr, Ygnd, 7)
    junction(ctx, Xvin, Ygnd, 7)
    gnd(ctx, Xvin, Ygnd, INK, LW)
    text(ctx, "GND", Xvin + 48, Ygnd + 46, 30, INK, "l", True)

    # ON: Vin → S → L → R zigzag → along GND to Vin/GND
    path_on = (
        [(Xvin, Yvin), (C[0], Yvin)] + list(ce) +
        [(Xsw, Ysw)] + list(coil_pts) +
        [(Xvout, Ysw)] + list(r_pts) +
        [(Xvin, Ygnd)]
    )
    # OFF loop: up D → L → R zig → GND bus → back to D
    path_off = (
        [(Xsw, Ygnd), (Xsw, Ysw)] + list(coil_pts) +
        [(Xvout, Ysw)] + list(r_pts) +
        [(Xvin, Ygnd), (Xsw, Ygnd)]
    )
    # Sampling nodes for animation probes (on schematic, not on plots)
    probes = {
        'Vb':  (B[0], B[1]),                               # BJT base
        'iL':  (Xl1, Ysw),                                 # right end of L
        'Vsw': (Xsw, Ysw),
        'Vout': (Xvout, Ysw),
    }
    return dict(L=L, C=C, E=E, B=B, ce=ce, coil_pts=coil_pts, r_pts=r_pts,
                Xsw=Xsw, path_on=path_on, path_off=path_off, probes=probes)


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
