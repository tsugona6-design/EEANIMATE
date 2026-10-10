#!/usr/bin/env python3
"""Royer converter teaching animation — simplified push-pull (refactored)."""
import cairo, math, subprocess
from pathlib import Path
import symbols as S
from symbols import hx, wire, junction, text, npn, gnd, coil_h, current_flow, flux_ring, bar_meter
OUT_DIR = Path(__file__).resolve().parent
OUT_MP4 = OUT_DIR / "royer_animation.mp4"
OUT_PNG = OUT_DIR / "royer_topology.png"

W, H, FPS, DUR = 1920, 1080, 60, 26.0
BG = (0xf6/255, 0xf8/255, 0xfa/255)
# Unified light-theme palette
INK  = hx('#1f2328')   # static schematic lines / idle BJTs
C_Q1 = hx('#0969da')   # Q1 branch, Ib1, Φ when Q1, waveform B
C_Q2 = hx('#1a7f37')   # Q2 branch, Ib2, Φ when Q2, waveform Im
C_VS = hx('#8250df')   # waveform Vs (violet, same family accent)
SAT  = hx('#cf222e')   # saturation only
G2   = hx('#6e7781')
PAN  = hx('#ffffff')
LW = 5.0
# aliases used below
BCOL, RCOL, A = C_Q1, C_Q2, C_VS
HALF = 1.8
HANDOFF = 0.40   # seconds for Ib fall→rise at each commutation

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ease(x):
    x = clamp(x); return x*x*(3-2*x)

def ramp(t, t0, t1):
    return ease((t-t0)/(t1-t0)) if t1 > t0 else 0.0

# ---------- which side is "supposed" to be on (hard target) ----------
def target_side(t):
    """Return 0 (off), 1 (Q1), or 2 (Q2)."""
    if t < 3.0:
        return 0
    if t < 12.5:
        return 1                    # Q1 builds up through asym/fb/sat
    if t < 14.5:
        # mid-commutation: hard target flips at midpoint
        return 1 if t < 13.5 else 2
    tt = t - 14.5
    n = int(tt / HALF)
    # continue after commutation with Q2 (n even → 2)
    return 2 if (n % 2 == 0) else 1

def switch_times():
    """Ordered (t_switch, from_side, to_side) for Q1↔Q2 handoffs only."""
    sw = [(12.5, 1, 2)]         # first commutation Q1→Q2
    t0, side = 14.5, 2          # after comm, Q2 holds; next flip at 14.5+HALF
    while t0 + HALF < DUR + 1:
        nxt = 1 if side == 2 else 2
        sw.append((t0 + HALF, side, nxt))
        t0 += HALF
        side = nxt
    return sw

def handoff_levels(t, t_sw, frm, to, dur=HANDOFF):
    """Around t_sw: outgoing falls in first ~45%, incoming rises in remaining.
    Returns dict {1: ib1_norm, 2: ib2_norm} in 0..1."""
    lev = {1: 0.0, 2: 0.0}
    u = (t - t_sw) / dur
    if frm == 0:
        # cold start — only rise of `to`
        if u < 0:
            return lev
        if u >= 1:
            lev[to] = 1.0; return lev
        lev[to] = ease(u); return lev
    if u < 0:
        lev[frm] = 1.0; return lev
    if u >= 1:
        lev[to] = 1.0; return lev
    if u < 0.45:
        lev[frm] = 1.0 - ease(u/0.45)
        lev[to] = 0.0
    else:
        lev[frm] = 0.0
        lev[to] = ease((u-0.45)/0.55)
    return lev

def ib_smooth(t):
    """Smoothed Ib1/Ib2 in 0..120 with fall-then-rise handoffs."""
    sw = switch_times()
    active = None
    for i, (ts, frm, to) in enumerate(sw):
        if t < ts:
            break
        active = i
    if active is None:
        # Before first commutation: asymmetry → Q1 locks on (smooth rise, no dip)
        if t < 3.0:
            return 0.0, 0.0
        if t < 6.0:
            u = ramp(t, 3.0, 6.0)
            return (45+50*u), (12+10*u)          # Ib1 ahead of Ib2
        u = ramp(t, 6.0, 7.5)                     # finish locking Q1
        return (95+(120-95)*u), (22*(1-u))
    ts, frm, to = sw[active]
    lev = handoff_levels(t, ts, frm, to)
    if active+1 < len(sw):
        ts2, f2, t2 = sw[active+1]
        if t >= ts2:
            lev = handoff_levels(t, ts2, f2, t2)
    return lev[1]*120.0, lev[2]*120.0

