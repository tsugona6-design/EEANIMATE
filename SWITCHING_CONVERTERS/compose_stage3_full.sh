#!/usr/bin/env bash
# 第三段精做：历史照 + Royer/Buck/Boost（各带 BJT 电流控制注释）+ SCR + 阿波罗
# 动画源：../ROYER ../BUCK-BJT ../BOOST-BJT（不改 Volti 源文件，仅叠加）
set -euo pipefail
cd "$(dirname "$0")"
FONT=/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
I=images
ROYER=../ROYER/royer_animation.mp4
BUCK=../BUCK-BJT/buck_animation.mp4
BOOST=../BOOST-BJT/boost_animation.mp4
FRAME=frame_03_stage3.mp4
# 若本地无新框架则从 POWER_HISTORY 取
[ -f "$FRAME" ] || FRAME=/workspace/POWER_HISTORY/media/videos/scenes/1080p60/Stage3Full.mp4
W=1344; H=756; X=288; Y=264
BG=0xf6f8fa; CAPBG=white@0.85; CAPFG=0x1f2328
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT

# 历史照 Ken Burns
kb() { # file dur caption dir
  local f=$1 d=$2 cap=$3 dir=$4
  local F=$((d*60)) Z
  [ "$dir" = in ] && Z="1+0.12*on/$F" || Z="1.12-0.12*on/$F"
  ffmpeg -v error -y -loop 1 -i "$f" -vf \
    "scale=$((W*2)):$((H*2)):force_original_aspect_ratio=decrease,pad=$((W*2)):$((H*2)):(ow-iw)/2:(oh-ih)/2:color=$BG,zoompan=z='$Z':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=${W}x${H}:fps=60,drawbox=x=0:y=ih-64:w=iw:h=64:color=$CAPBG:t=fill,drawtext=fontfile=$FONT:text='$cap':fontcolor=$CAPFG:fontsize=30:x=(w-tw)/2:y=h-48,format=yuv420p" \
    -t "$d" -c:v libx264 -crf 16 "$5"
}

# 电路动画：缩放 + 左上角电路名 + 右下角 BJT 驱动注释（全程）
anim_note() { # infile outfile title
  local inn=$1 out=$2 title=$3
  local NOTE='BJT需要通过合适的驱动电路产生所需的基极电流'
  ffmpeg -v error -y -i "$inn" -vf \
    "fps=60,scale=$W:$H:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=$W:$H:(ow-iw)/2:(oh-ih)/2:color=$BG,\
drawbox=x=12:y=12:w=220:h=40:color=white@0.88:t=fill,\
drawtext=fontfile=$FONT:text='${title}':fontcolor=0x1f2328:fontsize=28:x=22:y=18,\
drawbox=x=w-520:y=h-52:w=508:h=40:color=white@0.88:t=fill,\
drawtext=fontfile=$FONT:text='${NOTE}':fontcolor=0x1f2328:fontsize=20:x=w-508:y=h-42,\
format=yuv420p" \
    -an -c:v libx264 -crf 16 "$out"
}

echo "== 历史照"
kb "$I/01_bardeen_shockley_brattain_1948.jpg" 5 "贝尔实验室：Bardeen、Shockley、Brattain，1948年" in  "$T/01.mp4"
kb "$I/02_first_transistor_bell_labs.jpg"     5 "第一只晶体管（点接触），贝尔实验室，1947年" out "$T/02.mp4"

echo "== Royer / Buck / Boost（叠加 BJT 注释）"
anim_note "$ROYER"  "$T/03_royer.mp4"  "Royer变换器"
anim_note "$BUCK"   "$T/04_buck.mp4"   "Buck拓扑"
anim_note "$BOOST"  "$T/05_boost.mp4"  "Boost拓扑"

echo "== SCR / Apollo"
kb "$I/03_scr_power_thyristors.jpg"     5 "功率晶闸管（SCR），固态闸流管" in  "$T/06.mp4"
kb "$I/05_apollo_cm_battery_charger.jpg" 5 "阿波罗指令舱电池充电器，ITT，1964年" out "$T/07.mp4"

{ for n in 01 02 03_royer 04_buck 05_boost 06 07; do echo "file '$T/$n.mp4'"; done; } > "$T/l.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$T/l.txt" -c:v libx264 -crf 16 -r 60 -pix_fmt yuv420p "$T/slot.mp4"
SLOT_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$T/slot.mp4")
FRAME_DUR=$(python3 -c "print(int(float('$SLOT_DUR')+3))")
FADE_OUT=$(python3 -c "print(max(0.5, float('$SLOT_DUR')-0.5))")
FD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FRAME")
echo "slot=${SLOT_DUR}s frame_need=${FRAME_DUR}s frame_have=${FD}s"
if python3 -c "import sys; sys.exit(0 if float('$FD')+0.05>=float('$FRAME_DUR') else 1)"; then
  FR="$FRAME"
else
  ffmpeg -v error -y -i "$FRAME" -vf "tpad=stop_mode=clone:stop_duration=$(python3 -c "print(float('$FRAME_DUR')-float('$FD')+0.5)")" -c:v libx264 -crf 18 -r 60 "$T/frame_pad.mp4"
  FR="$T/frame_pad.mp4"
fi
# 同步框架到本目录
cp -f "$FRAME" frame_03_stage3.mp4 2>/dev/null || true

ffmpeg -v error -y -i "$FR" -i "$T/slot.mp4" -filter_complex \
 "[1:v]format=yuva420p,fade=in:st=0:d=0.5:alpha=1,fade=out:st=${FADE_OUT}:d=0.5:alpha=1,setpts=PTS-STARTPTS+1.5/TB[c];[0:v][c]overlay=$X:$Y:eof_action=pass:format=auto,format=yuv420p[v]" \
 -map "[v]" -t "$FRAME_DUR" -c:v libx264 -crf 18 -r 60 stage3_full.mp4

echo "完成: $(pwd)/stage3_full.mp4 (${FRAME_DUR}s)"
