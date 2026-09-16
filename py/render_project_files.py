import os
import glob
import sys
import asyncio
import site

# Dynamically find site-packages in active Python environment/sys.path
for path in list(sys.path):
    if "site-packages" in path and os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

# Add user site-packages dynamically if available
user_site = site.getusersitepackages()
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

import pya
from playwright.async_api import async_playwright

def render_klayout_file(input_path, output_png):
    layout = pya.Layout()
    layout.read(input_path)
    view = pya.LayoutView()
    view.show_layout(layout, True)
    view.zoom_fit()
    view.save_image(output_png, 1920, 1080)

def parse_xschem_to_svg(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    elements = []
    min_x, min_y, max_x, max_y = 1e9, 1e9, -1e9, -1e9

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        parts = line.split()
        cmd = parts[0]

        if cmd == 'L' and len(parts) >= 6:
            layer, x1, y1, x2, y2 = parts[1], float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5])
            min_x, max_x = min(min_x, x1, x2), max(max_x, x1, x2)
            min_y, max_y = min(min_y, y1, y2), max(max_y, y1, y2)
            color = '#00ff00' if layer == '4' else '#0080ff' if layer == '7' else '#a0a0a0'
            elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2" stroke-linecap="round" />')

        elif cmd == 'B' and len(parts) >= 6:
            layer, x1, y1, x2, y2 = parts[1], float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5])
            min_x, max_x = min(min_x, x1, x2), max(max_x, x1, x2)
            min_y, max_y = min(min_y, y1, y2), max(max_y, y1, y2)
            rx, ry = min(x1, x2), min(y1, y2)
            rw, rh = abs(x2 - x1), abs(y2 - y1)
            elements.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="none" stroke="#ff00ff" stroke-width="2" />')

        elif cmd == 'N' and len(parts) >= 5:
            x1, y1, x2, y2 = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
            min_x, max_x = min(min_x, x1, x2), max(max_x, x1, x2)
            min_y, max_y = min(min_y, y1, y2), max(max_y, y1, y2)
            elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#00ffff" stroke-width="1.5" stroke-linecap="round" />')

        elif cmd == 'T':
            raw = line
            while raw.count('{') > raw.count('}'):
                if i < len(lines):
                    raw += '\n' + lines[i].strip()
                    i += 1
                else:
                    break
            start_b = raw.find('{')
            end_b = raw.rfind('}')
            if start_b != -1 and end_b != -1:
                txt = raw[start_b+1:end_b]
                rest = raw[end_b+1:].strip().split()
                if len(rest) >= 2:
                    try:
                        tx, ty = float(rest[0]), float(rest[1])
                        min_x, max_x = min(min_x, tx), max(max_x, tx)
                        min_y, max_y = min(min_y, ty), max(max_y, ty)
                        txt_esc = txt.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        elements.append(f'<text x="{tx}" y="{ty}" fill="#ffffff" font-family="monospace" font-size="14">{txt_esc}</text>')
                    except ValueError:
                        pass

        elif cmd == 'C':
            raw = line
            while raw.count('{') > raw.count('}'):
                if i < len(lines):
                    raw += '\n' + lines[i].strip()
                    i += 1
                else:
                    break
            start_b = raw.find('{')
            end_b = raw.find('}')
            if start_b != -1 and end_b != -1:
                sym_path = raw[start_b+1:end_b]
                rest = raw[end_b+1:].strip()
                rest_parts = rest.split()
                if len(rest_parts) >= 2:
                    try:
                        cx, cy = float(rest_parts[0]), float(rest_parts[1])
                        min_x, max_x = min(min_x, cx), max(max_x, cx)
                        min_y, max_y = min(min_y, cy), max(max_y, cy)
                        sym_name = os.path.basename(sym_path)
                        elements.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="#ffff00" />')
                        elements.append(f'<text x="{cx+6}" y="{cy-4}" fill="#ffaa00" font-family="monospace" font-size="12">{sym_name}</text>')
                    except ValueError:
                        pass

    if min_x >= max_x or min_y >= max_y:
        min_x, min_y, max_x, max_y = -100, -100, 100, 100

    padding = 50
    view_x = min_x - padding
    view_y = min_y - padding
    view_w = (max_x - min_x) + 2 * padding
    view_h = (max_y - min_y) + 2 * padding

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_x} {view_y} {view_w} {view_h}" width="100%" height="100%" style="background-color: #001122;">
    {''.join(elements)}
    </svg>'''
    return svg

async def render_xschem_files(xschem_files, img_dir):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        for fpath in xschem_files:
            basename = os.path.basename(fpath)
            ext = os.path.splitext(basename)[1].lstrip('.')
            name = os.path.splitext(basename)[0]
            out_png = os.path.join(img_dir, f"{ext}_{name}.png")
            svg_content = parse_xschem_to_svg(fpath)
            html_content = f'<html><body style="margin:0; background:#001122; overflow:hidden;">{svg_content}</body></html>'
            await page.set_content(html_content)
            await page.screenshot(path=out_png)
            print(f"Rendered Xschem: {out_png}")
        await browser.close()

def main():
    img_dir = "img"
    os.makedirs(img_dir, exist_ok=True)

    # Render GDS files
    gds_files = sorted(glob.glob("gds/*.gds"))
    print(f"Found {len(gds_files)} GDS files.")
    for fpath in gds_files:
        basename = os.path.basename(fpath)
        name = os.path.splitext(basename)[0]
        out_png = os.path.join(img_dir, f"gds_{name}.png")
        render_klayout_file(fpath, out_png)
        print(f"Rendered GDS: {out_png}")

    # Render Magic files
    mag_files = sorted(glob.glob("mag/*.mag"))
    print(f"Found {len(mag_files)} Magic files.")
    for fpath in mag_files:
        basename = os.path.basename(fpath)
        name = os.path.splitext(basename)[0]
        out_png = os.path.join(img_dir, f"mag_{name}.png")
        render_klayout_file(fpath, out_png)
        print(f"Rendered Magic: {out_png}")

    # Render Xschem files (.sch and .sym)
    xschem_files = sorted(glob.glob("xschem/*.sch") + glob.glob("xschem/*.sym"))
    print(f"Found {len(xschem_files)} Xschem files.")
    asyncio.run(render_xschem_files(xschem_files, img_dir))

if __name__ == '__main__':
    main()
