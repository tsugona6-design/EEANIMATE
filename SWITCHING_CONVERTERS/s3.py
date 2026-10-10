from lib import *
DUR=45.0
BG=(0xf6/255,0xf8/255,0xfa/255)
D=hx('#1f2328'); A=hx('#1a7f37'); G2=hx('#6e7781'); PAN=hx('#ffffff')
ONC=hx('#1a7f37'); OFFC=hx('#0969da'); ACC=hx('#bf8700'); REDX=hx('#cf222e')
P=1.6

def titlebar(ctx,s,sub=None):
    rect(ctx,60,52,14,70,lw=0,fill=A,r=4)
    txt(ctx,s,96,86,50,D,'l',bold=True)
    if sub: txt(ctx,sub,1860,86,36,A,'r')

def npn(ctx,x,y,s=1.0,c=D,lw=LW,on=False,oncol=None):
    """Unified upright NPN BJT. Collector top, emitter bottom, base left.
    Local geometry at s=1: C=(20,-70), E=(20,70), B=(-60,0).
    Returns world (C, E, B)."""
    oc = oncol or ONC
    cc = oc if on else c
    ctx.save(); ctx.translate(x,y); ctx.scale(s,s)
    if on:
        ctx.new_path(); ctx.arc(5,0,78,0,2*math.pi); col((oc[0],oc[1],oc[2],0.15),ctx); ctx.fill()
    l=lw/max(s,0.01)
    # base lead + bar
    line(ctx,[(-60,0),(-20,0)],cc,l)
    line(ctx,[(-20,-34),(-20,34)],cc,l)
    # collector
    line(ctx,[(-20,-18),(20,-50),(20,-70)],cc,l)
    # emitter with arrow pointing out (down-right along emitter)
    line(ctx,[(-20,18),(20,50),(20,70)],cc,l)
    arrowhead(ctx,6,36,math.atan2(32,40),cc,15)
    ctx.restore()
    def W(px,py):
        return (x+px*s, y+py*s)
    return W(20,-70), W(20,70), W(-60,0)

def wavy_pts(x0,y,x1,n=5,amp=30):
    body=x1-x0; pts=[]
    for i in range(n):
        cx=x0+body*(i+0.5)/n; r=body/n/2
        for k in range(0,9):
            a=math.pi*(1-k/8)
            pts.append((cx+r*math.cos(a), y-amp*math.sin(a)*0.95))
    return pts

def draw_L(ctx,x0,y,x1,c=D,lw=LW,n=5):
    line(ctx,[(x0,y),(x0+6,y)],c,lw); line(ctx,[(x1-6,y),(x1,y)],c,lw)
    col(c,ctx); ctx.set_line_width(lw)
    body=x1-x0-12
    for i in range(n):
        cx=x0+6+body*(i+0.5)/n; r=body/n/2
        ctx.new_path(); ctx.arc(cx,y,r,math.pi,2*math.pi); ctx.stroke()

def flow_path(ctx,pts,c,t,speed=170,lw=10):
    if len(pts)<2: return
    line(ctx,pts,(c[0],c[1],c[2],0.16),lw*2.8)
    line(ctx,pts,c,lw,dash=[26,18],off=-t*speed)

def diode_ud(ctx,top,bot,c=D,lw=LW,s=34,on=False):
    """Vertical diode: anode at bot, cathode at top (freewheel orientation)."""
    diode(ctx,bot,top,ONC if on else c,lw,s,fill=hx('#1a7f37',0.3) if on else None)

def diode_lr(ctx,left,right,c=D,lw=LW,s=34,on=False):
    diode(ctx,left,right,ONC if on else c,lw,s,fill=hx('#1a7f37',0.3) if on else None)

