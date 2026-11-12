# -*- coding: utf-8 -*-
"""둘째 판 장별 명세의 장 수준 내용(제목·범위·경중·절 제목·진술 순서·특별 지시·자리 표시자·부록 D 점검표).

명세v2_수정.py(진술 수준) 뒤에 돌린다. 사용: python 명세v2_META.py [장 번호 ...]
"""
import io, json, os, sys

ROOT = r"C:\math\임시\주차함수_증명"
SPEC = os.path.join(ROOT, "파견", "명세v2")

COMMON_NOTES = [
    "장부 v2(`장부_v2.md`)의 글자·낱말만 쓴다. 첫 판 장 파일의 글자가 장부와 다르면 장부의 글자로 바꾸고, 바꾼 글자는 대조 파일 「첫 판에서 옮긴 문장의 바꾼 점」에 적는다.",
    "지위 표지는 첫 판의 것을 물려받지 않고 지침 7.3의 정의로 다시 판정한다. 이 글 안에 모든 단계가 손으로 적힌 결과는 「증명됨」이다.",
    "첫 판 문장에 있는 구별 문장·앞당김 참조·사족·지위 설명·기록 표기 문장·「관찰」 문단·정정 이력은 모두 뺀다(지침 4.6·6절).",
    "기록의 결과 이름(정리 T, 정리 F′ 등)은 진술 머리의 괄호에만 적고 본문은 라벨로만 부른다.",
]

