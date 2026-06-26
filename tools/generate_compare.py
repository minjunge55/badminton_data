#!/usr/bin/env python3
"""
경기 비교 분석 카드 (2페이지) - 실수 변화 + 득점 패턴 비교
사용법: python generate_compare.py <기존CSV> <신규CSV> <선수> <기존상대> <신규상대>
예시: python generate_compare.py bae_lee2.csv bae_kim.csv 배경은 이 김
"""
import sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright

TEMPLATE = Path("/home/claude/compare_capture.html")

def read_csv(path):
    raw = Path(path).read_bytes()
    for enc in ['utf-8-sig','utf-8','cp949']:
        try: return raw.decode(enc)
        except: continue
    return raw.decode('utf-8', errors='replace')

def build_html(old_csv, new_csv, player, old_opp, new_opp):
    html = TEMPLATE.read_text(encoding='utf-8')
    o = read_csv(old_csv).replace('`','\\`').replace('${','\\${')
    n = read_csv(new_csv).replace('`','\\`').replace('${','\\${')
    html = html.replace('OLD_PLACEHOLDER', o)
    html = html.replace('NEW_PLACEHOLDER', n)
    html = html.replace('const LABEL_OLD="vs 이";', f'const LABEL_OLD="vs {old_opp}";')
    html = html.replace('const LABEL_NEW="vs 김";', f'const LABEL_NEW="vs {new_opp}";')
    html = re.sub(r'(id="t1"[^>]*>)[^<]*(</)', lambda m: m.group(1)+f"{player} 실수 변화"+m.group(2), html)
    html = re.sub(r'(id="sub1"[^>]*>)[^<]*(</)', lambda m: m.group(1)+f"vs {old_opp} → vs {new_opp}"+m.group(2), html)
    return html

def screenshot(html, out_dir, prefix):
    tmp = out_dir / "_tmp_cmp.html"
    tmp.write_text(html, encoding='utf-8')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width":390,"height":844}, device_scale_factor=2)
        page.goto(f"file://{tmp.resolve()}")
        page.wait_for_timeout(900)
        for i, cid in enumerate(['card1','card2'], 1):
            out = out_dir / f"{prefix}_비교분석_{i}.png"
            page.locator(f"#{cid}").screenshot(path=str(out))
            print(f"✅ {out.name}")
        browser.close()
    tmp.unlink()

def main():
    if len(sys.argv) < 6:
        print("사용법: python generate_compare.py <기존CSV> <신규CSV> <선수> <기존상대> <신규상대>")
        sys.exit(1)
    old_csv, new_csv, player, old_opp, new_opp = sys.argv[1:6]
    out_dir = Path(new_csv).parent / "cards_output"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📊 경기 비교 분석 카드 (2페이지)\n   {player} · vs {old_opp} → vs {new_opp}\n")
    html = build_html(old_csv, new_csv, player, old_opp, new_opp)
    screenshot(html, out_dir, player)
    print(f"\n🎉 완료!")

if __name__ == "__main__":
    main()
