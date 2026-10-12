#!/usr/bin/env bash
# 第四段：历史照 + 六块电路占位（RC/NE555/半桥/全桥/反激/正激）+ MOSFET/电源应用照
set -euo pipefail
cd "$(dirname "$0")"
FONT=/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
I=images; PH=placeholders
FRAME=frame_04_stage4.mp4
W=1344; H=756; X=288; Y=264
BG=0xf6f8fa; CAPBG=white@0.85; CAPFG=0x1f2328
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT

kb() { # file dur caption dir out
  local f=$1 d=$2 cap=$3 dir=$4 out=$5
  local F=$((d*60)) Z; [ "$dir" = in ] && Z="1+0.12*on/$F" || Z="1.12-0.12*on/$F"
  ffmpeg -v error -y -loop 1 -i "$f" -vf \
    "scale=$((W*2)):$((H*2)):force_original_aspect_ratio=decrease,pad=$((W*2)):$((H*2)):(ow-iw)/2:(oh-ih)/2:color=$BG,zoompan=z='$Z':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=${W}x${H}:fps=60,drawbox=x=0:y=ih-64:w=iw:h=64:color=$CAPBG:t=fill,drawtext=fontfile=$FONT:text='$cap':fontcolor=$CAPFG:fontsize=28:x=(w-tw)/2:y=h-46,format=yuv420p" \
    -t "$d" -c:v libx264 -crf 16 "$out"
}

echo "== 历史照 / 占位"
kb "$I/02_signetics_ne555n_1978.jpg" 5 "Signetics NE555N，1978年" in  "$T/01.mp4"
kb "$I/03_first_555_die_1971.jpg"    5 "第一颗 555 管芯，约1971年" out "$T/02.mp4"
for n in 01_rc 02_ne555 03_halfbridge 04_fullbridge 05_flyback 06_forward; do
  cp "placeholders/ph${n}.mp4" "$T/ph_${n}.mp4"
done
kb "$I/05_ir_hexfet_mosfet.jpg"      5 "IR HEXFET 功率 MOSFET" in  "$T/09.mp4"
kb "$I/06_xt_pc_power_supply_pcb.jpg" 5 "XT 机 PC 开关电源 PCB" out "$T/10.mp4"
kb "$I/07_atx_power_supply_unit.jpg"  5 "ATX 计算机电源" in  "$T/11.mp4"

{
  echo "file '$T/01.mp4'"
  echo "file '$T/02.mp4'"
  for n in 01_rc 02_ne555 03_halfbridge 04_fullbridge 05_flyback 06_forward; do echo "file '$T/ph_${n}.mp4'"; done
  echo "file '$T/09.mp4'"
  echo "file '$T/10.mp4'"
  echo "file '$T/11.mp4'"
} > "$T/l.txt"

ffmpeg -v error -y -f concat -safe 0 -i "$T/l.txt" -c:v libx264 -crf 16 -r 60 -pix_fmt yuv420p "$T/slot.mp4"
SLOT_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$T/slot.mp4")
FRAME_DUR=$(python3 -c "print(int(float('$SLOT_DUR')+3))")
FADE_OUT=$(python3 -c "print(max(0.5, float('$SLOT_DUR')-0.5))")
FD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FRAME")
echo "slot=${SLOT_DUR}s need=${FRAME_DUR}s have=${FD}s"
FR="$FRAME"
if ! python3 -c "import sys; sys.exit(0 if float('$FD')+0.05>=float('$FRAME_DUR') else 1)"; then
  ffmpeg -v error -y -i "$FRAME" -vf "tpad=stop_mode=clone:stop_duration=$(python3 -c "print(float('$FRAME_DUR')-float('$FD')+0.5)")" -c:v libx264 -crf 18 -r 60 "$T/frame_pad.mp4"
  FR="$T/frame_pad.mp4"
fi
ffmpeg -v error -y -i "$FR" -i "$T/slot.mp4" -filter_complex \
 "[1:v]format=yuva420p,fade=in:st=0:d=0.5:alpha=1,fade=out:st=${FADE_OUT}:d=0.5:alpha=1,setpts=PTS-STARTPTS+1.5/TB[c];[0:v][c]overlay=$X:$Y:eof_action=pass:format=auto,format=yuv420p[v]" \
 -map "[v]" -t "$FRAME_DUR" -c:v libx264 -crf 18 -r 60 stage4_full.mp4
echo "完成: $(pwd)/stage4_full.mp4 (${FRAME_DUR}s)"