# ---------------- A. Intro ----------------
def intro(ctx,ta):
    titlebar(ctx,"固态开关到来：晶体管 / 晶闸管","可快速通断 · 取代汞弧管")
    # mercury
    rect(ctx,80,180,700,780,G2,4,fill=PAN,r=14)
    txt(ctx,"汞弧整流管",430,250,46,G2,bold=True)
    cx,cy=430,520
    ctx.new_path(); ctx.move_to(cx-140,cy+140)
    ctx.curve_to(cx-170,cy-20,cx-100,cy-160,cx,cy-180)
    ctx.curve_to(cx+100,cy-160,cx+170,cy-20,cx+140,cy+140)
    ctx.curve_to(cx+80,cy+190,cx-80,cy+190,cx-140,cy+140); ctx.close_path()
    col(hx('#6e7781',0.12),ctx); ctx.fill_preserve(); col(G2,ctx); ctx.set_line_width(5); ctx.stroke()
    ctx.new_path(); ctx.save(); ctx.translate(cx,cy+130); ctx.scale(110,28); ctx.arc(0,0,1,0,2*math.pi); ctx.restore()
    col(hx('#8b949e'),ctx); ctx.fill()
    txt(ctx,"体积大 · 慢 · 需维护",430,780,40,G2)
    if ta>1.2:
        a=ramp(ta,1.2,2.0)
        line(ctx,[(200,300),(660,740)],(REDX[0],REDX[1],REDX[2],a),10)
        line(ctx,[(660,300),(200,740)],(REDX[0],REDX[1],REDX[2],a),10)
    # solid state
    a2=ramp(ta,1.0,1.8)
    def neu(c):
        rect(c,840,180,1000,780,A,5,fill=PAN,r=14)
        txt(c,"功率晶体管（BJT）",1100,240,42,A,bold=True)
        C,E,B=npn(c,1050,500,2.0,on=True)
        txt(c,"C",C[0]+36,C[1],40,D,'l',bold=True)
        txt(c,"E",E[0]+36,E[1],40,D,'l',bold=True)
        txt(c,"B",B[0]-24,B[1],40,D,'r',bold=True)
        txt(c,"晶闸管（SCR）",1550,240,42,A,bold=True)
        sx,sy=1550,500
        line(c,[(sx,sy-130),(sx,sy-45)],D,6)
        c.move_to(sx-42,sy-45); c.line_to(sx+42,sy-45); c.line_to(sx,sy+28); c.close_path()
        col(hx('#1a7f37',0.3),c); c.fill_preserve(); col(A,c); c.set_line_width(5); c.stroke()
        line(c,[(sx-48,sy+28),(sx+48,sy+28)],A,6)
        line(c,[(sx,sy+28),(sx,sy+130)],D,6)
        line(c,[(sx+18,sy+5),(sx+85,sy+45)],A,5)
        txt(c,"A",sx+55,sy-110,40,D,'l',bold=True)
        txt(c,"K",sx+55,sy+110,40,D,'l',bold=True)
        txt(c,"G",sx+105,sy+45,40,A,'l',bold=True)
        rect(c,900,820,880,100,A,5,fill=hx('#dafbe1'),r=10)
        txt(c,"可快速通断  →  高频开关变换成为可能",1340,870,42,A,bold=True)
    group(ctx,a2,neu)

