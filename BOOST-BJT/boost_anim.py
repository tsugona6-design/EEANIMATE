#!/usr/bin/env python3
"""Boost converter teaching animation — Buck-style layout/probes/paths."""
import cairo, math, subprocess
from pathlib import Path
import symbols as S
from symbols import hx, wire, junction, text, current_flow
from boost_topology import draw_schematic, W, H, BG

OUT_DIR = Path(__file__).resolve().parent
OUT_MP4 = OUT_DIR / "boost_animation.mp4"

FPS, DUR = 60, 24.0
C_ON  = hx('#0969da')
C_VB  = hx('#bf8700')
C_OFF = hx('#1a7f37')
C_IL  = hx('#8250df')
C_VO  = hx('#bf3989')
G2    = hx('#6e7781')
PAN   = hx('#ffffff')
DIV   = hx('#e6edf2')

T_A0, T_A1 = 2.0, 11.0
T_B0, T_B1 = 12.0, 22.0
PER = 1.8
DA, DB = 0.35, 0.65
VSAT, VF = 0.10, 0.12  # ON≈Vsat near 0; OFF≈Vout+VF (high)

PAD = 28
OUTER = (PAD, PAD, W - 2 * PAD, H - 2 * PAD)
SCH_W = 900
WAVE_X0 = PAD + SCH_W
WAVE_W = W - PAD - WAVE_X0
WAVE_TOP = PAD + 160
WAVE_BOT = H - PAD - 160
WAVE_H = WAVE_BOT - WAVE_TOP
CELL_W = WAVE_W / 2
CELL_H = WAVE_H / 2


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def duty_at(t):
    if t < T_A0:
        return DA, False
    if t < T_A1:
        return DA, True
    if t < T_B0:
        return DA, False
    if t < T_B1:
        return DB, True
    return DB, False


def signals(t):
    """Boost levels: Vsw ON≈Vsat, OFF≈Vout+VF; Vout rises with D."""
    d, sw = duty_at(t)
    # Ideal boost Vo/Vin ≈ 1/(1-D); map into ~0.35..0.95 for plot
    vo_avg = clamp(0.38 / max(1.0 - d, 0.25), 0.35, 0.95)

    if t < 0.8:
        return dict(vb=0, il=0, vsw=0, vo=0, on=False, d=d)
    if not sw and t < T_A0:
        u = ease((t - 0.8) / 1.2)
        return dict(vb=0, il=0.15 * u, vsw=0, vo=0.25 * u, on=False, d=d)

    t0 = T_A0 if t < T_B0 else T_B0
    if T_A1 <= t < T_B0:
        return dict(vb=0, il=0.55, vsw=vo_avg + VF, vo=vo_avg, on=False, d=DA)

    frac = ((t - t0) / PER) % 1.0
    on = frac < d
    if on:
        il = 0.35 + 0.45 * (frac / max(d, 1e-6))
        rip = frac / max(d, 1e-6)
        vsw = VSAT
    else:
        il = 0.80 - 0.45 * ((frac - d) / max(1 - d, 1e-6))
        rip = 1.0 - (frac - d) / max(1 - d, 1e-6)
        vsw = vo_avg + VF
    vb = 1.0 if on else 0.0
    amp = 0.10 * (4.0 * d * (1.0 - d))
    vo = vo_avg + amp * (2.0 * rip - 1.0)
    return dict(vb=vb, il=il, vsw=vsw, vo=vo, on=on, d=d)


def cell_rect(col, row):
    return WAVE_X0 + col * CELL_W, WAVE_TOP + row * CELL_H, CELL_W, CELL_H


def plot_wave(ctx, x, y, w, h, f, c, t0, t1, zero=0.15, lw=3.5, n=360,
              level_labels=None):
    ax, ay, aw, ah = x + 52, y + 40, w - 70, h - 58
    zline = ay + ah * (1 - zero)
    wire(ctx, [(ax, zline), (ax + aw, zline)], hx('#d0d7de'), 2)
    wire(ctx, [(ax, ay), (ax, ay + ah)], hx('#d0d7de'), 2)
    span = ah * 0.78
    pts = []
    for i in range(n):
        u = t0 + (t1 - t0) * i / (n - 1)
        v = f(u)
        pts.append((ax + aw * i / (n - 1), zline - v * span))
    if len(pts) >= 2:
        wire(ctx, pts, c, lw)
    if level_labels:
        for val, lab in level_labels:
            ly = zline - val * span
            wire(ctx, [(ax - 2, ly), (ax + 12, ly)], hx('#afb8c1'), 1.5)
            text(ctx, lab, ax - 6, ly, 13, G2, 'r', False)


def draw_wave_cell(ctx, col, row, title, color, f, t, zero=0.15, level_labels=None):
    x, y, w, h = cell_rect(col, row)
    text(ctx, title, x + 20, y + 28, 28, color, 'l', True)
    t0 = max(0.0, t - 8.0)
    plot_wave(ctx, x, y, w, h, f, color, t0, t, zero=zero, level_labels=level_labels)


