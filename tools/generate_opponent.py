#!/usr/bin/env python3
"""
단식 상대 분석 카드 생성
사용법: python generate_opponent.py <CSV> <상대이름> <선수이름> <국가> <대회·라운드>
예시: python generate_opponent.py syj_semi.csv 야마구치 심유진 JPN "Indonesia Open 2026 준결"
"""
import sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright

TEMPLATE = Path("/home/claude/opponent_capture.html")

def build_html(csv_path, opp, me, country, detail):
    html = TEMPLATE.read_text(encoding='utf-8')
    raw = Path(csv_path).read_bytes()
    for enc in ['utf-8-sig','utf-8','cp949']:
        try: text = raw.decode(enc); break
        except: continue
    csv_escaped = text.replace('`','\\`').replace('${','\\${')
    html = re.sub(r"const CSV=`[\s\S]*?`;", f"const CSV=`{csv_escaped}`;", html)
    html = html.replace('>OPP_NAME<',  f'>{opp}<')
    html = html.replace('>ME_NAME<',   f'>{me}<')
    html = html.replace('>COUNTRY<',   f'>{country}<')
    html = html.replace('>DETAIL<',    f'>{detail}<')
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
    print(f"✅ {Path(out_path).name}")

def main():
    if len(sys.argv) < 6:
        print("사용법: python generate_opponent.py <CSV> <상대> <선수> <국가> <대회·라운드>")
        sys.exit(1)
    csv_path, opp, me, country, detail = sys.argv[1:]
    out_dir = Path(csv_path).parent / "cards_output"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_opp = opp.replace("/","_").replace(" ","_")
    out = out_dir / f"{Path(csv_path).stem}_상대분석_{safe_opp}.png"
    print(f"\n🎯 단식 상대 분석 카드")
    print(f"   {me} 기준 · vs {opp} ({country}) · {detail}\n")
    html = build_html(csv_path, opp, me, country, detail)
    screenshot(html, str(out))
    print(f"\n🎉 완료! → {out}")

if __name__ == "__main__":
    main()
