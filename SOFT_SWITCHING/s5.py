from lib import *
A=hx('#ff7b72'); VC=hx('#5fb3f9'); IC=hx('#e3a857'); ZC=hx('#7ee787')
def compare(ctx,ta):
    title(ctx,"硬开关 vs 软开关（ZVS）",A,"开关损耗 ∝ V × I 重叠")
    for k,(x0,name,zvs,t0) in enumerate([(130,"硬开关",False,0.5),(1010,"ZVS 软开关",True,3.5)]):
        prog=clamp((ta-t0)/2.5)
        al=1 if prog>0 else 0.25
        w,h,y0=780,440,300
        rect(ctx,x0-20,y0-90,w+40,h+300,hx('#30363d'),3,fill=hx('#11161d'))
        txt(ctx,name,x0+w/2,y0-40,52,ZC if zvs else A,bold=True)
        if prog<=0: 
            txt(ctx,"……",x0+w/2,y0+h/2,60,GREY); continue
        if not zvs:
            v=lambda u: 1-clamp((u-0.35)/0.3); i=lambda u: clamp((u-0.35)/0.3)
        else:
            v=lambda u: 1-ease((u-0.2)/0.2); i=lambda u: clamp((u-0.5)/0.25)
        N=500; n=int(N*prog)
        def Y(val): return y0+h-val*h*0.85
        if not zvs and n>2:
            ctx.new_path(); ctx.move_to(x0,Y(0))
            for j in range(n): u=j/(N-1); ctx.line_to(x0+w*u,Y(min(v(u),i(u))))
            ctx.line_to(x0+w*(n-1)/(N-1),Y(0)); ctx.close_path(); col(hx('#ff5a52',0.6),ctx); ctx.fill()
        line(ctx,[(x0,Y(0)),(x0+w,Y(0))],GREY,2.5)
        line(ctx,[(x0+w*j/(N-1),Y(v(j/(N-1)))) for j in range(max(n,2))],VC,7)
        line(ctx,[(x0+w*j/(N-1),Y(i(j/(N-1)))) for j in range(max(n,2))],IC,7)
        txt(ctx,"电压 V",x0+30,y0+10,40,VC,'l'); txt(ctx,"电流 I",x0+w-30,y0+10,40,IC,'r')
        if prog>0.85:
            if zvs:
                txt(ctx,"先把电压降到 0 再导通",x0+w/2,y0+h+70,44,ZC,bold=True)
                txt(ctx,"重叠 ≈ 0，损耗几乎消失",x0+w/2,y0+h+135,44,ZC)
                arrow(ctx,x0+w*0.45,y0+h*0.45,x0+w*0.42,Y(0)-14,ZC,5)
                txt(ctx,"ZVS",x0+w*0.47,y0+h*0.38,40,ZC,'l',bold=True)
            else:
                txt(ctx,"V 与 I 同时存在",x0+w/2,y0+h+70,44,A,bold=True)
                txt(ctx,"红色面积 = 开关损耗",x0+w/2,y0+h+135,44,A)
P=2.4; DT=0.05
def gates(p):
    return (DT<p<0.5-DT),(0.5+DT<p<1-DT)
