#!/usr/bin/env bash
# 第一段精做版：Manim 框架 + 历史图片（Ken Burns + 图注）+ Volti stage1_circuit.mp4 -> stage1_full.mp4（50s）
set -euo pipefail; cd "$(dirname "$0")"
FONT=/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc; I=images/stage1; T=$(mktemp -d); trap 'rm -rf $T' EXIT
# 媒体框（与 scenes.py LAYOUT 一致）
W=1344; H=756; X=288; Y=264
# 主题（与 scenes.py THEMES 对应）：PH_THEME=light|dark
if [ "${PH_THEME:-light}" = light ]; then BG=0xf6f8fa; CAPBG=white@0.85; CAPFG=0x1f2328; else BG=0x0d1117; CAPBG=black@0.6; CAPFG=white; fi
# 图片段: 文件|时长|图注|推拉方向(in/out)
SEGS=(
"$I/01_edison_jumbo_dynamo_pearl_st.jpg|6|爱迪生“巨无霸”直流发电机，纽约珍珠街电站，约1882—1890年|in"
"$I/02_motor_generator_set_1909.jpg|6|同步电动机-发电机组（交流→直流），1909年|out"
"$I/03_westinghouse_rotary_converter_1909.jpg|5|西屋 500 kW 旋转变流器，1909年|in"
"$I/04_central_london_railway_rotary_converter.jpg|5|伦敦中央铁路 900 kW 旋转变流器，约1900—1907年|out"
"$I/05_h_ward_leonard_portrait.jpg|5|H. Ward Leonard，1891年前后提出 Ward Leonard 调速系统|in"
"CIRCUIT|20||"
)
n=0
for s in "${SEGS[@]}"; do IFS='|' read -r f d cap dir <<<"$s"; n=$((n+1))
  if [ "$f" = CIRCUIT ]; then
    ffmpeg -v error -y -i stage1_circuit.mp4 -vf "trim=0:$d,setpts=PTS-STARTPTS,fps=60,scale=$W:$H:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=$W:$H:(ow-iw)/2:(oh-ih)/2:color=$BG,format=yuv420p" -an -c:v libx264 -crf 16 $T/$n.mp4
  else
    F=$((d*60)); [ "$dir" = in ] && Z="1+0.12*on/$F" || Z="1.12-0.12*on/$F"
    ffmpeg -v error -y -loop 1 -i "$f" -vf "scale=$((W*2)):$((H*2)):force_original_aspect_ratio=decrease,pad=$((W*2)):$((H*2)):(ow-iw)/2:(oh-ih)/2:color=$BG,zoompan=z='$Z':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=${W}x${H}:fps=60,drawbox=x=0:y=ih-64:w=iw:h=64:color=$CAPBG:t=fill,drawtext=fontfile=$FONT:text='$cap':fontcolor=$CAPFG:fontsize=30:x=(w-tw)/2:y=h-48,format=yuv420p" -t $d -c:v libx264 -crf 16 $T/$n.mp4
  fi
  echo "file '$T/$n.mp4'" >> $T/l.txt
done
ffmpeg -v error -y -f concat -safe 0 -i $T/l.txt -c:v libx264 -crf 16 -r 60 -pix_fmt yuv420p $T/slot.mp4
# slot 于 1.5s 进入，47s 后淡出（框架 50s，49s 起整体淡出）
ffmpeg -v error -y -i frame_01_stage1_full.mp4 -i $T/slot.mp4 -filter_complex \
 "[1:v]format=yuva420p,fade=in:st=0:d=0.5:alpha=1,fade=out:st=46.5:d=0.5:alpha=1,setpts=PTS-STARTPTS+1.5/TB[c];[0:v][c]overlay=$X:$Y:eof_action=pass:format=auto,format=yuv420p[v]" \
 -map "[v]" -t 50 -c:v libx264 -crf 18 -r 60 stage1_full.mp4
echo "完成: stage1_full.mp4"
