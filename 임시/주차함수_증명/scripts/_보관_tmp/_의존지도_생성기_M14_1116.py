# -*- coding: utf-8 -*-
"""19차 M14 2.3(의존지도 1절)의 세 지적을 생성기 `_gen_의존지도_1절.py`에서 고친다. 2026-11-16 20:4x.
(1) 「기록 주장」 열을 11-12 판에서 이어받을 때 `/` 앞 식별자 목록이 머리의 식별자 전부를 들지 않으면 머리 차례로 채운다({{5:old-5-1}}의 r6373c70).
(2) 이어받은 비고에서 처리가 끝난 조치 메모 일곱(「…는 부록 B에 없음 → 추가」류·「11.4 문헌 목록에 FKG 추가 요」), 장 파일 행 번호(「장6 461행; 」), 라벨 와일드카드(`{{7:fold-*}}`)를 걷어 낸다."""
import io
G = r"C:\math\임시\주차함수_증명\scripts\_gen_의존지도_1절.py"
s = io.open(G, encoding="utf-8").read()

def sub(a, b):
    global s
    n = s.count(a)
    if n != 1:
        raise SystemExit("%d건: %s" % (n, a[:70]))
    s = s.replace(a, b)

sub('''rows = []
all_inputs = set()
head_edges = {}
all_edges = {}
for k in order:
''', '''# 11-12 판 비고에서 걷어 내는 문구 — 현행과 반대로 읽히는 처리 완료 조치 메모, 장 파일 행 번호, 라벨 와일드카드(19차 M14 2.3)
NOTE_FIX = [
    ("; rba2ecf4는 부록 B에 없음 → 추가", ""),
    (" ra7615a0는 부록 B에 없음(출처로 적으면 추가)", ""),
    ("(장6 461행; 명제 ", "(명제 "),
    ("; rda45d0e·r4daca3d는 부록 B에 없음(rda45d0e 추가; r4daca3d는 출처 표기 여부 집필자 결정)", ""),
    (" 11.4 문헌 목록에 FKG 추가 요", ""),
    ("; rbeae3a3는 부록 B에 없음 → 추가", ""),
    ("; r7798355는 부록 B에 없음 → 추가", ""),
    ("; r9e782f5는 부록 B에 없음 → 추가", ""),
    ("{{7:fold-*}}", "{{7:fold-A}}·{{7:fold-R}}·{{7:fold-T}}·{{7:fold-L1}}·{{7:fold-DIP}}"),
]
note_fix_hits = {}
claims_fix = []

rows = []
all_inputs = set()
head_edges = {}
all_edges = {}
for k in order:
''')

sub('''    # 기록 주장
    if o and ids and set(RID.findall(o["claims"])) == ids and "/" in o["claims"]:
        claims = o["claims"]
    else:
        claims = ", ".join(sorted(ids)) if ids else "—"
''', '''    # 기록 주장(11-12 판의 칸을 이어받을 때 `/` 앞 식별자 목록이 머리의 식별자 전부를 들도록 머리 차례로 채운다 — 19차 M14 2.3)
    if o and ids and set(RID.findall(o["claims"])) == ids and "/" in o["claims"]:
        front, back = o["claims"].split("/", 1)
        have = set(RID.findall(front))
        lack = [x for x in dict.fromkeys(RID.findall(s["head"])) if x in ids and x not in have]
        if lack:
            front = front.rstrip() + ", " + ", ".join(lack) + " "
            claims_fix.append(k)
        claims = front + "/" + back
    else:
        claims = ", ".join(sorted(ids)) if ids else "—"
''')

sub('''    # 비고(11-12 판에서 이어받음; 지운 라벨은 「뺀 …」으로 표시)
    note = (o["note"] if o and o["note"] else "—")
''', '''    # 비고(11-12 판에서 이어받음; 지운 라벨은 「뺀 …」으로 표시; NOTE_FIX의 문구는 걷어 낸다)
    note = (o["note"] if o and o["note"] else "—")
    for a, b in NOTE_FIX:
        if a in note:
            note = note.replace(a, b)
            note_fix_hits[a] = note_fix_hits.get(a, 0) + 1
''')

sub('''      "/ 비고", sum(1 for k in order if old_rows.get(k, {}).get("note", "—") not in ("—", "")), "/ 부록 D", sum(1 for k in order if k in appd_of))
''', '''      "/ 비고", sum(1 for k in order if old_rows.get(k, {}).get("note", "—") not in ("—", "")), "/ 부록 D", sum(1 for k in order if k in appd_of))
print("M14 2.3 손질: 기록 주장 앞 목록 채움", claims_fix, "/ 비고 문구 걷어 냄", len(note_fix_hits), "종", {a[:18]: n for a, n in note_fix_hits.items()},
      "/ 안 맞은 문구", [a[:18] for a, _ in NOTE_FIX if a not in note_fix_hits])
''')

io.open(G, "w", encoding="utf-8", newline="\n").write(s)
print("생성기 패치 ok")
