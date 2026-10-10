from lib import *
A=hx('#d2a8ff'); B2=hx('#5fb3f9'); SINC=hx('#e3a857')
def tri(u,n):  # carrier, u in [0,1]
    x=(u*n)%1; return 4*abs(x-0.5)-1
def pwmgen(ctx,ta):
    title(ctx,"正弦 PWM：载波比较",A,"调制信号 > 载波 → 输出高")
    px,pw=180,1600
    prog=clamp((ta-0.5)/5.8)
    n=14; m=0.8
    s=lambda u: m*math.sin(2*math.pi*u)
    c=lambda u: tri(u,n)
    txt(ctx,"三角载波",px,230,42,GREY,'l'); txt(ctx,"调制信号（正弦）",px+260,230,42,SINC,'l')
    plot(ctx,px,270,pw,330,c,GREY,3,0,1,n=1600,prog=prog)
    plot(ctx,px,270,pw,330,s,SINC,7,0,1,n=1600,prog=prog,axis=False)
    txt(ctx,"PWM 输出",px,665,42,A,'l')
    p=lambda u: 0.9 if s(u)>c(u) else -0.9
    plot(ctx,px,700,pw,220,p,A,5,0,1,n=3000,prog=prog)
    xc=px+pw*prog
    line(ctx,[(xc,270),(xc,920)],hx('#ffffff',0.5),3)
    txt(ctx,"正半周脉冲变宽，负半周变窄 → 宽度按正弦变化",960,990,44,FG)
F=0.25  # fundamental Hz
NC=12
def hb_state(tt):
    u=(tt*F)%1
    s=0.85*math.sin(2*math.pi*u); c=tri(u,NC)
    return (s>c), s
def hbridge(ctx,ta):
    title(ctx,"MOSFET H 桥逆变：对角交替导通",A,"直流 → 交流")
    TOP,BOT,MID=260,800,530
    xl,xr=560,1100
    pwm,s=hb_state(ta)
    pos=pwm  # bipolar PWM: Q1Q4 when pwm high else Q2Q3
    line(ctx,[(200,TOP),(xr,TOP)]); line(ctx,[(200,BOT),(xr,BOT)])
    battery(ctx,200,TOP,BOT); txt(ctx,"Vdc",110,MID,46,FG,bold=True)
    on={1:pos,4:pos,2:not pos,3:not pos}
    cA=A; cB=B2
    d1,s1,_=nmos(ctx,xl-20,395,1.2,on=on[1],oncol=cA); d3,s3,_=nmos(ctx,xl-20,665,1.2,on=on[3],oncol=cB)
    d2,s2,_=nmos(ctx,xr+20,395,1.2,mirror=True,on=on[2],oncol=cB); d4,s4,_=nmos(ctx,xr+20,665,1.2,mirror=True,on=on[4],oncol=cA)
    for d,sx in [(d1,s1),(d3,s3)]: pass
    line(ctx,[(xl,TOP),d1]); line(ctx,[s1,d3]); line(ctx,[s3,(xl,BOT)])
    line(ctx,[(xr,TOP),d2]); line(ctx,[s2,d4]); line(ctx,[s4,(xr,BOT)])
    for x in (xl,xr):
        dot(ctx,x,TOP); dot(ctx,x,BOT); dot(ctx,x,MID)
    txt(ctx,"Q1",xl-150,395,44,cA if on[1] else FG,bold=True); txt(ctx,"Q3",xl-150,665,44,cB if on[3] else FG,bold=True)
    txt(ctx,"Q2",xr+150,395,44,cB if on[2] else FG,bold=True); txt(ctx,"Q4",xr+150,665,44,cA if on[4] else FG,bold=True)
    inductor(ctx,(xl,MID),(830,MID),FG,body=130,n=4); resistor(ctx,(830,MID),(xr,MID),FG,body=120)
    txt(ctx,"负载",830,MID+65,40,GREY)
    txt(ctx,"A",xl+30,MID-40,38,GREY); txt(ctx,"B",xr-30,MID-40,38,GREY)
    if pos: flow(ctx,[(200,TOP+80),(200,TOP),(xl,TOP),(xl,MID),(xr,MID),(xr,BOT),(200,BOT),(200,BOT-80)],cA,ta,220)
    else:   flow(ctx,[(200,TOP+80),(200,TOP),(xr,TOP),(xr,MID),(xl,MID),(xl,BOT),(200,BOT),(200,BOT-80)],cB,ta,220)
    # load current arrow (filtered, follows sine)
    il=math.sin(2*math.pi*(ta*F)-0.3)
    ac=SINC
    if abs(il)>0.08:
        L=60+90*abs(il)
        if il>0: arrow(ctx,830-L,875,830+L,875,ac,7)
        else: arrow(ctx,830+L,875,830-L,875,ac,7)
    txt(ctx,"负载电流 " + ("A→B" if il>0.08 else ("B→A" if il<-0.08 else "≈0")),830,935,42,ac,bold=True)
    # plot panel
    px,pw,py,ph=1340,520,300,420
    rect(ctx,px-30,py-60,pw+60,ph+140,hx('#30363d'),3,fill=hx('#11161d'))
    t0=ta-1/F
    v=lambda tau: 0.8 if hb_state(tau)[0] else -0.8
    plot(ctx,px,py,pw,ph,v,hx('#d2a8ff',0.55),3,t0,ta,n=1500)
    plot(ctx,px,py,pw,ph,lambda tau: math.sin(2*math.pi*tau*F-0.3)*0.75,SINC,8,t0,ta,n=400,axis=False)
    txt(ctx,"桥臂电压（PWM）",px,py-30,36,A,'l')
    txt(ctx,"滤波后输出（正弦）",px,py+ph+40,38,SINC,'l')
    txt(ctx,"Q1、Q4 导通" if pos else "Q2、Q3 导通",300,1010,48,cA if pos else cB,bold=True)
    txt(ctx,"对角两管成对开关，另一对关断",1590,1010,40,FG)
    dot(ctx,px+pw,py+ph/2-math.sin(2*math.pi*ta*F-0.3)*0.75*ph/2*0.92,11,SINC)
def draw(ctx,t):
    ta=clamp(t,0.5,19.5)
    a=ramp(t,6.6,7.4)
    group(ctx,1-a,pwmgen,min(ta,6.6))
    group(ctx,a,hbridge,max(ta,7.4)*0.6+0)  # slowed visual time
