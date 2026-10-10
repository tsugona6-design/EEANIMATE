#!/usr/bin/env bash
# 第三段精做版：Manim 框架 + 历史图片（Ken Burns + 图注）+ Volti stage3_circuit.mp4 -> stage3_full.mp4（62s）
set -euo pipefail; cd "$(dirname "$0")"
FONT=/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc; I=images/stage3; T=$(mktemp -d); trap 'rm -rf $T' EXIT
# 媒体框（与 scenes.py LAYOUT 一致）
W=1344; H=756; X=288; Y=264
# 主题（与 scenes.py THEMES 对应）：PH_THEME=light|dark
if [ "${PH_THEME:-light}" = light ]; then BG=0xf6f8fa; CAPBG=white@0.85; CAPFG=0x1f2328; else BG=0x0d1117; CAPBG=black@0.6; CAPFG=white; fi
# 图片段: 文件|时长|图注|推拉方向(in/out)
# 电路段时长：按 stage3_circuit.mp4 实际时长（勿写死）
CIRCUIT_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 stage3_circuit.mp4 | awk '{printf "%d", ($1+0.2)}')
echo "电路段 ${CIRCUIT_DUR}s"
SEGS=(
"$I/01_bardeen_shockley_brattain_1948.jpg|5|贝尔实验室：Bardeen、Shockley、Brattain，1948年|in"
"$I/02_first_transistor_bell_labs.jpg|5|第一只晶体管（点接触），贝尔实验室，1947年|out"
"CIRCUIT|${CIRCUIT_DUR}||"
"$I/03_scr_power_thyristors.jpg|5|功率晶闸管（SCR），固态闸流管|in"
"$I/05_apollo_cm_battery_charger.jpg|5|阿波罗指令舱电池充电器，ITT，1964年|out"
)
n=0
for s in "${SEGS[@]}"; do IFS='|' read -r f d cap dir <<<"$s"; n=$((n+1))
  if [ "$f" = CIRCUIT ]; then
    ffmpeg -v error -y -i stage3_circuit.mp4 -vf "trim=0:$d,setpts=PTS-STARTPTS,fps=60,scale=$W:$H:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=$W:$H:(ow-iw)/2:(oh-ih)/2:color=$BG,format=yuv420p" -an -c:v libx264 -crf 16 $T/$n.mp4
  elif [ "$dir" = vid ]; then
    ffmpeg -v error -y -i "$f" -vf "fps=60,scale=$W:$H:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=$W:$H:(ow-iw)/2:(oh-ih)/2:color=$BG,drawbox=x=0:y=ih-64:w=iw:h=64:color=$CAPBG:t=fill,drawtext=fontfile=$FONT:text='$cap':fontcolor=$CAPFG:fontsize=28:x=(w-tw)/2:y=h-48,format=yuv420p" -t $d -an -c:v libx264 -crf 16 $T/$n.mp4
  else
    F=$((d*60)); [ "$dir" = in ] && Z="1+0.12*on/$F" || Z="1.12-0.12*on/$F"
    ffmpeg -v error -y -loop 1 -i "$f" -vf "scale=$((W*2)):$((H*2)):force_original_aspect_ratio=decrease,pad=$((W*2)):$((H*2)):(ow-iw)/2:(oh-ih)/2:color=$BG,zoompan=z='$Z':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=${W}x${H}:fps=60,drawbox=x=0:y=ih-64:w=iw:h=64:color=$CAPBG:t=fill,drawtext=fontfile=$FONT:text='$cap':fontcolor=$CAPFG:fontsize=30:x=(w-tw)/2:y=h-48,format=yuv420p" -t $d -c:v libx264 -crf 16 $T/$n.mp4
  fi
  echo "file '$T/$n.mp4'" >> $T/l.txt
done
ffmpeg -v error -y -f concat -safe 0 -i $T/l.txt -c:v libx264 -crf 16 -r 60 -pix_fmt yuv420p $T/slot.mp4
SLOT_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $T/slot.mp4)
# 框架时长 = 1.5s 入场 + slot + 约1s 淡出余量
FRAME_DUR=$(python3 -c "print(int(float('$SLOT_DUR')+3.0))")
FADE_OUT=$(python3 -c "print(max(0.5, float('$SLOT_DUR')-0.5))")
echo "slot=${SLOT_DUR}s frame=${FRAME_DUR}s fade_out=${FADE_OUT}s"
# 若框架短于需要则临时用黑场垫长（Manim 帧应已够；否则用 pad）
FD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 frame_03_stage3.mp4)
python3 -c "import sys; sys.exit(0 if float('$FD')+0.05>=float('$FRAME_DUR') else 1)" || {
  echo "框架 ${FD}s 短于 ${FRAME_DUR}s，用末帧垫长"
  ffmpeg -v error -y -i frame_03_stage3.mp4 -vf "tpad=stop_mode=clone:stop_duration=$(python3 -c "print(float('$FRAME_DUR')-float('$FD')+0.5)")" -c:v libx264 -crf 18 -r 60 $T/frame_pad.mp4
  FRAME=$T/frame_pad.mp4
}
FRAME=${FRAME:-frame_03_stage3.mp4}
ffmpeg -v error -y -i "$FRAME" -i $T/slot.mp4 -filter_complex  "[1:v]format=yuva420p,fade=in:st=0:d=0.5:alpha=1,fade=out:st=${FADE_OUT}:d=0.5:alpha=1,setpts=PTS-STARTPTS+1.5/TB[c];[0:v][c]overlay=$X:$Y:eof_action=pass:format=auto,format=yuv420p[v]"  -map "[v]" -t "$FRAME_DUR" -c:v libx264 -crf 18 -r 60 stage3_full.mp4
echo "完成: stage3_full.mp4 (${FRAME_DUR}s)"
