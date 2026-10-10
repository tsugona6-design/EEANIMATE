# Royer 推挽变换器动画

Teaching animation of a simplified Royer push-pull converter (center-tapped primary + Q1/Q2).

## Layout
- `symbols.py` — reusable schematic symbols (NPN, coil, GND, current flow, flux ring, …)
- `royer_anim.py` — animation scene (26 s, 1920×1080, 60 fps)
- `royer_topology.py` — static simplified topology PNG
- `royer_animation.mp4` / `royer_topology.png` — outputs
- `royer_project.tar.gz` — archived project snapshot

## Render
```bash
/workspace/ve/bin/python royer_anim.py          # writes royer_animation.mp4 here
/workspace/ve/bin/python royer_anim.py still 8 13.6
/workspace/ve/bin/python royer_topology.py      # writes royer_topology.png here
```

## Notes
Primary project home: `/workspace/ANIMATE/ROYER/` only.
Legacy `/workspace/circ/` and `/workspace/power_history/` were removed after migration; do not rely on old symlink paths.
