# -*- coding: utf-8 -*-
"""R3 용어 규약 잔존 스캔(읽기 전용).

결정 95·96(ㄹ)·97·100의 낱말 규칙과 장부 3절 4열의 「(쓰지 않음)」·첫 판 낱말을
본문(장v2/장*.md)·부록(장v2/부록*.md)·장부·구조표·의존지도(1절·2.1절)·README에서
정규식으로 찾아 file:line과 앞뒤 문맥을 출력한다. 판정은 사람이 한다.

사용: python -I 검토정합_R3_낱말스캔.py [--particles] [--digits] > out.txt
"""
import glob, io, os, re, sys

ROOT = r"C:\math\임시\주차함수_증명"

def files():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "장*.md"))):
        out.append((p, None))
    for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "부록*.md"))):
        out.append((p, None))
    out.append((os.path.join(ROOT, "장부_v2.md"), None))
    out.append((os.path.join(ROOT, "구조표_v2.md"), None))
    out.append((os.path.join(ROOT, "의존지도_v2.md"), (1, 471)))
    out.append((os.path.join(ROOT, "원고_자료", "README.md"), None))
    out.append((os.path.join(ROOT, "원고_자료", "재실행표.md"), None))
    return out

# (이름, 정규식) — 낱말 규칙
PATTERNS = [
    # 결정 95
    ("95ㄱ 경계", r"경계"),
    ("95ㄴ 상해", r"상해"),
    ("95ㄷ 블록", r"블록"),
    ("95ㄹ 윤곽(윤곽 적분 제외)", r"윤곽(?! 적분)"),
    ("95ㅁ 쌍별 도달/감사 도달", r"쌍별 도달|감사 도달|도달 껍질"),
    ("95ㅂ 최대 나무", r"최대 나무|최대나무"),
    ("95ㅇ 미달", r"미달"),
    ("95 할인 방문 수 오타", r"할인 방문"),
    # 결정 96(ㄹ)
    ("96 상한", r"상한"),
    ("96 하한", r"하한"),
    ("96 판정 사슬", r"판정 사슬|판정사슬"),
    ("96 꼬리의 상한", r"꼬리의 상한|꼬리 상한"),
    ("96 셀 상한/하한, 해의 상한", r"셀 상한|셀 하한|해의 상한"),
    ("96 윤곽 핵/윤곽값", r"윤곽 핵|윤곽값|윤곽 값"),
    ("96 조화합 경계/EM 경계", r"조화합 경계|Maclaurin 경계|경계의 두 끝"),
    ("96 꼭대기 거리 지표의 상한", r"거리 지표의 상한"),
    ("96 상단/하단", r"상단|하단"),
    ("96 상계/하계 뒤에 끝 뜻 의심(구간의 상계)", r"구간의 상계|구간의 하계|구간 상계|구간 하계"),
    # 결정 97
    ("97 문턱 예산/예산 분해/무게 성장/동률의 나머지", r"문턱 예산|예산 분해|무게 성장|동률의 나머지"),
    ("97 예산", r"예산"),
    ("97 체류", r"체류"),
    ("97 V-핵심의 머묾 항등식", r"머묾 항등식"),
    # 결정 100
    ("100 젊은 경로", r"젊은 경로"),
    # 장부 3절 「(쓰지 않음)」 낱말
    ("3절 노드", r"노드"),
    ("3절 순증가", r"순증가|순 증가"),
    ("3절 멈춤 확률", r"멈춤 확률|멈춤확률"),
    ("3절 칸(판정 필요: 분할→구획, 적분 비교→구간)", r"칸"),
    ("3절 사슬 해/한 줄 사슬 모양", r"사슬 해\b|사슬 해[가-힣]|한 줄 사슬"),
    # 첫 판 낱말(둘째 판 낱말과 다른 행)
    ("첫판 선호 목록/목록", r"선호 목록|목록"),
    ("첫판 간격열/크기열/걸음열", r"간격열|크기열|걸음열|길이 열"),
    ("첫판 초과 수준/골격 수준/보증 수준", r"초과 수준|골격 수준|보증 수준"),
    ("첫판 중앙 비교/중앙 증가", r"중앙 비교|중앙 증가"),
    ("첫판 중앙 틈(이름이면 허용)", r"중앙 틈"),
    ("첫판 창 행/갱신 창/창 안/넓은 창/결손 창/창 척도", r"창 행|갱신 창|창 안|넓은 창|결손 창|창 척도"),
    ("첫판 띠 A", r"띠 A|띠 $A|띠 \$A"),
    ("첫판 둘째 벌크/첫 층 벌크", r"둘째 벌크|첫 층 벌크|첫층 벌크"),
    ("첫판 격자점/노드 위치", r"격자점|격자 점"),
    ("첫판 다섯 조각/네 조각/두 조각/조각남/조각나", r"다섯 조각|네 조각|두 조각|조각남|조각나|조각 \$\(G\)|조각 \$\(\\mathrm G\)"),
    ("첫판 머묾 이득", r"머묾 이득"),
    ("첫판 가중치", r"가중치"),
    ("첫판 결손(셋째·넷째 뜻) 의심: 결손의 원천/원천 질량/블록 원천", r"결손의 원천|원천 질량|블록 원천"),
    ("첫판 마디 SRC/숲–나무 재생 원천", r"마디|숲–나무 재생|숲-나무 재생"),
    ("첫판 Borel 걸음/Poisson 걸음/네 걸음", r"Borel 걸음|Poisson 걸음|네 걸음"),
    ("첫판 heavy path/core/supersolution", r"heavy path|\bcore\b|supersolution"),
    ("첫판 방법의 문턱/증가 문턱/반감 문턱", r"방법의 문턱|증가 문턱|반감 문턱"),
    ("첫판 가벼운 자리", r"가벼운 자리"),
    ("첫판 톱니 틈/빈틈", r"톱니 틈|빈틈"),
    ("첫판 강단봉", r"강단봉|강 단봉"),
    ("첫판 수준 위험률", r"수준 위험률"),
    ("첫판 환경 무게", r"환경 무게"),
    ("첫판 동반 숲/나머지 숲", r"동반 숲|나머지 숲"),
    ("첫판 구간 상한/구간 하한", r"구간 상한|구간 하한|구간의 상한|구간의 하한"),
    ("첫판 뿌리 문제/뿌리 명제", r"뿌리 문제|뿌리 명제"),
    ("첫판 Robbins 오차", r"Robbins 오차"),
    ("첫판 조건부 로그오목", r"조건부 로그오목"),
    ("첫판 D2S", r"D2S"),
    ("첫판 자르는 자리", r"자르는 자리"),
    ("첫판 칸 하계/거대 블록", r"칸 하계|거대 블록"),
    ("첫판 층층 구조/층 구조", r"층층 구조|층 구조"),
    ("첫판 자리 이름", r"자리 이름"),
    ("첫판 중앙(첫째·둘째 뜻) 의심: 중앙의/중앙에서/중앙 n", r"중앙(?! 행| 창| 띠| 틈| 비교| 증가)"),
    ("첫판 증인(반례 뜻 의심)", r"증인"),
    ("첫판 배치(5.2 타일 뜻 외 의심)", r"배치"),
    ("첫판 극 영역 둘째 뜻 의심: 전달", r"극 영역에서의 전달|극 영역 전달"),
    ("첫판 환경 이전 낱말: 동반", r"동반"),
    ("첫판 계산 보증의 층/보증 수준", r"보증의 층|보증 층|계산 층"),
    ("첫판 꼭짓점 수 질량", r"꼭짓점 질량|질량(?=.*꼭짓점 수)"),
    ("첫판 셀 경계 외 경계 이름 의심: 핵의 경계/양측 경계/명시 경계/균일 경계/계수 경계/판정의 경계/위 경계", r"핵의 경계|양측 경계|명시 경계|균일 경계|계수 경계|판정의 경계|위 경계|아래 경계|위쪽 경계|아래쪽 경계|경계값|경곗값"),
    ("3절 「장부」(뿌리 종류별 등식 뜻)", r"장부"),
    ("3절 「층」 계산 보증 뜻 의심", r"보증 층|등급 층"),
    ("3절 「포갬」 전 낱말", r"포개지는 층|층층"),
    ("3절 「쪼개짐」 전 낱말", r"조각남|조각나"),
    ("3절 「기록」 식별자 뜻 — 「기록 \\[r」 아님", r"식별자"),
]

