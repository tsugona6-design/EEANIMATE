# Buck converter (BJT) — topology + teaching animation

Independent copy under `/workspace/ANIMATE/BUCK-BJT/` (own `symbols.py`).

## Files
- `symbols.py` — schematic symbols (continuous coil, diode, capacitor, NPN, …)
- `buck_topology.py` — static topology PNG
- `buck_anim.py` — on/off current paths + Vg / iL / Vsw, two duty dwells
- `buck_topology.png`, `buck_animation.mp4`

## Render
```bash
/workspace/ve/bin/python buck_topology.py
/workspace/ve/bin/python buck_anim.py
/workspace/ve/bin/python buck_anim.py still 3.5 4.5
```

## Animation (24 s, 1920×1080, 60 fps, no audio)
- Duty A ≈ 0.35 (t=2–11), Duty B ≈ 0.65 (t=12–22)
- ON: blue path Vin→S→L→load; OFF: green path D→L→load
