# -*- coding: utf-8 -*-
"""부록 B의 86개 식별자: 시각·제목·폴더를 지식 저장소(events/<id>.json의 at, state.json의 title, 폴더 이름)와 대조한다."""
import json, re, sys, os, datetime
ROOT = r"C:\math\임시\주차함수_증명"
K = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge"
rows = []
for line in open(os.path.join(ROOT, "장v2", "부록B.md"), encoding="utf-8"):
    m = re.match(r"^\| (r[0-9a-f]{7}) \| ([0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}) \| (.*?) \| `(r[0-9a-f]+)` \|\s*$", line)
    if m:
        rows.append(m.groups())
print("부록 B 행 수:", len(rows))
state = json.load(open(os.path.join(K, "state.json"), encoding="utf-8"))["records"]
folders = os.listdir(os.path.join(K, "records"))
tzs = {"UTC": datetime.timezone.utc, "KST": datetime.timezone(datetime.timedelta(hours=9))}
bad = 0
prev_at = None
order_bad = 0
for ident, when, title, folder in rows:
    probs = []
    cand = [f for f in folders if f.startswith(ident)]
    if len(cand) != 1:
        probs.append(f"폴더 후보 {cand}")
    else:
        if cand[0] != folder:
            probs.append(f"폴더 이름 다름: {cand[0]}")
    ev_path = os.path.join(K, "events", folder + ".json")
    if os.path.exists(ev_path):
        ev = json.load(open(ev_path, encoding="utf-8"))
        at = ev["at"]
        if prev_at is not None and at < prev_at:
            order_bad += 1
            probs.append("시각 순서 역전")
        prev_at = at
        stamps = {name: datetime.datetime.fromtimestamp(at, tz).strftime("%m-%d %H:%M") for name, tz in tzs.items()}
        local = datetime.datetime.fromtimestamp(at).strftime("%m-%d %H:%M")
        stamps["local"] = local
        if when not in stamps.values():
            probs.append(f"시각 다름: 부록 {when} / 기록 {stamps}")
    else:
        probs.append("events 파일 없음")
    st = state.get(folder)
    if st is None:
        probs.append("state.json에 없음")
    else:
        if st["title"] != title:
            probs.append(f"제목 다름:\n    부록: {title}\n    기록: {st['title']}")
    rec_path = os.path.join(K, "records", folder, "record.json")
    if os.path.exists(rec_path):
        rj = json.load(open(rec_path, encoding="utf-8"))
        if rj.get("title") != title:
            probs.append(f"record.json 제목 다름: {rj.get('title')}")
    else:
        probs.append("record.json 없음")
    if probs:
        bad += 1
        print(f"[{ident}] {when}")
        for p in probs:
            print("   -", p)
print("문제 있는 행:", bad, "/ 시각 순서 역전:", order_bad)