# ---------------- B. Royer ----------------
def royer(ctx,ta):
    titlebar(ctx,"Royer 变换器（自激推挽）","自激推挽 DC→AC，早期开关电源里程碑")
    txt(ctx,"Bright & Royer · 约 1954–55",960,145,34,G2)
    # layout
    VinX=160; TOP,BOT,MID=260,720,490
    battery(ctx,VinX,TOP+40,BOT-40,D)
    txt(ctx,"Vin",80,MID,42,D,bold=True)
    # center tap of primary
    ctx_y=TOP
    # transformer primary center-tapped: left winding + right winding
    tx=980  # transformer core x
    # two BJTs
    # Q1 left bottomish
    q1x,q2x=420,700
    C1,E1,B1=npn(ctx,q1x,600,1.35,on=((int(ta*2.2)%2)==0),oncol=ONC)
    C2,E2,B2=npn(ctx,q2x,600,1.35,on=((int(ta*2.2)%2)==1),oncol=OFFC)
    txt(ctx,"Q1",q1x-90,600,40,ONC if (int(ta*2.2)%2)==0 else D,bold=True)
    txt(ctx,"Q2",q2x+90,600,40,OFFC if (int(ta*2.2)%2)==1 else D,bold=True)
    # emitters to ground (bot rail)
    line(ctx,[(VinX,BOT),(E1[0],BOT)],D,6); line(ctx,[(E2[0],BOT),(tx+80,BOT)],D,6)
    line(ctx,[E1,(E1[0],BOT)],D,6); line(ctx,[E2,(E2[0],BOT)],D,6)
    dot(ctx,E1[0],BOT,8); dot(ctx,E2[0],BOT,8)
    # collectors to primary ends
    # primary: C1 -- coil -- center tap -- coil -- C2
    pL0,pL1=C1[0],tx-40
    pR0,pR1=tx+40,C2[0]
    # vertical up from collectors then to windings
    line(ctx,[C1,(C1[0],TOP)],D,6); line(ctx,[C2,(C2[0],TOP)],D,6)
    draw_L(ctx,C1[0],TOP,tx-50,D,6,n=4)
    draw_L(ctx,tx+50,TOP,C2[0],D,6,n=4)
    # center tap down to Vin+
    line(ctx,[(tx,TOP),(tx,TOP-50),(VinX,TOP-50),(VinX,TOP+40)],D,6)
    dot(ctx,tx,TOP,9,D)
    txt(ctx,"中心抽头",tx+20,TOP-70,32,G2,'l')
    # transformer core
    line(ctx,[(tx-12,TOP-20),(tx-12,TOP+200)],G2,5)
    line(ctx,[(tx+12,TOP-20),(tx+12,TOP+200)],G2,5)
    txt(ctx,"变压器",tx,TOP+240,34,G2)
    # secondary
    draw_L(ctx,tx+80,TOP+80,tx+80+160,D,5,n=4)
    # actually vertical secondary better: two coils on right of core
    # redo secondary as vertical-ish horizontal windings on right
    line(ctx,[(tx+12,TOP+40),(tx+60,TOP+40)],D,5)
    draw_L(ctx,tx+60,TOP+40,tx+220,D,5,n=4)
    line(ctx,[(tx+12,TOP+140),(tx+60,TOP+140)],D,5)
    draw_L(ctx,tx+60,TOP+140,tx+220,D,5,n=4)
    line(ctx,[(tx+220,TOP+40),(tx+260,TOP+40),(tx+260,TOP+140),(tx+220,TOP+140)],D,5)
    # load
    resistor(ctx,(tx+300,TOP+40),(tx+300,TOP+140),D,5,body=70)
    txt(ctx,"负载",tx+360,TOP+90,34,D,'l')
    # feedback winding (magnetic feedback) — small winding + to bases
    line(ctx,[(tx-12,TOP+160),(tx-80,TOP+160)],ACC,4)
    draw_L(ctx,tx-200,TOP+160,tx-80,ACC,4,n=3)
    txt(ctx,"反馈绕组",tx-140,TOP+200,32,ACC)
    # feedback to bases (crossed for push-pull)
    fb=tx-200
    line(ctx,[(fb,TOP+160),(fb,B1[1]),(B1[0],B1[1])],ACC,4,dash=[10,8])
    line(ctx,[(tx-80,TOP+160),(tx-80,B2[1]-40),(B2[0]-20,B2[1]-40),(B2[0],B2[1])],ACC,4,dash=[10,8])
    txt(ctx,"磁反馈自激",300,TOP+200,34,ACC,bold=True)
    # which transistor on
    left_on=((int(ta*2.2)%2)==0)
    if left_on:
        # Vin+ -> CT -> left primary wavy -> Q1 C -> E -> gnd
        coil=wavy_pts(C1[0],TOP,tx-50,n=4,amp=26)
        path=[(VinX,TOP+80),(VinX,TOP-50),(tx,TOP-50),(tx,TOP)]+coil[::-1]+[(C1[0],TOP),C1,E1,(E1[0],BOT),(VinX,BOT),(VinX,BOT-40)]
        # fix: from CT along left winding to C1
        path=[(VinX,MID-40),(VinX,TOP-50),(tx,TOP-50),(tx,TOP)] + list(reversed(wavy_pts(C1[0],TOP,tx-50,n=4,amp=26))) + [(C1[0],TOP),C1,E1,(E1[0],BOT),(VinX,BOT)]
        flow_path(ctx,path,ONC,ta,160,9)
        # secondary current
        flow_path(ctx,[(tx+60,TOP+40),(tx+220,TOP+40),(tx+260,TOP+40),(tx+260,TOP+140),(tx+220,TOP+140),(tx+60,TOP+140)],ONC,ta,140,6)
    else:
        path=[(VinX,MID-40),(VinX,TOP-50),(tx,TOP-50),(tx,TOP)] + wavy_pts(tx+50,TOP,C2[0],n=4,amp=26) + [(C2[0],TOP),C2,E2,(E2[0],BOT),(VinX,BOT)]
        flow_path(ctx,path,OFFC,ta,160,9)
        flow_path(ctx,[(tx+220,TOP+40),(tx+60,TOP+40),(tx+60,TOP+140),(tx+220,TOP+140),(tx+260,TOP+140),(tx+260,TOP+40),(tx+220,TOP+40)],OFFC,ta,140,6)
    # saturation flip indicator
    ph=(ta*2.2)%1
    sat = ph>0.45 and ph<0.55
    if sat:
        txt(ctx,"磁芯饱和 → 极性翻转",960,860,44,REDX,bold=True)
    else:
        txt(ctx,"Q1 / Q2 交替导通 · 近似方波输出",960,860,44,A,bold=True)
    # output waveform mini
    px,py,pw,ph=1380,400,480,280
    rect(ctx,px-20,py-50,pw+40,ph+100,G2,3,fill=PAN)
    txt(ctx,"输出（近似方波）",px,py-25,34,A,'l')
    def sq(u):
        return 0.85 if (u%1)<0.5 else -0.85
    plot(ctx,px,py,pw,ph,sq,A,6,ta-3,ta,n=800,zero=0.5)
    txt(ctx,"自激推挽 DC→AC",960,940,42,D,bold=True)
    txt(ctx,"与单电感 Buck/Boost 不同谱系，同属开关变换思想",960,1000,34,G2)

