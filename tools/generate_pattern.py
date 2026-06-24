#!/usr/bin/env python3
"""
상대 분석 카드 (2페이지) - 실점위치+결과 / 랠리길이+실수위치
사용법: python generate_pattern.py <CSV> <상대이름> <부제>
예시: python generate_pattern.py bae_lee.csv 배경은 "WS · 단식"
"""
import sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright

TEMPLATE = Path("/home/claude/rally_pattern_capture.html")

def build_html(csv_path, opp, detail):
    html = TEMPLATE.read_text(encoding='utf-8')
    raw = Path(csv_path).read_bytes()
    for enc in ['utf-8-sig','utf-8','cp949']:
        try: text = raw.decode(enc); break
        except: continue
    csv_escaped = text.replace('`','\\`').replace('${','\\${')
    html = re.sub(r"const CSV=`[\s\S]*?`;", f"const CSV=`{csv_escaped}`;", html)
    for sid in ['ip1','ip1b']:
        html = re.sub(rf'(id="{sid}"[^>]*>)[^<]*(</)', lambda m: m.group(1)+opp+m.group(2), html)
    for sid in ['id','id2']:
        html = re.sub(rf'(id="{sid}"[^>]*>)[^<]*(</)', lambda m: m.group(1)+detail+m.group(2), html)
    return html

def screenshot(html, out_dir, prefix, opp):
    tmp = out_dir / "_tmp_pat.html"
    tmp.write_text(html, encoding='utf-8')
    safe = opp.replace("/","_").replace(" ","_")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width":390,"height":844}, device_scale_factor=2)
        page.goto(f"file://{tmp.resolve()}")
        page.wait_for_timeout(900)
        for i, cid in enumerate(['card1','card2'], 1):
            out = out_dir / f"{prefix}_상대분석_{safe}_{i}.png"
            page.locator(f"#{cid}").screenshot(path=str(out))
            print(f"✅ {out.name}")
        browser.close()
    tmp.unlink()

def main():
    if len(sys.argv) < 4:
        print("사용법: python generate_pattern.py <CSV> <상대이름> <부제>")
        sys.exit(1)
    csv_path, opp, detail = sys.argv[1:4]
    out_dir = Path(csv_path).parent / "cards_output"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n🎯 상대 분석 카드 (2페이지)\n   {opp} · {detail}\n")
    html = build_html(csv_path, opp, detail)
    screenshot(html, out_dir, Path(csv_path).stem, opp)
    print(f"\n🎉 완료!")

if __name__ == "__main__":
    main()
