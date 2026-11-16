# -*- coding: utf-8 -*-
"""정합 2차 검토(V1–V5)의 지적 반영. (1) 5.23–5.25 복원(결정 101의 전제 「서로만 부름」이 거짓 — 5.25가 WIN^V_0의 정의·5.26과 5.18 증명의 근거),
(2) 5.7절→5.6절 번호 당김, (3) 낱말 치환의 정정(장3 273, 단위원 분할 「구간」 통일, 7.6절의 𝔩, 해석적 연쇄 셋, 선호 수열, 감소 수준, 부록 C 덮개),
(4) 장부 1.3의 산 글자 e_15 복원과 글귀 둘, 3절 「덮개」·「배치」 행, 5절 5장 배정, 장5A 966행 문장, 「한쪽 상하계」 표현 손질.
멱등. 사용: python -I scripts/수학검사2/정합검토_반영4_1114.py [--dry]"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DRY = "--dry" in sys.argv
FILES = {}
LOG = []


def rd(rel):
    if rel not in FILES:
        FILES[rel] = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
    return FILES[rel]


def wr(rel, s):
    FILES[rel] = s


def rep(rel, old, new, must=True, count=1):
    s = rd(rel)
    c = s.count(old)
    if c == count and count > 0:
        wr(rel, s.replace(old, new)); LOG.append(("고침", rel, old[:50])); return True
    if c == 0 and new and new in s:
        return True
    if must:
        print(f"[앵커 {c}] {rel}: {old[:70]}")
    return False


# ---------- (1) 5.23–5.25 복원 ----------
snap = io.open(os.path.join(ROOT, "대조v2", "수학검사2", "전_정합1114", "장5B.md"), encoding="utf-8").read().split("\n")
a = next(i for i, l in enumerate(snap) if l.startswith("**보조정리 {{5:old-5-23}}"))
b = next(i for i, l in enumerate(snap) if l.startswith("**보조정리 {{5:stirling-bor}}"))
block = snap[a:b]  # 5.23·5.24·5.25와 이음 문장(끝의 빈 줄 포함)
cur = rd("장v2/장5B.md").split("\n")
if not any(l.startswith("**보조정리 {{5:old-5-23}}") for l in cur):
    j = next(i for i, l in enumerate(cur) if l.startswith("**보조정리 {{5:stirling-bor}}"))
    cur = cur[:j] + block + cur[j:]
    wr("장v2/장5B.md", "\n".join(cur)); LOG.append(("복원", "장5B 5.23–5.25", f"{len(block)}줄"))
rep("장v2/장5B.md", r"음의 쪽에서는 창 항 $\mathrm{WIN}_0$부터 막는다. 먼저 Borel 질량의 상하계와 세 제타 상수를 준비한다.",
    r"음의 쪽에서는 창 항 $\mathrm{WIN}_0$부터 막는다. 창 항을 막으려면 음의 부분 $(x_t(y))_-$의 크기를 알아야 하는데, 그 크기는 나무 하나의 가장 큰 나무 사슬을 고정하고 보면 드러난다. 사슬을 고정하면 둘째 차분에서 음수가 될 수 있는 항은 하나뿐이다.")
# 장부 4절: 세 행을 뺌에서 현행으로 되돌림
for lab, first, kind, name in (("5:old-5-23", "5.23", "보조정리", "사슬별 둘째 차분"), ("5:old-5-24", "5.24", "보조정리", "방문 확률"), ("5:old-5-25", "5.25", "보조정리", "창 경계")):
    rep("장부_v2.md", f"| {first} | {kind} | {name} |  | 뺌 | ({lab}) |", f"| {first} | {kind} | {name} |  | 5.5 | {{{{{lab}}}}} |")
# 결정 101 본문 정정
rep("대조v2/장부_설계_세션결정.md", r"같은 원칙으로 어느 진술·산문도 부르지 않는 고아 넷을 뺀다: 5.5절의 보조정리 사슬별 둘째 차분(`{{5:old-5-23}}`)·방문 확률(`{{5:old-5-24}}`)·창 경계(`{{5:old-5-25}}`; 셋은 서로만 부름)와 2.6절의 이름 없는 명제 `{{2:old-2-23}}`",
    r"같은 원칙으로 어느 진술·산문도 부르지 않는 고아를 뺀다: 2.6절의 이름 없는 명제 `{{2:old-2-23}}`(처음 함께 뺐던 5.5절의 보조정리 5.23·5.24·5.25는 2차 검토 V1이 5.25가 $\mathrm{WIN}^{\mathrm V}_0$의 정의이자 5.26·정리 5.18 증명의 근거임을 밝혀 복원했다 — 라벨 도달 검사가 기호 정의·이름 인용을 보지 못한 탓)")
rep("대조v2/장부_설계_세션결정.md", r"정합: 장부 4절 열두 행을 「뺌」으로,", r"정합: 장부 4절 아홉 행을 「뺌」으로,")

# ---------- (2) 5.7절 → 5.6절 ----------
rep("장v2/장5B.md", "\n### 5.7 조립\n", "\n### 5.6 조립\n")

# ---------- (3) 낱말 치환 정정(V3) ----------
rep("장v2/장3.md", r"칸 $C_\ell:=(x_\ell-w_n,x_\ell]$은", r"구획 $C_\ell:=(x_\ell-w_n,x_\ell]$은")
D7A = "장v2/부록D_장7A.md"
for old, new in (("먼 구획", "먼 구간"), ("구획 반폭", "구간 반폭"), ("구획 $i$", "구간 $i$"), ("구획 입력", "구간 입력"), ("구획별 상·하계", "구간별 상·하계"),
                 ("구획의 양 끝", "구간의 양 끝"), ("구획의 오른쪽 끝값", "구간의 오른쪽 끝값"), ("첫 구획", "첫 구간"), ("구획이 ", "구간이 ")):
    s = rd(D7A)
    if old in s:
        wr(D7A, s.replace(old, new)); LOG.append(("단위원 구간", old, s.count(old)))
rep("장v2/장7B.md", r"자르는 크기의 비용 $\mathrm{up}_n(\mathfrak l)$", r"밀기를 멈춘 자리의 비용 $\mathrm{up}_n(\mathfrak l)$")
rep("장v2/장7B.md", r"그 대가로 자르는 크기의 비용을 생존 확률의", r"그 대가로 밀기를 멈춘 자리의 비용을 생존 확률의")
rep("장부_v2.md", r"(기록 $J$; Fold의 자르는 크기)", r"(기록 $J$; $\mathrm{Fold}$ 합을 끊는 지표)")
rep("장v2/장7B.md", r"해석적 사슬", r"해석적 연쇄", count=3)
rep(D7A, r"$k\ge10^7$의 사슬", r"$k\ge10^7$의 연쇄")
rep("장v2/장7A.md", r"하나의 사슬로 잇는다", r"하나의 연쇄로 잇는다")
rep("장v2/부록D_장5A.md", r"모든 선호 목록의 전수 주차와 일치했", r"모든 선호 수열의 전수 주차와 일치했")
rep("장v2/부록D_장4.md", r"감소 위치", r"감소 수준", count=4)
rep("장v2/부록C.md", r"| 덮개 | 덮개 | 5.6 |", r"| 덮개 | 덮개 | 부록 D |")

# ---------- (4) 장부·부록 A 글귀 ----------
rep("장부_v2.md", r"$\mathrm{nv}=k-r-1$(그 변수; 기록·첫 판 $u$) |", r"$\mathrm{nv}=k-r-1$(그 변수; 기록·첫 판 $u$); $\mathrm e_{15}=\sum_{j\le15}1/j!$($e$의 유리 하계; 1차 $\epsilon_{15}$ — 5B 머리의 $\epsilon$과 겹쳐 로마체) |")
rep("장부_v2.md", r"$L-\mathrm{pos}_L$(오른쪽 토막 크기;", r"$L-\mathrm{pos}_L$(오른쪽 나무 크기;")
rep("장v2/부록A.md", r"가족이 비지 않는 가장 작은 $k$(가족 시작점)", r"가족이 비지 않는 가장 작은 $k$(가족의 첫 열)")
rep("장부_v2.md", r"가족이 비지 않는 가장 작은 $k$(가족 시작점)", r"가족이 비지 않는 가장 작은 $k$(가족의 첫 열)", must=False)
rep("장부_v2.md", r"| 덮개 | 구간 산술의 덮개(상자들의 모임) | 부록 D | 덮개 |", r"| 덮개 | 계산 인증이 범위를 빈틈없이 덮음(부록 D의 덮개 검사; 상자·층들의 모임) | 부록 D | 덮개 |")
# 5절 5장 배정에서 5장을 떠난 낱말
rep("장부_v2.md", r"조립 범위; 셀; 덮개; 원천별 비교 항;", r"조립 범위; 셀; 원천별 비교 항;", must=False)
rep("장부_v2.md", r"Gauss 체제, Airy 체제, 선도항, 주항; ", "", must=False)
rep("장부_v2.md", r"떠돌기, 떠돌기 한도; 방문 확률; 선도항, 주항; ", r"떠돌기, 떠돌기 한도; 방문 확률; ", must=False)
# 3절 「배치」 행(V3): 주차함수 뜻의 첫 판 낱말과 가르는 현행 뜻
lines = rd("장부_v2.md").split("\n")
row = r"| 배치 | 대상의 놓임새(5.2의 타일 배치, 6장의 무거운 꼭짓점 배치, 7B의 형제·자식 크기의 배치); 주차함수 자체를 가리키는 첫 판의 뜻으로는 쓰지 않는다 | 5.2 | 배치(주차함수의 뜻) |"
if row not in lines:
    i = next(k for k, l in enumerate(lines) if l.startswith("| 주차함수 | 모든 차가 자리를 얻는 선호 수열"))
    lines.insert(i + 1, row); wr("장부_v2.md", "\n".join(lines)); LOG.append(("행 삽입", "3절 배치", i + 2))
# 장5A 5.4.3 끝의 반 토막 문장
rep("장v2/장5A.md", r"$n\ge50001$을 택한 까닭은 정리 {{5:old-5-2}}가 $n\le50000$을 이미 덮기 때문이고, 그러면 $k=\ell+1\ge25001$이다.", r"$n\ge50001$을 택한 까닭은 정리 {{5:old-5-2}}가 $n\le50000$을 이미 덮기 때문이다.")
# 「한쪽 상하계」 표현 손질
rep("장v2/장7A.md", r"모든 항이 양이므로 각 인자의 한쪽 상하계에서 전체의 같은 쪽 상하계가 나온다", r"모든 항이 양이므로 각 인자를 한쪽으로 막으면 전체도 같은 쪽으로 막힌다")
rep(D7A, r"모든 항이 양이므로 인자별 한쪽 상하계;", r"모든 항이 양이므로 인자마다 필요한 쪽의 상계 또는 하계;")
rep(D7A, r"하계 $\mathcal J^{\mathrm L}$은 같은 식의 반대쪽 상하계.", r"하계 $\mathcal J^{\mathrm L}$은 같은 식을 반대쪽으로 막은 것.")
rep("장v2/부록D_장8.md", r"(모두 한쪽 상하계)", r"(모두 한쪽으로 막은 값)")
rep("장v2/부록D_장8.md", r"같은 격자와 같은 한쪽 상하계를 binary64로 평가했고", r"같은 격자에서 같은 쪽으로 막은 값을 binary64로 평가했고")
rep("장v2/부록D_장9.md", r"한쪽 상하계 하나를 평가한다.", r"한쪽으로 막은 값 하나를 평가한다.")
rep("장v2/부록D_장9.md", r"기록의 코드는 같은 한쪽 상하계를 배정밀도로 평가했고", r"기록의 코드는 같은 쪽으로 막은 값을 배정밀도로 평가했고")
rep("장v2/부록D_장9.md", r"구간의 끝에서 평가해 얻는 한쪽 상하계", r"구간의 끝에서 평가해 얻는 한쪽으로 막은 값")

for rel, s in FILES.items():
    if not DRY:
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(s)
for item in LOG:
    print(item)
print("파일", len(FILES), "(dry)" if DRY else "")
