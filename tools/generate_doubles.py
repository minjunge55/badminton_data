#!/usr/bin/env python3
"""
배드민턴 복식 분석 카드 자동 생성
사용법: python3 generate_doubles.py <CSV파일> [선수1] [선수2] [상대팀] [라운드]
예시:  python3 generate_doubles.py 김재현장하정32강.csv 김재현 장하정 "상대팀" 32강

출력: cards_output/<prefix>_p1_<선수1>.png, <prefix>_p2_<선수2>.png
"""

import sys
import re
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

TEMPLATE_PATH = Path(__file__).parent / "doubles_capture.html"

def load_csv(csv_path: str) -> str:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"파일이 없습니다: {os.path.abspath(csv_path)}")
    encodings = ["utf-8", "utf-8-sig", "cp949", "euc-kr", "latin-1"]
    for enc in encodings:
        try:
            with open(csv_path, encoding=enc) as f:
                content = f.read()
                print(f"   인코딩: {enc}")
                return content
        except (UnicodeDecodeError, UnicodeError):
            continue
    with open(csv_path, "rb") as f:
        raw = f.read()
    return raw.decode("utf-8", errors="replace")

def build_html(csv_text: str, p1: str, p2: str, opponent: str, round_name: str) -> str:
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    csv_escaped = csv_text.replace("`", "\\`").replace("${", "\\${")
    # CSV 변수 교체 (RAW 또는 CSV 둘 다 시도)
    import re
    html = re.sub(r"const (CSV|RAW)=`[\s\S]*?`;", f"const CSV=`{csv_escaped}`;", html)

    html = html.replace('value="김재현"', f'value="{p1}"')
    html = html.replace('value="장하정"', f'value="{p2}"')
    html = html.replace('value="상대 팀"', f'value="{opponent}"')
    html = html.replace('value="상대팀"', f'value="{opponent}"')
    html = html.replace('value="32강"',   f'value="{round_name}"')

    # pcsv 호출 변수명도 통일
    html = html.replace("pcsv(RAW)", "pcsv(CSV)")

    # 페이지 로드 후 자동 적용
    for init_call in ["AD=ckclk(pcsv(CSV));BS();RA();", "AD=ckclk(pcsv(RAW));BS();RA();"]:
        if init_call in html:
            html = html.replace(init_call, f"""{init_call}
document.getElementById('ip1').value="{p1}";
document.getElementById('ip2').value="{p2}";
document.getElementById('io').value="{opponent}";
document.getElementById('id').value="{round_name}";
RA();""")
            break
    return html

def take_screenshots(html: str, output_dir: str, prefix: str, p1: str, p2: str):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_html = output_dir / "_tmp_doubles.html"
    tmp_html.write_text(html, encoding="utf-8")

    # card1=p1 카드1, card2=p1 카드2, card3=p2 카드1, card4=p2 카드2
    outs = [
        (1, output_dir / f"{prefix}_1_{p1}_득점.png",   "card1"),
        (2, output_dir / f"{prefix}_2_{p1}_클락.png",   "card2"),
        (3, output_dir / f"{prefix}_3_{p2}_득점.png",   "card3"),
        (4, output_dir / f"{prefix}_4_{p2}_클락.png",   "card4"),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        page.goto(f"file://{tmp_html.resolve()}")
        page.wait_for_timeout(1000)

        for tab_n, out_path, card_id in outs:
            page.evaluate(f"SW({tab_n})")
            page.wait_for_timeout(400)
            page.locator(f"#{card_id}").screenshot(path=str(out_path))
            print(f"✅ 저장: {out_path.name}")

        browser.close()

    tmp_html.unlink()
    return [str(o) for _, o, _ in outs]

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    csv_path   = sys.argv[1]
    p1         = sys.argv[2] if len(sys.argv) > 2 else "Home1"
    p2         = sys.argv[3] if len(sys.argv) > 3 else "Home2"
    opponent   = sys.argv[4] if len(sys.argv) > 4 else "상대팀"
    round_name = sys.argv[5] if len(sys.argv) > 5 else "경기"

    prefix = Path(csv_path).stem

    print(f"\n🏸 배드민턴 복식 분석 카드 생성")
    print(f"   선수: {p1} / {p2}  vs  {opponent}  ({round_name})")
    print(f"   CSV: {csv_path}\n")

    if not TEMPLATE_PATH.exists():
        print(f"❌ 템플릿 파일 없음: {TEMPLATE_PATH}")
        print("   generate_doubles.py와 doubles_capture.html을 같은 폴더에 두세요.")
        sys.exit(1)

    csv_text = load_csv(csv_path)
    print(f"📄 CSV 로드 완료 ({csv_text.count(chr(10))}행)")

    html = build_html(csv_text, p1, p2, opponent, round_name)

    output_dir = Path(csv_path).parent / "cards_output"
    outs = take_screenshots(html, str(output_dir), prefix, p1, p2)
    print(f"\n🎉 완료! 저장 위치: {output_dir}")
    labels = [f"{p1} 득점", f"{p1} 클락", f"{p2} 득점", f"{p2} 클락"]
    for o, lbl in zip(outs, labels):
        print(f"   📸 {Path(o).name}  →  {lbl}")
    print()

if __name__ == "__main__":
    main()