# ---------------- duty helpers ----------------
def buck_D(t):
    # dwell1 ~14.3–19.3 D=0.35; ramp ~1s; dwell2 ~20.3–27.6 D=0.70
    if t<19.3: return 0.35
    if t<20.3: return 0.35+0.35*ramp(t,19.3,20.3)
    return 0.70

def boost_D(t):
    # dwell1 ~28.3–33.8 D=0.40; ramp ~1s; dwell2 ~34.8–41.6 D=0.65
    if t<33.8: return 0.40
    if t<34.8: return 0.40+0.25*ramp(t,33.8,34.8)
    return 0.65

def is_on(t,Df):
    return ((t%P)/P)<Df(t)

def wave_panel(ctx,ta,Df,on,mode='buck'):
    """iL triangle + Vsw or Vout curve."""
    px,pw=1120,720
    t0=ta-4.0*P
    g=lambda tau: 0.9 if ((tau%P)/P)<Df(tau) else -0.9
    def il(tau):
        Dd=Df(tau); p=(tau%P)/P
        r=(-1+2*p/Dd) if p<Dd else (1-2*(p-Dd)/max(1-Dd,0.05))
        return 0.5+(Dd-0.5)*0.3+0.35*r
    if mode=='buck':
        # switch node: Vin when on, ~0 when off (ideal diode)
        def vsw(tau):
            return 0.85 if ((tau%P)/P)<Df(tau) else -0.15
        vlab="开关节点 Vsw"; vc=ACC
    else:
        # boost switch node: 0 when on, Vout when off
        def vsw(tau):
            return -0.15 if ((tau%P)/P)<Df(tau) else 0.85
        vlab="开关节点 Vsw"; vc=ACC
    txt(ctx,"驱动 G",px,230,34,A,'l')
    plot(ctx,px,250,pw,90,g,A,4,t0,ta,n=900,zero=0.5)
    txt(ctx,"电感电流 iL",px,390,34,A,'l')
    plot(ctx,px,410,pw,160,il,D,5,t0,ta,n=900,zero=0.92,amp=140)
    txt(ctx,vlab,px,620,34,vc,'l')
    plot(ctx,px,640,pw,140,vsw,vc,5,t0,ta,n=900,zero=0.55)
    txt(ctx,"导通" if on else "关断",px+pw,230,38,ONC if on else OFFC,'r',bold=True)

TOP,BOT=300,640

