import lib
from lib import *
lib.BG=(0xf6/255,0xf8/255,0xfa/255)
D=hx('#1f2328'); A=hx('#b7791f'); G2=hx('#6e7781'); BL=hx('#0969da'); PAN=hx('#ffffff')
def kf(t):
    if t<6: return 0.6
    if t<10: return 0.6+0.4*ramp(t,6,9)
    if t<16: return 1.0-0.65*ramp(t,10.5,14)
    return 0.35+0.25*ramp(t,16,18.5)
def integ(f,t,n=200):
    if t<=0.5: return 0
    h=(t-0.5)/n; return sum(f(0.5+(i+0.5)*h) for i in range(n))*h
def T(ctx,s,x,y,sz=40,c=D,a='c',b=False): txt(ctx,s,x,y,sz,c,a,b)
def machine(ctx,x,y,lab,ang,r=90):
    circle(ctx,x,y,r,D,7,fill=PAN)
    for j in range(3):
        a=ang+j*2*math.pi/3
        line(ctx,[(x+r*0.35*math.cos(a),y+r*0.35*math.sin(a)),(x+r*0.78*math.cos(a),y+r*0.78*math.sin(a))],hx('#d0d7de'),8)
    T(ctx,lab,x,y,70 if len(lab)==1 else 56,A,b=True)
def shaft(ctx,x0,x1,y,ph):
    rect(ctx,x0,y-18,x1-x0,36,G2,4,fill=hx('#d0d7de'),r=6)
    for j in range(5):
        xx=x0+8+((j/5+ph)%1)*(x1-x0-16); line(ctx,[(xx,y-14),(xx-10,y+14)],A,5)