def strip_math(s):
    s = re.sub(r"\$\$.*?\$\$", "§", s)
    s = re.sub(r"\$[^$]*\$", "§", s)
    s = re.sub(r"`[^`]*`", "§", s)
    return s

def ctx(line, m, w=45):
    a = max(0, m.start() - w); b = min(len(line), m.end() + w)
    return line[a:b].replace("\t", " ")

def scan_words():
    data = {}
    for path, rng in files():
        with io.open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
        data[path] = (lines, rng)
    for name, pat in PATTERNS:
        rx = re.compile(pat)
        hits = []
        for path, (lines, rng) in data.items():
            for i, line in enumerate(lines, 1):
                if rng and not (rng[0] <= i <= rng[1]):
                    continue
                for m in rx.finditer(line):
                    hits.append((os.path.relpath(path, ROOT), i, ctx(line, m)))
        print(f"\n===== [{name}] /{pat}/  hits={len(hits)}")
        for p, i, c in hits:
            print(f"  {p}:{i}: …{c}…")

# ---------- 조사 검사 ----------
JONG = [chr(c) for c in range(0x3131, 0x314F)]
def has_batchim(ch):
    code = ord(ch) - 0xAC00
    if code < 0 or code > 11171: return None
    return (code % 28) != 0
def batchim_is_rieul(ch):
    code = ord(ch) - 0xAC00
    return (code % 28) == 8