def buck(ctx,ta):
    titlebar(ctx,"Buck 降压变换器","Vout ≈ D · Vin")
    Dd=buck_D(ta); on=is_on(ta,buck_D)
    VinX=150
    battery(ctx,VinX,TOP,BOT,D)
    txt(ctx,"Vin",75,470,42,D,bold=True); txt(ctx,"12 V",75,520,32,G2)
    # Upright high-side BJT: C to Vin+, E is switch node (horizontal to L)
    bx=360
    C,E,B=npn(ctx,bx,TOP+110,1.3,on=on)
    # Vin+ along top to above collector, down to C
    line(ctx,[(VinX,TOP),(C[0],TOP)],D,6)
    line(ctx,[(C[0],TOP),C],D,6)
    # ground rail
    line(ctx,[(VinX,BOT),(1020,BOT)],D,6)
    # switch node = emitter; horizontal bus at ey
    ey=E[1]; swx=E[0]
    line(ctx,[E,(swx+30,ey)],D,6)  # short out from emitter
    nx=swx+30  # node x after emitter
    dot(ctx,nx,ey,9,D)
    # diode anode at ground, cathode at switch node (ey)
    diode(ctx,(nx,BOT),(nx,ey),ONC if not on else D,6,38,fill=hx('#1a7f37',0.3) if not on else None)
    # ensure diode vertical leads: diode() already draws
    line(ctx,[(nx,BOT),(nx,BOT)],D,0)
    dot(ctx,nx,BOT,8,D)
    txt(ctx,"S",bx-100,TOP+110,42,ONC if on else D,bold=True)
    line(ctx,[B,(B[0]-50,B[1])],G2,4)
    txt(ctx,"基极驱动",B[0]-60,B[1]+45,30,G2,'r')
    txt(ctx,"D",nx-50,(ey+BOT)/2,42,OFFC if not on else G2,bold=True)
    # inductor at ey height
    L0,L1=nx+50,780
    line(ctx,[(nx,ey),(L0,ey)],D,6)
    draw_L(ctx,L0,ey,L1,D,6,n=5)
    txt(ctx,"L",(L0+L1)/2,ey-55,42,D,bold=True)
    line(ctx,[(L1,ey),(900,ey)],D,6)
    capacitor(ctx,(900,ey),(900,BOT),D,6)
    txt(ctx,"C",850,(ey+BOT)/2,42,D,bold=True); dot(ctx,900,ey,8); dot(ctx,900,BOT,8)
    line(ctx,[(900,ey),(1020,ey)],D,6)
    resistor(ctx,(1020,ey),(1020,BOT),D,6,body=120)
    txt(ctx,"R",1075,(ey+BOT)/2,42,D,bold=True)
    # CURRENT: follow wires; wavy only on L
    coil=wavy_pts(L0,ey,L1,n=5,amp=32)
    if on:
        path=[(VinX,TOP+50),(VinX,TOP),(C[0],TOP),C,E,(nx,ey)]+coil+[(900,ey),(1020,ey),(1020,BOT),(VinX,BOT),(VinX,BOT-40)]
        flow_path(ctx,path,ONC,ta,180,10)
        txt(ctx,"导通：Vin → S(BJT) → L → 负载",560,720,40,ONC,bold=True)
    else:
        path=[(nx,BOT),(nx,ey)]+coil+[(900,ey),(1020,ey),(1020,BOT),(nx,BOT)]
        flow_path(ctx,path,OFFC,ta,180,10)
        txt(ctx,"关断：L 经二极管续流",560,720,40,OFFC,bold=True)
    txt(ctx,"电流沿导线正交走线；电感处沿线圈示意",560,770,32,G2)
    wave_panel(ctx,ta,buck_D,on,'buck')
    txt(ctx,f"D = {Dd:.2f}　　Vout ≈ D·Vin = {Dd*12:.1f} V",960,920,50,D,bold=True)
    if ta<19.8:
        txt(ctx,"工况① 低占空比（停留观察）",960,980,36,A,bold=True)
    else:
        txt(ctx,"工况② 高占空比（停留观察）",960,980,36,A,bold=True)

