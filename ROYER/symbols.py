#!/usr/bin/env python3
"""Reusable schematic symbols for power-electronics teaching animations."""
import cairo, math

INK = (0.10, 0.12, 0.14, 1.0)
LW = 5.0

def col(ctx, c):
    if len(c) == 3:
        ctx.set_source_rgb(*c)
    else:
        ctx.set_source_rgba(*c)

def hx(h, a=1.0):
    h = h.lstrip('#')
    return (int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255, a)

def wire(ctx, pts, c=INK, lw=LW, dash=None, off=0):
    if len(pts) < 2:
        return
    col(ctx, c); ctx.set_line_width(lw)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if dash:
        ctx.set_dash(dash, off)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke(); ctx.set_dash([])

def junction(ctx, x, y, r=8, c=INK):
    ctx.new_path(); ctx.arc(x, y, r, 0, 2*math.pi); col(ctx, c); ctx.fill()

def text(ctx, s, x, y, size=40, c=INK, anchor='c', bold=False):
    ctx.select_font_face("Noto Sans CJK SC", cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    x0 = x - e.x_advance/2 if anchor == 'c' else (x if anchor == 'l' else x - e.x_advance)
    col(ctx, c); ctx.move_to(x0, y + size*0.35); ctx.show_text(s); ctx.new_path()

def arrowhead(ctx, x, y, ang, size=18, c=INK):
    """Filled arrowhead at (x,y) pointing in direction ang (radians)."""
    col(ctx, c)
    ctx.move_to(x, y)
    ctx.line_to(x - size*math.cos(ang - 0.45), y - size*math.sin(ang - 0.45))
    ctx.line_to(x - size*math.cos(ang + 0.45), y - size*math.sin(ang + 0.45))
    ctx.close_path(); ctx.fill()

def current_flow(ctx, pts, c, t, speed=160, lw=9, reverse=False):
    """Dashed flowing current along a polyline (point order = conventional path).
    Particle travel offset flipped so inductor wavy flow matches Vin→CT→coil→BJT."""
    if len(pts) < 2:
        return
    if reverse:
        pts = list(reversed(pts))
    wire(ctx, pts, (c[0], c[1], c[2], 0.18), lw*2.6)
    # Particle travel: -t*speed (flipped again per user — waves were still reversed)
    wire(ctx, pts, c, lw, dash=[24, 18], off=(-t*speed if not reverse else +t*speed))

def resistor(ctx, p0, p1, c=INK, lw=LW, zig=6, amp=16):
    """Zigzag resistor between two points (axis-aligned preferred)."""
    x0, y0 = p0; x1, y1 = p1
    dx, dy = x1-x0, y1-y0
    L = math.hypot(dx, dy) or 1
    ux, uy = dx/L, dy/L
    px, py = -uy, ux  # perpendicular
    body = L*0.55
    s0 = (L-body)/2
    wire(ctx, [(x0, y0), (x0+ux*s0, y0+uy*s0)], c, lw)
    pts = [(x0+ux*s0, y0+uy*s0)]
    for i in range(zig):
        along = s0 + body*(i+0.5)/zig
        side = amp if i % 2 == 0 else -amp
        pts.append((x0+ux*along+px*side, y0+uy*along+py*side))
    pts.append((x0+ux*(s0+body), y0+uy*(s0+body)))
    wire(ctx, pts, c, lw)
    wire(ctx, [(x0+ux*(s0+body), y0+uy*(s0+body)), (x1, y1)], c, lw)

def coil_points(p0, p1, n=4, bulge=1.0, steps_per=10):
    """Polyline along coil semicircles from p0 to p1 (same geometry as coil())."""
    x0, y0 = p0; x1, y1 = p1
    dx, dy = x1-x0, y1-y0
    L = math.hypot(dx, dy) or 1
    ang = math.atan2(dy, dx)
    pad = min(10, L*0.08)
    span = L - 2*pad
    r = (span/n/2) * bulge
    pts = [(x0, y0), (x0+math.cos(ang)*pad, y0+math.sin(ang)*pad)]
    for i in range(n):
        cx = x0 + math.cos(ang)*(pad + span*(i+0.5)/n)
        cy = y0 + math.sin(ang)*(pad + span*(i+0.5)/n)
        # Match coil() cairo arc(pi → 2pi): upper semicircle in screen coords (+y down)
        for k in range(steps_per+1):
            a = math.pi + math.pi*k/steps_per  # pi → 2pi (through 3pi/2 = up)
            lx, ly = r*math.cos(a), r*math.sin(a)
            # rotate by ang and translate
            wx = cx + lx*math.cos(ang) - ly*math.sin(ang)
            wy = cy + lx*math.sin(ang) + ly*math.cos(ang)
            pts.append((wx, wy))
    pts.append((x1-math.cos(ang)*pad, y1-math.sin(ang)*pad))
    pts.append((x1, y1))
    return pts

def coil(ctx, p0, p1, c=INK, lw=LW, n=4, bulge=1.0):
    """Inductor coil between p0 and p1; semicircles on the 'left' when going p0→p1.
    Returns the wavy polyline (same as coil_points)."""
    pts = coil_points(p0, p1, n=n, bulge=bulge)
    # draw: end stubs + arcs (match prior look)
    x0, y0 = p0; x1, y1 = p1
    dx, dy = x1-x0, y1-y0
    L = math.hypot(dx, dy) or 1
    ang = math.atan2(dy, dx)
    pad = min(10, L*0.08)
    wire(ctx, [(x0, y0), (x0+math.cos(ang)*pad, y0+math.sin(ang)*pad)], c, lw)
    wire(ctx, [(x1-math.cos(ang)*pad, y1-math.sin(ang)*pad), (x1, y1)], c, lw)
    span = L - 2*pad
    r = span/n/2
    col(ctx, c); ctx.set_line_width(lw)
    for i in range(n):
        cx = x0 + math.cos(ang)*(pad + span*(i+0.5)/n)
        cy = y0 + math.sin(ang)*(pad + span*(i+0.5)/n)
        ctx.new_path()
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(ang)
        ctx.arc(0, 0, r*bulge, math.pi, 2*math.pi)
        ctx.restore(); ctx.stroke()
    return pts

def coil_h(ctx, x0, y, x1, c=INK, lw=LW, n=4):
    return coil(ctx, (x0, y), (x1, y), c, lw, n)

def transformer_core(ctx, x, y0, y1, c=INK, lw=4.5, gap=12):
    wire(ctx, [(x-gap/2, y0), (x-gap/2, y1)], c, lw)
    wire(ctx, [(x+gap/2, y0), (x+gap/2, y1)], c, lw)

def gnd(ctx, x, y, c=INK, lw=LW):
    """Ground symbol hanging down from (x,y)."""
    wire(ctx, [(x, y), (x, y+16)], c, lw)
    for i, w in enumerate([40, 26, 12]):
        wire(ctx, [(x-w/2, y+20+i*11), (x+w/2, y+20+i*11)], c, lw)

def npn(ctx, x, y, s=1.0, c=INK, lw=LW, mirror=False, on=False, oncol=None):
    """Upright NPN BJT. Collector top, emitter bottom, base left (or right if mirror).

    Emitter arrow is drawn in world space on the emitter arm, pointing toward
    the emitter terminal (out of the device), so mirroring stays correct.

    Returns world (collector, emitter, base).
    """
    oc = oncol or hx('#1a7f37')
    cc = oc if on else c
    sx = -1.0 if mirror else 1.0

    def W(px, py):
        return (x + px*s*sx, y + py*s)

    if on:
        ctx.new_path(); ctx.arc(x, y, 72*s, 0, 2*math.pi)
        col(ctx, (oc[0], oc[1], oc[2], 0.14)); ctx.fill()

    # Base lead + bar
    wire(ctx, [W(-70, 0), W(-22, 0)], cc, lw)
    wire(ctx, [W(-22, -38), W(-22, 38)], cc, lw)
    # Collector arm
    wire(ctx, [W(-22, -20), W(22, -55), W(22, -78)], cc, lw)
    # Emitter arm
    wire(ctx, [W(-22, 20), W(22, 55), W(22, 78)], cc, lw)

    # Arrow flush on emitter diagonal, pointing toward emitter terminal
    ax0, ay0 = W(-22, 20)
    ax1, ay1 = W(22, 55)
    ang = math.atan2(ay1-ay0, ax1-ax0)
    tip_x = ax0 + 0.88*(ax1-ax0)
    tip_y = ay0 + 0.88*(ay1-ay0)
    arrowhead(ctx, tip_x, tip_y, ang, size=16*s, c=cc)

    C, E, B = W(22, -78), W(22, 78), W(-70, 0)
    # Current path through slanted collector/emitter arms (not through body center):
    # C stub → collector diagonal → bar → emitter diagonal → E stub
    ce_path = [
        C,
        W(22, -55),
        W(-22, -20),
        W(-22, 20),
        W(22, 55),
        E,
    ]
    return C, E, B, ce_path

def flux_ring(ctx, cx, cy, ang, radius=55, c=INK, lw=7, cw=True, label=None):
    """Circular flux-direction arrow. ang = tip angle (radians).
    cw=True → tip travels clockwise on screen (cairo y-down); arrowhead matches.
    """
    span = 1.55 * math.pi
    col(ctx, c); ctx.set_line_width(lw)
    ctx.new_path()
    if cw:
        # clockwise on screen: math angle decreasing → arc_negative
        ctx.arc_negative(cx, cy, radius, ang + span, ang)
        tang = ang - math.pi/2
    else:
        ctx.arc(cx, cy, radius, ang - span, ang)
        tang = ang + math.pi/2
    ctx.stroke()
    tip_x = cx + radius*math.cos(ang)
    tip_y = cy + radius*math.sin(ang)
    arrowhead(ctx, tip_x, tip_y, tang, size=20, c=c)
    if label:
        text(ctx, label, cx, cy - radius - 34, 30, c, 'c', True)

def bar_meter(ctx, x, y_bottom, height, fill_h, c, track=hx('#d0d7de'), label=None, max_h=100):
    """Vertical meter bar. y_bottom is bottom of track; fill_h in px upward."""
    bw = 20
    fill_h = max(0, min(fill_h, max_h))
    col(ctx, track); ctx.rectangle(x-bw/2, y_bottom-max_h, bw, max_h); ctx.fill()
    if fill_h > 1:
        col(ctx, c); ctx.rectangle(x-bw/2, y_bottom-fill_h, bw, fill_h); ctx.fill()
    wire(ctx, [(x-bw/2-2, y_bottom-max_h),(x+bw/2+2, y_bottom-max_h),
               (x+bw/2+2, y_bottom),(x-bw/2-2, y_bottom),(x-bw/2-2, y_bottom-max_h)], INK, 2.5)
    if label:
        text(ctx, label, x, y_bottom+26, 26, c, 'c', True)
