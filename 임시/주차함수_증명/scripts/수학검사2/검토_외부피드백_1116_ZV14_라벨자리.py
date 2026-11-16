# -*- coding: utf-8 -*-
"""ZV14 검산 — 장10의 다섯 항목이 가리키는 증명 범위 안에 어느 라벨이 있는지, 11.3절 108행의
둘째 증명 열이 어느 10장 진술을 적는지를 센다. 읽기 전용(stdout만). 실행: python -I 이 파일.

진술 범위 = 머리 줄(`**정리 {{10:…}} …**`)부터 다음 머리 줄 또는 `### ` 전까지. 준비 문단은 그 앞
진술의 범위에 섞이므로, 항목이 가리키는 준비 문단은 앵커 문구로 따로 센다.
"""
import io, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P10 = os.path.join(ROOT, "장v2", "장10.md")
P11 = os.path.join(ROOT, "장v2", "장11.md")
P2 = os.path.join(ROOT, "장v2", "장2.md")

HEAD = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{10:([^}]+)\}\}")

def read(p):
    with io.open(p, encoding="utf-8", newline="") as f:
        return f.read().split("\n")

def ranges(lines):
    out, cur, start = {}, None, None
    for i, l in enumerate(lines, 1):
        m = HEAD.match(l)
        if m or l.startswith("### ") or l.startswith("## "):
            if cur is not None:
                out[cur] = (start, i - 1)
            cur, start = (m.group(2), i) if m else (None, None)
    if cur is not None:
        out[cur] = (start, len(lines))
    return out

LABELS = ["{{2:old-2-45}}", "{{2:old-2-37}}", "{{2:old-2-31}}", "{{2:old-2-13}}", "{{2:old-2-46}}",
          "{{2:old-2-26}}", "{{10:old-8-14}}", "{{10:old-8-28}}", "{{10:old-8-25}}", "{{10:reduction-ga}}"]
TARGETS = ["old-8-31", "reduction-ga", "reduction-na", "old-8-33", "old-8-35", "bulk-majorants", "old-8-14", "old-8-19", "old-8-20", "old-8-22", "old-8-30"]

def count_in(lines, a, b, tok):
    return sum(l.count(tok) for l in lines[a - 1:b])

