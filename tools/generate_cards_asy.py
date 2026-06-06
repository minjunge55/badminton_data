#!/usr/bin/env python3
"""
배드민턴 단식 분석 카드 자동 생성
사용법: python3 generate_cards.py <CSV파일> [선수명] [상대명] [라운드]
예시:  python3 generate_cards.py 안세영_32강.csv 안세영 "타이 추잉" 32강

출력: card1_코트.png, card2_클락.png (390x844 아이폰14 사이즈)
"""

import sys
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

# ── HTML 템플릿 경로 ──────────────────────────────────────────────
TEMPLATE_PATH = Path(__file__).parent / "singles_asy.html"

def load_csv(csv_path: str) -> str:
    """CSV 파일 읽기 (여러 인코딩 시도)"""
    import os
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"파일이 없습니다: {os.path.abspath(csv_path)}")
    
    encodings = ["utf-8", "utf-8-sig", "cp949", "euc-kr", "latin-1", "iso-8859-1", "utf-16"]
    for enc in encodings:
        try:
            with open(csv_path, encoding=enc) as f:
                content = f.read()
                print(f"   인코딩: {enc}")
                return content
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    # 마지막 수단: 바이너리로 읽어서 강제 디코딩
    with open(csv_path, "rb") as f:
        raw = f.read()
    print(f"   인코딩: binary fallback")
    return raw.decode("utf-8", errors="replace")

def build_html(csv_text: str, player: str, opponent: str, round_name: str) -> str:
    """HTML 템플릿에 CSV 데이터와 선수 정보 주입"""
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    # 1. CSV 데이터 교체
    csv_escaped = csv_text.replace("`", "\\`").replace("${", "\\${")
    html = re.sub(
        r"const CSV=`[\s\S]*?`;",
        f"const CSV=`{csv_escaped}`;",
        html
    )

    # 2. 기본값 교체 (입력 필드 value)
    html = html.replace('value="안세영"', f'value="{player}"')
    html = html.replace('value="상대 선수"', f'value="{opponent}"')
    html = html.replace('value="32강"', f'value="{round_name}"')

    # 3. 페이지 로드 시 자동으로 이름 업데이트 트리거
    html = html.replace(
        "AD=ckclk(pcsv(CSV));BS();R();",
        f"""AD=ckclk(pcsv(CSV));BS();R();
// 선수명 자동 적용
document.getElementById('ip').value="{player}";
document.getElementById('io').value="{opponent}";
document.getElementById('id').value="{round_name}";
R();"""
    )

    return html

def take_screenshots(html: str, output_dir: str, prefix: str):
    """Playwright로 카드 스크린샷 찍기 (카드3 자동 감지)"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    tmp_html = output_dir / "_tmp_card.html"
    tmp_html.write_text(html, encoding="utf-8")

    out1 = output_dir / f"{prefix}_1_코트.png"
    out2 = output_dir / f"{prefix}_2_클락.png"
    out3 = output_dir / f"{prefix}_3_클락이어서.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2
        )
        page.goto(f"file://{tmp_html.resolve()}")
        page.wait_for_timeout(800)

        # 카드1
        page.evaluate("SW(1)")
        page.wait_for_timeout(200)
        page.locator("#card1").screenshot(path=str(out1))
        print(f"✅ 카드1 저장: {out1.name}")

        # 카드2
        page.evaluate("SW(2)")
        page.wait_for_timeout(200)
        page.locator("#card2").screenshot(path=str(out2))
        print(f"✅ 카드2 저장: {out2.name}")

        # 카드3 없음 (타일 한 장에 통합)
        out3 = None

        browser.close()

    tmp_html.unlink()
    return str(out1), str(out2), None


def main():
    # 인자 파싱
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    csv_path   = sys.argv[1]
    player     = sys.argv[2] if len(sys.argv) > 2 else "선수"
    opponent   = sys.argv[3] if len(sys.argv) > 3 else "상대 선수"
    round_name = sys.argv[4] if len(sys.argv) > 4 else "경기"

    # CSV 이름 기반 출력 prefix
    prefix = Path(csv_path).stem

    print(f"\n🏸 배드민턴 단식 분석 카드 생성")
    print(f"   선수: {player}  vs  {opponent}  ({round_name})")
    print(f"   CSV: {csv_path}\n")

    if not TEMPLATE_PATH.exists():
        print(f"❌ 템플릿 파일 없음: {TEMPLATE_PATH}")
        print("   generate_cards.py와 singles_asy.html을 같은 폴더에 두세요.")
        sys.exit(1)

    # 1. CSV 읽기
    csv_text = load_csv(csv_path)
    print(f"📄 CSV 로드 완료 ({csv_text.count(chr(10))}행)")

    # 2. HTML 생성
    html = build_html(csv_text, player, opponent, round_name)

    # 3. 스크린샷
    output_dir = Path(csv_path).parent / "cards_output"
    out1, out2, out3 = take_screenshots(html, str(output_dir), prefix)

    print(f"\n🎉 완료! 저장 위치: {output_dir}")
    print(f"   📸 {Path(out1).name}  →  카카오톡 전송")
    print(f"   📸 {Path(out2).name}  →  카카오톡 전송")
    if out3:
        print(f"   📸 {Path(out3).name}  →  카카오톡 전송")
    print()


if __name__ == "__main__":
    main()
