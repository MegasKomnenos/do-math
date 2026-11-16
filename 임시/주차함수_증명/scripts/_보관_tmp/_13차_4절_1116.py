# -*- coding: utf-8 -*-
"""13차 수리 공통 안내의 4절 자리표시자를 본문으로 바꾸고, 의존지도 생성기의 두 자리(T14-4 표기 문단·T14-5 뺌 표 옮김)를 고친다. 2026-11-16."""
import io, os
ROOT = r"C:\math\임시\주차함수_증명"
P = os.path.join(ROOT, "파견", "전체검토13_수리_공통_1116.md")
B = os.path.join(ROOT, "파견", "_13차_4절_본문_1116.md")
c = io.open(P, encoding="utf-8").read()
body = io.open(B, encoding="utf-8").read().rstrip("\n") + "\n"
PH = "## 4. 이번 차례의 배정 메모(세션이 보고를 훗어 적은 임자와 주의; 판정이 아니다)\n\n(T1–T14 보고 회수 뒤 작성)\n"
PH2 = "## 4. 이번 차례의 배정 메모(세션이 보고를 훑어 적은 임자와 주의; 판정이 아니다)\n\n(T1–T14 보고 회수 뒤 작성)\n"
n = c.count(PH2)
assert n == 1, n
c = c.replace(PH2, body)
io.open(P, "w", encoding="utf-8", newline="\n").write(c)
os.remove(B)
print("공통 4절 ok", len(c))

G = os.path.join(ROOT, "scripts", "_gen_의존지도_1절.py")
g = io.open(G, encoding="utf-8").read()
old1 = "「문헌」은 11.4절 표에서 그 라벨을 「쓰인 자리」로 든 행(11-12 판의 칸은 쓰지 않는다)."
new1 = "「문헌」은 11.4절 표에서 그 라벨을 「쓰인 자리」로 든 행(11-12 판의 칸은 쓰지 않는다; 「쓰인 자리」가 증명의 근거가 아니라 설명 자리임을 밝힌 행 — Knuth의 갈고리 길이 공식 — 은 입력이 아니므로 넣지 않는다)."
assert g.count(old1) == 1, g.count(old1)
g = g.replace(old1, new1)
old2 = '''    else:
        how = "11-12 판에만 있던 라벨(장부 4절에 뺌 행 없음; 결정 73·97 또는 집필 회수 때 뺌·대체)"
        tag = lab_tag(k)
    gone_rows.append('''
new2 = '''    else:
        # 2026-11-16 13차 T14-5: 같은 이름의 라벨이 다른 장에 살아 있으면 뺀 것이 아니라 옮긴 것이다(대응표와 같은 규칙; 예: 5:zeta-constants → 2:zeta-constants).
        moved = [c for c in cur if c.split(":", 1)[1] == k.split(":", 1)[1] and c != k]
        if moved:
            how = "옮김(%s %s절; 장부 4절 머리말)" % (lab_tag(moved[0]), st[moved[0]]["section"])
        else:
            how = "11-12 판에만 있던 라벨(장부 4절에 뺌 행 없음; 결정 73·97 또는 집필 회수 때 뺌·대체)"
        tag = lab_tag(k)
    gone_rows.append('''
assert g.count(old2) == 1, g.count(old2)
g = g.replace(old2, new2)
io.open(G, "w", encoding="utf-8", newline="\n").write(g)
print("생성기 ok")