def ir(p): return math.sin(2*math.pi*p-0.6)
def llc(ctx,ta):
    title(ctx,"LLC 谐振半桥",A,"谐振电流近似正弦，开关管 ZVS 导通")
    tt=ta-7.4
    p=(tt/P)%1
    g1,g2=gates(p); i=ir(p)
    TOP,BOT,MID=200,560,380
    line(ctx,[(150,TOP),(430,TOP)]); line(ctx,[(150,BOT),(1000,BOT)])
    battery(ctx,150,TOP,BOT); txt(ctx,"Vin",70,MID,44,FG,bold=True)
    d1,s1,_=nmos(ctx,410,265,1.0,on=g1,oncol=A); d2,s2,_=nmos(ctx,410,495,1.0,on=g2,oncol=A)
    line(ctx,[(430,TOP),d1]); line(ctx,[s1,d2]); line(ctx,[s2,(430,BOT)]); dot(ctx,430,MID)
    txt(ctx,"Q1",300,265,40,A if g1 else FG,bold=True); txt(ctx,"Q2",300,495,40,A if g2 else FG,bold=True)
    capacitor(ctx,(430,MID),(560,MID)); txt(ctx,"Cr",495,MID-65,40,FG,bold=True)
    inductor(ctx,(560,MID),(760,MID),FG,body=130,n=4); txt(ctx,"Lr",660,MID-60,40,FG,bold=True)
    line(ctx,[(760,MID),(960,MID)]); dot(ctx,850,MID); dot(ctx,850,BOT)
    inductor(ctx,(850,MID),(850,BOT),FG,body=110,n=3); txt(ctx,"Lm",800,(MID+BOT)/2,40,FG,'r',bold=True)
    inductor(ctx,(960,MID),(960,BOT),FG,body=130,n=4,flip=False)
    line(ctx,[(960,BOT),(1000,BOT)]) 
    line(ctx,[(995,MID),(995,BOT)],GREY,4); line(ctx,[(1007,MID),(1007,BOT)],GREY,4)
    # secondary
    ctx.save(); ctx.translate(2042,0); ctx.scale(-1,1); inductor(ctx,(1000,MID),(1000,BOT),FG,body=130,n=4); ctx.restore()
    txt(ctx,"变压器",990,BOT+50,36,GREY)
    cy=(MID+BOT)/2; R1,R2=TOP+10,BOT+70
    dot(ctx,1042,cy)
    line(ctx,[(1042,MID),(1080,MID),(1080,R1),(1120,R1)]); diode(ctx,(1120,R1),(1260,R1),FG,5,30); line(ctx,[(1260,R1),(1500,R1)])
    line(ctx,[(1042,BOT),(1120,BOT)]); diode(ctx,(1120,BOT),(1260,BOT),FG,5,30); line(ctx,[(1260,BOT),(1320,BOT),(1320,R1)]); dot(ctx,1320,R1)
    line(ctx,[(1042,cy),(1100,cy),(1100,BOT-16)]); ctx.new_path(); ctx.arc(1100,BOT,16,-math.pi/2,math.pi/2); col(FG,ctx); ctx.set_line_width(LW); ctx.stroke()
    line(ctx,[(1100,BOT+16),(1100,R2),(1500,R2)])
    txt(ctx,"D1",1190,R1-50,36,FG,bold=True); txt(ctx,"D2",1190,BOT-50,36,FG,bold=True)
    capacitor(ctx,(1410,R1),(1410,R2)); resistor(ctx,(1500,R1),(1500,R2))
    dot(ctx,1410,R1); dot(ctx,1410,R2)
    txt(ctx,"Co",1370,cy+20,38,FG,'r',bold=True); txt(ctx,"负载",1550,cy,38,FG,'l',bold=True)

    # resonant current flow along tank
    path=[(430,MID),(960,MID),(960,BOT),(430,BOT) ]
    path=[(432,MID),(960,MID)]
    if abs(i)>0.05:
        pts=path if i>0 else path[::-1]
        line(ctx,pts,(IC[0],IC[1],IC[2],0.3*abs(i)),26)
        line(ctx,pts,IC,9,dash=[30,22],off=-tt*240*1)
    txt(ctx,"ir →" if i>0.05 else ("← ir" if i<-0.05 else "ir"),600,MID+60,40,IC,bold=True)
    # waveforms
    px,pw=260,1540; y1=705
    U0=3
    gp=lambda k: (lambda u: 0.8 if gates(u%1)[k] else -0.8)
    txt(ctx,"Q1 驱动",px-20,y1+25,34,A,'r'); plot(ctx,px,y1,pw,50,gp(0),A,4,0,U0,n=1500)
    txt(ctx,"Q2 驱动",px-20,y1+105,34,hx('#ffb3ad'),'r'); plot(ctx,px,y1+80,pw,50,gp(1),hx('#ffb3ad'),4,0,U0,n=1500)
    txt(ctx,"谐振电流 ir",px-20,y1+260,34,IC,'r')
    plot(ctx,px,y1+170,pw,180,lambda u: ir(u%1),IC,6,0,U0,n=900)
    def tri(u):
        q=(u-0.1)%1; return 0.5*(1-4*abs(q-0.5)) if True else 0
    if False: plot(ctx,px,y1+170,pw,180,lambda u: 0.5*(4*abs(((u+0.25-0.0954)%1)-0.5)-1),hx('#e3a857',0.5),3,0,U0,n=900,axis=False)
    # ZVS markers
    for k in range(3):
        for off,lab in [(DT,"Q1"),(0.5+DT,"Q2")]:
            u=(k+off)/U0; x=px+pw*u
            line(ctx,[(x,y1-10),(x,y1+350)],hx('#7ee787',0.6),3,dash=[8,8])
            if k==0: txt(ctx,"ZVS",x,y1-30,32,ZC,bold=True)
            else: txt(ctx,"ZVS",x,y1-30,32,ZC,bold=True)
    cxp=px+pw*((tt/P)%U0)/U0
    line(ctx,[(cxp,y1-10),(cxp,y1+350)],hx('#ffffff',0.6),4)
    if any(abs(p-o)<0.04 for o in (DT,0.5+DT)):
        txt(ctx,"ZVS 导通：电流先经体二极管，Vds≈0",1180,1040,40,ZC,bold=True) if False else None
def draw(ctx,t):
    ta=clamp(t,0.5,19.5)
    a=ramp(t,6.6,7.4)
    group(ctx,1-a,compare,min(ta,6.6))
    group(ctx,a,llc,max(ta,7.4))
