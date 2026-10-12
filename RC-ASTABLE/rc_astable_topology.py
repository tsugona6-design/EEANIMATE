#!/usr/bin/env python3
"""Simplified RC astable — C1/C2 same height, diagonal coupling to opposite bases."""
import cairo
from pathlib import Path
import symbols as S
from symbols import hx, wire, junction, text, npn, gnd, capacitor, resistor

OUT = Path(__file__).resolve().parent / "rc_astable_topology.png"
W, H = 1920, 1080
BG = (0xF6 / 255, 0xF8 / 255, 0xFA / 255)
INK = hx("#1f2328")
G2 = hx("#6e7781")
LW = 5.0


def draw(ctx):
    S.col(ctx, (*BG, 1))
    ctx.paint()

    Cx = W / 2
    half = 340
    Q1x, Q2x = Cx - half, Cx + half
    s = 1.3
    Qy = 600
    Yvin, Ygnd = 130, 900
    Ycoll = 300

    C1, E1, B1, _ = npn(ctx, Q1x, Qy, s=s, c=INK, lw=LW, mirror=True)
    C2, E2, B2, _ = npn(ctx, Q2x, Qy, s=s, c=INK, lw=LW, mirror=False)
    Xc1, Xc2 = C1[0], C2[0]

    text(ctx, "Q1", Q1x - 100, Qy - 10, 42, INK, "r", True)
    text(ctx, "Q2", Q2x + 100, Qy - 10, 42, INK, "l", True)

    wire(ctx, [(Xc1, Yvin), (Xc2, Yvin)], INK, LW)
    text(ctx, "Vin", Cx, Yvin - 44, 40, INK, "c", True)

    resistor(ctx, (Xc1, Yvin), (Xc1, Ycoll), INK, LW, zig=5, amp=13)
    resistor(ctx, (Xc2, Yvin), (Xc2, Ycoll), INK, LW, zig=5, amp=13)
    text(ctx, "Rc", Xc1 - 44, (Yvin + Ycoll) / 2, 28, G2, "r", False)
    text(ctx, "Rc", Xc2 + 44, (Yvin + Ycoll) / 2, 28, G2, "l", False)
    wire(ctx, [(Xc1, Ycoll), C1], INK, LW)
    wire(ctx, [(Xc2, Ycoll), C2], INK, LW)
    junction(ctx, Xc1, Ycoll, 7)
    junction(ctx, Xc2, Ycoll, 7)

    # C1 and C2 at the same height; diagonal wires to opposite bases
    Yh = Ycoll + 100
    cap_span = 110

    wire(ctx, [(Xc1, Ycoll), (Xc1, Yh)], INK, LW)
    capacitor(ctx, (Xc1, Yh), (Xc1 + cap_span, Yh), INK, LW, plate=36, gap=11)
    wire(ctx, [(Xc1 + cap_span, Yh), B2], INK, LW)  # diagonal → Q2 base
    text(ctx, "C1", Xc1 + cap_span / 2, Yh - 42, 32, INK, "c", True)

    wire(ctx, [(Xc2, Ycoll), (Xc2, Yh)], INK, LW)
    capacitor(ctx, (Xc2, Yh), (Xc2 - cap_span, Yh), INK, LW, plate=36, gap=11)
    wire(ctx, [(Xc2 - cap_span, Yh), B1], INK, LW)  # diagonal → Q1 base
    text(ctx, "C2", Xc2 - cap_span / 2, Yh - 42, 32, INK, "c", True)

    resistor(ctx, E1, (E1[0], Ygnd - 40), INK, LW, zig=5, amp=13)
    resistor(ctx, E2, (E2[0], Ygnd - 40), INK, LW, zig=5, amp=13)
    wire(ctx, [(E1[0], Ygnd - 40), (E1[0], Ygnd)], INK, LW)
    wire(ctx, [(E2[0], Ygnd - 40), (E2[0], Ygnd)], INK, LW)
    text(ctx, "Re", E1[0] - 46, (E1[1] + Ygnd) / 2, 30, INK, "r", True)
    text(ctx, "Re", E2[0] + 46, (E2[1] + Ygnd) / 2, 30, INK, "l", True)

    wire(ctx, [(E1[0], Ygnd), (E2[0], Ygnd)], INK, LW)
    junction(ctx, E1[0], Ygnd, 7)
    junction(ctx, E2[0], Ygnd, 7)
    gnd(ctx, Cx, Ygnd, INK, LW)
    text(ctx, "GND", Cx + 72, Ygnd + 52, 30, INK, "l", False)


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    draw(ctx)
    surf.write_to_png(str(OUT))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
