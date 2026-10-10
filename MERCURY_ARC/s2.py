from lib import *
import random
DUR=30.0
BG=(0xf6/255,0xf8/255,0xfa/255)
D=hx('#1f2328'); A=hx('#0969da'); G2=hx('#6e7781'); PAN=hx('#ffffff')
PH=[hx('#bf8700'),hx('#1a7f37'),hx('#cf222e')]
ARC=hx('#0550ae'); MER=hx('#8b949e')
# timing
# 0.5-9.5 structure; 9.5-10.2 fade; 10.2-17.5 waveforms; 17.5-18.2 fade;
# 18.2-27.0 grid control; 27.0-27.5 fade; 27.5-29.5 application; 29.5-30 hold
def alpha_deg(t):
    # 0 until ~20s, then ramp to 75° by 25.5
    return 75*ramp(t,20.0,25.5)
def vout_val(th,al):
    # three-phase full envelope of positive peaks delayed by alpha
    a=math.radians(al); best=0; bv=-2
    for k in range(3):
        # natural commutation at 30+k*120; delayed by alpha
        start=math.radians(30)+a+k*2*math.pi/3
        age=(th-start)%(2*math.pi)
        if age<2*math.pi/3:
            v=math.sin(th-k*2*math.pi/3)
            if v>bv: bv=v; best=k
    return best, max(bv,0)
def bulb(ctx,cx,cy,active=None,ta=0,show_grid=False,arc_to=None,ignite=False):
    # glass envelope
    ctx.new_path(); ctx.move_to(cx-210,cy+190)
    ctx.curve_to(cx-250,cy-20,cx-160,cy-200,cx,cy-220)
    ctx.curve_to(cx+160,cy-200,cx+250,cy-20,cx+210,cy+190)
    ctx.curve_to(cx+120,cy+255,cx-120,cy+255,cx-210,cy+190); ctx.close_path()
    col(hx('#0969da',0.06),ctx); ctx.fill_preserve(); col(G2,ctx); ctx.set_line_width(6); ctx.stroke()
    # mercury pool
    ctx.new_path(); ctx.save(); ctx.translate(cx,cy+175); ctx.scale(170,38); ctx.arc(0,0,1,0,2*math.pi); ctx.restore()
    col(hx('#57606a'),ctx); ctx.fill()
    ctx.new_path(); ctx.save(); ctx.translate(cx,cy+160); ctx.scale(150,18); ctx.arc(0,0,1,0,2*math.pi); ctx.restore()
    col(hx('#8b949e'),ctx); ctx.fill()
    txt(ctx,"汞池阴极 (−)",cx,cy+260,42,D,bold=True)
    # cathode lead
    line(ctx,[(cx,cy+195),(cx,cy+255)],D,6); arrow(ctx,cx,cy+220,cx,cy+255,A,5,18)
    txt(ctx,"阴极引出",cx+85,cy+240,32,A,'l')
    # anodes
    ax=[cx-140,cx,cx+140]; ay=cy-70
    for i in range(3):
        # anode stem from top
        line(ctx,[(ax[i],cy-210),(ax[i],ay-50)],D,5)
        rect(ctx,ax[i]-28,ay-50,56,70,D,4,fill=hx('#d0d7de'),r=6)
        if show_grid:
            # grid as dashed ring under anode
            line(ctx,[(ax[i]-48,ay+40),(ax[i]+48,ay+40)],A,5,dash=[12,8])
            # gate lead
            line(ctx,[(ax[i]+48,ay+40),(ax[i]+90,ay+40)],A,4)
        txt(ctx,"ABC"[i],ax[i],ay-70,36,PH[i],bold=True)
        if i==2:
            txt(ctx,"阳极",ax[i]+70,ay-20,40,D,'l',bold=True)
            if show_grid: txt(ctx,"栅极",ax[i]+100,ay+45,40,A,'l',bold=True)
    # starting/igniter electrode
    ix,iy=cx-195,cy+100
    line(ctx,[(ix,cy-210),(ix,iy)],G2,5)
    # tip dipping toward pool
    line(ctx,[(ix,iy),(ix+40,cy+155)],G2,5)
    circle(ctx,ix+40,cy+155,10,G2,4,fill=hx('#d0d7de'))
    txt(ctx,"引燃极",ix-20,iy-30,36,G2,'r')
    if ignite:
        # spark to pool
        random.seed(int(ta*20))
        pts=[(ix+40,cy+155)]
        for j in range(6):
            u=(j+1)/6
            pts.append((ix+40+(cx-ix-40)*u+random.uniform(-10,10),
                        cy+155+(cy+175-cy-155)*u+random.uniform(-6,6)))
        line(ctx,pts,hx('#0969da',0.8),5)
    # main arc
    if arc_to is not None:
        random.seed(int(ta*40)+arc_to)
        x0=cx+random.uniform(-50,50); y0=cy+155
        x1,y1=ax[arc_to],ay+20
        pts=[]
        for j in range(14):
            u=j/13
            pts.append((x0+(x1-x0)*u+(random.uniform(-16,16) if 0<j<13 else 0),
                        y0+(y1-y0)*u+(random.uniform(-8,8) if 0<j<13 else 0)))
        for w,al in [(46,0.10),(26,0.22),(10,0.85)]:
            line(ctx,pts,(ARC[0],ARC[1],ARC[2],al),w)
        ctx.new_path(); ctx.arc(x0,y0,28,0,2*math.pi); col(hx('#0969da',0.45),ctx); ctx.fill()
        # unidirectional arrow (right of bulb, clear of igniter)
        mx=cx+250; my=cy+40
        arrow(ctx,mx,my+55,mx,my-55,A,7,28)
        txt(ctx,"单向导通",mx+30,my-10,36,A,'l',bold=True)
        txt(ctx,"阴极 → 阳极",mx+30,my+40,34,A,'l')
