# -*- coding: utf-8 -*-
"""2차 대조·2장 회수에서 나온 전역 조정: 불변식(기록 용어 문장 꼴, 괄호 균형을 참고로), 공통지침(기록 이름에 식별자), 장부(Z_k·H_k·𝔳_k 2.2, P_s(k) 2.9, (SC) 재표기)."""
import io


def patch(path, pairs):
    s = io.open(path, encoding="utf-8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, s.count(old), old[:70])
        s = s.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    print("patched", path)


patch("임시/주차함수_증명/scripts/불변식.py", [
    ('        for m in re.finditer(r"기록(?:은|이|에서는)? 이를 ([^\\s,.]+)(?:라|이라) 부른다", ln):',
     '        for m in re.finditer(r"기록(?:은|이|에서는|들은)?(?: 이를| 이것을| 이 양을| 이 사건을)? ([^\\s,.()]+)(?:라|이라)고? 부른다", ln):'),
    ('''        for o, c in ["{}", "()", "[]"]:
            if s.count(o) != s.count(c):
                failures.append(f"{start}: 문단의 {o}{c} 불균형 ({s.count(o)} vs {s.count(c)})")''',
     '''        if s.count("{") != s.count("}"):
            failures.append(f"{start}: 문단의 중괄호 불균형 ({s.count('{')} vs {s.count('}')})")
        for o, c in ["()", "[]"]:
            if s.count(o) != s.count(c):
                notes.append(f"{start}: 문단의 {o}{c} 개수 차이 ({s.count(o)} vs {s.count(c)}; 반열린 구간이면 정상)")'''),
])

patch("임시/주차함수_증명/파견/집필_공통지침.md", [
    ("- 기록의 이름: 기록이 붙인 이름(정리 AR, 명제 S)은 첫 진술의 괄호에만 적는다. 같은 이름이 두 기록에 있으면(보조정리 C, 정리 A 등) 식별자를 함께 적는다. 본문의 논증은 새 번호로만 가리킨다.",
     "- 기록의 이름: 기록이 붙인 이름(정리 AR, 명제 S)은 첫 진술의 괄호에만 적고, 괄호에는 늘 식별자를 함께 적는다: \"(기록 [rae1f209]의 정리 AR)\". 이름이 숫자 번호(정리 8.1, 명제 3.1, 보조정리 1)이면 이 글의 번호와 겹치므로 식별자 없이 적지 않는다. 본문의 논증은 새 번호로만 가리킨다."),
])

patch("임시/주차함수_증명/장부_기호용어이름.md", [
    (r"| $\mathscr K_{n,k}(y)$, $Z_k$, $H_k$ | 얼린 용량 다항식, 용량 $>k$ 자리 수, 용량 $=k$ 자리 수 | 2.7 | 기존 2.7 | $H_k(s)$ Borel 꼬리(4.3) |",
     r"| $\mathscr K_{n,k}(y)$ | 얼린 용량 다항식 | 2.7 | 기존 2.7 | |" + "\n" +
     r"| $Z_k$, $H_k$, $\mathfrak v_k(Z,H)$ | 용량 $>k$ 자리 수, 용량 $=k$ 자리 수, 섬유 부호식 $(1+1/k)^Z+(1-1/k)^{Z+H}-2$ | 2.2(명제 8.1의 증명이 씀; 2장 집필에서 앞당김) | 기존 2.7·6.1 | $H_k(s)$ Borel 꼬리(4.3). 6.1은 되가리킴 |"),
    (r"| (SM), (DM0), (SC) | 크기 결합의 부등식: $s_{N+1}(y)\le s_N(y)$; $s_{m-1}(k)\le s_m(k+1)$; $A_{N,\ell}/p_N\le A_{N+1,\ell+1}/p_{N+1}$ | 2.8 | 기존 6.6, [r60a6f55], [rb6a2cd0] §1.3 | |",
     r"| (SM), (DM0), (SC) | 크기 결합의 부등식: $s_{N+1}(y)\le s_N(y)$; $s_{m-1}(k)\le s_m(k+1)$; (SC) $A_{N,\ell}/p_N\le A_{N+1,\ell+1}/p_{N+1}$는 (DM0)의 개수 재표기 | 2.8 | 기존 6.6, [r60a6f55], [r79ee9e0]/c-lemma-sh, [rb6a2cd0] §1.3 | (SM)·(DM0)은 증명됨, 결합 진술은 문헌 위 비형식 |"),
    (r"| $P_s(k)$, $Q_s(k)$, $m_1(k)$, $\Upsilon_k$, $\hat\Upsilon_k$, $\mathcal T_n(t)$, $\tilde\pi_n(t)$ | 머리 합, 빚 뺀 머리 합, 증가 시작점, 상수와 상계, 표시 나무 무게 | 6.8 | 기존 | |",
     r"| $P_s(k)$ | 머리 합 $\sum_{t=k}^s x_t(k)$ | 2.9(2장 집필에서 앞당김; 6.8이 되가리킴) | 기존 6.8 | 6.5의 $P_m(j)$와 구별 문장은 2.9에 |" + "\n" +
     r"| $Q_s(k)$, $m_1(k)$, $\Upsilon_k$, $\hat\Upsilon_k$, $\mathcal T_n(t)$, $\tilde\pi_n(t)$ | 빚 뺀 머리 합, 증가 시작점, 상수와 상계, 표시 나무 무게 | 6.8 | 기존 | $\mathcal T_n(t)$는 5.5.2의 꼬리합 $\mathcal T_s(y)$와 구별 문장 |"),
])
print("done")
