#!/usr/bin/env python3
"""Japan Open 단식 (Last ball 존) 카드 - 코트위치 + 랠리시간, 2페이지"""
import sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright
TEMPLATE = Path("/home/claude/japan_capture.html")
def build(csv_path, player, opp, detail):
    html = TEMPLATE.read_text(encoding='utf-8')
    raw = Path(csv_path).read_bytes()
    for enc in ['utf-8-sig','utf-8','cp949']:
        try: text=raw.decode(enc); break
        except: continue
    text=text.replace('`','\\`').replace('${','\\${')
    html=re.sub(r"const CSV=`[\s\S]*?`;", f"const CSV=`{text}`;", html)
    for sid in ['ip1','ip1b']:
        html=re.sub(rf'(id="{sid}"[^>]*>)[^<]*(</)', lambda m:m.group(1)+player+m.group(2), html)
    for sid in ['ip2','ip2b']:
        html=re.sub(rf'(id="{sid}"[^>]*>)[^<]*(</)', lambda m:m.group(1)+opp+m.group(2), html)
    for sid in ['id1','id2']:
        html=re.sub(rf'(id="{sid}"[^>]*>)[^<]*(</)', lambda m:m.group(1)+detail+m.group(2), html)
    return html
def main():
    csv_path, player, opp, detail = sys.argv[1:5]
    out_dir=Path(csv_path).parent/"cards_output"; out_dir.mkdir(parents=True,exist_ok=True)
    html=build(csv_path,player,opp,detail)
    tmp=out_dir/"_tmp_jp.html"; tmp.write_text(html,encoding='utf-8')
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
        pg.goto(f"file://{tmp.resolve()}"); pg.wait_for_timeout(800)
        for i,cid in enumerate(['card1','card2'],1):
            out=out_dir/f"{Path(csv_path).stem}_{i}.png"
            pg.locator(f"#{cid}").screenshot(path=str(out)); print(f"✅ {out.name}")
        b.close()
    tmp.unlink()
if __name__=="__main__": main()