def structure(ctx,ta):
    rect(ctx,60,52,14,70,lw=0,fill=A,r=4)
    txt(ctx,"汞弧整流器：结构剖视",96,86,54,D,'l',bold=True)
    txt(ctx,"电子整流 · 无旋转机械",1860,86,38,A,'r')
    # progressive reveal
    show_grid=False
    # which anode is lit
    th=(ta*2*math.pi*0.4)%(2*math.pi)
    k,_=vout_val(th,0)
    ign=0.8<ta<2.5 or (int(ta*3)%11==0 and ta>3)
    bulb(ctx,520,480,active=k,ta=ta,show_grid=False,arc_to=k if ta>2.2 else None,ignite=ign and ta<4)
    # callouts panel
    px=1050
    rect(ctx,px,200,780,720,G2,4,fill=PAN,r=16)
    items=[
        (0.5,"① 玻璃泡内抽成真空，底部是液态汞池阴极"),
        (2.0,"② 顶部插入多个石墨阳极，接交流各相"),
        (3.5,"③ 引燃极短暂接触汞池，点燃初始电弧"),
        (5.0,"④ 电弧跳到电位最高的阳极，维持导通"),
        (6.5,"⑤ 电流只能从阴极流向阳极 → 整流作用"),
        (8.0,"⑥ 工频工作，没有机械旋转部件"),
    ]
    for t0,s in items:
        a=ramp(ta,t0,t0+0.6)
        if a<=0: continue
        y=250+items.index((t0,s))*100
        col((A[0],A[1],A[2],a),ctx)
        ctx.arc(px+50,y,14,0,2*math.pi); ctx.fill()
        txt(ctx,s,px+80,y,36,(D[0],D[1],D[2],a),'l')
    # diode symbol inset
    if ta>7.0:
        a=ramp(ta,7.0,7.8)
        group(ctx,a,lambda c: (
            diode(c,(px+180,820),(px+380,820),A,8,50),
            txt(c,"等效：单向整流",px+500,820,40,A,'l',bold=True)
        ))