META = {
    1: dict(title="문제",
        scope="주차함수와 최대 변위를 정의하고, 개수열과 단봉성 문제 P를 세우며, 주 정리의 진술과 증명의 지도, 그리고 읽는 법(지위·표기·좌표)을 준다. 독자가 이 장만 읽고도 무엇이 증명되는지와 글의 길을 알 수 있어야 한다.",
        weights="가벼운 장이다. 정의 넷과 Pollak 셈(표준)은 짧고 정확하게. 1.4의 증명 지도는 정의된 대상만으로 세 조각(중앙·오른쪽·왼쪽)과 두 독립 증명의 관계를 말한다. 1.5의 좌표와 자리 이름은 뒤의 모든 장이 쓰므로 정의가 완전해야 한다(새로운 것은 없으나 빠짐이 있으면 안 된다).",
        sections={"1.1": "선형 탐사와 주차함수", "1.2": "변위와 최대 변위", "1.3": "개수열과 단봉성", "1.4": "주 정리와 증명의 지도", "1.5": "읽는 법: 지위, 표기, 좌표"},
        intros={
            "1.1": "첫 두 문단은 새로 쓴다. Konheim–Weiss가 분석한 선형 탐사 과정의 사실에서 출발해 주차 과정을 서술하고 정의 1.1, 명제 1.2(Pollak 셈)로 간다. 대괄호 안내문과 「이 글은 …」 꼴의 자기 언급은 쓰지 않는다.",
            "1.3": "「열」은 $b_{\\cdot,\\ell}$(수준을 고정한 수열)만 뜻한다. 두 이웃 열의 비교는 「위치 $(n,k)$」로 부르되 그 낱말의 정의는 1.5에 있으므로 1.3에서는 쓰지 않는다. 작은 $n$의 표를 둔다.",
            "1.4": "주 정리의 진술, 세 조각(중앙·오른쪽·왼쪽)의 개관, 왼쪽이 둘째 층 비교 하나로 줄고 두 독립 증명으로 닫힌다는 사실, 11장이 보증을 적는다는 한 문장. 지위의 설명은 1.5로 보낸다. 첫 판 1.4의 「적혀 있지만 싣지 않은」 양보문은 쓰지 않는다.",
            "1.5": "진술 없는 절. 다섯 지위의 정의 표(증명됨·비형식 증명·계산 증거·형식 증명·추측·발견적; 뒤 둘은 이 글에 쓰이지 않음을 표 안에서만), 「이 글의 증명은 모두 사람이 읽는 증명이며 기계 검증을 거치지 않았다」는 한 문장, 식별자 `[r…]`가 결과를 처음 세운 기록의 출처라는 규칙, 부록 A·B·C·D와 자료 묶음의 쓰임, 산술 등급 넷의 이름, 좌표와 자리 이름의 정의(위치 $(n,k)$, 한 칸 차분 $d_{n,k}$, 비 $\\lambda=k/n$, 오른쪽·왼쪽 절반(위치 기준: $n\\le2k$ 오른쪽, $n\\ge2k+1$ 왼쪽), $j$째 층, 중앙 행과 한가운데, 중앙 창·임계 창과 눈금 $k^{2/3}$, 벌크, 중앙 띠·둘째 층 띠·꼬리 띠, 극 영역). 나무가 필요한 이름(무거운 꼭짓점·성분)은 2.5에서 정의하므로 여기서 쓰지 않는다. 첫 판 3.4절의 어휘 문단이 재료다(원고.md 941–1017행 부근).",
        },
        order={}, notes=COMMON_NOTES + ["1.5의 좌표 낱말은 장부 v2 3절의 뜻과 글자 그대로 일치해야 한다. 장부에 없는 자리 이름이 필요하면 반환에 적는다."],
        todo=[], D_items=[]),
    2: dict(title="기본 표현",
        scope="결과 순열과 섬유, 마지막 차 재귀, 라벨 숲, 최대 나무 사슬, Borel 분포와 생존 확률, 얼린 용량 다항식, 크기 단조성, 나무를 고정한 행 차분, 지수 공식과 다섯 조각, Borel 갱신 집합, 그리고 새 절 2.12의 사슬 전개·이동 꼬리·사슬 정규화. 뒤의 모든 장이 이 장의 진술을 라벨로 부른다.",
        weights="표준과 새로운 것이 섞인 장. 2.1–2.4는 표준에 가깝고 짧게, 2.5·2.7·2.8·2.9·2.10·2.12는 이 연구가 세운 것이므로 증명을 완전히 전개한다. 2.12의 이동 꼬리(`{{2:moving-tail}}`)는 고비다(Bonferroni·볼록성 논증).",
        sections={"2.1": "결과 순열과 용량", "2.2": "섬유는 단봉이 아니다", "2.3": "마지막 차 재귀", "2.4": "라벨 숲", "2.5": "가장 큰 나무와 최대 나무 사슬", "2.6": "Borel 분포, 임계 볼츠만 법칙, 생존 확률", "2.7": "얼린 용량 다항식과 동률–막힘 항등식", "2.8": "크기 단조성과 수준 방문 보존", "2.9": "나무를 고정한 행 차분과 문턱 부분나무", "2.10": "지수 공식과 다섯 조각 분해", "2.11": "Borel 갱신 집합과 갱신 다리", "2.12": "지정 사슬의 전개와 이동 꼬리의 균일 추정"},
        intros={
            "2.2": "정리 2.5의 마지막 문장($n\\le6$의 모든 섬유 전수)은 부록 D 항목으로 보내고 본문에는 「부록 D.{{D:fiber-enumeration}}의 계산으로 확인된다」 한 문장만 둔다.",
            "2.5": "명제 2.20의 상계값 계산은 부록 D(`{{D:fiber-nonunimodal-bound}}`).",
            "2.8": "첫 판 2.31은 세 부등식 (SM)·(DM0)·(SC)만의 정리로 다시 진술한다. 결합의 존재와 Fleurat 인용, 그 해석에 기댄 문장은 쓰지 않는다. (나)의 귀납 증명이 셋을 모두 덮는다(의존지도 v2 3절 (ㅁ)). 새 따름정리 `{{2:ratio-e}}`는 (나)에서 두 줄로 따른다.",
            "2.9": "첫 판 2.39의 괄호 「이름은 3.4절에서 정한다」는 쓰지 않는다(이름은 1.5에 있다).",
            "2.12": "새 절. 5장(`{{5:third-group}}`·`{{5:marked-recursion}}`)과 6장(다섯 조각·$v_m<0$)이 함께 쓰는 세 결과를 기록에서 모든 단계로 전개한다. 2.5·2.9·2.11의 대상만으로 진술한다.",
        },
        order={"2.7": ["{{2:old-2-27}}", "{{2:old-2-28}}", "{{2:old-2-29}}", "{{2:old-2-30}}", "{{2:J-egf}}"],
               "2.8": ["{{2:old-2-31}}", "{{2:ratio-e}}", "{{2:old-2-32}}", "{{2:old-2-33}}", "{{2:old-2-34}}"],
               "2.12": ["{{2:chain-expansion}}", "{{2:moving-tail}}", "{{2:chain-normalization}}"]},
        notes=COMMON_NOTES + ["2.6·2.11의 영어 병기(임계 볼츠만 법칙(critical Boltzmann law), 확률보행(random walk), 갱신함수(renewal function), 크기 편향(size-biased), 사다리 시각(ladder epoch))는 첫 정의 자리에 한 번만."],
        todo=[],
        D_items=[{"label": "{{D:fiber-enumeration}}", "for": "{{2:old-2-5}}", "sources": [{"record": "r81e7051", "note": "n≤6 섬유 전수(정확 정수); 증거 파일 경로는 기록 §재현 절"}]},
                 {"label": "{{D:fiber-nonunimodal-bound}}", "for": "{{2:old-2-20}}", "sources": [{"record": "r88bed8a", "note": "명제 F의 상계값 계산"}]}]),
    3: dict(title="극한 법칙과 문제의 어려움",
        scope="해싱 극한(Petersson·Janson의 정리를 문헌 인용), 극한 밀도의 봉우리(정리 3.3, 증명 전부), 로그오목성의 실패(정리 3.4 증명 전부, 정리 3.5 계산 증거), 봉우리의 위치(정리 3.6). 사슬이 쓰는 것은 정리 3.6뿐이고 나머지는 문제가 자명하지 않은 까닭을 보이는 자리다.",
        weights="가벼운 장이되 안의 증명은 완전하다. 정리 3.3(멜린 변환은 문헌, 나머지 손 증명)과 정리 3.6(손 증명 전부; 외부 입력 없음 → 「증명됨」)은 전개하고, 3.4·3.5의 계산은 방법·범위·산술 등급을 부록 D에.",
        sections={"3.1": "해싱 극한", "3.2": "극한 밀도의 봉우리", "3.3": "로그오목성의 실패", "3.4": "봉우리의 위치"},
        intros={
            "3.1": "명제 3.1: 대응은 증명하고 극한 진술은 Petersson, *The maximum displacement for linear probing hashing*의 정리를 저자·논문·Theorem 번호로 인용한다(지침 4.3). 명제 3.2: 멜린 변환 $\\mathbb E X^s$와 그 유효 범위는 Janson, arXiv:1002.4135, Theorem 1.12를 인용하고, 곱 표현 자체의 증명(세 인자의 모멘트를 곱해 멜린 변환과 맞추고 분포 동일성)은 첫 판 873행의 논증을 옮긴다(기록 [r81e7051] `limiting-shape.md` §2가 출처).",
            "3.3": "정리 3.4의 $n\\le80$ 계산과 정리 3.5의 계산은 부록 D. 다른 강화의 반례 목록은 쓰지 않는다.",
            "3.4": "정리 3.6만 남는다. 첫 판 3.4의 어휘 문단은 1.5로 갔고 극한 정리의 언급은 쓰지 않는다. 증명의 유리수 한 값(7309649993107890414228499/15500000000000000000000000<0.4716)은 닫힌 꼴 정확 산술이므로 본문에 둔다.",
        },
        order={}, notes=COMMON_NOTES,
        todo=[],
        D_items=[{"label": "{{D:logconcavity-failure-n80}}", "for": "{{3:old-3-4}}", "sources": [{"record": "r81e7051", "note": "n≤80 정확 계산"}]},
                 {"label": "{{D:cumulative-logconcavity}}", "for": "{{3:old-3-5}}", "sources": [{"record": "r81e7051", "note": "누적 로그오목성 실패의 계산(방법·범위·산술 등급)"}]}]),
    4: dict(title="분할과 중앙",
        scope="네 위치쌍 분할, 감소 뒤의 로그오목성 Q와 P의 함의, 중앙 틈의 증명(정리 4.5–4.7과 새 보조정리 셋), 왼쪽·횡단·조건부 로그오목성의 동치. 중앙 틈은 오른쪽 절반과 왼쪽 절반을 잇는 고리다.",
        weights="4.3 중앙 틈이 고비다. 첫 판의 한 문단 전사를 보조정리와 번호 단계로 다시 조직한다: 적분 표현(`{{4:e-integral}}`, 작성자 증명), 상쇄 분해, 실수 비교(정리 4.7), Gauss 계수의 경계(`{{4:gauss-coeff}}`), 두 보정의 수직선 적분(`{{4:two-corrections}}`), 조립, 정수 인증(부록 D). 4.1·4.2·4.4는 표준에 가깝고 짧게.",
        sections={"4.1": "위치쌍 분할", "4.2": "감소 뒤의 로그오목성", "4.3": "중앙 틈", "4.4": "왼쪽, 횡단, 조건부 로그오목성의 동치"},
        intros={"4.3": "`{{4:e-integral}}`은 기록이 「적분 인자 해」라고만 적은 단계를 이 글이 증명하는 자리다. $F_*$·$K$·$Q_k$의 정의에서 ODE를 적분인자로 풀어 (R7)(R8)을 유도하고 그 문장 앞에 `(작성자 판단)`을 붙인다. 16≤n≤20000의 정수 구간 인증은 부록 D(`{{D:central-gap-integer}}`)."},
        order={"4.3": ["{{4:old-4-5}}", "{{4:old-4-6}}", "{{4:e-integral}}", "{{4:old-4-7}}", "{{4:gauss-coeff}}", "{{4:two-corrections}}"]},
        notes=COMMON_NOTES + ["정리 4.8의 20≤n≤1000 정확 계산은 부록 D 항목(`{{D:crossing-small-n}}`)으로."],
        todo=[],
        D_items=[{"label": "{{D:central-gap-integer}}", "for": "{{4:old-4-5}}", "sources": [{"record": "rce3dc75", "note": "§8.2 16≤n≤20000의 정수 구간 인증"}]},
                 {"label": "{{D:crossing-small-n}}", "for": "{{4:old-4-8}}", "sources": [{"record": "rce3dc75", "note": "20≤n≤1000 정확 계산"}]}]),
    5: dict(title="오른쪽 절반",
        scope="유한 인증(정리 5.1·5.2), 오른쪽 끝의 감소와 임계 창의 증가(5.3–5.7과 그 전제 보조정리 서른), 세 명제의 동치, 명시적 띠·임계 창·잔여 $W^\\sharp$(5.12–5.17과 전제 여덟), $W$의 증명(5.18–5.38), $X$의 증명(5.39–5.41과 `{{5:arc-leading}}`), 조립. 첫 판에서 결과식만 두었던 5.2의 정리들 뒤에 약 700행의 손 보조정리가 들어온다.",
        weights="가장 무거운 장. 5.2의 전제 보조정리(타일 모형 사슬, FKG, 핵 계수 경계, 셋째 묶음 비교), 5.4의 포락선·재귀·핵 끼움, 5.5의 재조직(5.5.6·5.5.8 전사 문단 → 보조정리와 단계), 5.6의 전개가 고비다. 5.1·5.3·5.7은 가볍다. 13조각 포락선의 단항식 15개·조각 상수·영역 II·III 식(약 35식)은 부록 D에 수식으로 옮기고, 단항식 계수의 유도는 작성자 증명으로 쓴다.",
        sections={"5.1": "유한 인증", "5.2": "오른쪽 끝의 감소와 임계 창의 증가", "5.3": "세 명제의 동치", "5.4": "명시적 띠, 임계 창, 잔여 $W^\\sharp$", "5.5": "$W$의 증명", "5.6": "$X$의 증명", "5.7": "조립"},
        intros={
            "5.1": "정리 5.1·5.2의 명세(범위, 알고리즘, 산술 등급, 독립 재계산)는 부록 D. 정리 5.1의 부록 D 항목은 뒤의 장들이 「정리 5.1의 범위 안」으로 가리키는 $n\\le15$ 정확 행도 덮는다.",
            "5.2": "진술 순서는 전제가 앞선다. 5.3의 전제(`{{5:tail-poly}}`→`{{5:rational-cert}}`→`{{5:sharp-546}}`), 5.4의 전제(`{{5:green-connection}}`→`{{5:source-rep}}`→`{{5:cayley-ratio}}`), 5.5의 전제(타일 모형 `{{5:marked-riccati}}`→`{{5:response-kernel}}`→`{{5:fixed-size-response}}`→`{{5:inverse-renewal}}`→`{{5:renewal-fkg}}`→`{{5:suff-cond}}`→`{{5:lemma-L}}`), 5.6의 전제(`{{5:kernel-C-bound}}`, `{{5:kernel-bounds}}`, `{{5:third-group}}`, `{{5:last-gap}}`, `{{5:sign-sandwich}}`), 5.7의 전제(`{{5:first-moment-weight}}`, `{{5:marked-recursion}}`, `{{5:parity-tail}}`). 정리 5.4의 (G)는 $p_k/p_{k-1}$이 든 꼴로 적는다. 정리 5.7의 $O(\\eta^2)$는 명시 나머지 $\\varepsilon_k(\\eta)$로.",
            "5.4": "정리 5.12의 둘째 보정 (3.5)를 포함한다(첫 판에 진술 없음). 정리 5.13의 §7.1 설계 상수와 §8.4 구간 검증 상수는 부록 D.",
            "5.5": "5.5.6·5.5.8의 전사 문단을 보조정리와 번호 단계로 재조직한다(내용을 빼지 않음). 정리 5.32·5.37의 상수는 검토의 정정값(0.71216, 7.7148)만 쓰고 코드의 미정정 1.3352092는 쓰지 않는다. 13조각 포락선 식 전부는 부록 D(`{{D:thirteen-piece-envelope}}`)로, 단항식 계수의 유도(U1 다섯 사실→전개)는 작성자 증명으로 본문에 쓰고 `(작성자 판단)`을 붙인다.",
            "5.6": "`{{5:arc-leading}}`은 5.40 전개의 전제이므로 5.40 앞에 둔다. 보조정리 5.41의 「계수표」는 존재하지 않는다. 계수 생성 알고리즘(전개·세 기법·닫힌 꼴 모멘트 $F(a)=\\sqrt{\\pi/2}\\sqrt a/(a+1)$, $J^{\\mathcal D}_m=(-2)^mF^{(m)}$)과 산술 등급·덮개 결과(잎 193, 최소 0.0466)를 부록 D에 명세한다. notes-lemmaV.md의 중간값은 쓰지 않고 최종판($c_I=2.04$, 앞인자 3)만.",
            "5.7": "오른쪽 절반의 덮개 표만. 보증 서술은 11장으로.",
        },
        order={
            "5.2": ["{{5:tail-poly}}", "{{5:rational-cert}}", "{{5:sharp-546}}", "{{5:old-5-3}}",
                    "{{5:green-connection}}", "{{5:source-rep}}", "{{5:SR-implies-QR}}", "{{5:cayley-ratio}}", "{{5:old-5-4}}",
                    "{{5:marked-riccati}}", "{{5:response-kernel}}", "{{5:fixed-size-response}}", "{{5:inverse-renewal}}", "{{5:renewal-fkg}}", "{{5:suff-cond}}", "{{5:lemma-L}}", "{{5:old-5-5}}",
                    "{{5:kernel-C-bound}}", "{{5:kernel-bounds}}", "{{5:third-group}}", "{{5:last-gap}}", "{{5:sign-sandwich}}", "{{5:old-5-6}}",
                    "{{5:first-moment-weight}}", "{{5:marked-recursion}}", "{{5:parity-tail}}", "{{5:old-5-7}}"],
            "5.4": ["{{5:weight-envelope}}", "{{5:marked-chain-rec}}", "{{5:kernel-sandwich}}", "{{5:omitted-tail}}", "{{5:old-5-12}}", "{{5:cover-edge}}",
                    "{{5:unit-circle}}", "{{5:cut-rep}}", "{{5:hat-normalization}}", "{{5:old-5-13}}", "{{5:old-5-14}}", "{{5:old-5-15}}", "{{5:old-5-16}}", "{{5:old-5-17}}"],
            "5.6": ["{{5:old-5-39}}", "{{5:arc-leading}}", "{{5:old-5-40}}", "{{5:old-5-41}}"],
        },
        notes=COMMON_NOTES + [
            "FKG 부등식(Fortuin–Kasteleyn–Ginibre 1971), Wallis 부등식, Robbins 부등식, Jensen 부등식은 문헌 인용(진술과 출처만).",
            "장이 크므로 절 단위로 파일을 쌓아 가며 써도 된다. 다만 산출은 한 파일 `장v2/장5.md`다.",
            "첫 판 5.5.6의 「넓은 창」과 6.9·7장의 「창」은 장부 v2가 「착지 창」 하나로 정했다.",
        ],
        todo=[],
        D_items=[
            {"label": "{{D:exact-n20000}}", "for": "{{5:old-5-1}}", "sources": [{"record": "r19de912", "note": "n≤20000 정확 정수 인증(생산자·peer 독립 구현)"}, {"record": "rc9aee43", "note": "n≤10000 모형 없는 행 인증"}]},
            {"label": "{{D:c50}}", "for": "{{5:old-5-2}}", "sources": [{"record": "r19de912", "note": "C50: n≤50000 인증의 명세"}]},
            {"label": "{{D:sharp-546-certificates}}", "for": "{{5:old-5-3}}", "sources": [{"record": "ra88ba51", "note": "100개 인증서 재실행(정확 정수·유리수)"}]},
            {"label": "{{D:newton-m170}}", "for": "{{5:old-5-4}}", "sources": [{"record": "r708d99c", "note": "§5.2–5.3 단항·Newton 기저 인증"}]},
            {"label": "{{D:tail-T1-partAB}}", "for": "{{5:old-5-5}}", "sources": [{"record": "r5ddf8a8", "note": "Part A 171≤m≤9999 9829점 구간 산술"}, {"record": "r0dc57fa", "note": "Part B 상수"}]},
            {"label": "{{D:bernstein-signs}}", "for": "{{5:old-5-6}}", "sources": [{"record": "r690be93", "note": "76구간 192차·35구간 96차 Bernstein 계수 부호(정확 산술)"}]},
            {"label": "{{D:band-A-certification}}", "for": "{{5:old-5-12}}", "sources": [{"record": "r13b0b8f", "note": "정리 A·A⁺의 인증(생산자·peer 독립)"}]},
            {"label": "{{D:critical-window-rig}}", "for": "{{5:old-5-13}}", "sources": [{"record": "ra4c01fc", "note": "§7.1 둘러싸기 설계 상수, §7.2 덮개, §8.4 구간 검증 상수"}]},
            {"label": "{{D:thirteen-piece-envelope}}", "for": "{{5:old-5-32}}", "sources": [{"record": "r8a9b11e", "note": "13조각 포락선(단항식 15·조각 상수·영역 II·III 식)과 ζ·κ 셀 적분, 꼬리 처리; 정정값 0.71216·7.7148"}]},
            {"label": "{{D:lemma-H-interval}}", "for": "{{5:old-5-40}}", "sources": [{"record": "r5f5cf73", "note": "전 영역 구간 산술 덮개"}]},
            {"label": "{{D:lemma-V-coefficients}}", "for": "{{5:old-5-41}}", "sources": [{"record": "r5f5cf73", "note": "certify2.py의 계수 생성 알고리즘과 덮개(잎 193, 최소 0.0466)"}]},
        ]),
    6: dict(title="첫 층의 추정",
        scope="두 증명이 함께 쓰는 첫 층($k<N\\le2k+1$)의 결과를 한 장에 모은다: 첫 층 생존의 상계(정리 F′), 제한 성장비·표시 나무 무게·위험률, 머묾 법칙, 점질량과 대각선 하계((Diag)·(D)), 첫 층 꼬리합과 V-core(정리 U), UL 꼬리합의 다섯 조각과 (V). 첫 판에서는 7·8장과 6.7절에 흩어져 진술만 있던 것들이다.",
        weights="새 장이며 거의 전부가 전개다. 정리 F′(85행), 머묾 법칙(153행), (Diag) 첫 층 정리(169행), 정리 U(94행), 다섯 조각(약 260행)이 고비다. 두 증명의 공통 입력이므로 경중 배분상 「가벼운 것」이지만 증명은 완전히 전개한다(위치와 표지만 가볍게).",
        sections={"6.1": "첫 층 생존의 상계", "6.2": "제한 성장비, 표시 나무 무게, 위험률", "6.3": "머묾 법칙", "6.4": "점질량과 대각선 하계", "6.5": "첫 층 꼬리합과 V-core", "6.6": "UL 꼬리합의 다섯 조각과 (V)"},
        intros={
            "6.2": "표시 나무 무게 $\\mathcal T_n(s)=\\binom ns s^{s-1}A_{n-s,k-1}$와 그 정규화의 정의를 이 절 머리에 둔다(첫 판 6.8절 2077행 문단에서 옮기되 「환경 무게」 병기와 5.5.2절 꼬리합에 대한 구별 문장은 뺀다; 글자는 장부 v2). 그 뒤 두 나무 꼴(`{{6:old-7-19}}`), c-sharp(`{{6:old-7-20}}`, 전개), 표시 나무 무게의 증가(`{{6:old-7-21}}`), (Hz)(`{{6:old-7-24}}`, 전개).",
            "6.3": "첫 판의 「체류 법칙」은 장부 v2에서 「머묾 법칙」이다.",
            "6.4": "순서: 따름정리 8.11 → 정리 8.12 → `{{6:pair-rearrange}}` → `{{6:diag-first-layer}}` → `{{6:cor-L}}` → `{{6:D-bound}}`. `{{6:D-bound}}`에는 첫 판 6.8절 2075–2081행의 $\\Upsilon_k$·$\\hat\\Upsilon_k$ 상계와 7.3절 2630행의 (D)·(Υ) 서술이 들어온다.",
            "6.5": "첫 판 6.7절의 표(UL, V, V*)를 옮기되 UL♭·FC 행은 쓰지 않는다. 정리 6.19의 셋째 걸음은 `{{6:theorem-U}}`와 네 적분의 정의(첫 판 부록 A 16행)로, 넷째 걸음은 6.4의 `{{6:old-8-11}}`을 가리킨다. 상수 50.6의 위합은 부록 D.",
            "6.6": "다섯 조각의 전개. 사슬 전개·이동 꼬리는 2.12를 가리킨다. 순서: `{{6:path-shift}}` → `{{6:theorem-D}}` → `{{6:prop-W}}` → `{{6:prop-R}}` → `{{6:lemma-H}}` → `{{6:lemma-Hprime}}` → `{{6:lemma-M}}` → `{{6:critical-front}}` → `{{6:far-window}}` → `{{6:small-k-bulk}}` → `{{6:first-layer-end}}` → `{{6:above-window}}` → `{{6:v-negative}}` → (V)의 모든 $L$. 명제 W (가)의 13개 검사와 정리 D의 기저 $L\\le700$은 부록 D.",
        },
        order={
            "6.2": ["{{6:old-7-19}}", "{{6:old-7-20}}", "{{6:old-7-21}}", "{{6:old-7-24}}"],
            "6.4": ["{{6:old-8-11}}", "{{6:old-8-12}}", "{{6:pair-rearrange}}", "{{6:diag-first-layer}}", "{{6:cor-L}}", "{{6:D-bound}}"],
            "6.5": ["{{6:old-6-18}}", "{{6:theorem-U}}", "{{6:old-6-19}}"],
            "6.6": ["{{6:path-shift}}", "{{6:theorem-D}}", "{{6:prop-W}}", "{{6:prop-R}}", "{{6:lemma-H}}", "{{6:lemma-Hprime}}", "{{6:lemma-M}}", "{{6:critical-front}}", "{{6:far-window}}", "{{6:small-k-bulk}}", "{{6:first-layer-end}}", "{{6:above-window}}", "{{6:v-negative}}"],
        },
        notes=COMMON_NOTES + ["Borel–Tanner 공식은 기록에 증명이 없으면 문헌 인용(Tanner 1953), 있으면 2.11의 보조정리에서 끌어온다. Robbins 부등식·Euler–Maclaurin 경계는 문헌 인용."],
        todo=[],
        D_items=[
            {"label": "{{D:theorem-U-constant}}", "for": "{{6:theorem-U}}", "sources": [{"record": "r845b205", "note": "상수 50.6의 위합(부록 A 적분 상수)"}]},
            {"label": "{{D:theorem-D-base}}", "for": "{{6:theorem-D}}", "sources": [{"record": "r5bbc534", "note": "기저 L≤700의 검사"}]},
            {"label": "{{D:prop-W-thirteen}}", "for": "{{6:prop-W}}", "sources": [{"record": "r29c10cd", "note": "명제 W (가)의 13개 검사"}]},
            {"label": "{{D:v-negative-k3131}}", "for": "{{6:v-negative}}", "sources": [{"record": "r29c10cd", "note": "k=3131, d≤13의 부등식 13개(방향 반올림 구간 재계산은 2차 대조)"}]},
        ]),
    7: dict(title="왼쪽 절반의 환원",
        scope="모멘트 판정과 볼록–꺾임 분해, 왼쪽 잔여 증가와 문턱(명제 6.7의 증명 전개, 열 인증, 유한 전파, 자기일관 상계), 유한 크기 전달과 극 영역(정리 6.11·6.12 전개, 극의 유일성·단조성, 정리 F, 보조정리 P, 극 영역 명제 R·N·W), 중앙 띠와 모멘트 인증, 토막 원천과 흡수 귀납(대각선 접기, 정리 PD), 원천 쪽(명제 6.17 전개), 주 정리와 둘째 층 비교의 동치, 남은 것.",
        weights="무거운 장. 7.2(명제 6.7 116행, 정리 S 약 150행), 7.3(정리 C 50행, 극 사실, 극 영역 약 300행), 7.4(정리 6.13 손 부분 약 440행), 7.5(대각선 접기 93행, 정리 PD), 7.6(명제 6.17 약 230행)이 모두 전개 대상이다. 7.1·7.7·7.8은 옮김.",
        sections={"7.1": "모멘트 판정과 볼록–꺾임 분해", "7.2": "왼쪽 잔여 증가와 문턱", "7.3": "유한 크기 전달과 극 영역", "7.4": "중앙 띠와 모멘트 인증", "7.5": "토막 원천과 흡수 귀납", "7.6": "원천 쪽", "7.7": "주 정리와 둘째 층 비교의 동치", "7.8": "남은 것"},
        intros={
            "7.2": "순서: 정리 6.6 → `{{7:factorial-moment}}` → 명제 6.7(전개) → 정리 6.8 → 명제 6.9(+ `{{7:band-propagation}}`, `{{7:column-lemma}}`, `{{7:seed-transfer}}`) → 정리 6.10 → `{{7:lemma-R-sc}}` → `{{7:self-consistent-S}}` → `{{7:cor-S-prime}}` → `{{7:S-infinity}}`. 6.2·6.4의 배경 서술(참값 관찰, 둘째 극소, Jensen 문턱)은 쓰지 않는다. 명제 6.7·정리 6.8은 증명이 글 안에 있으므로 「증명됨」, 명제 6.9는 「증명됨, 계산 보조(정확 정수 구간)」.",
            "7.3": "순서: `{{7:riccati}}` → `{{7:supermultiplicative}}` → `{{7:pole-unique}}` → `{{7:pole-monotone}}` → 정리 6.11(전개) → `{{7:fourier-lemmas}}` → `{{7:X-cert}}` → 정리 6.12(전개) → `{{7:transfer-F}}` → `{{7:lemma-P-pole}}` → `{{7:polar-R}}` → `{{7:polar-N}}` → `{{7:polar-W}}`. 첫 판 1885행의 「$N^\\circ_k\\le n<2k^{3/2}$은 X′의 귀결」 문장은 쓰지 않는다(극 영역은 `{{7:polar-W}}`로만 닫는다). 정리 6.12의 미지지 주장 넷은 쓰지 않는다.",
            "7.4": "정리 6.13의 손 부분(판정 항 $q_j$의 정의 2줄·$c=k$ 값 2줄·유도 3문장, 보조정리 P·T1·T·P♯, 수직선·Hermite 적용)을 전개한다. 순서: `{{7:moment-recursion}}` → `{{7:variance-formula}}` → `{{7:error-induction}}` → `{{7:theorem-C-moment}}` → 정리 6.13. 정수 인증·유리수 감사·(A1)–(A5) 7,700열·정리 D 1160열은 부록 D.",
            "7.5": "순서: 정리 6.14 → 명제 6.15 → `{{7:fold-A}}` → `{{7:fold-R}}` → `{{7:fold-T}}` → `{{7:fold-L1}}` → `{{7:fold-DIP}}` → `{{7:polar-PD}}` → `{{7:prop-PF}}`. 열 2001–3130의 $Q^\\star$는 여기서 닫힌다. 정리 Q-fin(1130열)은 부록 D(오기 $e^{3/25370}$ 대신 바른 하계 25233).",
            "7.6": "명제 6.17 (가)의 위험률 항등식·정리 H*와 전제 사슬 전부, (나)는 7.5의 `{{7:polar-PD}}`를 가리킨다. `{{7:src-plus}}`. 손 증명은 $k\\ge3131$에 한함을 진술에 담는다. 기록 오기 둘(3.8267→3.8249, 0.99988→0.999875)은 바른 값만.",
            "7.7": "명제 6.20의 증명에서 분할 무게 $w_m$의 비감소는 6.2의 `{{6:old-7-21}}`로 닫고 $w_m=\\mathcal T_t(m+1)/(t\\,A_t)$의 한 줄을 적는다(작성자 판단 표시). 정리 6.22 뒤에 놓였던 첫 판 문단들(머리 합·출발 빚·$m_1(k)$·$H^*$, 표시 나무 무게, $\\Upsilon_k$)은 이 절에 쓰지 않는다(9.1·6.2·6.4로 갔다). 정리 6.22의 지위 설명 문장(「이 동치는 비형식이다. 입력에 …」)은 쓰지 않는다.",
            "7.8": "$\\mathcal R_2$의 진술과 9장·10장이 각각 그것을 닫는다는 사실. 입력 목록과 공유·고유 입력의 서술은 11.3을 가리키는 한 문장으로.",
        },
        order={
            "7.2": ["{{7:old-6-6}}", "{{7:factorial-moment}}", "{{7:old-6-7}}", "{{7:old-6-8}}", "{{7:band-propagation}}", "{{7:column-lemma}}", "{{7:seed-transfer}}", "{{7:old-6-9}}", "{{7:old-6-10}}", "{{7:lemma-R-sc}}", "{{7:self-consistent-S}}", "{{7:cor-S-prime}}", "{{7:S-infinity}}"],
            "7.3": ["{{7:riccati}}", "{{7:supermultiplicative}}", "{{7:pole-unique}}", "{{7:pole-monotone}}", "{{7:old-6-11}}", "{{7:fourier-lemmas}}", "{{7:X-cert}}", "{{7:old-6-12}}", "{{7:transfer-F}}", "{{7:lemma-P-pole}}", "{{7:polar-R}}", "{{7:polar-N}}", "{{7:polar-W}}"],
            "7.4": ["{{7:moment-recursion}}", "{{7:variance-formula}}", "{{7:error-induction}}", "{{7:theorem-C-moment}}", "{{7:old-6-13}}"],
            "7.5": ["{{7:old-6-14}}", "{{7:old-6-15}}", "{{7:fold-A}}", "{{7:fold-R}}", "{{7:fold-T}}", "{{7:fold-L1}}", "{{7:fold-DIP}}", "{{7:polar-PD}}", "{{7:prop-PF}}"],
            "7.6": ["{{7:old-6-16}}", "{{7:old-6-17}}", "{{7:src-plus}}"],
        },
        notes=COMMON_NOTES + [
            "Fekete 보조정리, Faà di Bruno 공식, Harris 부등식, Robbins 부등식은 문헌 인용.",
            "기호 충돌 셋($A_s$, $\\rho_s$, $\\delta_s$; [r475ada3])과 $d_{n,k}$(소인 질량; [r7c079be]), $Q_k$, $\\kappa_1$, $N_k$, $\\eta$, $H_k$, $K_n$, $Q_c$, $\\mathcal L$, $\\tau_k$, $a_n$, $u_n$는 장부 v2의 글자로.",
        ],
        todo=[],
        D_items=[
            {"label": "{{D:column-certification-k500}}", "for": "{{7:column-lemma}}", "sources": [{"record": "rc9aee43", "note": "380열 144비트 정수 구간 계산(peer 160비트 재인증 5열)"}]},
            {"label": "{{D:seed-certificates-k120}}", "for": "{{7:seed-transfer}}", "sources": [{"record": "r9e782f5", "note": "n≥16, k≤120의 119개 정확 유리수 인증서(producer/certificate-k*.json)"}]},
            {"label": "{{D:self-consistent-constants}}", "for": "{{7:self-consistent-S}}", "sources": [{"record": "rad00a59", "note": "상수 세 층(정확 유리수+mpmath 구간)과 k=6098 한 점"}]},
            {"label": "{{D:xcert-partAB}}", "for": "{{7:old-6-12}}", "sources": [{"record": "rf451d83", "note": "Part A·B 인증(501≤k≤5000 열별; k-구간)"}]},
            {"label": "{{D:polar-blocks-488}}", "for": "{{7:polar-R}}", "sources": [{"record": "r89eb039", "note": "488블록 binary64 바깥 부풀림 구간(peer 재인증)과 L15 2472구간"}]},
            {"label": "{{D:band102-integer}}", "for": "{{7:old-6-13}}", "sources": [{"record": "r475ada3", "note": "정수 전용 인증 F2"}, {"record": "r6b37c7e", "note": "정리 4.B 유한 틈의 정수 인증·유리수 감사"}]},
            {"label": "{{D:moment-certification}}", "for": "{{7:theorem-C-moment}}", "sources": [{"record": "r10ff8c2", "note": "(A1)–(A5) 7,700열 binary64와 정리 D 1160열 정확 유리수 재계산"}]},
            {"label": "{{D:Q-fin-1130}}", "for": "{{7:polar-PD}}", "sources": [{"record": "r207f124", "note": "정리 Q-fin 1130열 binary64(명시 반올림 한계; 검토 재계산 1135열+112열 정수 방향 반올림)"}]},
        ]),
    8: dict(title="둘째 층 띠",
        scope="둘째 층 띠 $103\\le\\nu\\le0.48k$에서 줄기 이득이 문턱 나무 손실을 이긴다는 비교. 비교의 꼴(한 블록 재귀와 비교 원리), 창의 수준 질량 하계(Jensen·탈출 하계, 봉투 보조정리 H·H-G, 정리 W), 생존 인자의 상쇄와 용량 이동, 띠 정리(B′·B‴). 9장과 10장이 함께 기대는 입력이다.",
        weights="고비는 8.2의 정리 W와 봉투 보조정리, 8.4의 띠 정리다. 봉투 식 전부(식 4+정의 3, 여섯 조각 6)를 본문에 적고, 셀 검사와 12001점 표는 부록 D. 탈출 봉투의 $y$-감소성과 여섯 조각의 $k$-단조성은 자리 표시자(아래).",
        sections={"8.1": "비교의 꼴", "8.2": "창의 수준 질량 하계", "8.3": "생존 인자의 상쇄와 용량 이동", "8.4": "띠 정리"},
        intros={
            "8.2": "순서: `{{8:jensen-lower}}` → `{{8:escape-lower}}` → `{{8:lowest-violation}}` → `{{8:prop-U-apriori}}` → `{{8:envelope-H}}` → `{{8:envelope-HG}}` → 정리 W(`{{8:old-6-28}}`). 정리 W 증명의 둘째 단계(봉투 표가 하계임을 쓰는 자리)에 지침 4.7의 자리 표시자를 둔다. 보조정리 H·H-G의 식은 기록 §3.5와 보고서 §3.9.2·`window_lib.py`의 docstring에서 옮기고 출처를 적는다.",
            "8.4": "`{{8:hazard-H1}}`을 정리 B‴ 앞에 둔다(위험률 다듬기 $0.44k<\\nu\\le0.48k$가 쓴다). 상자 검사 206,727개(배정밀도)는 부록 D.",
        },
        order={"8.2": ["{{8:jensen-lower}}", "{{8:escape-lower}}", "{{8:lowest-violation}}", "{{8:prop-U-apriori}}", "{{8:envelope-H}}", "{{8:envelope-HG}}", "{{8:old-6-28}}"],
               "8.4": ["{{8:old-6-29}}", "{{8:hazard-H1}}", "{{8:old-6-33}}"]},
        notes=COMMON_NOTES + [
            "첫 판 6.9절 머리의 「창」 정의와 「5.5절의 창과 다른 뜻」 구별 문장은 쓰지 않는다. 장부 v2의 「착지 창」을 쓴다.",
            "첫 판 6.9절의 참값 비 관찰(2.17, 1.842, 4–6)과 어려움의 서술 가운데 증명에 쓰이지 않는 수치 관찰은 쓰지 않는다.",
            "8장의 용량 변수 $c$는 장부 v2의 $y$다.",
            "Lagrange 반전, Euler–Maclaurin 경계, Robbins 부등식은 문헌 인용.",
        ],
        todo=[{"where": "8.2, 정리 W(`{{8:old-6-28}}`) 증명의 둘째 단계(12001점 표의 마디값이 하계임을 쓰는 자리)와 보조정리 H-G(`{{8:envelope-HG}}`) 뒤",
               "statement": "탈출 봉투 $Q^{\\mathrm{env}}_G(y)$가 $y\\in[0.2,6.001]$에서 비증가이고, 여섯 조각 $P,R_1,R_2,D_1,D_2,D_3$가 고정 $y$에서 $k\\ge6600$에 대해 단조라는 것(따라서 표의 마디값 $Q^{\\mathrm{env}}(y_{i+1})$이 셀 $[y_i,y_{i+1}]$ 위의 하계라는 것)",
               "fill": "연구 인스턴스가 공표하는 기록(2026-11-12 요청에 대한 답)의 증명을 옮기고 2차 대조를 거친다. 그때까지 자리 표시자만 두고 그 성질을 쓰는 문장은 「[todo]의 진술 아래」라고 적는다"}],
        D_items=[
            {"label": "{{D:window-mass-env}}", "for": "{{8:old-6-28}}", "sources": [{"record": "r030ffae", "note": "(가)·(나) 셀 검사와 12001점 봉투 표(binary64 평가, 인증 아님); 생성 규칙"}]},
            {"label": "{{D:band-boxes}}", "for": "{{8:old-6-33}}", "sources": [{"record": "r030ffae", "note": "상자 206,727개 배정밀도 검사, 최솟값 1.0094"}]},
        ]),
    9: dict(title="벌크의 첫째 증명(P◇ 경로)",
        scope="머리 합 조건 $H^*$·$H^*_+$와 무게중심 정지 확률(입력), 문턱 손실을 둘로 가르기, 행 조건의 해석적 증명, 띠의 닫힘, 쌍 부등식, 조립. $\\mathcal R_2$에서 $LRP_2$를 증명해 주 정리를 완성하는 첫째 길이다.",
        weights="두 증명 사슬의 하나이므로 무겁다. 9.1의 머리 합 정리 1(136행)과 9.4·9.5의 정리들은 완전히 전개한다. 보조정리 7.10은 작성자 증명. 9.6은 조립이므로 가볍다.",
        sections={"9.1": "입력: 머리 합 조건", "9.2": "문턱 손실을 둘로 가르기", "9.3": "행 조건의 해석적 증명", "9.4": "띠의 닫힘", "9.5": "쌍 부등식", "9.6": "조립"},
        intros={
            "9.1": "절 머리에 머리 합 $P_s(k)$, 출발 빚, 빚 뺀 머리 합, 증가 시작점 $m_1(k)$의 정의(첫 판 6.8절 2071행 문단에서 옮김)를 둔다. 순서: `{{9:F5-upper}}` → `{{9:theorem-A-plus}}` → `{{9:prop-H}}` → `{{9:head-sum-1}}` → `{{9:head-sum-2}}` → `{{9:H-star}}` → `{{9:H-star-plus}}` → `{{9:centroid-stop}}`.",
            "9.2": "보조정리 7.10은 기록의 두 문장 근거를 2.10의 생성함수로 펼쳐 이 글이 증명한다(`(작성자 판단)`). 보조정리 7.12는 [r77e234e] §7 보조정리 F로 전개.",
            "9.3": "정리 7.13은 6.1의 `{{6:old-7-13}}`을 가리킨다. 정리 AR (2)·(3)의 Robbins 상수 0.734·0.8825의 출처를 대조 파일에 적는다. 적분값은 부록 D.",
            "9.4": "`{{9:regeneration-S}}`를 명제 7.18 앞에 둔다. 7.19·7.20·7.21·7.24는 6.2를 가리킨다. 정리 7.23(`{{9:old-7-23}}`)은 7.22 다음이다. LP 확인은 부록 D.",
            "9.5": "한 변수 확인은 부록 D.",
            "9.6": "입력 목록은 11.3을 가리키는 한 문장으로. 첫 판 7.6절(7.47–7.49)은 쓰지 않는다.",
        },
        order={"9.1": ["{{9:F5-upper}}", "{{9:theorem-A-plus}}", "{{9:prop-H}}", "{{9:head-sum-1}}", "{{9:head-sum-2}}", "{{9:H-star}}", "{{9:H-star-plus}}", "{{9:centroid-stop}}"],
               "9.4": ["{{9:regeneration-S}}", "{{9:old-7-18}}", "{{9:old-7-22}}", "{{9:old-7-23}}", "{{9:old-7-25}}", "{{9:old-7-26}}", "{{9:old-7-27}}", "{{9:old-7-28}}", "{{9:old-7-29}}", "{{9:old-7-30}}", "{{9:old-7-31}}", "{{9:old-7-32}}", "{{9:old-7-33}}", "{{9:old-7-34}}"]},
        notes=COMMON_NOTES + ["첫 판 7장의 「$\\mathcal T_n(t)$는 5.5.2절의 꼬리합과 글자가 같지만 다른 양」 류의 구별 문장은 장부 v2의 글자로 사라진다."],
        todo=[],
        D_items=[
            {"label": "{{D:m1-column-reading}}", "for": "{{9:head-sum-2}}", "sources": [{"record": "r2ec875c", "note": "M1(3132≤k≤19403): 정리 5.1 인증 파일의 열 판독(위반 0, 최대 0.7095)"}]},
            {"label": "{{D:H-star-plus-interval}}", "for": "{{9:H-star-plus}}", "sources": [{"record": "r33475a7", "note": "s≥k+2의 충분조건 G(X,w)≤Θ 세 영역 방향 반올림 구간 산술(검토 재실행)"}]},
            {"label": "{{D:AR-integrals}}", "for": "{{9:old-7-16}}", "sources": [{"record": "rae1f209", "note": "정리 AR의 적분값"}]},
            {"label": "{{D:band-LP}}", "for": "{{9:old-7-33}}", "sources": [{"record": "rb6a2cd0", "note": "정리 P·P⁺·P⁺⁺의 유한 확인과 선형 계획 계산"}]},
            {"label": "{{D:pair-one-variable}}", "for": "{{9:old-7-35}}", "sources": [{"record": "r5909c9e", "note": "정리 P◇의 한 변수 확인"}]},
        ]),
    10: dict(title="벌크의 둘째 증명(FLQ 경로)",
        scope="둘째 층의 $1/p$ 장부, 머묾 꼴, 명제 FLQ와 함의, FLQ를 머묾 질량 하나로 줄이기, 얼린 볼록 몫·젊은 사슬·상위해 원리, 균일 증명, 조립. $Q^\\star_2$를 증명해 주 정리를 완성하는 둘째 길이다.",
        weights="두 증명 사슬의 하나이므로 무겁다. 모두 옮김이지만 첫 판 8.5·8.6의 전사 문단은 보조정리와 번호 단계로 다시 조직한다. 10.4의 점질량 상계·머묾 법칙은 6장을 가리킨다.",
        sections={"10.1": "둘째 층의 $1/p$ 장부", "10.2": "머묾 꼴", "10.3": "명제 FLQ와 함의", "10.4": "FLQ를 머묾 질량 하나로 줄이기", "10.5": "얼린 볼록 몫, 젊은 사슬, 상위해 원리", "10.6": "균일 증명", "10.7": "조립"},
        intros={
            "10.1": "보조정리 8.3(c)의 분할 무게 비감소는 6.2의 `{{6:old-7-21}}`과 같은 사실이다. 여기서 다시 증명하거나 그 라벨을 가리킨다(둘 중 하나; 가리키면 $w_m=\\mathcal T_n(m+1)/(n\\,A_n)$ 한 줄).",
            "10.4": "8.11–8.13은 6.4·6.3을 가리킨다.",
            "10.5": "명제 8.23의 30자리 수치 적분(두 적분값)은 부록 D. 「상해 원리」는 장부 v2에서 「상위해 원리」, (SS)는 「상위해 조건」.",
            "10.6": "네 가족(둘째 층 위치를 $\\nu$의 범위 넷으로 나눈 부류)의 시작점 검사는 부록 D.",
            "10.7": "입력 비교 표는 11.3을 가리키는 한 문장으로. 첫 판 8.8절(8.38)은 쓰지 않는다.",
        },
        order={},
        notes=COMMON_NOTES + ["첫 판 8장의 「$c$」(용량)는 장부 v2의 $y$다. 8.1의 「이 장은 행을 $n$으로」 선언 문장은 쓰지 않는다(장부가 정한다)."],
        todo=[],
        D_items=[
            {"label": "{{D:M-natural-integrals}}", "for": "{{10:old-8-23}}", "sources": [{"record": "re71a735", "note": "두 적분 0.7998520, 2.7171423의 30자리 수치 적분"}]},
            {"label": "{{D:four-families}}", "for": "{{10:old-8-36}}", "sources": [{"record": "re71a735", "note": "네 가족의 시작점 검사"}]},
        ]),
    11: dict(title="보증",
        scope="이 글의 모든 증명이 글 안에 있거나 학술 문헌의 정리를 인용한다는 사실과 식별자가 가리키는 기록의 성격(11.1), 컴퓨터 계산의 명세 색인(11.2), 두 증명의 공유 입력과 고유 입력(11.3), 문헌(11.4). 진술은 없고 산문과 표다.",
        weights="가벼운 장. 11.1은 연구 체계를 출처를 읽는 데 필요한 만큼만 말한다(기록은 작성과 독립된 검토를 거쳤고, 이 글의 진술과 상수는 그 검토가 확인한 것이라는 일반 문장; 개별 정정은 적지 않는다). 11.2·11.3은 표가 정본이고 7.8·9.6·10.7이 이것을 가리킨다.",
        sections={"11.1": "증명의 성격과 출처", "11.2": "컴퓨터 계산의 명세", "11.3": "공유 입력과 고유 입력", "11.4": "문헌"},
        intros={
            "11.1": "지위 낱말의 뜻은 1.5를 가리키지 않고 되풀이하지도 않는다. 「검토」·「기록」은 출처 설명에 필요한 만큼만. 첫 판 9.1의 「진술만 둔 결과」 표는 쓰지 않는다.",
            "11.2": "표의 열: 부록 D 항목(라벨 `부록 D.{{D:이름}}`), 확인하는 진술(라벨), 산술 등급, 쓰인 곳(장·절), 독립 재계산. 모든 장의 부록 D 조각이 모인 뒤 세션이 채우므로, 집필자는 표의 틀과 머리 산문만 쓰고 행은 세션이 넣는다는 표시(`<!-- 세션 채움 -->`)를 둔다.",
            "11.3": "첫 판 8.7의 표와 9.3의 표를 합친 정본. 공유 입력(정리 5.1, 중앙 띠, 둘째 층 띠와 정리 W·B′, (V)와 V-core, 원천 쪽, 열 2001–3130의 $Q^\\star$, 모멘트 인증과 극 영역, $W$ 이후의 사슬)과 고유 입력(P◇: $H^*_+$와 9장의 유한 확인; FLQ: 네 가족 검사와 명제 M♮의 두 적분값). 라벨로 가리킨다.",
            "11.4": "인용한 학술 문헌(Konheim–Weiss, Pollak, Petersson, Janson, Aguilar-Fraga 외, FKG, Fekete, Tanner, Robbins, Euler–Maclaurin 경계의 출처, Wallis, Harris, Faà di Bruno, Lagrange 반전, Hermite–Hadamard)과 각 정리가 쓰인 자리(라벨). 사슬 밖 문장은 쓰지 않는다.",
        },
        order={}, notes=COMMON_NOTES + ["11장만 연구 체계(기록, 검토)를 말할 수 있다(지침 8절). 다른 장이 쓴 식별자의 집합은 조립 뒤 세션이 부록 B와 맞춘다."],
        todo=[], D_items=[]),
}