def branch_alpha(t):
    """Smooth 0..1 strength for Q1/Q2 current-path highlight."""
    ib1, ib2 = ib_smooth(t)
    return clamp(ib1/110.0), clamp(ib2/110.0)

def flux_flip(t):
    """Flux sense follows the dominant base current (Q1→+1, Q2→−1)."""
    ib1, ib2 = ib_smooth(t)
    if ib2 > ib1 and ib2 > 2:
        return -1
    if ib1 > 2:
        return 1
    # idle / startup
    return 1

# ---------- flux / waveforms (crisp at sat; direction tied to active side) ----------
def phase_info(t):
    """Core teaching signals (Vs, B, Im, sat). Ib comes from ib_smooth()."""
    a1, a2 = branch_alpha(t)
    side = target_side(t)
    flip = 1 if side == 1 else (-1 if side == 2 else 0)

    if t < 0.5:
        return dict(seg='hold', flux=0, sat=False, vsec=0, im=0, flip=1)
    if t < 3.0:
        return dict(seg='power', flux=0, sat=False, vsec=0, im=0, flip=1, vin_on=ramp(t,0.5,2.5))
    if t < 6.0:
        u = ramp(t, 3.0, 5.5)
        return dict(seg='asym', flux=0.12*u, sat=False, vsec=0.08*u, im=0.08*u, flip=1)
    if t < 10.0:
        u = ramp(t, 6.0, 9.5)
        return dict(seg='fb', flux=0.18+0.72*u, sat=False, vsec=0.25+0.65*u, im=0.18+0.55*u, flip=1)
    if t < 12.5:
        u = ramp(t, 10.0, 12.0)
        return dict(seg='sat', flux=0.95, sat=True, vsec=0.9*(1-0.45*u), im=0.85+0.45*u, flip=1)
    if t < 14.5:
        u = ramp(t, 12.5, 14.0)
        fl = 1 if t < 13.5 else -1
        return dict(seg='comm', flux=0.95-1.7*u, sat=u<0.35,
                    vsec=0.9-1.8*u, im=1.2-2.0*u, flip=fl)
    # oscillation
    tt = t - 14.5
    n = int(tt / HALF)
    frac = tt/HALF - n
    q2 = (n % 2 == 0)
    flip = -1 if q2 else 1
    if frac < 0.72:
        flux = (0.12 + 0.82*frac/0.72) * flip
        sat = False
        vsec = 0.9 * flip
        im = (0.15 + 0.55*frac/0.72) * flip
    else:
        u = (frac-0.72)/0.28
        flux = 0.94 * flip
        sat = True
        vsec = 0.9*(1-0.55*u) * flip
        im = (0.7 + 0.7*u) * flip
    return dict(seg='osc', flux=flux, sat=sat, vsec=vsec, im=im, flip=flip)

def flux_angle(t, omega=2.6):
    """Integrate tip angle; velocity sign = flip (Q1 → +ang, Q2 → −ang)."""
    ang = 0.0
    # sample coarsely for stability / speed
    dt = 1.0/30.0
    n = max(1, int(t/dt))
    for i in range(n):
        ti = (i+0.5)*dt
        if ti > t: break
        fl = flux_flip(ti)
        ang += omega * fl * dt
    return ang

def wave_funcs():
    def vsec(u): return clamp(phase_info(u)['vsec'], -1.2, 1.2)
    def B(u):    return clamp(phase_info(u)['flux'], -1.2, 1.2)
    def Im(u):   return clamp(phase_info(u)['im'], -1.4, 1.4)
    return vsec, B, Im

