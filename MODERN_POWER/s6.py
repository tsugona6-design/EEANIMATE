from lib import *
A=hx('#39d0d8'); SI=hx('#8b949e'); WB=hx('#d2a8ff'); OR=hx('#e3a857')
def sync(ctx,ta):
    title(ctx,"同步整流：MOSFET 取代二极管",A,"降低导通损耗")
    m=ramp(ta,2.4,3.4)
    cx,cy=560,560
    line(ctx,[(cx,260),(cx,cy-150)],FG,7); line(ctx,[(cx,cy+150),(cx,880)],FG,7)
    def dio(c): diode(c,(cx,cy+150),(cx,cy-150),FG,8,90)
    group(ctx,1-m,dio)
    def fet(c):
        c.save(); d,s,g=nmos(c,cx-50,cy,2.5,on=True,oncol=A,lw=7); c.restore()
        line(c,[(cx,cy-150),d],A,7); line(c,[s,(cx,cy+150)],A,7)
        txt(c,"G",g[0]-40,g[1],44,A,bold=True)
    group(ctx,m,fet)
    flow(ctx,[(cx,880),(cx,cy+165)],OR,ta,180,8); flow(ctx,[(cx,cy-165),(cx,260)],OR,ta,180,8)
    txt(ctx,"整流二极管" if m<0.5 else "同步整流 MOSFET",cx,190,52,A if m>=0.5 else FG,bold=True)
    txt(ctx,"P ≈ Vf · I（Vf≈0.7 V）" if m<0.5 else "P ≈ I² · Rds(on)",cx,960,48,FG)
    # loss bar
    bx,by,bh,bw=1250,280,560,150
    loss=1-0.8*m
    rect(ctx,bx,by,bw,bh,GREY,4,r=10)
    hh=(bh-12)*loss
    c=(RED[0]*(1-m)+A[0]*m,RED[1]*(1-m)+A[1]*m,RED[2]*(1-m)+A[2]*m,1)
    rect(ctx,bx+6,by+bh-6-hh,bw-12,hh,lw=0,fill=c,r=8)
    txt(ctx,"导通损耗",bx+bw/2,by-50,46,FG,bold=True)
    txt(ctx,f"{loss*100:.0f}%",bx+bw+30,by+bh-hh,48,c,'l',bold=True)
def sic(ctx,ta):
    title(ctx,"宽禁带器件：Si → SiC / GaN",A,"开关更快、体积更小")
    pr=clamp((ta-6.4)/1.8)
    for k,(y0,name,c,rt) in enumerate([(260,"Si MOSFET",SI,0.09),(560,"SiC / GaN",A,0.012)]):
        x0,w,h=230,900,200
        txt(ctx,name,x0,y0-30,46,c,'l',bold=True)
        line(ctx,[(x0,y0+h),(x0+w,y0+h)],GREY,2.5)
        def v(u,rt=rt):
            q=u%0.5
            if q<0.25: return clamp(q/rt)
            return 1-clamp((q-0.25)/rt)
        pts=[(x0+w*j/599,y0+h-v(j/599)*h*0.9) for j in range(max(2,int(600*pr)))]
        line(ctx,pts,c,7)
    txt(ctx,"开关沿更陡 → 开关损耗更低、频率更高",680,880,44,FG,bold=True)
    # size boxes
    s=ramp(ta,8.2,9.4)
    bx=1650
    rect(ctx,bx-170,260,340,240,SI,5,fill=hx('#21262d'))
    txt(ctx,"Si 方案",bx,380,44,SI,bold=True)
    sz=240-80*s
    rect(ctx,bx-sz/2,560,sz,sz*0.7,A,5,fill=hx('#0f2a2c'))
    txt(ctx,"SiC/GaN",bx,560+sz*0.35,36,A,bold=True)
    if s>0.5: txt(ctx,"同功率，体积更小",bx,880,42,A,bold=True)