# 사전 설계의 세션 결정(대조v2/장부_설계_세션결정.md)에서 온 장별 지시
EXTRA_NOTES = {
    1: [
        "1.4 개관의 왼쪽·오른쪽 절반은 1.5의 위치 기준($n\\le2k$ / $n\\ge2k+1$)으로 적는다. 첫 판 1.4의 첨자 기준 문장은 위치 기준으로 고쳐 쓰되, 고친 문장이 참인지 확인한다(두 기준은 중앙의 한 칸에서만 다르다).",
    ],
    2: [
        "2.1의 선호 용량은 $h_i:=i-\\max(\\{j<i:\\sigma_j>\\sigma_i\\}\\cup\\{0\\})$로 바로 정의한다. 첫 판의 $t_i$는 전역 기호가 아니다: 그 자리는 $i-h_i$로 적고(정리 2.3의 범위 $i-h_i<a_{\\sigma_i}\\le i$, 보조정리 2.15의 용량 구간 $(i-h_i,\\,i]$), 증명 안에서 이름이 꼭 필요하면 장부 1.3의 국소 기호 $z_i$를 쓴다.",
        "자리 $i$에 선 차의 변위는 $d_{\\sigma_i}$로 적는다($d_i$는 차 $i$의 변위). 결과 순열 $\\sigma_i$의 정의(자리 $i$에 선 차)와 맞는지 확인하고 어긋나면 반환에 적는다.",
    ],
    5: [
        "첫 판 5.5.4(정리 5.28 등)의 보조 변수 $v=m-d$와 $\\mathrm{EB}(v)$의 인수는 장부 1.3이 정한 5장 국소 글자로 적는다(꼭짓점 지표 $v$는 쓰지 않는다). 5.5.7–5.5.8의 척도 변수도 장부 1.3의 글자대로($\\zeta$는 1.5의 중앙 창 좌표이므로 쓰지 않는다).",
    ],
    7: [
        "7.5의 뿌리 자리 법칙 $\\mathcal P^{(k)}_m(j)$는 마지막 차 자리 법칙 $\\mathcal P_m(j)$의 용량판이다. 정의 문장에 $\\mathcal P^{(k)}_m(j)=\\Pr_m(s_m=j\\mid M\\le k-1)$을 적고 그 등식을 한 줄로 확인한다(마지막 차의 선호 $\\min(j,k)$가지, 두 조각 $A_{j-1,k-1}A_{m-j,k-1}$).",
    ],
    9: [
        "첫 판 7.1의 $A^{(G)}_N$의 위첨자 $G$는 가장 큰 나무의 크기 $G$가 아니라 「모든 나무의 크기가 이 값 이하」라는 문턱 매개변수다. 장부대로 나무 크기 변수 $t$로 $A^{(t)}_N$이라 적고 $A^\\circ_N=A^{(k+1)}_N$, $A^\\diamond_N=A^{(k+103)}_N$으로 둔다. 7.1의 합 지표 $g$도 나무 크기 변수 $t$ 또는 묶인 지표로 바꾼다.",
        "평평한 꼬리는 $\\mathrm{flat}_k(t)$다(첫 판 7.3의 $\\mathfrak t_k(s)$). $\\varphi^\\flat_k=1+kD_k=k\\,\\mathrm{flat}_k(k+1)$.",
    ],
    10: [
        "첫 판 8.3의 「창 안」($m_0$의 미결 범위)은 장부 3절의 「미결 범위」로 적는다. 다만 첫 판 8.3·3372와 8.6·3724의 그 범위가 착지 창($k<m\\le k+q_{\\max}$)과 같으면 「착지 창 안」으로 적고 반환에 어느 쪽을 택했는지 적는다.",
    ],
}