def plot_wave(ctx, x, y, w, h, f, c, t0, t1, zero=0.5, lw=4.5, n=500, color_fn=None, sat_fn=None):
    """color_fn(u)->half-cycle color; sat_fn(u)->True paints only that sample red (B sat mark)."""
    wire(ctx, [(x, y+h*zero), (x+w, y+h*zero)], hx('#d0d7de'), 2)
    wire(ctx, [(x, y), (x, y+h)], hx('#d0d7de'), 2)
    samples = []
    for i in range(n):
        u = t0 + (t1-t0)*i/(n-1)
        v = f(u)
        px = x + w*i/(n-1)
        py = y + h*zero - v*h*min(zero, 1-zero)*0.9
        if sat_fn and sat_fn(u):
            cc = SAT
        elif color_fn:
            cc = color_fn(u)
        else:
            cc = c
        samples.append((px, py, cc))
    run = [samples[0]]
    for samp in samples[1:]:
        if samp[2] == run[-1][2]:
            run.append(samp)
        else:
            wire(ctx, [(p[0], p[1]) for p in run], run[0][2], lw)
            run = [run[-1], samp]
    if len(run) >= 2:
        wire(ctx, [(p[0], p[1]) for p in run], run[0][2], lw)
    elif run:
        junction(ctx, run[0][0], run[0][1], 5, run[0][2])
    junction(ctx, samples[-1][0], samples[-1][1], 6, samples[-1][2])

def draw_circuit(ctx, t, st):
    Cx = 500
    Yprim = 300
    Qy = 560
    s_bjt = 1.3
    c_off = 22 * s_bjt
    P_half = 200
    half = P_half + c_off
    Q1x, Q2x = Cx - half, Cx + half
    P_left, P_right = Cx - P_half, Cx + P_half

    ib1, ib2 = ib_smooth(t)
    a1, a2 = clamp(ib1/110.0), clamp(ib2/110.0)

    # +Vin
    wire(ctx, [(Cx, Yprim), (Cx, 160)])
    ctx.new_path(); ctx.arc(Cx, 160, 11, 0, 2*math.pi)
    S.col(ctx, INK); ctx.set_line_width(LW); ctx.stroke()
    text(ctx, "+Vin", Cx, 110, 40, INK, 'c', True)

    # Primary halves — keep wavy polylines for current routing
    # Current from CT: left half traversed CT→P_left (reverse of drawn left coil)
    coil_left = coil_h(ctx, P_left, Yprim, Cx-16, INK, LW, n=4)   # P_left → near CT
    coil_right = coil_h(ctx, Cx+16, Yprim, P_right, INK, LW, n=4) # near CT → P_right
    wire(ctx, [(Cx-16, Yprim), (Cx+16, Yprim)])
    junction(ctx, Cx, Yprim)
    junction(ctx, P_left, Yprim, 7)
    junction(ctx, P_right, Yprim, 7)
    # Paths along windings from center tap outward
    path_wL = [(Cx, Yprim), (Cx-16, Yprim)] + list(reversed(coil_left))  # CT → left end
    path_wR = [(Cx, Yprim), (Cx+16, Yprim)] + list(coil_right)           # CT → right end

    q1_on = a1 > 0.45
    q2_on = a2 > 0.45
    C1, E1, B1, path1 = npn(ctx, Q1x, Qy, s_bjt, on=q1_on, oncol=BCOL)
    C2, E2, B2, path2 = npn(ctx, Q2x, Qy, s_bjt, mirror=True, on=q2_on, oncol=RCOL)
    text(ctx, "Q1", Q1x - 130, Qy, 46, BCOL if q1_on else INK, 'r', True)
    text(ctx, "Q2", Q2x + 130, Qy, 46, RCOL if q2_on else INK, 'l', True)

    wire(ctx, [C1, (C1[0], Yprim)])
    wire(ctx, [C2, (C2[0], Yprim)])

    yg = 800
    wire(ctx, [E1, (E1[0], yg)])
    wire(ctx, [E2, (E2[0], yg)])
    gnd(ctx, E1[0], yg)
    gnd(ctx, E2[0], yg)

    # Ib bars — smoothed fall/rise
    bar_meter(ctx, E1[0] - 75, yg - 8, 90, ib1 * 90/120, BCOL, label="Ib1", max_h=90)
    bar_meter(ctx, E2[0] + 75, yg - 8, 90, ib2 * 90/120, RCOL, label="Ib2", max_h=90)

    # Current paths with alpha from smoothed branch strength
    if a1 > 0.05:
        c1 = (C_Q1[0], C_Q1[1], C_Q1[2], 0.35 + 0.65*a1)
        # Vin → CT → wavy left winding → collector arm path → GND
        current_flow(ctx,
                     [(Cx, 180)] + path_wL + [(C1[0], Yprim)] + path1 + [(E1[0], yg)],
                     c1, t, 150, 5+5*a1)
    if a2 > 0.05:
        c2 = (C_Q2[0], C_Q2[1], C_Q2[2], 0.35 + 0.65*a2)
        current_flow(ctx,
                     [(Cx, 180)] + path_wR + [(C2[0], Yprim)] + path2 + [(E2[0], yg)],
                     c2, t, 150, 5+5*a2)

    # Flux ring: direction follows dominant transistor (via flux_flip / Ib).
    # Inverted vs earlier build (user said prior sense was wrong):
    #   Q1 dominant → cw=False; Q2 dominant → cw=True.
    flux = st['flux']
    flip = flux_flip(t)
    if abs(flux) > 0.04 or a1 > 0.05 or a2 > 0.05 or st['seg'] in ('fb', 'sat', 'comm', 'osc', 'asym'):
        ang = flux_angle(t)
        cw = flip < 0
        fc = SAT if st['sat'] else (BCOL if flip > 0 else RCOL)
        flux_ring(ctx, Cx, Yprim + 150, ang, radius=52, c=fc, lw=7, cw=cw, label="Φ")

