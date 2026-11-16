# -*- coding: utf-8 -*-
"""R2 (ㄱ)(ㄴ): 장부 1.1·1.2(글자·뜻·정의 절 열)·1.3(글자·뜻·자리 열)·2절·3절(낱말·뜻·절 열)·7절(이 글의 글자·이동 열)에 첫 판 낱말·지운 개념이 남았는지 훑는다(읽기 전용)."""
import io, re, sys
ROOT = r"C:\math\임시\주차함수_증명"
L = io.open(ROOT + r"\장부_v2.md", encoding="utf-8").read().split("\n")
BAD = ["블록", "체류", "윤곽", "젊은 경로", "판정 사슬", "순증가", "멈춤 확률", "노드", "조각남", "걸음열", "크기열", "간격열", "초과 수준", "골격 수준", "보증 수준", "칸 하계", "두 조각 적분", "숲–나무 재생", "중앙 비교", "중앙 증가", "창 행", "갱신 창", "둘째 벌크", "첫 층 벌크", "소인 블록", "k-블록", "다섯 조각", "원천 질량", "블록 원천", "마디 SRC", "Borel 걸음", "네 걸음", "heavy path", "사슬 해", "열별 증가 문턱", "반감 문턱", "강단봉", "수준 위험률", "환경 무게", "동반 숲", "나머지 숲", "뿌리 문제", "뿌리 명제", "Robbins 오차", "감소 위치", "증가 위치", "거대 블록", "층층 구조", "미달 수", "자르는 자리", "문턱 예산", "예산 분해", "무게 성장", "동률의 나머지", "꼬리 오목성", "피벗", "lm-core", "moment-band", "moment-window", "S∞", "S_\infty", "마지막 102항", "Lambda_\nu", "mathfrak L_\nu", "Bd^\Lambda", "mathcal X_n,\mathcal Y_n", "명제 U", "정리 B″", "정리 TC", "(R₀)", "E^\ast", "q_J", "\delta/y^{2/3}", "장부의 이차 몫", "띠 전체 정리", "점질량", "문턱값"]
def rows(a, b, ncol):
    for n in range(a-1, b):
        ln = L[n]
        if ln.startswith("|") and not ln.startswith("|---"):
            cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
            yield n+1, cells[:ncol]
out = io.StringIO()
for name, a, b, ncol in [("1.1", 20, 43, 3), ("1.2", 43, 341, 4), ("1.3", 341, 416, 3), ("2절", 416, 503, 9), ("3절", 503, 706, 3), ("7절(글자·이동 열)", 1200, 1412, 4)]:
    for n, cells in rows(a, b, ncol):
        if name.startswith("7절"):
            cells = [cells[0]] + cells[3:4]
        txt = " | ".join(cells)
        for w in BAD:
            if w in txt:
                i = txt.find(w)
                out.write(f"[{name} {n}] 「{w}」: …{txt[max(0,i-60):i+len(w)+40]}…\n")
sys.stdout.buffer.write(out.getvalue().encode("utf-8"))