# 2026-11-12 저녁: 봉투 단조성 기록 [rfc69320] 공표에 따른 8장 갱신(합의 v2 결정 15; 자리 표시자 소멸)
_m8 = META[8]
_m8["scope"] = _m8["scope"].replace("봉투 보조정리 H·H-G, 정리 W", "봉투 보조정리 H·H-G, 봉투의 두 단조성·끼움·닫힌 꼴·허용 오차, 정리 W")
_m8["weights"] = ("고비는 8.2의 정리 W와 봉투 정리들(탈출 봉투의 $y$-비증가, 끼움 정리, 닫힌 꼴 봉투), 8.4의 띠 정리다. "
                  "봉투 식 전부(식 4+정의 3, 여섯 조각 6)와 두 단조성·끼움·닫힌 꼴·허용 오차의 증명을 본문에 적고, (가)·(나) 셀 검사·12001점 표·저장 표의 구간 산술 확인은 부록 D.")
_m8["intros"]["8.2"] = ("순서: `{{8:jensen-lower}}` → `{{8:escape-lower}}` → `{{8:lowest-violation}}` → `{{8:prop-U-apriori}}` → `{{8:envelope-H}}` → `{{8:envelope-HG}}` → "
                        "`{{8:pieces-k-monotone}}` → `{{8:escape-y-monotone}}` → `{{8:jensen-H-ii}}` → `{{8:table-lower-bound}}` → `{{8:envelope-code-monotone}}` → `{{8:closed-form-envelope}}` → `{{8:table-tolerance}}` → 정리 W(`{{8:old-6-28}}`). "
                        "봉투 정리 일곱은 기록 [rfc69320](2026-11-12 공표; 검토가 13개 주장 전부 지지)에서 전개한다. 그 검토(`review/feedback.md` §2·§4)가 정정한 것을 따른다: 표 호출 범위 $[0,6]$, 명제 F 이음새 경우의 닫기, 정리 CF (c)의 의존(정리 B를 씀), 반올림 방향이 틀린 수치 다섯. "
                        "같은 요청의 독립 둘째 증명 기록 [r0e82912]는 쓰지 않고 인용하지 않는다(결정 10). 보조정리 H·H-G의 식은 기록 §3.5와 보고서 §3.9.2·`window_lib.py`의 docstring에서 옮기고 출처를 적는다.")
