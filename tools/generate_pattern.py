#!/usr/bin/env python3
"""
랠리 패턴 분석 카드 (국내 테스트용)
사용법: python generate_pattern.py <CSV> <제목> <부제>
예시: python generate_pattern.py bae_lee.csv "배 vs 이" "국내 테스트"
"""
import sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright

TEMPLATE = Path("/home/claude/rally_pattern_capture.html")

def build_html(csv_path, title, detail):
    html = TEMPLATE.read_text(encoding='utf-8')
    raw = Path(csv_path).read_bytes()
    for enc in ['utf-8-sig','utf-8','cp949']:
        try: text = raw.decode(enc); break
        except: continue
    csv_escaped = text.replace('`','\\`').replace('${','\\${')
    html = re.sub(r"const CSV=`[\s\S]*?`;", f"const CSV=`{csv_escaped}`;", html)
    html = re.sub(r'(id="ip1"[^>]*>)[^<]*(</)', lambda m: m.group(1)+title+m.group(2), html)
    html = re.sub(r'(id="id"[^>]*>)[^<]*(</)', lambda m: m.group(1)+detail+m.group(2), html)
    return html

def screenshot(html, out_path):
    tmp = Path(out_path).parent / "_tmp_pat.html"
    tmp.write_text(html, encoding='utf-8')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width":390,"height":844}, device_scale_factor=2)
        page.goto(f"file://{tmp.resolve()}")
        page.wait_for_timeout(900)
        page.locator("#card").screenshot(path=str(out_path))
        browser.close()
    tmp.unlink()
    print(f"✅ {Path(out_path).name}")

def main():
    if len(sys.argv) < 4:
        print("사용법: python generate_pattern.py <CSV> <제목> <부제>")
        sys.exit(1)
    csv_path, title, detail = sys.argv[1:4]
    out_dir = Path(csv_path).parent / "cards_output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{Path(csv_path).stem}_패턴분석.png"
    print(f"\n🏸 랠리 패턴 분석 카드\n   {title} · {detail}\n")
    html = build_html(csv_path, title, detail)
    screenshot(html, str(out))
    print(f"\n🎉 완료! → {out}")

if __name__ == "__main__":
    main()