def boost(ctx,ta):
    titlebar(ctx,"Boost 升压变换器","Vout = Vin / (1 − D)")
    Dd=boost_D(ta); on=is_on(ta,boost_D)
    VinX=150
    battery(ctx,VinX,TOP,BOT,D)
    txt(ctx,"Vin",75,470,42,D,bold=True); txt(ctx,"12 V",75,520,32,G2)
    line(ctx,[(VinX,TOP),(280,TOP)],D,6)
    line(ctx,[(VinX,BOT),(1020,BOT)],D,6)
    L0,L1=280,500
    draw_L(ctx,L0,TOP,L1,D,6,n=5)
    txt(ctx,"L",(L0+L1)/2,TOP-55,42,D,bold=True)
    swx=560
    line(ctx,[(L1,TOP),(swx,TOP)],D,6); dot(ctx,swx,TOP,9); dot(ctx,swx,BOT,8)
    # upright BJT shunt
    C,E,B=npn(ctx,swx-5,470,1.25,on=on)
    line(ctx,[(swx,TOP),C],D,6)
    line(ctx,[E,(swx,BOT)],D,6)
    line(ctx,[B,(B[0]-40,B[1])],G2,4)
    txt(ctx,"S",swx-115,470,42,ONC if on else D,bold=True)
    # diode to output
    diode_lr(ctx,(swx,TOP),(740,TOP),on=(not on),s=36)
    txt(ctx,"D",650,TOP-55,42,OFFC if not on else G2,bold=True)
    line(ctx,[(740,TOP),(880,TOP)],D,6)
    capacitor(ctx,(880,TOP),(880,BOT),D,6)
    txt(ctx,"C",830,470,42,D,bold=True); dot(ctx,880,TOP,8); dot(ctx,880,BOT,8)
    line(ctx,[(880,TOP),(1020,TOP)],D,6)
    resistor(ctx,(1020,TOP),(1020,BOT),D,6,body=120)
    txt(ctx,"R",1075,470,42,D,bold=True)
    coil=wavy_pts(L0,TOP,L1,n=5,amp=32)
    if on:
        path=[(VinX,TOP+40),(VinX,TOP)]+coil+[(swx,TOP),C,E,(swx,BOT),(VinX,BOT),(VinX,BOT-40)]
        flow_path(ctx,path,ONC,ta,180,10)
        flow_path(ctx,[(880,TOP),(1020,TOP),(1020,BOT),(880,BOT),(880,TOP)],hx('#1a7f37',0.4),ta,100,6)
        txt(ctx,"导通：L 储能；电容供负载",560,710,40,ONC,bold=True)
    else:
        path=[(VinX,TOP+40),(VinX,TOP)]+coil+[(swx,TOP),(740,TOP),(880,TOP),(1020,TOP),(1020,BOT),(VinX,BOT),(VinX,BOT-40)]
        flow_path(ctx,path,OFFC,ta,180,10)
        txt(ctx,"关断：Vin + L 一起向负载放电",560,710,40,OFFC,bold=True)
    txt(ctx,"电流沿导线走线；电感处沿线圈示意",560,760,32,G2)
    wave_panel(ctx,ta,boost_D,on,'boost')
    txt(ctx,f"D = {Dd:.2f}　　Vout = Vin/(1−D) = {12/(1-Dd):.0f} V",960,920,50,D,bold=True)
    if ta<34.3:
        txt(ctx,"工况① 低占空比（停留观察）",960,980,36,A,bold=True)
    else:
        txt(ctx,"工况② 高占空比（停留观察）",960,980,36,A,bold=True)

def closing(ctx,ta):
    titlebar(ctx,"开关变换思想成型","自激推挽与单电感拓扑同源异流")
    cards=[
        (140,"Royer","自激推挽","DC→AC 方波\n磁反馈翻转",ACC),
        (700,"Buck","降压","Vout ≈ D·Vin",ONC),
        (1260,"Boost","升压","Vout = Vin/(1−D)",OFFC),
    ]
    for x,a,b,c,col_ in cards:
        rect(ctx,x,280,500,420,col_,6,fill=PAN,r=16)
        txt(ctx,a,x+250,400,56,col_,bold=True)
        txt(ctx,b,x+250,490,44,D)
        for i,line_s in enumerate(c.split('\n')):
            txt(ctx,line_s,x+250,560+i*50,34,G2)
    txt(ctx,"晶体管快速通断 + 磁储能 = 现代开关电源的起点",960,820,46,A,bold=True)
    txt(ctx,"（不展开具体应用场景）",960,900,34,G2)

def draw(ctx,t):
    t=clamp(t,0.5,44.5)
    # A 0.5-3.5; B 3.5-14; C 14-28; D 28-42; E 42-45
    aA=1-ramp(t,3.2,3.8)
    aB=ramp(t,3.2,3.8)*(1-ramp(t,13.6,14.3))
    aC=ramp(t,13.6,14.3)*(1-ramp(t,27.6,28.3))
    aD=ramp(t,27.6,28.3)*(1-ramp(t,41.6,42.3))
    aE=ramp(t,41.6,42.3)
    if aA>0.01: group(ctx,aA,intro,min(t,3.2))
    if aB>0.01: group(ctx,aB,royer,clamp(t,3.8,13.6))
    if aC>0.01: group(ctx,aC,buck,clamp(t,14.3,27.6))
    if aD>0.01: group(ctx,aD,boost,clamp(t,28.3,41.6))
    if aE>0.01: group(ctx,aE,closing,max(t,42.3))