_m8["order"]["8.2"] = ["{{8:jensen-lower}}", "{{8:escape-lower}}", "{{8:lowest-violation}}", "{{8:prop-U-apriori}}", "{{8:envelope-H}}", "{{8:envelope-HG}}",
                       "{{8:pieces-k-monotone}}", "{{8:escape-y-monotone}}", "{{8:jensen-H-ii}}", "{{8:table-lower-bound}}", "{{8:envelope-code-monotone}}", "{{8:closed-form-envelope}}", "{{8:table-tolerance}}", "{{8:old-6-28}}"]
_m8["todo"] = []
_m8["D_items"].append({"label": "{{D:stored-table-check}}", "for": "{{8:table-tolerance}}",
                       "sources": [{"record": "rfc69320", "note": "§8.4 저장된 표의 엄밀한 확인(mpmath 구간 산술, 바깥쪽 반올림 30자리; 위반 0, 최소 여유 4.74e-13)과 §10.3 재현; 자료: evidence/peer/peer_table_vs_closed_form.py·.out, peer_closed_form_constants.py·.out, peer_constants.py·.out; 검토의 독립 재현 review/evidence/rv_code_exact.py·.out, rv_constants.py·.out. 산술 등급: 방향 반올림 구간(저장값은 정확 유리수)"}]})
