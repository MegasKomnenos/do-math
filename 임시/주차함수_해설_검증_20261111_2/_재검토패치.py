# -*- coding: utf-8 -*-
"""기각·무처분 재검토(세션 직권) 패치.

두 기각 보관 파일에서 채택한 항목의 조각(원래/대체)을 뽑고, 세션이 정한 문면 수정을 대체에 적용한 뒤
원고에 넣는다. 기본은 건식 검사(원래 문면이 원고에 정확히 한 번 나타나는지, 수정 치환이 대체에 정확히
한 번 맞는지)만 하고, --apply를 주면 쓴다. 판단과 근거는 같은 디렉토리의 기각_재검토.md에 있다.
"""
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8")
RUN = "임시/주차함수_해설_검증_20261111_2"
P = "임시/주차함수_해설/원고.md"
APPLY = "--apply" in sys.argv

def parse_archive(path):
    text = io.open(path, encoding="utf-8").read()
    items = {}
    for m in re.finditer(r"\n## (R\d-\S+)\n(.*?)(?=\n## R|\Z)", text, re.S):
        iid, body = m.group(1), m.group(2)
        pieces = {}
        for pm in re.finditer(r"### 조각 (\d+) — ([^\n]*)\n(?:원래:\n```\n(.*?)\n```\n)?대체:\n```\n(.*?)\n```", body, re.S):
            pieces[int(pm.group(1))] = {"where": pm.group(2), "old": pm.group(3), "new": pm.group(4)}
        items[iid] = pieces
    return items

A1 = parse_archive(f"{RUN}/_기각보관/parking-exposition-2-라운드1.md")
A2 = parse_archive(f"{RUN}/_기각보관/parking-exposition-2-라운드2.md")

def sub1(text, old, new, n=1):
    c = text.count(old)
    assert c == n, (c, old[:60])
    return text.replace(old, new)

R = []  # (label, old, new) — old는 원고 문면, new는 넣을 문면

def adopt(archive, iid, k, mods=(), label=None):
    pc = archive[iid][k]
    assert pc["old"] is not None, (iid, k)
    new = pc["new"]
    for old_s, new_s, *cnt in mods:
        new = sub1(new, old_s, new_s, cnt[0] if cnt else 1)
    R.append((label or f"{iid} 조각 {k}", pc["old"], new))

def insert_after_row(archive, iid, k, prefix, mods=()):
    """부록 C 행 삽입: prefix로 시작하는 행 바로 뒤에 대체 행을 넣는다."""
    pc = archive[iid][k]
    new_row = pc["new"]
    for old_s, new_s in mods:
        new_row = sub1(new_row, old_s, new_s)
    R.append((f"{iid} 조각 {k} (삽입)", ("__ROW__", prefix), new_row))

# ── 라운드 1 ──────────────────────────────────────────────────────────────
# R1-03 반영: 중앙의 두 기술을 갈라 적는 문면(사실 오류 없음, 명확성 개선).
adopt(A1, "R1-03", 1)

# R1-08 수정 반영: (3743,3742)에서 집계 S가 성립한다는 진술을 지우고, 기록이 인증한 두 점만 적는다(r708d99c §7.1).
R.append(("R1-08 (589행)",
    "합친 $S_{n,k}$ 자체는 같은 점에서 성립한다.",
    "합친 $S_{n,k}$는 조각별 부등식이 마찬가지로 깨지는 $(k,m)=(4000,3999)$와 $(8000,7999)$에서 구간 산술로 인증되었고, $(3743,3742)$ 자체에서는 인증되지 않았다."))
R.append(("R1-08 (772행)",
    "거짓이기 때문인데, 같은 점에서 집계된 $S_{n,k}$는 성립한다.",
    "거짓이기 때문이다. 집계된 $S_{n,k}$는 원천별 비교가 마찬가지로 깨지는 $(k,m)=(4000,3999)$와 $(8000,7999)$에서 구간 산술로 인증되었다."))

