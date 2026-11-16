# -*- coding: utf-8 -*-
"""M11: 부록 B의 식별자·제목·폴더·시각을 기록 폴더의 record.json 등과 대조한다."""
import re, os, json, glob, datetime
REC = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
tB = open(r"C:\math\임시\주차함수_증명\장v2\부록B.md", encoding="utf-8").read()
rows = re.findall(r"^\| (r[0-9a-f]{7}) \| ([^|]+) \| ([^|]+) \| `([^`]+)` \|", tB, re.M)
print("B 행:", len(rows))
dirs = os.listdir(REC)
for rid, tm, title, folder in rows:
    cands = [d for d in dirs if d.startswith(rid)]
    if len(cands) != 1: print(rid, "폴더 후보:", cands); continue
    d = cands[0]
    if d != folder: print(rid, "폴더 이름 차이: B=", folder, " 실제=", d)
    p = os.path.join(REC, d, "record.json")
    try: j = json.load(open(p, encoding="utf-8"))
    except Exception as e: print(rid, "record.json 읽기 실패", e); continue
    rt = (j.get("title") or "").strip()
    if rt != title.strip(): print(f"{rid} 제목 차이:\n   B : {title.strip()}\n   기록: {rt}")
    # 시각: 폴더 안 파일 mtime 또는 record.json 안의 시각 필드
    tfields = {k: v for k, v in j.items() if isinstance(v, str) and re.search(r"2026-11-\d\d", v)}
    mt = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%m-%d %H:%M")
    exp = os.path.join(REC, d, "exposition.md")
    mte = datetime.datetime.fromtimestamp(os.path.getmtime(exp)).strftime("%m-%d %H:%M") if os.path.exists(exp) else "-"
    print(f"{rid} B시각={tm.strip()} record.json mtime={mt} exposition mtime={mte} 시각필드={tfields if tfields else '-'}")
# 지식 저장소 판 번호 확인 자료
for name in ["index.md", "board.md"]:
    p = os.path.join(os.path.dirname(REC), name)
    if os.path.exists(p):
        txt = open(p, encoding="utf-8").read()
        m = re.findall(r"판\s*(\d{3})|version[^\d]{0,10}(\d{3})|v(\d{3})\b", txt)
        print(name, "판 번호 후보:", sorted({x for tup in m for x in tup if x})[:20], "| 머리:", txt[:300].replace("\n", " / "))
idx = os.path.join(os.path.dirname(REC), "index")
if os.path.isdir(idx):
    fs = sorted(os.listdir(idx)); print("index/ 파일 수", len(fs), fs[:5], fs[-5:])