_m8["notes"] = _m8["notes"] + ["8.2의 봉투 정리 일곱은 기록의 글자($Q^{\\mathrm{env}}_G$, $P,R_1,R_2,D_1,D_2,D_3$, $q_{k,k'}$, $U$, $V$, $\\mathrm{Bpart}$, $\\mathrm{Corr}$, $B_\\infty$, $E^*$, $\\hat E$, $\\tilde Q$, $Q^{\\mathrm{cf}}$, $\\Lambda^+$, $r_G$ 등)을 장부 v2의 글자로 옮겨 쓴다. 장부에 자리가 없는 기호는 8장 여유 글자에서 고르고 대조 파일에 적는다(사전의 기록 대조가 이 기록을 덮는다)."]


# 2026-11-12 저녁: 기록 대조 반영 뒤의 장별 지시(세션 결정 28·33–35)
EXTRA_NOTES.setdefault(1, []).append("1.5에서 변수 글자 $k$, $r=n-\\ell-1=n-k$, $N=n-k$, $\\nu=n-2k$, $d$, $q$를 정의한다(장부 1.1). 결손의 두 셈법(3장의 $n+1-M_n$, 뒤 장들의 $m-M$)의 관계를 한 문장으로 적는다.")
EXTRA_NOTES.setdefault(2, []).append("첫 판 정의 2.21(Borel 질량 $\\mathrm{Bor}(m)$)은 2.6이 아니라 2.5에 둔다(2.5의 가장 큰 나무 핵 $\\pi_n(m)$이 쓴다). 사슬 전개의 정규화 인자는 $\\mathrm{nf}(n,d)$다(가산 오차항이 아니라 $\\ge1$인 곱 인자).")
EXTRA_NOTES.setdefault(6, []).append("평평한 핵심 $\\varphi^\\flat_k$의 정의는 $k\\sum_{t=k+1}^{2k+1}x_t(k)$다(6.5의 $D_k$를 6.4에서 미리 쓰지 않는다).")
EXTRA_NOTES.setdefault(7, []).append("극 $\\rho_k$($C_k(\\rho_k)=1$인 양의 근)의 정의를 7.3이 아니라 7.2에 둔다(7.2의 $\\mathfrak P_k(\\infty)$가 쓴다).")
EXTRA_NOTES.setdefault(8, []).append("Riemann 제타 함수의 값은 장부의 산세리프 명명 상수 $\\mathsf z_{1/2}$, $\\mathsf z_{-1/2}$, $\\mathsf z_{3/2}$로 적는다(8.2에서 한 번 정의; 이탤릭 $\\zeta$는 중앙 창 좌표다). 수치와 인증 구간은 부록 D.")
EXTRA_NOTES.setdefault(10, []).append("$\\mathrm{DDL}(k)$는 10.4에서, $\\mathrm{DDL}_2$·$\\mathrm{DDL}^\\natural$·$\\mathfrak H_d$는 10.5에서 정의한다. 10.4의 진술은 $\\mathrm{DDL}_2$를 부르지 않는다.")


