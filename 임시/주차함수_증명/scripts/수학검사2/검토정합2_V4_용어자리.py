# -*- coding: utf-8 -*-
"""V4: 장부 1.2·3절 글귀가 가리키는 본문 정의 자리(첫 출현의 절 머리)를 찾는다. 읽기 전용. 부분 문자열 검색."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORDER = ["장1", "장2", "장3", "장4", "장5A", "장5B", "장6", "장7A", "장7B", "장8", "장9", "장10", "장11"]
BS = "\\"
TERMS = [
 ("a_j 적분 변수", [BS + "mathsf a_j", BS + "mathsf a_0"]), ("w^3/3", ["e^{-w^3/3}", "e^{-y^3/3}"]),
 ("He_j", [BS + "mathrm{He}_j"]), ("x_k", [BS + "mathsf x_k"]), ("n_PD", ["n_{" + BS + "mathrm{PD}}"]),
 ("R_2", [BS + "mathcal R_2"]), ("xi q_0", ["q_0/y^{2/3}", BS + "delta/y^{2/3}"]),
 ("J^ast", [BS + "mathcal J^" + BS + "ast", BS + "mathcal J^*"]), ("E^ast", ["E^" + BS + "ast"]),
 ("Omega", [BS + "Omega(" + BS + "xi)", BS + "Omega_c"]), ("Bor_le", [BS + "mathrm{Bor}_{" + BS + "le}", BS + "mathrm{Bor}_" + BS + "le"]),
 ("dup_m", [BS + "mathrm{dup}_m"]), ("km_N", [BS + "mathrm{km}_N"]), ("q_fb", ["q_{" + BS + "mathrm{fb}}"]), ("nu_1", [BS + "nu_1(k)"]),
 ("R_0 꼬리표", ["(" + BS + "mathrm R_0)", "(R₀)"]), ("벌크 수준 질량", ["벌크 수준 질량", "벌크 점질량"]),
 ("k_0", ["k_0"]), ("PM_y", [BS + "mathrm{PM}_y"]), ("구획 하계", ["구획 하계", "칸 하계"]), ("두 부분 적분", ["두 부분 적분", "두 조각 적분"]),
 ("재생 원천", ["재생 원천"]), ("크기 수열", ["크기 수열", "크기열"]), ("쪼개짐", ["쪼개짐"]), ("g(theta)/g(kappa)", [BS + "mathfrak g(" + BS + "theta)", BS + "mathfrak g(" + BS + "kappa)"]),
 ("토막", ["토막"]), ("Quad_n", [BS + "mathrm{Quad}_n"]), ("한 걸음 항등식", ["한 걸음 항등식"]),
 ("c_0 프락투어", [BS + "mathfrak c_0"]), ("d_k 프락투어", [BS + "mathfrak d_k"]), ("C_n 필기체", [BS + "mathcal C_n"]),
 ("O_n", [BS + "mathcal O_n"]), ("rq", [BS + "mathrm{rq}"]), ("thr_n", [BS + "mathrm{thr}_n"]),
 ("용량 가중", ["용량 가중"]), ("창 항", ["창 항"]), ("허용 숲", ["허용 숲", "허용 나무"]),
 ("대각선 둘째 차분", ["대각선 둘째 차분"]), ("사슬 생존 곱", ["사슬 생존 곱", "생존 곱"]), ("나무 함수", ["나무 함수"]),
 ("상쇄 분해", ["상쇄 분해", "중앙 상쇄 항등식"]), ("원 비교", ["원 비교"]), ("Green 응답", ["Green 응답"]), ("Green 표현", ["Green 표현"]),
 ("꼭대기 보정", ["꼭대기 보정"]), ("중복 몫", ["중복 몫"]), ("기울임 증분", ["기울임 증분"]), ("용량 구간", ["용량 구간"]),
 ("오차 예산", ["오차 예산"]), ("보조 뿌리", ["보조 뿌리"]), ("격자점", ["격자점"]), ("첫 층 벌크", ["첫 층 벌크", "첫 층 안쪽"]),
 ("덮개", ["덮개"]), ("선도항", ["선도항"]), ("주항", ["주항"]), ("엄격 단봉", ["엄격 단봉"]), ("Bor^tail", [BS + "mathrm{Bor}^{" + BS + "mathrm{tail}}"]),
 ("첫째 보정", ["첫째 보정", "둘째 보정"]), ("r 칸", ["$r$ 칸"]), ("갱신열", ["갱신열"]), ("덮개 몫", ["덮개 몫"]),
 ("이차 몫", ["이차 몫", "선형 몫"]), ("구획", ["구획"]), ("안장점", ["안장점"]), ("인증 구간", ["인증 구간"]),
 ("위 끝", ["위 끝", "아래 끝"]), ("중앙 틈", ["중앙 틈"]), ("두 나무 꼴", ["두 나무 꼴"]), ("껍질", ["껍질"]), ("착지 환경", ["착지 환경"]),
 ("V-핵심", ["V-핵심"]), ("평평한 핵심", ["평평한 핵심"]), ("바닥", ["바닥"]), ("성장률", ["성장률"]), ("무게 증분", ["무게 증분", "감소율", "제한 성장비"]),
 ("경계", ["경계"]), ("함의", ["함의", "동치"]), ("초과", ["초과"]), ("문턱", ["문턱"]), ("상위해", ["상위해"]), ("포락선", ["포락선"]),
 ("전달 범위", ["전달 범위"]), ("임계 볼츠만", ["임계 볼츠만 법칙", "Borel 분포"]), ("눈금 한 칸/ulp", ["한 칸"]),
 ("$t$ 나무 크기(2장)", ["크기 $t$", "$t$를 나무"]), ("$u$,$v$ 꼭짓점", ["꼭짓점 $u$", "$u$, $v$", "$u,v$"]), ("용량 변수 y", ["용량 $y$"]),
]
texts = {ch: io.open(os.path.join(ROOT, "장v2", ch + ".md"), encoding="utf-8").read().split("\n") for ch in ORDER}


def find(alts, maxn=3):
    out = []
    for ch in ORDER:
        hdr = ""; sub = ""
        for i, l in enumerate(texts[ch], 1):
            if l.startswith("### "):
                hdr = l[4:60]; sub = ""
            elif l.startswith("#### "):
                sub = l[5:60]
            elif l.startswith("## "):
                hdr = l[3:60]; sub = ""
            if any(a in l for a in alts):
                out.append(f"{ch}:{i} [{hdr}{(' > ' + sub) if sub else ''}] {l.strip()[:170]}")
                if len(out) >= maxn:
                    return out
    return out


for name, alts in TERMS:
    print(f"\n## {name}  {alts}")
    r = find(alts)
    print("\n".join(r) if r else "   (없음)")