def draw(ctx,t):
    ta=clamp(t,0.5,19.5); k=kf(ta)
    rect(ctx,60,52,14,70,lw=0,fill=A,r=4); T(ctx,"沃德-伦纳德系统（Ward Leonard）",96,86,56,D,"l",True); T(ctx,"电 → 机械 → 电 → 机械",1860,86,40,A,"r")
    ctx.new_path()
    y=380
    a1=ta*2*math.pi*0.5; a2=integ(kf,ta)*2*math.pi*0.6
    # AC source
    circle(ctx,130,y,62,D,6,fill=PAN)
    line(ctx,[(130-38+i,y-24*math.sin(i/76*2*math.pi+ta*6)) for i in range(0,77,4)],A,6)
    T(ctx,"交流电网",130,y+100,38)
    line(ctx,[(130,y-62),(130,y-120),(330,y-120),(330,y-80)],D,6); line(ctx,[(192,y),(270,y)],D,6)
    flow(ctx,[(130,y-62),(130,y-120),(330,y-120),(330,y-80)],A,ta,120,6)
    machine(ctx,360,y,"M~",a1); T(ctx,"交流电动机",360,y+135,38)
    shaft(ctx,450,690,y,ta*0.8)
    machine(ctx,780,y,"G",a1); T(ctx,"直流发电机",675,y-110,36,D,"r")
    # armature loop
    mx=1230
    top=[(780,y-90),(780,y-150),(mx,y-150),(mx,y-90)]
    line(ctx,top,D,6); line(ctx,[(870,y),(1140,y)],D,6)
    flow(ctx,top,A,ta,60+220*k,5+5*k); flow(ctx,[(1140,y+0),(870,y)],A,ta,60+220*k,5+5*k)
    T(ctx,f"电枢直接相连   U = {220*k:.0f} V",1005,y-195,40,A,b=True)
    machine(ctx,mx,y,"M",a2); T(ctx,"直流电动机",1185,y-110,36,D,"r")
    fy,ry=670,790
    def fcoil(cx,c):
        inductor(ctx,(cx-60,y+120),(cx+60,y+120),c,6,body=110,n=4)
        line(ctx,[(cx-60,y+120),(cx-60,y+67)],c,6); line(ctx,[(cx+60,y+120),(cx+60,y+67)],c,6)
        dot(ctx,cx-60,y+67,8,c); dot(ctx,cx+60,y+67,8,c)
    fcoil(780,A); T(ctx,"励磁绕组",780,y+168,34,A,b=True)
    line(ctx,[(720,y+120),(620,y+120),(620,fy)],D,6); battery(ctx,620,fy,ry,D)
    line(ctx,[(620,ry),(1040,ry),(1040,fy)],D,6)
    resistor(ctx,(1040,fy),(880,fy),D,6,body=110)
    line(ctx,[(880,fy),(880,y+120),(840,y+120)],D,6)
    px=905+(1-k)*100
    arrow(ctx,px-40,fy+70,px+30,fy-45,BL,6)
    T(ctx,"变阻器",960,fy-70,36,BL,b=True)
    arr='↑' if (8<ta<10.6 or 16<ta<18.6) else ('↓' if 10.6<ta<14.2 else '')
    T(ctx,f"If {arr}",560,(fy+ry)/2,40,BL,'r',b=True)
    T(ctx,"励磁电源",830,ry+45,34,D)
    fcoil(1230,G2); T(ctx,"恒定励磁",1230,y+168,34,G2,b=True)
    line(ctx,[(1170,y+120),(1110,y+120),(1110,ry),(1360,ry)],G2,6); battery(ctx,1360,fy,ry,G2)
    line(ctx,[(1360,fy),(1360,y+120),(1290,y+120)],G2,6)
    T(ctx,"固定电源",1235,ry+45,34,G2)
    # shaft to drum + elevator
    dx=1480
    shaft(ctx,1320,dx-45,y,integ(kf,ta)*0.5)
    circle(ctx,dx,y,50,D,7,fill=hx('#d0d7de'))
    for j in range(4):
        a=a2+j*math.pi/2; line(ctx,[(dx,y),(dx+44*math.cos(a),y+44*math.sin(a))],D,4)
    pos=integ(kf,ta)*19
    cy=760-pos
    line(ctx,[(dx+50,y),(dx+50,cy-55)],D,4)
    rect(ctx,dx-10,cy-55,120,110,A,6,fill=hx('#fff4e0'))
    T(ctx,"电梯",dx+50,cy,36,A,b=True)
    line(ctx,[(dx-30,820),(dx+130,820)],G2,4)
    # tachometer
    line(ctx,[(dx,y-50),(dx,y-125),(1696,y-125),(1696,y-94)],G2,4,dash=[12,8])
    T(ctx,"同轴测速",1600,y-160,32,G2)
    tx,ty=1770,y-20
    circle(ctx,tx,ty,105,D,7,fill=PAN)
    for i in range(7):
        a=math.pi*(0.8+1.4*i/6)
        line(ctx,[(tx+78*math.cos(a),ty+78*math.sin(a)),(tx+95*math.cos(a),ty+95*math.sin(a))],D,4)
    a=math.pi*(0.8+1.4*k)
    line(ctx,[(tx,ty),(tx+80*math.cos(a),ty+80*math.sin(a))],BL,8); dot(ctx,tx,ty,11,BL)
    T(ctx,"转速表",tx,ty+50,32,G2)
    T(ctx,f"n = {1500*k:.0f}",tx,ty+150,46,BL,b=True); T(ctx,"r/min",tx,ty+200,34,G2)
    # energy flow
    ey=950
    for bx,s in [(250,"电（交流）"),(730,"机械"),(1210,"电（直流）"),(1690,"机械（负载）")]:
        rect(ctx,bx-170,ey-48,340,96,A,5,fill=PAN); T(ctx,s,bx,ey,42,D,b=True)
    for xa in (420,900,1380):
        xb=xa+140
        line(ctx,[(xa,ey),(xb,ey)],hx('#b7791f',0.35),4)
        for j in range(3):
            ph=(j/3+ta*0.6)%1; arrowhead(ctx,xa+15+ph*(xb-xa-15),ey,0,(A[0],A[1],A[2],math.sin(ph*math.pi)),30)
