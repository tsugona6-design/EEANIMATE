#!/usr/bin/env python3
"""Simplified Royer push-pull topology: Q1/Q2 + center-tapped primary only."""
import cairo, math
from pathlib import Path
OUT=Path(__file__).resolve().parent/"royer_topology.png"

W, H = 1920, 1080
BG = (0xf6/255, 0xf8/255, 0xfa/255)
INK = (0.10, 0.12, 0.14, 1.0)
LW = 4.0

def col(ctx, c):
    ctx.set_source_rgba(*c)

def line(ctx, pts, c=INK, lw=LW):
    col(ctx, c); ctx.set_line_width(lw)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke()

def dot(ctx, x, y, r=8, c=INK):
    ctx.new_path(); ctx.arc(x, y, r, 0, 2*math.pi); col(ctx, c); ctx.fill()

def txt(ctx, s, x, y, size=40, c=INK, anchor='c', bold=False):
    ctx.select_font_face("Noto Sans CJK SC", cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    x0 = x - e.x_advance/2 if anchor == 'c' else (x if anchor == 'l' else x - e.x_advance)
    col(ctx, c); ctx.move_to(x0, y + size*0.35); ctx.show_text(s); ctx.new_path()

def coil_h(ctx, x0, y, x1, c=INK, lw=LW, n=4, amp=28):
    """Horizontal winding from x0 to x1, semicircles bulging upward."""
    pad = 10
    line(ctx, [(x0, y), (x0 + pad, y)], c, lw)
    line(ctx, [(x1 - pad, y), (x1, y)], c, lw)
    span = x1 - x0 - 2*pad
    col(ctx, c); ctx.set_line_width(lw)
    for i in range(n):
        cx = x0 + pad + span*(i + 0.5)/n
        r = span/n/2
        ctx.new_path(); ctx.arc(cx, y, r, math.pi, 2*math.pi); ctx.stroke()

def npn(ctx, x, y, s=1.0, c=INK, lw=LW, mirror=False):
    """Upright NPN: C top, E bottom (arrow out), B left (or right if mirror). Returns (C, E, B)."""
    ctx.save(); ctx.translate(x, y); ctx.scale(-s if mirror else s, s)
    l = lw / s
    line(ctx, [(-70, 0), (-22, 0)], c, l)
    line(ctx, [(-22, -38), (-22, 38)], c, l)
    line(ctx, [(-22, -20), (22, -55), (22, -78)], c, l)
    line(ctx, [(-22, 20), (22, 55), (22, 78)], c, l)
    ang = math.atan2(35, 44)
    ax, ay = 4, 32
    col(ctx, c)
    ctx.move_to(ax + 16*math.cos(ang), ay + 16*math.sin(ang))
    ctx.line_to(ax - 12*math.cos(ang - 0.5), ay - 12*math.sin(ang - 0.5))
    ctx.line_to(ax - 12*math.cos(ang + 0.5), ay - 12*math.sin(ang + 0.5))
    ctx.close_path(); ctx.fill()
    ctx.restore()
    sx = -1 if mirror else 1
    return (x + 22*s*sx, y - 78*s), (x + 22*s*sx, y + 78*s), (x - 70*s*sx, y)

def gnd(ctx, x, y, c=INK, lw=LW):
    line(ctx, [(x, y), (x, y + 18)], c, lw)
    for i, w in enumerate([44, 28, 12]):
        yy = y + 22 + i*12
        line(ctx, [(x - w/2, yy), (x + w/2, yy)], c, lw)

def draw(ctx):
    col(ctx, (*BG, 1)); ctx.paint()

    # Symmetric layout about vertical center Cx
    Cx = W / 2          # 960
    Yprim = 340         # primary winding height
    Qy = 620            # BJT centers
    YGND = 880
    s_bjt = 1.35
    c_off = 22 * s_bjt   # collector x offset from BJT center
    P_half = 220
    half = P_half + c_off  # so collectors sit directly under primary ends
    Q1x = Cx - half
    Q2x = Cx + half
    # Mirror Q2 BJT so bases face outward (true left-right visual symmetry)
    # Actually for schematic symmetry of the PUSH-PULL power path, both BJTs
    # usually face the same way (base left). For left-right symmetry of the
    # power topology, place Q1 left, Q2 right with identical orientation,
    # and primary centered above between them.

    # Primary: left end -- coil -- CT -- coil -- right end  (horizontal, centered)
    P_left = Cx - P_half
    P_right = Cx + P_half
    coil_h(ctx, P_left, Yprim, Cx - 20, n=4, amp=30)
    coil_h(ctx, Cx + 20, Yprim, P_right, n=4, amp=30)
    # CT gap bridge + dot
    line(ctx, [(Cx - 20, Yprim), (Cx + 20, Yprim)])
    dot(ctx, Cx, Yprim)

    # +Vin stub up from CT
    line(ctx, [(Cx, Yprim), (Cx, 160)])
    ctx.new_path(); ctx.arc(Cx, 160, 12, 0, 2*math.pi)
    col(ctx, INK); ctx.set_line_width(LW); ctx.stroke()
    txt(ctx, "+Vin", Cx, 110, 42, INK, 'c', True)

    # BJTs (identical upright NPN)
    C1, E1, B1 = npn(ctx, Q1x, Qy, s_bjt)
    C2, E2, B2 = npn(ctx, Q2x, Qy, s_bjt, mirror=True)
    txt(ctx, "Q1", Q1x - 120, Qy, 48, INK, 'r', True)
    txt(ctx, "Q2", Q2x + 120, Qy, 48, INK, 'l', True)

    # Collectors → primary ends (pure vertical, symmetric)
    line(ctx, [C1, (C1[0], Yprim)])
    line(ctx, [C2, (C2[0], Yprim)])
    dot(ctx, P_left, Yprim, 7)
    dot(ctx, P_right, Yprim, 7)

    # Emitters → GND (symmetric)
    line(ctx, [E1, (E1[0], YGND)])
    line(ctx, [E2, (E2[0], YGND)])
    line(ctx, [(E1[0], YGND), (E2[0], YGND)])
    gnd(ctx, E1[0], YGND)
    gnd(ctx, E2[0], YGND)
    txt(ctx, "GND", Cx, YGND + 80, 36, INK, 'c')

    # Tiny note that this is the simplified push-pull half
    txt(ctx, "Royer 推挽（简化）", Cx, 1010, 48, INK, 'c', True)

def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    draw(ctx)
    out = str(OUT)
    surf.write_to_png(out)
    print("wrote", out)

if __name__ == "__main__":
    main()
