# mm→px for kicad_schematic_v2 (light, left for waves)
SX_RAW, SY_RAW = 10.100935279267292, 10.09965372615796
CROP = (707, 302, 1191, 1131)
SCALE = 1.1821471652593487
PASTE = (40, 50)

def mm(mx, my):
    rx, ry = mx * SX_RAW, my * SY_RAW
    x0, y0, _, _ = CROP
    ox, oy = PASTE
    return (rx - x0) * SCALE + ox, (ry - y0) * SCALE + oy