def draw_schematic_probes(ctx, info):
    probes = info.get('probes', {})
    specs = [
        ('Vb',  C_VB, probes.get('Vb')),
        ('iL',  C_IL, probes.get('iL')),
        ('Vsw', C_ON, probes.get('Vsw')),
        ('Vout', C_VO, probes.get('Vout')),
    ]
    for lab, col, pt in specs:
        if not pt:
            continue
        x, y = pt
        ctx.new_path()
        ctx.arc(x, y, 11, 0, 2 * math.pi)
        S.col(ctx, (col[0], col[1], col[2], 0.22))
        ctx.fill()
        junction(ctx, x, y, 7, col)
        if lab == 'Vb':
            text(ctx, lab, x - 18, y - 24, 26, col, 'r', True)
        elif lab == 'iL':
            text(ctx, lab, x + 14, y - 28, 26, col, 'l', True)
        elif lab == 'Vsw':
            text(ctx, lab, x + 16, y - 28, 26, col, 'l', True)
        else:
            text(ctx, lab, x + 16, y - 28, 26, col, 'l', True)


def draw(ctx, t):
    t = clamp(t, 0, DUR)
    S.col(ctx, (*BG, 1)); ctx.paint()

    ox, oy, ow, oh = OUTER
    S.col(ctx, PAN if len(PAN) == 4 else (*PAN, 1))
    ctx.rectangle(ox, oy, ow, oh)
    ctx.fill()
    wire(ctx, [(ox, oy), (ox + ow, oy), (ox + ow, oy + oh), (ox, oy + oh), (ox, oy)],
         hx('#d0d7de'), 3)

    wire(ctx, [(WAVE_X0, oy + 12), (WAVE_X0, oy + oh - 12)], DIV, 2)
    mid_x = WAVE_X0 + CELL_W
    mid_y = WAVE_TOP + CELL_H
    wire(ctx, [(WAVE_X0 + 12, mid_y), (ox + ow - 12, mid_y)], DIV, 2)
    wire(ctx, [(mid_x, WAVE_TOP), (mid_x, WAVE_BOT)], DIV, 2)

    sig = signals(t)
    on = sig['on']
    info = draw_schematic(ctx, on=on, oncol=C_ON, compact=True)

    switching = t >= T_A0 and not (T_A1 <= t < T_B0)
    if switching:
        if on:
            c = (C_ON[0], C_ON[1], C_ON[2], 0.9)
            current_flow(ctx, info['path_on'], c, t, speed=140, lw=7)
            # Lighter dashed loop: C discharging into load while switch is ON
            c_cap = (C_VO[0], C_VO[1], C_VO[2], 0.70)
            current_flow(ctx, info['path_on_cap'], c_cap, t * 0.85 + 0.4, speed=100, lw=6)
            text(ctx, "ON  (b)", info['Xsw'] + 55, info['L']['Ysw'] - 70, 24, C_ON, 'l', True)
        else:
            c = (C_OFF[0], C_OFF[1], C_OFF[2], 0.9)
            current_flow(ctx, info['path_off'], c, t, speed=140, lw=7)
            text(ctx, "OFF  (D)", info['Xsw'] + 55, info['L']['Ysw'] - 70, 24, C_OFF, 'l', True)

    draw_schematic_probes(ctx, info)

    d, _ = duty_at(t)
    text(ctx, f"D ≈ {d:.2f}", WAVE_X0 - 24, PAD + 32, 24, G2, 'r', True)

    # Boost Vsw: low≈Vsat when ON, high≈Vout+VF when OFF
    draw_wave_cell(ctx, 0, 0, "Vb", C_VB, lambda u: signals(u)['vb'], t, zero=0.12)
    draw_wave_cell(ctx, 1, 0, "iL", C_IL, lambda u: signals(u)['il'], t, zero=0.12)
    draw_wave_cell(ctx, 0, 1, "Vsw", C_ON, lambda u: signals(u)['vsw'], t, zero=0.18,
                   level_labels=[(VSAT, "Vsat"), (0.85, "Vout+VF")])
    draw_wave_cell(ctx, 1, 1, "Vout", C_VO, lambda u: signals(u)['vo'], t, zero=0.12)


def render(out):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra',
           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
           '-pix_fmt', 'yuv420p', '-r', str(FPS), '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(round(DUR * FPS))
    for i in range(nf):
        draw(ctx, i / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    p.wait()
    print('wrote', out, 'frames', nf, 'dur', DUR)


def still(t, path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    draw(ctx, t)
    surf.write_to_png(path)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'still':
        for t in sys.argv[2:]:
            still(float(t), str(OUT_DIR / f'boost_{t}.png'))
    else:
        render(str(OUT_MP4))