def bidir(ctx,ta):
    title(ctx,"双向 DC/DC：能量可正可反",A,"储能 · 新能源汽车")
    fwd=ta<15.5
    rv=ramp(ta,15.3,15.7)
    yc=600
    # battery
    rect(ctx,110,yc-130,250,260,A,6,fill=hx('#11161d'))
    rect(ctx,205,yc-155,60,25,A,0,fill=A,r=5)
    soc=0.8-0.25*clamp((ta-11)/4.5)+0.25*clamp((ta-15.5)/4)
    hh=200*soc
    rect(ctx,140,yc+100-hh,190,hh,lw=0,fill=hx('#39d0d8',0.6),r=6)
    txt(ctx,"电池",235,yc+180,46,FG,bold=True)
    txt(ctx,f"{soc*100:.0f}%",235,yc,44,WHITE,bold=True)
    # DC/DC box with two mosfets & inductor
    bx0,bx1=520,960
    rect(ctx,bx0,yc-170,bx1-bx0,340,A,6,fill=hx('#11161d'))
    txt(ctx,"双向 DC/DC",(bx0+bx1)/2,yc+215,46,FG,bold=True)
    inductor(ctx,(bx0,yc),(720,yc),FG,5,body=110,n=3)
    d1,s1,_=nmos(ctx,780,yc-80,0.85,lw=5,on=(int(ta*4)%2==0),oncol=A)
    d2,s2,_=nmos(ctx,780,yc+80,0.85,lw=5,on=(int(ta*4)%2==1),oncol=A)
    line(ctx,[(720,yc),(d1[0],yc)],FG,5); line(ctx,[s1,d2],FG,5)
    line(ctx,[d1,(d1[0],yc-150),(bx1,yc-150)],FG,5); line(ctx,[s2,(s2[0],yc+150),(bx1,yc+150)],FG,5)
    # bus
    busx=1120
    line(ctx,[(busx,yc-200),(busx,yc+200)],OR,14)
    txt(ctx,"直流母线",busx,yc+250,42,OR,bold=True)
    # inverter + grid/motor
    rect(ctx,1260,yc-110,280,220,A,6,fill=hx('#11161d'))
    txt(ctx,"逆变器",1400,yc-30,44,FG,bold=True); txt(ctx,"DC ⇄ AC",1400,yc+35,38,GREY)
    circle(ctx,1730,yc-80,70,FG,6,fill=hx('#11161d')); txt(ctx,"M",1730,yc-80,60,OR,bold=True)
    txt(ctx,"电机",1840,yc-80,38,FG,'l') if False else None
    for i in range(3):
        x=1660+i*60; line(ctx,[(x,yc+70),(x,yc+150)],FG,5)
    line(ctx,[(1640,yc+70),(1820,yc+70)],FG,5)
    txt(ctx,"电机 / 电网",1730,yc+200,42,FG,bold=True)
    line(ctx,[(1540,yc),(1600,yc),(1600,yc-80),(1660,yc-80)],FG,5)
    line(ctx,[(1600,yc),(1600,yc+70),(1640,yc+70)],FG,5)
    # energy flows
    segs=[[(360,yc),(bx0,yc)],[(bx1,yc),(busx,yc)],[(busx,yc),(1260,yc)]]
    c=OR if fwd else A
    for sgm in segs:
        pts=sgm if fwd else sgm[::-1]
        flow(ctx,pts,c,ta,200,10)
    # MCU
    rect(ctx,600,190,580,130,WB,6,fill=hx('#1d1630'))
    txt(ctx,"数字控制 / MCU",890,255,50,WB,bold=True)
    for x in (740,1040):
        line(ctx,[(x,320),(x,yc-175 if x<960 else yc-205)],WB,4,dash=[14,10],off=-ta*60)
    txt(ctx,"PWM",700,380,34,WB,'r'); txt(ctx,"采样",1080,380,34,WB,'l')
    lab="放电：电池 → 母线 → 电机/电网" if fwd else "充电/回馈：电机/电网 → 母线 → 电池"
    txt(ctx,lab,960,960,52,c,bold=True)
    big=1 if fwd else -1
    ax=960; 
    if fwd: arrow(ctx,ax-140,1030,ax+140,1030,c,8)
    else: arrow(ctx,ax+140,1030,ax-140,1030,c,8)
def draw(ctx,t):
    ta=clamp(t,0.5,19.5)
    a=ramp(t,5.7,6.3); b=ramp(t,10.7,11.3)
    group(ctx,1-a,sync,min(ta,5.7))
    group(ctx,a*(1-b),sic,clamp(ta,6.3,10.7))
    group(ctx,b,bidir,max(ta,11.3))
