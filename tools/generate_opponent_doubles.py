#!/usr/bin/env python3
"""
복식/혼복 상대 분석 카드 생성
사용법: python generate_opponent_doubles.py <CSV> <상대팀> <선수1> <선수2> <국가> <대회·라운드>
예시: python generate_opponent_doubles.py 준결.csv 고이주딘 서승재 김원호 MAS "Indonesia Open 2026 준결"
"""
import sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright

TEMPLATE = Path("/home/claude/opponent_doubles_capture.html")

def build_html(csv_path, opp, p1, p2, country, detail):
    html = TEMPLATE.read_text(encoding='utf-8')
    raw = Path(csv_path).read_bytes()
    for enc in ['utf-8-sig','utf-8','cp949']:
        try: text = raw.decode(enc); break
        except: continue
    csv_escaped = text.replace('`','\\`').replace('${','\\${')
    html = re.sub(r'const CSV=`[\s\S]*?`;', f'const CSV=`{csv_escaped}`;', html)
    # contenteditable 텍스트 교체
    import re as _re
    html = _re.sub(r'(id="ip1"[^>]*>)[^<]*(</)', lambda m: m.group(1)+opp+m.group(2), html)
    html = _re.sub(r'(id="ip2"[^>]*>)[^<]*(</)', lambda m: m.group(1)+p1+'/'+p2+m.group(2), html)
    html = _re.sub(r'(id="io"[^>]*>)[^<]*(</)', lambda m: m.group(1)+country+m.group(2), html)
    html = _re.sub(r'(id="id"[^>]*>)[^<]*(</)', lambda m: m.group(1)+detail+m.group(2), html)
    return html

def screenshot(html, out_path):
    tmp = Path(out_path).parent / "_tmp_opp_d.html"
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
    if len(sys.argv) < 7:
        print("사용법: python generate_opponent_doubles.py <CSV> <상대팀> <선수1> <선수2> <국가> <대회·라운드>")
        sys.exit(1)
    csv_path, opp, p1, p2, country, detail = sys.argv[1:]
    out_dir = Path(csv_path).parent / "cards_output"
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = Path(csv_path).stem
    safe_opp = opp.replace("/","_").replace(" ","_")
    out = out_dir / f"{prefix}_상대분석_{safe_opp}.png"
    print(f"\n🎯 복식/혼복 상대 분석 카드")
    print(f"   {p1}/{p2} 기준 · vs {opp} ({country}) · {detail}\n")
    html = build_html(csv_path, opp, p1, p2, country, detail)
    screenshot(html, str(out))
    print(f"\n🎉 완료! → {out}")

if __name__ == "__main__":
    main()