# 2026-11-12 밤: 1장 회수 뒤 세션 판단
EXTRA_NOTES.setdefault(1, []).append("1.5는 「띠」를 행 범위를 한 좌표로 잰 구간의 통칭으로 정의하고 중앙 띠·둘째 층 띠만 정의한다(꼬리 띠는 5.4). 오른쪽·왼쪽 절반은 1.4가 처음 정의하고 1.5는 되풀이하지 않는다. 1.5는 꼬리 좌표 $r=n-\\ell-1$과 환경 크기 $N=n-k$가 같은 수임을 한 문장으로 밝힌다(4·5장은 $r$, 6–10장은 $N$).")
EXTRA_NOTES.setdefault(2, []).append("「첫 층」의 나무 크기 꼴($k<t\\le2k+1$)은 2.5에서 나무를 정의한 뒤 적는다. 무거운·가벼운의 경계값 $k$ 귀속은 각 대상의 정의에 적는다.")
EXTRA_NOTES.setdefault(9, []).append("9장은 꼬리 좌표 $r$ 대신 환경 크기 $N=n-k$(같은 수)를 쓴다. 1.5의 좌표 $\\hat x=(r+1)(\\ell+1)^{-2/3}$는 $(N+1)k^{-2/3}$으로 적는다.")


# 2026-11-12 밤: 1장 2차 대조 뒤 세션 결정
EXTRA_NOTES.setdefault(1, []).append("주 정리는 라벨 `{{1:main-theorem}}`의 정리로 세우고 지위는 「비형식 증명」, 식별자는 9.6·10.7의 두 닫는 정리의 기록이다(구조표 9.6·10.7 행). 1.3의 작은 $n$ 표는 부록 D `{{D:exact-n20000}}`을 한 문장으로 가리킨다. 1.5는 뒤 장이 정의하는 낱말(해싱 극한, 극)을 쓰지 않고 좌표의 정의만 적는다. 행 $n$의 증인 $\\ell^\\ast_n$은 가장 작은 증인이다.")