# R1-24 수정 반영: 왼쪽에 없는 것을 기록(rfbe72a8 43행)대로 「죽인 걸음을 행별 비교로 옮기는 틀 전체」로 적는다.
R.append(("R1-24 (8.5절)",
    "오른쪽 절반에서는 무거운 꼭짓점이 한 사슬이어서 사슬 부분이 5.5절의 장치(역방향 걸음, 꼭대기 행의 흡수)로 다루어졌고, 왼쪽에서는 무거운 성분이 둘 이상이어서 같은 장치의 왼쪽 판이 없다.",
    "오른쪽 절반에서는 무거운 꼭짓점이 한 사슬이어서 원 비교 전체가 5.5절의 장치(역방향 걸음, 꼭대기 행의 흡수)로 다루어졌다. 왼쪽에서도 사슬 부분 $d^{ch}$에는 같은 역방향 걸음 표현이 정확히 있다. 행을 Borel 무게로 더해 경로를 아래에서 위로 읽으면 조건 없는 Borel 걸음이 되고, 오른쪽과 다른 점은 크기 $k+1$ 이상의 걸음에 경로 밖 숲의 생존 확률 $\\Pr_g(M\\le k-1)<1$이 죽임으로 붙는다는 것뿐이다. 왼쪽에 없는 것은 그 죽인 걸음을 행별 비교로 옮기는 틀, 곧 오른쪽에서 역방향 걸음 위에 세운 나머지 장치(꼭대기 행의 흡수, 5.5.8절의 열 모멘트 상계, 5.5.10절의 귀납 틀) 전체의 왼쪽 판이다 [rfbe72a8]."))

# R1-29: R2-M4 조각 2가 같은 문단을 기록대로 다시 쓰므로 그것으로 해소된다(아래).

# R1-30 수정 반영(최소): 원고가 맞으나 기록이 극한을 B에 대해 세운 사실과 보조정리 2.21의 등식을 한 구로 잇는다.
R.append(("R1-30 (8.4절)",
    "4.3절에서 비교한 두 양 $e_n$과 $J_n(k-1)$의 임계 창 극한이 바로 $2h_2$와 $q_0$다.",
    "4.3절에서 비교한 두 양 $e_n$과 $J_n(k-1)$의 임계 창 극한이 바로 $2h_2$와 $q_0$다(임계 창의 위치는 $n\\le2k-1$이라 보조정리 2.21로 $J_n(k-1)=B_{n,k-1}$이고, 기록은 극한을 막힌 목록 수 $B_{n,k-1}$에 대해 세웠다)."))

# ── 라운드 2 ──────────────────────────────────────────────────────────────
# R2-03 수정 반영: 조각 1 그대로(U→U_ℓ), 조각 2는 6.8절 언급을 뺀다(6.8절의 U는 다른 양이다. 원고 1477행).
adopt(A2, "R2-03", 1)
adopt(A2, "R2-03", 2, mods=[("과 다른 함수이며, 4.3절과 6.8절이 같은 뜻으로 다시 쓴다)", "과 다른 함수이며, 4.3절이 같은 뜻으로 다시 쓴다)")])

# R2-09 기각 유지: 기록 ra4c01fc §11.2가 t≈32를 적으므로 원고는 기록과 다르지 않다.

# R2-10 수정 반영: 귀속은 바로잡되 부등식의 정체를 사실대로 적는다(검토 의견은 e^x≥1, 원고 계산은 e^x≥1+x).
adopt(A2, "R2-10", 1, mods=[("아래 계산은 둘째 기록의 검토 의견이 같은 부등식 $e^x\\ge1$로 적은 것이다",
                              "둘째 기록 [r23f10e9]의 검토 의견은 $e^x\\ge1$만으로 같은 하계 $\\frac d2+\\frac{5d}{2y}>0$을 적었고, 아래 계산은 $e^x\\ge1+x$를 써서 같은 하계에 이른다")])

# R2-13 수정 반영: 「인자마다 단조」라는 새 주장 없이 기록의 절차(끝점 선택, 인자별 불리한 끝점)를 적는다.
adopt(A2, "R2-13", 1, mods=[("각 인자는 $\\lambda$에 대해서도 단조이므로, 소구간 안의 값은 인자마다 불리한 쪽 끝점에서 잰 값으로 막는다.",
                              "기록은 각 소구간에서 $\\lambda$에 대한 최악값을 끝점 $\\lambda_a$ 또는 $\\lambda_b$로 잡되, 인자마다 불리한 쪽 끝점을 따로 고른다. 예를 들어 $H$는 $\\rho$와 $Q$에 증가하므로 $\\rho$에는 $\\lambda_a$를, $Q$에는 $\\lambda_b$를 넣은 값이 소구간 전체의 하계가 된다.")])

# R2-15 수정 반영(표기): 식별자를 r 뒤 일곱 자리로 고친다. 부록 C 행은 r9bf2dc6(11-10 21:24) 뒤, r696d62c(22:02) 앞.
adopt(A2, "R2-15", 1, mods=[("[r2ec875c7]", "[r2ec875c]", 2)])
insert_after_row(A2, "R2-15", 2, "| r9bf2dc6 |", mods=[("| r2ec875c7 |", "| r2ec875c |")])

