#!/usr/bin/env python3
"""RC astable — KiCad v2, paths + bars + 2×2 waveforms (slower pace)."""
import cairo, math, subprocess
from pathlib import Path
from PIL import Image
import numpy as np
import symbols as S
from symbols import hx, text, current_flow, wire
from kicad_map import mm

OUT_DIR = Path(__file__).resolve().parent
OUT_MP4 = OUT_DIR / "rc_astable_animation.mp4"
BG_PNG = OUT_DIR / "kicad_bg.png"

W, H = 1920, 1080
FPS, DUR = 60, 30.0   # slower overall

C_BLUE = hx("#0969da")
C_GREEN = hx("#1a7f37")
C_PURPLE = hx("#8250df")
C_YELLOW = hx("#bf8700")
C_BAR = hx("#8250df")
C_NEG = hx("#cf222e")
C_VB = hx("#bf8700")
INK = hx("#1f2328")
G2 = hx("#6e7781")
TRACK = hx("#e6edf2")
PAN = hx("#ffffff")
DIV = hx("#e6edf2")

T_RUN0 = 2.0
HALF = 2.0
OVERLAP = 0.08          # brief both-slightly-on flip window (frac of half)
# Normalized to VCC=5V → 1.0 (physics from user)
VCC = 1.00              # 5 V
VSAT = 0.04             # ~0.2 V
VBE = 0.14              # ~0.7 V
VCAP0 = VCC - VBE       # ~4.3/5 — C voltage just before commutation
VB_SPIKE = VSAT - VCAP0 # ~−4.1/5 when collector snaps to sat


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def vb_recover(u):
    """Phase B: base recovers from spike toward VBE via Rb→C (IR≈(VCC−Vb)/R into C)."""
    u = clamp(u)
    # exponential; almost all charging current into C until BE forwards (~VBE)
    return VB_SPIKE + (VBE - VB_SPIKE) * (1.0 - math.exp(-u / 0.34))