def main():
    L10, L11, L2 = read(P10), read(P11), read(P2)
    R = ranges(L10)
    print("# 장10 진술 범위와 라벨 수 (범위: 머리 줄 ~ 다음 머리/절 제목 전)")
    for t in TARGETS:
        a, b = R[t]
        hits = {lab: count_in(L10, a, b, lab) for lab in LABELS}
        hits = {k: v for k, v in hits.items() if v}
        print(f"  {{{{10:{t}}}}} {a}-{b}: {hits}")
    print()
    print("# 항목별 앵커 문구의 행 (문구로 찾는다; 없으면 '없음')")
    anchors = {
        "1·610 방문 확률(라벨 없음)": "\\Pr^y(q\\text{를 지남})=\\mathrm{tilt}_{q_0}(q)\\mathrm{Ren}(q_0-q)\\ge",
        "1·612 Ren 상계 두 인자(라벨 없음)": "\\le\\ \\frac1{2\\pi}\\sum_{i=1}^{\\mathfrak l-1}(q+i)",
        "1·606 사슬 공식·전이 확률": "\\ge\\mathfrak s_{q_0}(y)-\\pi^0_{y+q_0-1}(y)",
        "2·561 (iii) 음 아닌 항": "음 아닌 항 $[s_{m_0}(k+1)-s_{m_0+1}(k+1)]$과",
        "2·559 (ii) ς≥0": "\\varsigma_{m_0}(k)\\ge0$을 버리고",
        "2·655 결손 차": "Abel 합과 $\\mathfrak s_d(y)-\\mathfrak s_{d+1}(y)\\ge0$",
        "2·109 10.1절 준비 문단 (DM0)": "정리 {{2:old-2-31}}의 (DM0)로 음이 아니다",
        "2·502 10.5절 준비 문단 (SM)": "결손 차라 부르며 정리 {{2:old-2-31}}의 (SM)으로 음이 아니다",
        "3·695 r_* 가리킴": "명제 {{10:old-8-14}}의 증명 (5)의 $\\mathsf r_\\ast$",
        "3·709 10.24(ii)의 괄호": "명제 {{10:reduction-ga}}(ii)의 괄호",
        "3·249 r_* 정의": "벌크 상수는",
        "4·386 준비 문단 첫 문장": "얼린 사슬이 걸음 수 $z$만에 초과 $q$에 이를 확률은",
        "4·390 둘째 등식 2.38(나)": "둘째 등식은 보조정리 {{2:old-2-37}}(나)이고",
        "5·539 두 자리만 바꾸어": "명제 {{10:old-8-14}}의 증명을 두 자리만 바꾸어 따른다",
        # 둘째 단계 뒤에는 아래 「후」 문구가 있고 위의 1·610, 1·612, 2·561, 3·695, 4·386, 4·390 「전」 문구는 없어야 한다.
        "후 1-ㄷ 610": "보조정리 {{2:old-2-45}}로 $\\Pr^y(q\\text{를 지남})=\\mathrm{tilt}_{q_0}(q)\\mathrm{Ren}(q_0-q)\\ge",
        "후 1-ㄹ 614": "첫 부등식은 보조정리 {{2:old-2-37}}(라)의 $\\mathrm{Ren}(j)\\le(2\\pi j)^{-1/2}$를 두 인자에",
        "후 2-ㄴ 561": "음 아닌 두 항 $[s_{m_0}(k+1)-s_{m_0+1}(k+1)]$(정리 {{2:old-2-31}}의 (SM))과",
        "후 3-ㄴ 695": "벌크는 10.4절의 $\\mathsf r_\\ast$의 정의식에",
        "후 4 386": "보조정리 {{2:old-2-45}}의 첫 식(걸음 수를 고정한 방문 확률)과 둘째 식에 따라",
        "후 4 390": "$\\mathrm{Bor}^{*z}$는 2.5절의 Borel–Tanner 질량이며, $\\mathrm{Ren}(j)=j\\mathrm{Bor}(j)$는 보조정리 {{2:old-2-37}}(가)다",
        "후 6-ㄱ 281": "$g$가 증가하고(보조정리 {{10:old-8-3}}(b))",
        "후 6-ㄴ 585": "첫째, 보조정리 {{2:old-2-26}}(다)의 $1-g(m)\\le\\frac3{2m}$과",
    }
    for k, a in anchors.items():
        rows = [i for i, l in enumerate(L10, 1) if a in l]
        print(f"  {k}: {rows if rows else '없음'}")
    print()
    print("# 장2 보조정리 old-2-45 진술의 두 식과 증명의 걸음 수 고정 식 (ZV9가 첫 식을 더한 뒤: 진술에 Bor^{*i} 식이 있어야 한다)")
    for i, l in enumerate(L2, 1):
        if "\\Pr^y(\\text{사슬이 }q\\text{를 지남})=\\mathrm{tilt}_{q_0}(q)" in l:
            print(f"  진술 방문 확률 식: {i}행; 같은 줄에 걸음 수 고정 식 Bor^{{*i}}: {'있음' if '\\mathrm{Bor}^{*i}(q_0-q)' in l else '없음'}")
        if "\\mathrm{Bor}^{*i}(q_0-q)" in l and "보조정리 {{2:old-2-37}}(나)" in l:
            print(f"  증명의 Bor^{{*i}} 합 → Ren: {i}행")
    print()
    print("# 장11 108행 「2장의 표현」 둘째 증명 열이 적는 10장 진술")
    row = [l for l in L11 if l.startswith("| 2장의 표현:")]
    assert len(row) == 1, "108행을 찾지 못함"
    cols = row[0].split(" | ")
    second = cols[-1]
    for t in TARGETS:
        print(f"  {{{{10:{t}}}}}: {'있음' if ('{{10:'+t+'}}') in second else '없음'}")
    for key in ["(보조정리 {{2:old-2-45}})", "(보조정리 {{2:old-2-37}})", "(정리 {{2:old-2-31}})", "(정리 {{2:old-2-13}})"]:
        j = second.find(key)
        seg = second[max(0, second.rfind(", ", 0, j)):j + len(key)] if j >= 0 else "없음"
        print(f"  {key} 앞 구절: {seg}")

if __name__ == "__main__":
    main()