def waveforms(ctx,ta):
    rect(ctx,60,52,14,70,lw=0,fill=A,r=4)
    txt(ctx,"三相交流 → 脉动直流",96,86,54,D,'l',bold=True)
    txt(ctx,"工频整流、无机械旋转",1860,86,38,A,'r')
    # three phase sources icons
    for i,n in enumerate("ABC"):
        x=160+i*160
        circle(ctx,x,250,48,PH[i],5,fill=PAN)
        pts=[(x-28+j,250-18*math.sin(j/56*2*math.pi+ta*5+i*2*math.pi/3)) for j in range(0,57,3)]
        line(ctx,pts,PH[i],5)
        txt(ctx,n,x,310,40,PH[i],bold=True)
    arrow(ctx,620,250,750,250,A,7)
    txt(ctx,"汞弧整流",680,200,36,A)
    # output symbol
    rect(ctx,780,200,160,100,A,5,fill=PAN,r=10)
    txt(ctx,"Vdc",860,250,46,A,bold=True)
    # plot
    px,py,pw,ph=120,380,1680,460
    rect(ctx,px-20,py-40,pw+40,ph+120,G2,3,fill=PAN)
    U0=4*math.pi
    prog=clamp((ta-10.5)/5.5)
    for i in range(3):
        f=lambda u,i=i: math.sin(u-i*2*math.pi/3)
        plot(ctx,px,py,pw,ph,f,(PH[i][0],PH[i][1],PH[i][2],0.45),4,0,U0,n=900,prog=prog,axis=(i==0),zero=0.55)
    def vo(u):
        return vout_val(u%(2*math.pi),0)[1]
    pts=plot(ctx,px,py,pw,ph,vo,A,8,0,U0,n=1000,prog=prog,axis=False,zero=0.55)
    if len(pts)>2:
        ctx.new_path(); ctx.move_to(px,py+ph*0.55)
        for p in pts: ctx.line_to(*p)
        ctx.line_to(pts[-1][0],py+ph*0.55); ctx.close_path(); col(hx('#0969da',0.15),ctx); ctx.fill()
    # average
    avg=0.827
    yav=py+ph*0.55-avg*ph*0.55*0.92
    if prog>0.5:
        line(ctx,[(px,yav),(px+pw*prog,yav)],hx('#0969da',0.9),4,dash=[18,12])
        txt(ctx,"平均 Vdc",px+pw*prog-10,yav-36,40,A,'r',bold=True)
    # legend
    txt(ctx,"三相电压",px,py+ph+50,36,G2,'l')
    txt(ctx,"整流输出（脉动直流）",px+280,py+ph+50,36,A,'l',bold=True)
    txt(ctx,"包络线跟随最高正极电压",px+780,py+ph+50,36,G2,'l')
    # cursor
    if prog>0.05:
        cxp=px+pw*prog
        line(ctx,[(cxp,py),(cxp,py+ph)],hx('#1f2328',0.35),3)
def gridctrl(ctx,ta):
    rect(ctx,60,52,14,70,lw=0,fill=A,r=4)
    txt(ctx,"栅极相控：触发角 α 调压",96,86,54,D,'l',bold=True)
    al=alpha_deg(ta)
    txt(ctx,f"触发角 α = {al:.0f}°",1860,86,42,A,'r',bold=True)
    th=(ta*2*math.pi*0.45)%(2*math.pi)
    k,_=vout_val(th,al)
    bulb(ctx,420,500,active=k,ta=ta,show_grid=True,arc_to=k,ignite=False)
    # alpha dial (left of bulb, clear of cathode)
    dx,dy=140,620
    circle(ctx,dx,dy,78,D,5,fill=PAN)
    a=math.pi*(1.15+0.7*(al/90))
    line(ctx,[(dx,dy),(dx+58*math.cos(a),dy+58*math.sin(a))],A,8); dot(ctx,dx,dy,10,A)
    txt(ctx,"触发角 α",dx,dy+115,36,A,bold=True)
    # wave panel
    px,py,pw,ph=900,200,920,520
    rect(ctx,px-20,py-20,pw+40,ph+160,G2,3,fill=PAN)
    U0=4*math.pi
    for i in range(3):
        f=lambda u,i=i: math.sin(u-i*2*math.pi/3)
        plot(ctx,px,py,pw,ph,f,(PH[i][0],PH[i][1],PH[i][2],0.35),3,0,U0,n=800,axis=(i==0),zero=0.55)
    def vo(u):
        return vout_val(u%(2*math.pi),al)[1]
    pts=plot(ctx,px,py,pw,ph,vo,A,7,0,U0,n=1000,axis=False,zero=0.55)
    if len(pts)>2:
        ctx.new_path(); ctx.move_to(px,py+ph*0.55)
        for p in pts: ctx.line_to(*p)
        ctx.line_to(pts[-1][0],py+ph*0.55); ctx.close_path(); col(hx('#0969da',0.18),ctx); ctx.fill()
    avg=0.827*math.cos(math.radians(al))
    yav=py+ph*0.55-max(avg,0)*ph*0.55*0.92
    line(ctx,[(px,yav),(px+pw,yav)],hx('#cf222e',0.85),4,dash=[16,10])
    pct=max(avg/0.827*100,0)
    txt(ctx,f"平均 Vdc ≈ {pct:.0f}%",px+pw-10,yav-34,40,hx('#cf222e'),'r',bold=True)
    # firing marks
    for n in range(3):
        # mark delayed start for each phase in first cycle
        start=(math.radians(30)+math.radians(al)+n*2*math.pi/3)
        if start>U0: continue
        xx=px+pw*(start/U0)
        if 0<=start<=U0:
            line(ctx,[(xx,py),(xx,py+ph*0.55)],A,3,dash=[8,6])
            if n==0: txt(ctx,"α 延迟",xx+8,py+30,32,A,'l')
    txt(ctx,"α 增大 → 导通推迟 → 平均电压下降",px,py+ph+50,40,D,'l',bold=True)
    txt(ctx,"相控调压，晶闸管相控的前身",px,py+ph+110,44,A,'l',bold=True)
    # cursor
    cxp=px+pw*((ta*2*math.pi*0.45)%U0)/U0
    line(ctx,[(cxp,py),(cxp,py+ph)],hx('#1f2328',0.35),3)