PARTICLES = [
    # (particle, needs_batchim(True=이어야 함, False=없어야 함))
    ("을", True), ("를", False), ("은", True), ("는", False),
    ("이", True), ("가", False), ("과", True), ("와", False), ("으로", True),
]

def scan_particles():
    print("\n===== [조사 검사] 받침 불일치 의심 (수식·코드 제거 뒤; 앞 글자가 한글일 때만)")
    for path, rng in files():
        with io.open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
        for i, line in enumerate(lines, 1):
            if rng and not (rng[0] <= i <= rng[1]): continue
            s = strip_math(line)
            for part, need in PARTICLES:
                for m in re.finditer(r"([가-힣])" + part + r"(?=[\s,.;:)\]」』!?]|$)", s):
                    prev = m.group(1)
                    hb = has_batchim(prev)
                    if hb is None: continue
                    if hb != need:
                        # 자주 나오는 정당한 낱말 제외
                        word = s[max(0, m.start()-3):m.end()]
                        if part == "이" and re.search(r"(거리|자리|사이|차이|이)이$", word): pass
                        print(f"  {os.path.relpath(path, ROOT)}:{i}: [{prev}{part}] …{ctx(s, m, 30)}…")
            # 로 뒤(받침 있고 ㄹ 아님)
            for m in re.finditer(r"([가-힣])로(?=[\s,.;:)\]」!?]|$)", s):
                prev = m.group(1)
                hb = has_batchim(prev)
                if hb and not batchim_is_rieul(prev):
                    print(f"  {os.path.relpath(path, ROOT)}:{i}: [{prev}로] …{ctx(s, m, 30)}…")

def scan_digits():
    print("\n===== [수사 치환 검사] 숫자 바로 뒤 한글(띄어쓰기 없음; 수식 제거 뒤)")
    for path, rng in files():
        with io.open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
        for i, line in enumerate(lines, 1):
            if rng and not (rng[0] <= i <= rng[1]): continue
            s = strip_math(line)
            for m in re.finditer(r"(?<![\w.])(\d+)([가-힣]+)", s):
                tail = m.group(2)
                if re.match(r"^(장|절|행|열|차|배|번|째|쪽|개|년|월|일|시|분|초|항|자리|단계|비트|진|차원|중|겹|회|칸|층|곳|줄|등|차례|판|권|호|도|배정밀도|자리까지|자릿수|번째)", tail):
                    continue
                print(f"  {os.path.relpath(path, ROOT)}:{i}: [{m.group(0)}] …{ctx(s, m, 30)}…")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args or "--words" in args: scan_words()
    if "--particles" in args: scan_particles()
    if "--digits" in args: scan_digits()