def apply(ch):
    path = os.path.join(SPEC, f"장{ch}.json")
    spec = json.load(io.open(path, encoding="utf-8"))
    m = META[ch]
    spec["title"] = m["title"]
    spec["scope"] = m["scope"]
    spec["weights"] = m["weights"]
    spec["notes"] = m["notes"] + EXTRA_NOTES.get(ch, [])
    spec["todo"] = m["todo"]
    spec["D_items"] = m["D_items"]
    by_sec = {s["sec"]: s for s in spec["sections"]}
    for sec, title in m["sections"].items():
        if sec not in by_sec:
            by_sec[sec] = {"sec": sec, "title": title, "items": []}
            spec["sections"].append(by_sec[sec])
        by_sec[sec]["title"] = title
        if sec in m.get("intros", {}):
            by_sec[sec]["intro"] = m["intros"][sec]
    for sec, order in m.get("order", {}).items():
        s = by_sec[sec]
        have = {it["label"]: it for it in s["items"]}
        missing = [l for l in order if l not in have]
        extra = [l for l in have if l not in order]
        if missing or extra:
            print(f"  장{ch} {sec}: 순서 목록에 없음 {extra} / 명세에 없음 {missing}")
        s["items"] = [have[l] for l in order if l in have] + [have[l] for l in have if l not in order]

    def seckey(x):
        try:
            return tuple(int(t) for t in x["sec"].split("."))
        except Exception:
            return (999,)
    spec["sections"].sort(key=seckey)
    io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(spec, ensure_ascii=False, indent=1))
    print(f"장{ch}: META 적용(절 {len(spec['sections'])}, D 항목 {len(spec['D_items'])}, todo {len(spec['todo'])})")


# --- 11장 추가 지시(세션, 2026-11-13) ---
EXTRA_NOTES.setdefault(11, []).append("11장은 1–10장이 모두 조립된 뒤에 쓴다. 전체 흐름과 번호는 조립본 `원고.md`에서 읽고, 다른 장의 진술을 가리킬 때는 라벨(`장v2/장N.md`의 진술 머리에 있는 `{{N:이름}}`)로 적는다(조립이 번호로 바꾼다). 11장에는 진술이 없으므로 라벨을 새로 만들지 않는다.")
EXTRA_NOTES.setdefault(11, []).append("11.3의 공유 입력·고유 입력 표는 첫 판 표를 옮기지 않고 조립본에서 다시 만든다: 7.8·9.6·10.7의 고리 문장, 9장·10장 닫는 정리의 머리에 적힌 「…에 의존」과 증명이 부르는 라벨을 읽어, 두 증명이 함께 기대는 입력과 각각만 기대는 입력을 라벨로 적는다(근거 열에 그 입력을 쓰는 자리의 라벨). 지위 낱말은 1.5의 정의와 지침 7.3 현행(세션 결정 38: 라벨 의존은 지위를 바꾸지 않고, 계산 진술에 기댈 때만 「X에 의존」)대로 적고 되풀이해 설명하지 않는다.")
EXTRA_NOTES.setdefault(11, []).append("11.2는 표의 틀(열: 부록 D 항목 라벨 `부록 D.{{D:이름}}`, 확인하는 진술의 라벨, 산술 등급, 쓰인 곳(장·절), 독립 재계산)과 머리 산문만 쓰고 행 자리에 `<!-- 세션 채움 -->` 한 줄을 둔다. 산술 등급의 이름은 넷뿐이다(지침 7.3).")
EXTRA_NOTES.setdefault(11, []).append("11.4의 문헌 목록은 첫 판 목록을 베끼지 않는다. 조립본 1–10장(과 부록 D 조각)에서 실제로 인용된 학술 문헌을 전부 찾아(저자·연도·제목·정리 번호를 적은 자리를 grep으로 모은다) 저자·제목·판·정리 번호·이 글에서 쓰인 자리(라벨)를 적는다. 예상되는 것: Konheim–Weiss, Pollak, Petersson, Janson, Cayley, Stanley *Enumerative Combinatorics* 2권(Prop. 5.3.2, Thm 5.4.2), Flajolet–Sedgewick *Analytic Combinatorics*, Robbins 1955, Fortuin–Kasteleyn–Ginibre 1971·Harris 1960·Grimmett *Percolation* Thm 2.4, Fekete, Tanner(Borel–Tanner), Faà di Bruno, Hermite–Hadamard, Jensen, Euler–Maclaurin(Apostol), Corless 외 1996(Lambert W), Wallis. 본문에 없는 문헌은 적지 않고, 본문에 있는데 목록에 빠진 것이 없게 한다.")
EXTRA_NOTES.setdefault(11, []).append("11.1은 연구 체계를 출처를 읽는 데 필요한 만큼만 말한다: 식별자 [r…]는 결과를 처음 세운 연구 기록이고 각 기록은 작성과 독립된 검토를 거쳤으며 이 글의 진술과 상수는 그 검토가 확인한 것이라는 일반 문장. 개별 정정·운영 경위·세션은 적지 않는다. 지위 낱말의 뜻은 1.5를 가리키지도 되풀이하지도 않는다.")
EXTRA_NOTES.setdefault(11, []).append("한 번의 도구 호출로 쓰는 분량은 12,000 토큰 이하로 나눈다(장 파일은 절 단위로 나누어 쓴 뒤 이어 붙인다). 반환문도 6,000 토큰 이하.")

if __name__ == "__main__":
    chs = [int(a) for a in sys.argv[1:]] or list(range(1, 12))
    for ch in chs:
        apply(ch)