def application(ctx,ta):
    rect(ctx,60,52,14,70,lw=0,fill=A,r=4)
    txt(ctx,"典型应用：直流牵引与电解供电",96,86,54,D,'l',bold=True)
    txt(ctx,"闸流管 / 引燃管同期并存",1860,86,36,G2,'r')
    # left: tram
    rect(ctx,80,180,860,780,G2,4,fill=PAN,r=16)
    txt(ctx,"电力牵引（电车 / 地铁）",510,240,44,A,bold=True)
    # overhead wire
    line(ctx,[(140,320),(860,320)],G2,4)
    # tram
    tx=200+((ta-27.5)*180)%480
    rect(ctx,tx,420,280,140,A,6,fill=hx('#ddf4ff'),r=10)
    for i in range(3):
        rect(ctx,tx+25+i*85,445,70,50,A,3,fill=PAN,r=4)
    circle(ctx,tx+60,580,22,D,5,fill=hx('#d0d7de')); circle(ctx,tx+220,580,22,D,5,fill=hx('#d0d7de'))
    line(ctx,[(tx+140,420),(tx+100,360),(tx+160,320)],D,5)
    # rails
    line(ctx,[(140,605),(860,605)],G2,5)
    line(ctx,[(140,620),(860,620)],G2,3)
    # rectifier box feeding tram
    rect(ctx,180,700,280,160,A,5,fill=hx('#ddf4ff'),r=10)
    txt(ctx,"汞弧整流",320,760,40,A,bold=True)
    txt(ctx,"AC → DC",320,820,36,D)
    arrow(ctx,480,780,560,780,A,6)
    rect(ctx,580,720,280,140,D,5,fill=PAN,r=10)
    txt(ctx,"直流牵引电机",720,790,38,D,bold=True)
    # right: electrolysis
    rect(ctx,980,180,860,780,G2,4,fill=PAN,r=16)
    txt(ctx,"电解 / 电化学直流电源",1410,240,44,A,bold=True)
    # tank
    rect(ctx,1120,360,580,320,D,6,fill=hx('#ddf4ff'),r=8)
    # electrodes
    for i,lab in enumerate([("阳极板","+"),("阴极板","−"),("阳极板","+")]):
        x=1220+i*180
        rect(ctx,x,400,50,240,D if i!=1 else A,5,fill=hx('#d0d7de') if i!=1 else hx('#0969da',0.4),r=4)
        txt(ctx,lab[1],x+25,520,44,A if i==1 else D,bold=True)
        txt(ctx,lab[0],x+25,670,32,A if i==1 else D)
    txt(ctx,"电解槽",1410,720,40,D,bold=True)
    # supply
    rect(ctx,1180,780,460,120,A,5,fill=hx('#ddf4ff'),r=10)
    txt(ctx,"汞弧整流 → 大电流 Vdc",1410,840,40,A,bold=True)
    # footnote
    txt(ctx,"同期还有闸流管、引燃管等气体放电管，同属可控电子整流路线",960,1000,38,G2)
def draw(ctx,t):
    t=clamp(t,0.5,29.5)
    # segments with crossfades
    a1=1-ramp(t,9.5,10.2)
    a2=ramp(t,9.5,10.2)*(1-ramp(t,17.5,18.2))
    a3=ramp(t,17.5,18.2)*(1-ramp(t,27.0,27.5))
    a4=ramp(t,27.0,27.5)
    if a1>0.01: group(ctx,a1,structure,min(t,9.5))
    if a2>0.01: group(ctx,a2,waveforms,max(t,10.2))
    if a3>0.01: group(ctx,a3,gridctrl,max(t,18.2))
    if a4>0.01: group(ctx,a4,application,max(t,27.5))
