#!/usr/bin/env python3
"""
득점 패턴 그룹 분석 카드 (앞/사이드/뒤)
사용법: python generate_group.py <CSV1> <CSV2> <선수> <상대1> <상대2>
예시: python generate_group.py bae_lee2.csv bae_kim.csv 배경은 이다희 김민선
"""
import sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright

TEMPLATE = Path("/home/claude/group_pattern_capture.html")

def read_csv(path):
    raw = Path(path).read_bytes()
    for enc in ['utf-8-sig','utf-8','cp949']:
        try: return raw.decode(enc)
        except: continue
    return raw.decode('utf-8', errors='replace')

def build_html(csv1, csv2, player, opp1, opp2):
    html = TEMPLATE.read_text(encoding='utf-8')
    o = read_csv(csv1).replace('`','\\`').replace('${','\\${')
    n = read_csv(csv2).replace('`','\\`').replace('${','\\${')
    html = html.replace('OLD_PLACEHOLDER', o).replace('NEW_PLACEHOLDER', n)
    html = html.replace('const LABEL_OLD="vs 이다희";', f'const LABEL_OLD="vs {opp1}";')
    html = html.replace('const LABEL_NEW="vs 김민선";', f'const LABEL_NEW="vs {opp2}";')
    html = re.sub(r'(id="t1"[^>]*>)[^<]*(</)', lambda m: m.group(1)+f"{player} 득점 루트"+m.group(2), html)
    return html

def screenshot(html, out_path):
    tmp = Path(out_path).parent / "_tmp_grp.html"
    tmp.write_text(html, encoding='utf-8')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width":390,"height":844}, device_scale_factor=2)
        page.goto(f"file://{tmp.resolve()}")
        page.wait_for_timeout(800)
        page.locator("#card").screenshot(path=str(out_path))
        browser.close()
    tmp.unlink()
    print(f"✅ {Path(out_path).name}")

def main():
    if len(sys.argv) < 6:
        print("사용법: python generate_group.py <CSV1> <CSV2> <선수> <상대1> <상대2>")
        sys.exit(1)
    csv1, csv2, player, opp1, opp2 = sys.argv[1:6]
    out_dir = Path(csv2).parent / "cards_output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{player}_득점루트.png"
    print(f"\n🎯 득점 패턴 그룹 분석\n   {player} · vs {opp1} / vs {opp2}\n")
    html = build_html(csv1, csv2, player, opp1, opp2)
    screenshot(html, str(out))
    print(f"\n🎉 완료! → {out}")

if __name__ == "__main__":
    main()