# R2-25 수정 반영: binary64를 형식의 이름으로만 정의하고 보증 층과 섞지 않는다.
adopt(A2, "R2-25", 1, mods=[("(IEEE 754 표준의 64비트 부동소수점 형식. 아래에서 부동소수점 산술의 보증 층을 이 이름으로 가리킨다)",
                              "(IEEE 754 표준의 64비트 부동소수점 형식. 아래에서 이 이름은 계산이 그 형식의 부동소수점으로 수행되었음을 뜻하고, 그 계산의 보증 층이 1.4절의 세 층 가운데 어느 것인지는 자리마다 함께 적는다)")])

# R2-29 수정 반영: 근거 없는 「기록의 마디 이름」 구절을 뺀다.
adopt(A2, "R2-29", 1, mods=[("판정 이름 UL·V·V*·UL♭은 기록의 마디 이름이며, 대문자", "대문자")])

# R2-M2 수정 반영: 6절 전체에 숲 크기 뜻을 주지 않고, 쓰임별 절 범위를 정확히 적는다.
pc = A2["R2-M2"][1]
R.append(("R2-M2 (부록 A m 행)", pc["old"],
    "| $m$, $\\delta_n$ | 중앙 $\\lceil n/2\\rceil$(4.1, 4.3. 6절이 중앙을 말할 때도 이 뜻); 4.2절·5.2절에서는 꼬리 지표 $n-k$, 곧 열 $k$가 행의 오른쪽 끝에서 떨어진 거리; 5.5절과 6.5–6.8절에서는 숲(곧 행)이나 블록의 크기. $\\delta_n$은 중앙의 한 칸 차분 $b_{n,m}-b_{n,m-1}$ (4.1, 4.3) |"))

# R2-M4 수정 반영(표기와 한 문장): 식별자 일곱 자리, 1% 문턱의 자리를 기록(r3889c6a 83·442행)대로.
adopt(A2, "R2-M4", 1)
adopt(A2, "R2-M4", 2, mods=[("[r97dbedcf]", "[r97dbedc]"),
                             (", $n/k\\gtrsim6$부터야 실극만의 식이 측정값과 $1\\%$ 안에서 맞는다.",
                              ". 실극만의 식이 측정값과 $1\\%$ 안에 들기 시작하는 자리는 $k$에 따라 $n/k\\approx3.4$–$5.3$이고, $n/k\\gtrsim6$부터는 실극이 지배한다.")])
adopt(A2, "R2-M4", 3)
insert_after_row(A2, "R2-M4", 4, "| r29b01e8 |", mods=[("| r97dbedcf |", "| r97dbedc |")])

# R2-21 반영(무처분 → 수리): 실제 증가 진술을 정리 3.8 안에 넣고 7.2절의 참조를 정확히 한다.
adopt(A2, "R2-21", 1)
adopt(A2, "R2-21", 2)

# ── 적용 ──────────────────────────────────────────────────────────────────
t = io.open(P, encoding="utf-8").read()
bad = 0
for label, old, new in R:
    if isinstance(old, tuple):  # row insert
        prefix = old[1]
        lines = t.split("\n")
        idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
        if len(idx) != 1:
            print(f"[어긋남] {label}: 접두 행 {len(idx)}개"); bad += 1; continue
        if any(l.startswith(new.split("|")[1].join(["|", "|"])) for l in lines):
            print(f"[어긋남] {label}: 이미 있는 행"); bad += 1; continue
        lines.insert(idx[0] + 1, new)
        t = "\n".join(lines)
        print(f"[삽입] {label}")
        continue
    c = t.count(old)
    if c != 1:
        print(f"[어긋남] {label}: 원래 문면 {c}회"); bad += 1; continue
    t = t.replace(old, new)
    print(f"[치환] {label}")
print(f"항목 {len(R)}건, 어긋남 {bad}건, 결과 {len(t.splitlines())}행")
if bad:
    sys.exit(1)
if APPLY:
    io.open(P, "w", encoding="utf-8", newline="\n").write(t)
    print("원고에 썼다.")
else:
    io.open(f"{RUN}/_재검토_건식결과.md", "w", encoding="utf-8", newline="\n").write(t)
    print(f"건식 결과 → {RUN}/_재검토_건식결과.md (원고는 그대로)")
