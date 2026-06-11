#!/usr/bin/env python3
"""
상대 분석 카드 생성
사용법: python generate_opponent.py <CSV> <상대이름> <선수이름> <국가> <대회·라운드>
예시: python generate_opponent.py asy_final.csv 야마구치 안세영 JPN "Indonesia Open 2026 결승"
"""
import sys, re, base64, csv as csvmod, io
from pathlib import Path
from playwright.sync_api import sync_playwright

TEMPLATE = Path("/home/claude/opponent_asy_capture.html")

# 존 매핑
ZONE_MAP = {
    '앞사이드':'앞-사이드(앞사각)', '뒷사이드':'뒤-사이드(뒷사각)',
    '앞앞':'앞-앞(헤어핀싸움)', '옆옆':'옆-옆(중간볼)',
    '사이드뒤':'사이드-뒤', '뒤앞':'뒤-앞',
    '앞뒤':'앞-뒤', '사이드앞':'사이드-앞', '뒤뒤':'뒤뒤',
}

def build_html(csv_path, opp, me, country, detail):
    html = TEMPLATE.read_text(encoding='utf-8')
    # CSV 읽기
    raw = Path(csv_path).read_bytes()
    for enc in ['utf-8-sig','utf-8','cp949']:
        try: text = raw.decode(enc); break
        except: continue
    # CSV 교체
    csv_escaped = text.replace('`','\\`').replace('${','\\${')
    html = re.sub(r'const CSV=`[\s\S]*?`;', f'const CSV=`{csv_escaped}`;', html)
    # 값 교체
    html = html.replace('value="야마구치 아카네"', f'value="{opp}"')
    html = html.replace('value="안세영"',           f'value="{me}"')
    html = html.replace('value="JPN"',              f'value="{country}"')
    html = html.replace('value="Indonesia Open 2026 결승"', f'value="{detail}"')
    return html

def screenshot(html, out_path):
    tmp = Path(out_path).parent / "_tmp_opp.html"
    tmp.write_text(html, encoding='utf-8')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width":390,"height":844}, device_scale_factor=2)
        page.goto(f"file://{tmp.resolve()}")
        page.wait_for_timeout(800)
        page.locator("#card").screenshot(path=str(out_path))
        browser.close()
    tmp.unlink()
    print(f"✅ 저장: {out_path}")

def main():
    if len(sys.argv) < 6:
        print("사용법: python generate_opponent.py <CSV> <상대> <선수> <국가> <대회·라운드>")
        sys.exit(1)
    csv_path, opp, me, country, detail = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    prefix = Path(csv_path).stem
    out_dir = Path(csv_path).parent / "cards_output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{prefix}_상대분석_{opp}.png"
    print(f"\n🎯 상대 분석 카드")
    print(f"   {me} 기준 · vs {opp} ({country}) · {detail}\n")
    html = build_html(csv_path, opp, me, country, detail)
    screenshot(html, str(out))
    print(f"\n🎉 완료! → {out}")

if __name__ == "__main__":
    main()