def signals(t):
    """Phase A commutation + Phase B hold/recover; brief overlap conduction."""
    if t < 0.8:
        u = ease(t / 0.8)
        return dict(vc1=0.15*u, vc2=0.15*u, vb1=0.0, vb2=0.0,
                    active=False, q1=False, q2=False, overlap=False,
                    q1_lvl=0.0, q2_lvl=0.0, frac=0.0, spike=False)
    if t < T_RUN0:
        u = ease((t - 0.8) / (T_RUN0 - 0.8))
        return dict(vc1=VSAT, vc2=0.3 + 0.7*u, vb1=VBE*u, vb2=0.05,
                    active=True, q1=True, q2=False, overlap=False,
                    q1_lvl=u, q2_lvl=0.0, frac=0.5, spike=False)

    tau = t - T_RUN0
    n = int(tau // HALF)
    frac = (tau % HALF) / HALF
    q1_half = (n % 2 == 0)   # this half: Q1 is the one that just turned / is ON

    if frac < OVERLAP:
        # Phase A: flip — incoming collector falls, outgoing rises; C holds → Vb spikes
        u = ease(frac / OVERLAP)
        if q1_half:
            # Q1 turning on, Q2 turning off
            vc1 = VCC * (1 - u) + VSAT * u
            vc2 = VSAT * (1 - u) + VCC * u
            vb1 = VBE * u                    # Q1 base drive rising
            vb2 = vc1 - VCAP0                # C1 holds → VB2 → spike (~−4.1)
            q1_lvl, q2_lvl = u, 1.0 - u      # overlap conduction
        else:
            vc2 = VCC * (1 - u) + VSAT * u
            vc1 = VSAT * (1 - u) + VCC * u
            vb2 = VBE * u
            vb1 = vc2 - VCAP0
            q1_lvl, q2_lvl = 1.0 - u, u
        return dict(vc1=vc1, vc2=vc2, vb1=vb1, vb2=vb2,
                    active=True, q1=q1_half, q2=not q1_half, overlap=True,
                    q1_lvl=q1_lvl, q2_lvl=q2_lvl, frac=frac, spike=True)

    # Phase B: hold — ON sat, OFF open; timing base recovers via Rb→C→ON
    u_rec = (frac - OVERLAP) / max(1.0 - OVERLAP, 1e-6)
    if q1_half:
        vc1, vc2 = VSAT, VCC
        vb1 = VBE
        vb2 = vb_recover(u_rec)
        q1_lvl, q2_lvl = 1.0, 0.0
    else:
        vc2, vc1 = VSAT, VCC
        vb2 = VBE
        vb1 = vb_recover(u_rec)
        q1_lvl, q2_lvl = 0.0, 1.0
    return dict(vc1=vc1, vc2=vc2, vb1=vb1, vb2=vb2,
                active=True, q1=q1_half, q2=not q1_half, overlap=False,
                q1_lvl=q1_lvl, q2_lvl=q2_lvl, frac=frac, spike=False)


def cap_voltages(t):
    """True capacitor voltages (coll plate − base plate), scaled to VCC=1.

    Purple UP = +, red DOWN = −. At commutation C voltage is continuous (~+0.86);
    the *other* C jumps + as its collector rises. During recover V_C = VSAT − Vb
    falls (may go slightly negative near VBE).
    """
    s = signals(t)
    return s["vc1"] - s["vb2"], s["vc2"] - s["vb1"]


# Wave panel (right)
PAD = 28
WAVE_X0 = 1080
WAVE_W = W - WAVE_X0 - PAD
WAVE_TOP = 100
WAVE_BOT = H - 90
CELL_W = WAVE_W / 2
CELL_H = (WAVE_BOT - WAVE_TOP) / 2


def build_paths():
    VCC = mm(91.44, 50.80)
    GND = mm(91.44, 87.63)
    X1, X2 = 77.47, 107.95
    Yv, Ym, Yb, Ye, Yg = 50.80, 67.31, 74.93, 80.01, 87.63

    Cj1, Cj2 = mm(X1, Ym), mm(X2, Ym)
    top1, top2 = mm(X1, Yv), mm(X2, Yv)
    E1, E2 = mm(X1, Ye), mm(X2, Ye)
    g1, g2 = mm(X1, Yg), mm(X2, Yg)
    B1, B2 = mm(83.82, Yb), mm(101.60, Yb)
    N2, N3 = mm(87.63, Ym), mm(95.25, Ym)
    R2top, R3top = mm(87.63, Yv), mm(95.25, Yv)
    C1_L, C1_R = mm(83.06, Ym), mm(86.36, Ym)
    C2_L, C2_R = mm(97.79, Ym), mm(101.09, Ym)
    d_to_B2_a, d_to_B2_b = mm(88.90, Ym), mm(96.52, Yb)
    d_from_B1_a, d_from_B1_b = mm(87.63, Yb), mm(95.25, Ym)

    path_q1 = [VCC, top1, Cj1, mm(X1, 72.39), E1, g1, GND]
    path_q2 = [VCC, top2, Cj2, mm(X2, 72.39), E2, g2, GND]
    path_c1_via_r2 = [VCC, R2top, N2, C1_R, C1_L, Cj1, mm(X1, 72.39), E1, g1, GND]
    path_c2_via_r3 = [VCC, R3top, N3, C2_L, C2_R, Cj2, mm(X2, 72.39), E2, g2, GND]
    q1_be = [mm(79.50, 74.93), mm(79.50, 75.55), mm(79.10, 75.90),
             mm(78.55, 76.35), mm(78.00, 76.85), mm(77.47, 77.47),
             mm(77.47, 80.01), g1, GND]
    q2_be = [mm(105.90, 74.93), mm(105.90, 75.55), mm(106.30, 75.90),
             mm(106.85, 76.35), mm(107.40, 76.85), mm(107.95, 77.47),
             mm(107.95, 80.01), g2, GND]
    path_c2_q1on = [VCC, top2, Cj2, C2_R, C2_L, N3, d_from_B1_b, d_from_B1_a, B1] + q1_be
    path_c1_q2on = [VCC, top1, Cj1, C1_L, C1_R, N2, d_to_B2_a, d_to_B2_b, B2] + q2_be
    spike_q1 = [B2, d_to_B2_b, d_to_B2_a, N2, C1_R, C1_L, Cj1, mm(X1, 72.39), E1, g1, GND]
    spike_q2 = [B1, d_from_B1_a, d_from_B1_b, N3, C2_L, C2_R, Cj2, mm(X2, 72.39), E2, g2, GND]

    path_base_q1 = [
        VCC, R3top, N3, d_from_B1_b, d_from_B1_a, B1,
        mm(79.50, 74.93), mm(79.50, 75.55),
        mm(79.10, 75.90), mm(78.55, 76.35),
        mm(78.00, 76.85), mm(77.47, 77.47),
        mm(77.47, 80.01), g1, GND,
    ]
    path_base_q2 = [
        VCC, R2top, N2, d_to_B2_a, d_to_B2_b, B2,
        mm(105.90, 74.93), mm(105.90, 75.55),
        mm(106.30, 75.90), mm(106.85, 76.35),
        mm(107.40, 76.85), mm(107.95, 77.47),
        mm(107.95, 80.01), g2, GND,
    ]

    # Outside schematic: left of left / right of schematic (before waves)
    q1x = mm(78.74, 74.93)[0]
    q2x = mm(106.68, 74.93)[0]
    midy = mm(91.44, 69.2)[1]
    bar_c1 = (max(28, q1x - 110), midy)
    bar_c2 = (min(WAVE_X0 - 50, q2x + 110), midy)

    return dict(
        path_q1=path_q1, path_q2=path_q2,
        path_c1_via_r2=path_c1_via_r2, path_c2_via_r3=path_c2_via_r3,
        path_c2_q1on=path_c2_q1on, path_c1_q2on=path_c1_q2on,
        spike_q1=spike_q1, spike_q2=spike_q2,
        path_base_q1=path_base_q1, path_base_q2=path_base_q2,
        Q1=mm(78.74, 74.93), Q2=mm(106.68, 74.93),
        bar_c1=bar_c1, bar_c2=bar_c2,
    )


PATHS = build_paths()
BG_ARR = None


def load_bg():
    im = Image.open(BG_PNG).convert("RGB")
    assert im.size == (W, H)
    arr = np.array(im)
    bgra = np.empty((H, W, 4), dtype=np.uint8)
    bgra[:, :, 0] = arr[:, :, 2]
    bgra[:, :, 1] = arr[:, :, 1]
    bgra[:, :, 2] = arr[:, :, 0]
    bgra[:, :, 3] = 255
    return bgra


def blit_bg(ctx):
    global BG_ARR
    if BG_ARR is None:
        BG_ARR = load_bg()
    surf = cairo.ImageSurface.create_for_data(BG_ARR, cairo.FORMAT_ARGB32, W, H)
    ctx.set_source_surface(surf, 0, 0)
    ctx.paint()


def bipolar_bar(ctx, cx, cy, v, label, half_h=64, bw=16, vmin=-1.0, vmax=1.0):
    top, bot = cy - half_h, cy + half_h
    S.col(ctx, TRACK)
    ctx.rectangle(cx - bw / 2, top, bw, 2 * half_h)
    ctx.fill()
    wire(ctx, [(cx - bw / 2 - 4, cy), (cx + bw / 2 + 4, cy)], hx("#afb8c1"), 2)
    wire(ctx, [(cx - bw / 2, top), (cx + bw / 2, top),
               (cx + bw / 2, bot), (cx - bw / 2, bot), (cx - bw / 2, top)], INK, 2.0)
    v = max(vmin, min(vmax, v))
    if v >= 0:
        fh = (v / vmax) * half_h if vmax else 0
        if fh > 1:
            S.col(ctx, C_BAR)
            ctx.rectangle(cx - bw / 2 + 1, cy - fh, bw - 2, fh)
            ctx.fill()
    else:
        fh = (v / vmin) * half_h if vmin else 0
        if fh > 1:
            S.col(ctx, C_NEG)
            ctx.rectangle(cx - bw / 2 + 1, cy, bw - 2, fh)
            ctx.fill()
    text(ctx, label, cx, top - 16, 18, C_BAR, "c", True)
    text(ctx, "+", cx + bw / 2 + 10, top + 6, 14, G2, "l", False)
    text(ctx, "−", cx + bw / 2 + 10, bot - 2, 14, G2, "l", False)


def cell_rect(col, row):
    return (WAVE_X0 + col * CELL_W, WAVE_TOP + row * CELL_H, CELL_W, CELL_H)


def plot_wave(ctx, x, y, w, h, f, c, t0, t1, zero=0.15, lw=3.0, n=360,
              v_scale=1.0, draw_axes=True, neg_color=None):
    """If neg_color set, segments with f(u)<0 are drawn in neg_color (else c)."""
    ax, ay, aw, ah = x + 48, y + 36, w - 62, h - 52
    zline = ay + ah * (1 - zero)
    if draw_axes:
        wire(ctx, [(ax, zline), (ax + aw, zline)], hx("#d0d7de"), 1.6)
        wire(ctx, [(ax, ay), (ax, ay + ah)], hx("#d0d7de"), 1.6)
    span = ah * 0.72 * v_scale
    vals, pts = [], []
    for i in range(n):
        u = t0 + (t1 - t0) * i / (n - 1)
        v = f(u)
        vals.append(v)
        pts.append((ax + aw * i / (n - 1), zline - v * span))
    if len(pts) < 2:
        return
    if neg_color is None:
        wire(ctx, pts, c, lw)
        return
    # Split into runs by sign; interpolate zero-crossings for clean joins
    def lerp_pt(i0, i1, v0, v1):
        if abs(v1 - v0) < 1e-12:
            t = 0.5
        else:
            t = (0.0 - v0) / (v1 - v0)
        t = max(0.0, min(1.0, t))
        x0, y0 = pts[i0]
        x1, y1 = pts[i1]
        return (x0 + t * (x1 - x0), y0 + t * (y1 - y0))

    seg = [pts[0]]
    pos = vals[0] >= 0.0
    for i in range(1, len(pts)):
        ppos = vals[i] >= 0.0
        if ppos != pos:
            zpt = lerp_pt(i - 1, i, vals[i - 1], vals[i])
            seg.append(zpt)
            wire(ctx, seg, c if pos else neg_color, lw)
            seg = [zpt, pts[i]]
            pos = ppos
        else:
            seg.append(pts[i])
    if len(seg) >= 2:
        wire(ctx, seg, c if pos else neg_color, lw)


def draw_wave_cell(ctx, col, row, title, color, f, t, zero=0.12, v_scale=1.0,
                   overlay=None, title2=None, color2=None, neg_color=None):
    x, y, w, h = cell_rect(col, row)
    text(ctx, title, x + 14, y + 22, 22, color, "l", True)
    if title2 and color2:
        text(ctx, title2, x + 14 + 90, y + 22, 22, color2, "l", True)
    t0 = max(0.0, t - 10.0)
    plot_wave(ctx, x, y, w, h, f, color, t0, t, zero=zero, v_scale=v_scale,
              neg_color=neg_color)
    if overlay:
        f2, c2, lw2 = overlay
        plot_wave(ctx, x, y, w, h, f2, c2, t0, t, zero=zero, v_scale=v_scale,
                  lw=lw2, draw_axes=False)


def draw(ctx, t):
    t = clamp(t, 0, DUR)
    blit_bg(ctx)
    P = PATHS
    st = signals(t)

    # Wave card
    ox, oy = WAVE_X0 - 16, PAD
    ow, oh = W - WAVE_X0 - PAD + 16, H - 2 * PAD
    S.col(ctx, PAN)
    ctx.rectangle(ox, oy, ow, oh)
    ctx.fill()
    wire(ctx, [(ox, oy), (ox + ow, oy), (ox + ow, oy + oh), (ox, oy + oh), (ox, oy)],
         hx("#d0d7de"), 2.5)
    mid_x = WAVE_X0 + CELL_W
    mid_y = WAVE_TOP + CELL_H
    wire(ctx, [(WAVE_X0, mid_y), (W - PAD - 8, mid_y)], DIV, 2)
    wire(ctx, [(mid_x, WAVE_TOP), (mid_x, WAVE_BOT)], DIV, 2)

    text(ctx, "RC Astable", WAVE_X0 - 30, 40, 30, INK, "r", True)
    ly = H - 32
    text(ctx, "Q1 coll.", 80, ly, 18, C_BLUE, "l", True)
    text(ctx, "Q2 coll.", 220, ly, 18, C_GREEN, "l", True)
    text(ctx, "C coupling", 360, ly, 18, C_PURPLE, "l", True)
    text(ctx, "Ib path", 500, ly, 18, C_YELLOW, "l", True)
    text(ctx, "C voltage", 600, ly, 18, C_BAR, "l", True)

    v1, v2 = cap_voltages(t)
    bipolar_bar(ctx, P["bar_c1"][0], P["bar_c1"][1], v1, "Vc1")
    bipolar_bar(ctx, P["bar_c2"][0], P["bar_c2"][1], v2, "Vc2")

    # Vc: raised zero; capacitor voltage (same as bars) — neg segment red
    draw_wave_cell(ctx, 0, 0, "Vc1", C_BLUE,
                   lambda u: cap_voltages(u)[0], t, zero=0.30, v_scale=0.82,
                   neg_color=C_NEG)
    draw_wave_cell(ctx, 1, 0, "Vc2", C_GREEN,
                   lambda u: cap_voltages(u)[1], t, zero=0.30, v_scale=0.82,
                   neg_color=C_NEG)
    draw_wave_cell(ctx, 0, 1, "Vb1", C_VB, lambda u: signals(u)["vb1"], t,
                   zero=0.55, v_scale=0.72)
    draw_wave_cell(ctx, 1, 1, "Vb2", C_VB, lambda u: signals(u)["vb2"], t,
                   zero=0.55, v_scale=0.72)

    if not st["active"]:
        return

    q1l, q2l = st["q1_lvl"], st["q2_lvl"]
    # Collector currents (overlap: both visible)
    if q1l > 0.05:
        current_flow(ctx, P["path_q1"], (*C_BLUE[:3], 0.55 + 0.40 * q1l), t,
                     speed=90, lw=5 + 3 * q1l)
    if q2l > 0.05:
        current_flow(ctx, P["path_q2"], (*C_GREEN[:3], 0.55 + 0.40 * q2l), t,
                     speed=90, lw=5 + 3 * q2l)

    if st["overlap"] or st["spike"]:
        # Phase A: coupling spike on timing C + other C charging via rising collector
        if st["q1"]:
            current_flow(ctx, P["spike_q1"], (*C_PURPLE[:3], 0.90), t, speed=110, lw=6)
            current_flow(ctx, P["path_c2_q1on"], (*C_PURPLE[:3], 0.75), t * 0.85 + 0.3,
                         speed=70, lw=5)
            text(ctx, "flip → Q1", P["Q1"][0] - 50, P["Q1"][1] + 95, 22, C_BLUE, "c", True)
        else:
            current_flow(ctx, P["spike_q2"], (*C_PURPLE[:3], 0.90), t, speed=110, lw=6)
            current_flow(ctx, P["path_c1_q2on"], (*C_PURPLE[:3], 0.75), t * 0.85 + 0.3,
                         speed=70, lw=5)
            text(ctx, "flip → Q2", P["Q2"][0] + 50, P["Q2"][1] + 95, 22, C_GREEN, "c", True)
    else:
        # Phase B: Rb→C→ON charging + base drive of ON device
        if st["q1"]:
            current_flow(ctx, P["path_base_q1"], (*C_YELLOW[:3], 0.90), t * 0.8 + 0.4,
                         speed=70, lw=5)
            current_flow(ctx, P["path_c1_via_r2"], (*C_PURPLE[:3], 0.88), t * 0.9 + 0.2,
                         speed=75, lw=6)   # IR2 into C1
            current_flow(ctx, P["path_c2_q1on"], (*C_PURPLE[:3], 0.70), t * 0.85 + 0.5,
                         speed=70, lw=5)
            text(ctx, "Q1 ON", P["Q1"][0] - 60, P["Q1"][1] + 95, 24, C_BLUE, "c", True)
        else:
            current_flow(ctx, P["path_base_q2"], (*C_YELLOW[:3], 0.90), t * 0.8 + 0.4,
                         speed=70, lw=5)
            current_flow(ctx, P["path_c2_via_r3"], (*C_PURPLE[:3], 0.88), t * 0.9 + 0.2,
                         speed=75, lw=6)
            current_flow(ctx, P["path_c1_q2on"], (*C_PURPLE[:3], 0.70), t * 0.85 + 0.5,
                         speed=70, lw=5)
            text(ctx, "Q2 ON", P["Q2"][0] + 60, P["Q2"][1] + 95, 24, C_GREEN, "c", True)


def render(out):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(round(DUR * FPS))
    for i in range(nf):
        draw(ctx, i / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
        if i % 180 == 0:
            print(f"  frame {i}/{nf}", flush=True)
    p.stdin.close()
    rc = p.wait()
    print("wrote", out, "frames", nf, "dur", DUR, "ffmpeg", rc)


def still(t, path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    draw(ctx, t)
    surf.write_to_png(path)
    print("still", path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "still":
        for t in sys.argv[2:]:
            still(float(t), str(OUT_DIR / f"rc_astable_{t}.png"))
    else:
        render(str(OUT_MP4))
