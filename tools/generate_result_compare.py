#!/usr/bin/env python3
"""경기 결과·실수 비중 비교 카드"""
import sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright
TEMPLATE = Path("/home/claude/result_compare_capture.html")
def read_csv(path):
    raw = Path(path).read_bytes()
    for enc in ['utf-8-sig','utf-8','cp949']:
        try: return raw.decode(enc)
        except: continue
    return raw.decode('utf-8', errors='replace')
def main():
    csv1, csv2, player, opp1, opp2 = sys.argv[1:6]
    html = TEMPLATE.read_text(encoding='utf-8')
    o = read_csv(csv1).replace('`','\\`').replace('${','\\${')
    n = read_csv(csv2).replace('`','\\`').replace('${','\\${')
    html = html.replace('OLD_PLACEHOLDER', o).replace('NEW_PLACEHOLDER', n)
    html = html.replace('const LABEL_OLD="vs 이다희";', f'const LABEL_OLD="vs {opp1}";')
    html = html.replace('const LABEL_NEW="vs 김민선";', f'const LABEL_NEW="vs {opp2}";')
    html = re.sub(r'(id="t1"[^>]*>)[^<]*(</)', lambda m: m.group(1)+f"{player} 결과 비교"+m.group(2), html)
    out_dir = Path(csv2).parent / "cards_output"; out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{player}_결과비교.png"
    tmp = out_dir / "_tmp_rc.html"; tmp.write_text(html, encoding='utf-8')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width":390,"height":844}, device_scale_factor=2)
        pg.goto(f"file://{tmp.resolve()}"); pg.wait_for_timeout(800)
        pg.locator("#card").screenshot(path=str(out)); b.close()
    tmp.unlink(); print(f"✅ {out}")
if __name__=="__main__": main()
