import cairo, math, subprocess, sys
import numpy as np
W,H,FPS,DUR=1920,1080,60,20.0
BG=(0x0d/255,0x11/255,0x17/255)
def hx(h,a=1.0):
    h=h.lstrip('#'); return (int(h[0:2],16)/255,int(h[2:4],16)/255,int(h[4:6],16)/255,a)
FG=hx('#e6edf3'); GREY=hx('#8b949e'); DIM=hx('#3a414b'); RED=hx('#ff5a52'); WHITE=hx('#ffffff')
LW=6
def col(c,ctx):
    ctx.set_source_rgba(*c)
def clamp(x,a=0,b=1): return max(a,min(b,x))
def ease(x):
    x=clamp(x); return x*x*(3-2*x)
def ramp(t,t0,t1): return ease((t-t0)/(t1-t0))
def txt(ctx,s,x,y,size=44,c=FG,anchor='c',bold=False):
    ctx.select_font_face("Noto Sans CJK SC",cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e=ctx.text_extents(s)
    if anchor=='c': x0=x-e.x_advance/2
    elif anchor=='l': x0=x
    else: x0=x-e.x_advance
    col(c,ctx); ctx.move_to(x0,y+size*0.36); ctx.show_text(s); ctx.new_path()
def line(ctx,pts,c=FG,lw=LW,dash=None,off=0):
    col(c,ctx); ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    if dash: ctx.set_dash(dash,off)
    ctx.stroke(); ctx.set_dash([])
def flow(ctx,pts,c,t,speed=160,lw=9,glow=True):
    if glow: line(ctx,pts,(c[0],c[1],c[2],0.22*c[3] if len(c)>3 else 0.22),lw*3)
    line(ctx,pts,c,lw,dash=[30,22],off=-t*speed)
def circle(ctx,x,y,r,c=FG,lw=LW,fill=None):
    ctx.new_path()
    ctx.arc(x,y,r,0,2*math.pi)
    if fill: col(fill,ctx); ctx.fill_preserve()
    col(c,ctx); ctx.set_line_width(lw); ctx.stroke()
def dot(ctx,x,y,r=9,c=FG):
    ctx.new_path()
    ctx.arc(x,y,r,0,2*math.pi); col(c,ctx); ctx.fill()
def rect(ctx,x,y,w,h,c=FG,lw=LW,fill=None,r=12):
    ctx.new_sub_path(); ctx.arc(x+w-r,y+r,r,-math.pi/2,0); ctx.arc(x+w-r,y+h-r,r,0,math.pi/2)
    ctx.arc(x+r,y+h-r,r,math.pi/2,math.pi); ctx.arc(x+r,y+r,r,math.pi,1.5*math.pi); ctx.close_path()
    if fill: col(fill,ctx); ctx.fill_preserve()
    if lw: col(c,ctx); ctx.set_line_width(lw); ctx.stroke()
    else: ctx.new_path()
def arrowhead(ctx,x,y,ang,c=FG,s=22):
    col(c,ctx); ctx.move_to(x,y)
    ctx.line_to(x-s*math.cos(ang-0.45),y-s*math.sin(ang-0.45)); ctx.line_to(x-s*math.cos(ang+0.45),y-s*math.sin(ang+0.45)); ctx.close_path(); ctx.fill()
def arrow(ctx,x0,y0,x1,y1,c=FG,lw=LW,s=26):
    a=math.atan2(y1-y0,x1-x0)
    line(ctx,[(x0,y0),(x1-s*0.6*math.cos(a),y1-s*0.6*math.sin(a))],c,lw); arrowhead(ctx,x1,y1,a,c,s)
# components: oriented between two points (horizontal or vertical)
def _frame(ctx,p0,p1):
    x0,y0=p0;x1,y1=p1; L=math.hypot(x1-x0,y1-y0); a=math.atan2(y1-y0,x1-x0)
    ctx.save(); ctx.translate(x0,y0); ctx.rotate(a); return L
def resistor(ctx,p0,p1,c=FG,lw=LW,body=110):
    L=_frame(ctx,p0,p1); s=(L-body)/2; n=6; pts=[(0,0),(s,0)]
    for i in range(n): pts.append((s+body*(i+0.5)/n,(-22 if i%2==0 else 22)))
    pts+= [(s+body,0),(L,0)]; line(ctx,pts,c,lw); ctx.restore()
def inductor(ctx,p0,p1,c=FG,lw=LW,body=130,n=4,flip=False):
    L=_frame(ctx,p0,p1); s=(L-body)/2; line(ctx,[(0,0),(s,0)],c,lw); line(ctx,[(s+body,0),(L,0)],c,lw)
    r=body/n/2; col(c,ctx); ctx.set_line_width(lw)
    for i in range(n):
        cx=s+r*(2*i+1)
        if flip: ctx.arc_negative(cx,0,r,math.pi,0) if False else ctx.arc(cx,0,r,0,math.pi)
        else: ctx.arc(cx,0,r,math.pi,2*math.pi)
        ctx.stroke()
    ctx.restore()
def capacitor(ctx,p0,p1,c=FG,lw=LW,gap=22,plate=70):
    L=_frame(ctx,p0,p1); m=L/2
    line(ctx,[(0,0),(m-gap/2,0)],c,lw); line(ctx,[(m+gap/2,0),(L,0)],c,lw)
    line(ctx,[(m-gap/2,-plate/2),(m-gap/2,plate/2)],c,lw+1); line(ctx,[(m+gap/2,-plate/2),(m+gap/2,plate/2)],c,lw+1); ctx.restore()
def diode(ctx,p0,p1,c=FG,lw=LW,s=34,fill=None):
    """anode p0 -> cathode p1"""
    L=_frame(ctx,p0,p1); m=L/2
    line(ctx,[(0,0),(m-s/2,0)],c,lw); line(ctx,[(m+s/2,0),(L,0)],c,lw)
    ctx.move_to(m-s/2,-s*0.75); ctx.line_to(m+s/2,0); ctx.line_to(m-s/2,s*0.75); ctx.close_path()
    col(fill or c,ctx); ctx.fill_preserve(); col(c,ctx); ctx.set_line_width(lw*0.7); ctx.stroke()
    line(ctx,[(m+s/2,-s*0.8),(m+s/2,s*0.8)],c,lw); ctx.restore()
def battery(ctx,x,ytop,ybot,c=FG,lw=LW,label=None):
    m=(ytop+ybot)/2
    line(ctx,[(x,ytop),(x,m-14)],c,lw); line(ctx,[(x,m+14),(x,ybot)],c,lw)
    line(ctx,[(x-50,m-14),(x+50,m-14)],c,lw+1); line(ctx,[(x-28,m+14),(x+28,m+14)],c,lw+5)
    txt(ctx,"+",x+62,m-38,40,c)
def nmos(ctx,x,y,s=1.0,c=FG,lw=LW,mirror=False,rot=0,on=False,oncol=None):
    """N-channel enhancement MOSFET with body diode. local: drain (20,-60) top, source (20,60) bottom, gate (-60,0).
    Returns world coords of (drain, source, gate)."""
    ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(-s if mirror else s,s)
    cc=oncol if on else c
    if on:
        ctx.new_path(); ctx.arc(5,0,78,0,2*math.pi); col((cc[0],cc[1],cc[2],0.16),ctx); ctx.fill()
    l=lw/s
    line(ctx,[(-60,0),(-22,0)],cc,l); line(ctx,[(-22,-30),(-22,30)],cc,l)
    for a,b in [(-34,-16),(-8,8),(16,34)]: line(ctx,[(-8,a),(-8,b)],cc,l)
    line(ctx,[(-8,-25),(20,-25),(20,-60)],cc,l)
    line(ctx,[(-8,25),(20,25),(20,60)],cc,l)
    line(ctx,[(0,0),(20,0),(20,25)],cc,l)
    arrowhead(ctx,-6,0,math.pi,cc,16)
    # body diode (anode at source, cathode at drain)
    line(ctx,[(20,-45),(50,-45),(50,-10)],cc,l*0.8); line(ctx,[(50,10),(50,45),(20,45)],cc,l*0.8)
    ctx.move_to(40,10); ctx.line_to(60,10); ctx.line_to(50,-8); ctx.close_path(); col(cc,ctx); ctx.fill()
    line(ctx,[(39,-9),(61,-9)],cc,l*0.8)
    dot(ctx,20,-45,4.5,cc); dot(ctx,20,45,4.5,cc)
    ctx.restore()
    def W_(px,py):
        px=-px if mirror else px; px*=s; py*=s
        return (x+px*math.cos(rot)-py*math.sin(rot), y+px*math.sin(rot)+py*math.cos(rot))
    return W_(20,-60),W_(20,60),W_(-60,0)
def plot(ctx,x,y,w,h,f,c,lw=5,t0=0,t1=1,n=600,prog=1.0,axis=True,ylab=None,zero=0.5,amp=None):
    """f(u) in [-1,1] mapped to box; u in [t0,t1]"""
    if axis:
        line(ctx,[(x,y+h*zero),(x+w,y+h*zero)],GREY,2.5); line(ctx,[(x,y),(x,y+h)],GREY,2.5)
        if ylab: txt(ctx,ylab,x-14,y+h*0.5,36,c,'r')
    N=max(2,int(n*prog)); pts=[]
    for i in range(N):
        u=i/(n-1); v=f(t0+(t1-t0)*u)
        pts.append((x+w*u, y+h*zero - v*(amp if amp else h*min(zero,1-zero)*0.92)))
    line(ctx,pts,c,lw)
    return pts
def group(ctx,alpha,fn,*a):
    if alpha<=0.001: return
    ctx.push_group(); fn(ctx,*a); ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha)
def title(ctx,s,A,sub=None):
    rect(ctx,60,52,14,70,lw=0,fill=A,r=4)
    txt(ctx,s,96,86,56,FG,'l',bold=True)
    if sub: txt(ctx,sub,1860,86,40,A,'r')
def render(draw,out,dur=None,bg=None):
    dur=DUR if dur is None else dur; bg=BG if bg is None else bg
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf)
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgra','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
         '-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart',out]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    nf=int(round(dur*FPS))
    for i in range(nf):
        t=i/FPS
        ctx.set_source_rgb(*bg); ctx.paint()
        draw(ctx,t)
        surf.flush(); p.stdin.write(bytes(surf.get_data()))
    p.stdin.close(); p.wait()
def still(draw,t,out,bg=None):
    bg=BG if bg is None else bg
    surf=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); ctx=cairo.Context(surf)
    ctx.set_source_rgb(*bg); ctx.paint(); draw(ctx,t); surf.write_to_png(out)