def draw_waves(ctx, t):
    px, py, pw, ph = 1000, 140, 860, 860
    S.col(ctx, PAN); ctx.rectangle(px, py, pw, ph); ctx.fill()
    wire(ctx, [(px,py),(px+pw,py),(px+pw,py+ph),(px,py+ph),(px,py)], G2, 2.5)
    vsec, B, Im = wave_funcs()
    t0 = max(0.5, t - 8.0)
    def half_color(u):
        return C_Q1 if flux_flip(u) > 0 else C_Q2

    def b_sat_mark(u):
        """Short red tip only at B saturation peaks — never whole half-cycle / slope."""
        st = phase_info(u)
        if st['seg'] == 'sat':
            # first buildup tip: ~0.3 s at end of flat B before commutation
            return 11.95 <= u <= 12.40
        if st['seg'] == 'osc':
            tt = u - 14.5
            frac = (tt / HALF) - int(tt / HALF)
            # sat starts at frac>=0.72 with B flat at tip; paint only ~0.15s onset
            return 0.72 <= frac <= 0.82
        return False  # ignore comm declining flux

    rows = [
        (py+50,  "Vs", vsec, C_VS, None, None),
        (py+320, "B",  B,    C_Q1, half_color, b_sat_mark),
        (py+590, "Im", Im,   C_Q2, half_color, None),
    ]
    for y0, lab, fn, c, cfn, sfn in rows:
        lc = half_color(t) if cfn else c
        text(ctx, lab, px+28, y0+10, 34, lc, 'l', True)
        plot_wave(ctx, px+70, y0+30, pw-110, 200, fn, c, t0, t, color_fn=cfn, sat_fn=sfn)

def draw(ctx, t):
    t = clamp(t, 0, DUR)
    ta = clamp(t, 0.5, DUR-0.5)
    st = phase_info(ta)
    S.col(ctx, (*BG, 1)); ctx.paint()
    draw_circuit(ctx, ta, st)
    draw_waves(ctx, ta)

def render(out):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    cmd = ['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgra',
           '-s',f'{W}x{H}','-r',str(FPS),'-i','-',
           '-an','-c:v','libx264','-preset','medium','-crf','18',
           '-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(round(DUR*FPS))
    for i in range(nf):
        draw(ctx, i/FPS)
        surf.flush(); p.stdin.write(bytes(surf.get_data()))
    p.stdin.close(); p.wait()
    print('wrote', out, 'frames', nf, 'dur', DUR)

def still(t, path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    draw(ctx, t)
    surf.write_to_png(path)

if __name__ == '__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='still':
        for t in sys.argv[2:]:
            still(float(t), str(OUT_DIR / f"royer_{t}.png"))
    else:
        render(str(OUT_MP4))
