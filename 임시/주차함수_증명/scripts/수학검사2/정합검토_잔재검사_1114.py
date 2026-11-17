# -*- coding: utf-8 -*-
"""결정 101·102 반영 뒤 잔재 전수 검사. 지운 라벨·낱말·낡은 글귀가 원고·장부·구조표·의존지도·자료 묶음 글에 남았는지 센다.
허용 자리(부록 B 기록 제목, 장부 3절 4열의 첫 판 낱말, 2절 첫 판 열, 4절 뺌 행, 의존지도 1.1절, 구조표의 설계 기록 주석)는 뺀다.
사용: python -I scripts/수학검사2/정합검토_잔재검사_1114.py"""
import glob
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILES = [p for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "*.md"))) if not p.endswith("부록B.md")]
FILES += [os.path.join(ROOT, n) for n in ("장부_v2.md", "구조표_v2.md", "의존지도_v2.md")]
FILES += [os.path.join(ROOT, "원고_자료", n) for n in ("README.md", "재실행표.md", "빠른_확인.py")]
FILES += [os.path.join(ROOT, "scripts", n) for n in ("_gen_재실행표.py", "_재실행표_여유.json")]

TOKENS = [
    "{{5:old-5-16}}", "{{5:old-5-17}}", "{{5:old-5-39}}", "{{5:dawson-facts}}", "{{5:arc-leading}}", "{{5:gauss-moments}}", "{{5:old-5-40}}", "{{5:old-5-41}}",
    "{{2:old-2-23}}",  # 5.23–5.25는 2026-11-15 결정 103으로 복원되어 더는 잔재가 아니다 "lemma-H-interval", "lemma-V-coefficients", "r5f5cf73/",
    "두 항 부등식", "안장점", "Gauss 체제", "Airy 체제", "인증 구간", "첫 층 안쪽", "젊은 경로", "체류", "판정 사슬", "V-core", "크기열", "걸음열", "초과열",
    "상해", "숲–나무 재생 원천", "칸 하계", "두 조각 적분", "초과 수준", "블록", "명제 U의", "명제 X의", "(R₀)", "E^\\ast", "10.38", "한쪽 경계", "경계식", "유리 경계",
    "증인 위치 경계", "사슬 해", "자르는 자리", "윤곽 핵", "멈춤 확률", "순증가", "예산 분해", "문턱 예산", "머묾 항등식", "마지막 102항", "꼬리 오목성",
    "run_a0", "run_all_log", "인증 아님", "5.6절",
]
# 허용: (토큰, 파일 이름 조각, 줄 조건 함수)
def allowed(tok, fname, line):
    if fname.endswith("장부_v2.md"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("| ") else []
        if "| 뺌 |" in line:
            return True                                             # 4절 뺌 행
        if len(cells) == 4 and tok in cells[3]:
            return True                                             # 3절 4열(첫 판 낱말)
        if len(cells) == 7 and tok in cells[5]:
            return True                                             # 1.2 6열(첫 판 글자)
        if len(cells) == 4 and line.startswith("| (Q") and tok in cells[2]:
            return True                                             # 2절 3열(첫 판)
        if tok in ("명제 U의", "명제 X의") and "기록" in line:
            return True                                             # 1.3·4절의 기록 이름 설명
        if tok == "(R₀)" and "[r8a9b11e]" in line:
            return True                                             # 7절 기록 꼬리표
        if tok == "E^\\ast" and "기록 $E^*$" in line or (tok == "E^\\ast" and "[rfc69320]" in line):
            return True
        if tok == "블록" and ("행렬" in line or "Toeplitz" in line):
            return True
        if tok == "체류" and "체류 꼴" in cells[3:4] if cells else False:
            return True
        if tok == "상해" and "상위해, 상해" in line:
            return True
        if tok == "5.6절" and "결정 101" in line:
            return True
    if fname.endswith("의존지도_v2.md"):
        if tok.startswith("{{") or tok in ("두 항 부등식", "마지막 102항", "꼬리 오목성", "안장점", "인증 구간"):
            return "1.1" in line or line.startswith("| `{{") and "뺌" in line  # 1.1절 뺌·대체 표
    if fname.endswith("구조표_v2.md"):
        return True if tok in ("{{5:arc-leading}}", "두 항 부등식", "마지막 102항", "꼬리 오목성", "10.38", "5.6절") else False
    if fname.endswith("부록C.md"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("| ") else []
        if len(cells) == 3 and tok in cells[1]:
            return True                                             # 낱말 표 「기록의 용어」 열
        if tok == "블록" and ("행렬" in line or "Toeplitz" in line):
            return True
    if tok == "블록" and ("Toeplitz" in line or "행렬" in line or "열 블록" in line or "`blk" in line or "블록 경로" in line or "블록 전체" in line or "블록 통계" in line):
        return True
    if tok == "인증 구간" and "인증 구간 폭" in line:
        return True                                                 # 7.5의 다른 뜻
    if tok == "체류" and ("체류 꼴" in line and ("첫 판" in line or fname.endswith("부록C.md"))):
        return True
    if tok == "상해" and ("상해석" in line or "손상해" in line):
        return True
    if tok == "예산 분해" and "결정 97" in line:
        return True
    return False


hits = {}
for p in FILES:
    fname = os.path.relpath(p, ROOT)
    for i, line in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        for tok in TOKENS:
            if tok in line and not allowed(tok, fname, line):
                hits.setdefault(tok, []).append(f"{fname}:{i}: {line.strip()[:110]}")
# 부록 D의 「칸」(허용 꼴 제외)
kan = []
for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "부록D_*.md"))):
    for i, line in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        s = re.sub(r"\$r\$ 칸|한 칸|번째 칸|증인의 칸|표의 칸|한 칸만", "", line)
        if "칸" in s:
            kan.append(f"{os.path.basename(p)}:{i}: {line.strip()[:110]}")
if kan:
    hits["칸(부록 D)"] = kan
# 개수 대조
d_items = sum(len(re.findall(r"^### D\.\{\{D:", io.open(p, encoding="utf-8").read(), re.M)) for p in glob.glob(os.path.join(ROOT, "장v2", "부록D_*.md")))
rows_112 = len(re.findall(r"^\| 부록 D\.\{\{D:", io.open(os.path.join(ROOT, "장v2", "장10.md"), encoding="utf-8").read(), re.M))
rows_re = len(re.findall(r"^\| D\.\{\{D:", io.open(os.path.join(ROOT, "원고_자료", "재실행표.md"), encoding="utf-8").read(), re.M))
print(f"부록 D 항목 {d_items}, 10.2 행 {rows_112}, 재실행표 행 {rows_re}")
total = sum(len(v) for v in hits.values())
print("잔재", total)
for tok, v in hits.items():
    print(f"== {tok} ({len(v)})")
    for x in v[:12]:
        print("   ", x)
