# -*- coding: utf-8 -*-
"""1장 집필 회수 뒤 세션 판단의 반영: 장부 v2 3절·1.1, META(1·9장)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rw(path, fn):
    s = io.open(path, encoding="utf-8").read()
    t = fn(s)
    if t != s:
        io.open(path, "w", encoding="utf-8", newline="\n").write(t)
        print("patched", os.path.relpath(path, ROOT))
    else:
        print("unchanged", os.path.relpath(path, ROOT))


def patch_ledger(s):
    # 3절: 띠의 뜻을 통칭으로
    a = "| 띠 | 행 $n$을 $\\nu=n-2k$로 재어 가른 범위의 통칭(아래 셋에만 쓴다) | 1.5 | 띠(다섯 뜻) |"
    b = "| 띠 | 행의 범위를 한 좌표로 잰 구간의 통칭(중앙 띠·둘째 층 띠는 $\\nu=n-2k$로, 꼬리 띠는 비 $r^{3/2}/n$으로 잰다; 이 셋에만 쓴다) | 1.5 | 띠(다섯 뜻) |"
    assert s.count(a) == 1, "띠 행"
    s = s.replace(a, b)
    # 절반: 첫 정의 절 1.4
    a = "| 절반(오른쪽·왼쪽) | 위치 $(n,k)$에서 $n\\le2k$인 쪽과 $n\\ge2k+1$인 쪽(1.4의 개관도 이 기준으로 적는다) | 1.5 |"
    assert s.count(a) == 1, "절반 행"
    s = s.replace(a, "| 절반(오른쪽·왼쪽) | 위치 $(n,k)$에서 $n\\le2k$인 쪽과 $n\\ge2k+1$인 쪽(1.4의 개관이 처음 정의하고 1.5는 되풀이하지 않는다) | 1.4 |")
    # 첫 층: 나무 크기 꼴은 2.5
    a = "| 첫 층 | $k<n\\le2k$인 행, 곧 나무 크기 $k<t\\le2k+1$(자식 토막의 크기로 세면 $k\\le t-1\\le2k$; 본문은 늘 나무 크기로 말한다) | 1.5 |"
    assert s.count(a) == 1, "첫 층 행"
    s = s.replace(a, "| 첫 층 | $k<n\\le2k$인 행(1.5); 숲의 말로는 나무 크기 $k<t\\le2k+1$(2.5에서 나무를 정의한 뒤 적는다; 자식 토막의 크기 셈법 $k\\le t-1\\le2k$은 쓰지 않는다) | 1.5, 2.5 |")
    # 무거운·가벼운: 경계 귀속
    a = "| 무거운, 가벼운 | 용량(또는 문턱)보다 큰 쪽과 작은 쪽:"
    assert s.count(a) == 1, "무거운 행"
    s = s.replace(a, "| 무거운, 가벼운 | 용량(또는 문턱)보다 큰 쪽과 작은 쪽(경계값 $k$ 자체의 귀속은 그 낱말을 쓰는 대상의 정의에 적는다):")
    # 단계·수열: 일반어
    a = "| 단계 | 증명의 단계(첫째·둘째 단계) | 2.3 |"
    assert s.count(a) == 1, "단계 행"
    s = s.replace(a, "| 단계 | 증명의 단계(첫째·둘째 단계); 일반어라 정의 없이 쓴다 | —(일반어) |")
    a = "| 수열 | 일반 유한·무한 수열(간격 수열, 크기 수열, 걸음 수열, 용량 구간 길이 수열) | 1.3 |"
    assert s.count(a) == 1, "수열 행"
    s = s.replace(a, "| 수열 | 일반 유한·무한 수열(간격 수열, 크기 수열, 걸음 수열, 용량 구간 길이 수열); 일반어라 정의 없이 쓴다 | —(일반어) |")
    # 상자: 1.5의 상자 여유가 먼저 쓴다
    a = "| 상자 | 구간 산술 검사의 $(k,\\nu)$ 단위 | 8.4 |"
    assert s.count(a) == 1, "상자 행"
    s = s.replace(a, "| 상자 | 구간 산술 검사의 단위(변수 범위의 직사각형; 8.4에서는 $(k,\\nu)$ 상자) | 1.5(상자 여유), 8.4 |")
    # 1.1: r은 4·5장, N은 6–10장; 둘은 같은 수
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("| $r:=n-\\ell-1$ |"):
            cells = ln.split(" | ")
            cells[2] = "4, 5"
            cells[3] = cells[3] + " 같은 수 $n-k$를 6–10장은 환경 크기 $N$으로 부른다(1.5가 한 문장으로 밝힌다); 9장은 $N$을 쓴다"
            lines[i] = " | ".join(cells)
        if ln.startswith("| $N:=n-k$ |"):
            cells = ln.split(" | ")
            cells[2] = "6, 7, 8, 9, 10"
            if "꼬리 좌표 $r$과 같은 수" not in cells[3]:
                cells[3] = cells[3] + " 4·5장의 꼬리 좌표 $r$과 같은 수(1.5가 밝힌다)"
            lines[i] = " | ".join(cells)
    return "\n".join(lines)


rw(os.path.join(ROOT, "장부_v2.md"), patch_ledger)


def patch_meta(s):
    block = r'''
# 2026-11-12 밤: 1장 회수 뒤 세션 판단
EXTRA_NOTES.setdefault(1, []).append("1.5는 「띠」를 행 범위를 한 좌표로 잰 구간의 통칭으로 정의하고 중앙 띠·둘째 층 띠만 정의한다(꼬리 띠는 5.4). 오른쪽·왼쪽 절반은 1.4가 처음 정의하고 1.5는 되풀이하지 않는다. 1.5는 꼬리 좌표 $r=n-\\ell-1$과 환경 크기 $N=n-k$가 같은 수임을 한 문장으로 밝힌다(4·5장은 $r$, 6–10장은 $N$).")
EXTRA_NOTES.setdefault(2, []).append("「첫 층」의 나무 크기 꼴($k<t\\le2k+1$)은 2.5에서 나무를 정의한 뒤 적는다. 무거운·가벼운의 경계값 $k$ 귀속은 각 대상의 정의에 적는다.")
EXTRA_NOTES.setdefault(9, []).append("9장은 꼬리 좌표 $r$ 대신 환경 크기 $N=n-k$(같은 수)를 쓴다. 1.5의 좌표 $\\hat x=(r+1)(\\ell+1)^{-2/3}$는 $(N+1)k^{-2/3}$으로 적는다.")

'''
    anchor = "def apply(ch):"
    if "1장 회수 뒤 세션 판단" not in s:
        s = s.replace(anchor, block + anchor)
    return s


rw(os.path.join(ROOT, "scripts", "명세v2_META.py"), patch_meta)
