# -*- coding: utf-8 -*-
"""점검 X1(고아와 죽은 가지) — 파견문 3절 X1이 요구한 전수 검색 토큰과 X1이 더한 토큰의 남은 수를 파일별로 센다.
읽기만 한다. 출력은 _out.txt. 부록 A·B·C는 V6 영역이라 따로 표시한다."""
import re, datetime
from pathlib import Path
ROOT = Path(r"C:/math/임시/주차함수_증명")
CH = ["1","2","3","4","5A","5B","6","7A","7B","8","10","11"]
FILES = [ROOT/"장v2"/f"장{c}.md" for c in CH] + sorted((ROOT/"장v2").glob("부록D_장*.md")) + [ROOT/"장v2"/f"부록{x}.md" for x in "ABC"]
TOKENS = [
 ("「9장」", r"9장"), ("{{9:", r"\{\{9:"), ("9: (라벨 꼴)", r"(?<![0-9])9:[A-Za-z]"), ("첫째 증명", r"첫째 증명"), ("둘째 증명", r"둘째 증명"),
 ("두 증명", r"두 증명"), ("두 길", r"두 길"), ("두 마무리", r"두 마무리"), ("공유 입력", r"공유 입력"), ("고유 입력", r"고유 입력"),
 ("LRP_2", r"LRP\}_2|LRP_2"), ("regen", r"mathrm\{regen\}"), ("mathsf{FS}", r"mathsf\{FS\}"), ("mathrm{lk}", r"mathrm\{lk\}"), (r"P\Diamond", r"P\Diamond"),
 ("7:old-6-22", r"7:old-6-22"), ("2:old-2-39", r"2:old-2-39"), ("2:old-2-41", r"2:old-2-41"), ("6:increment-bounds", r"6:increment-bounds"),
 ("6:D-bound", r"6:D-bound"), ("6:pair-rearrange", r"6:pair-rearrange"), ("10:regen-vs-ledger", r"10:regen-vs-ledger"), ("11.4절", r"11\.4절"),
 ("둘째 문턱", r"둘째 문턱"), ("1.05 (수)", r"(?<![0-9.])1\.05(?![0-9])"), ("3.6k^{2/3}", r"3\.6k\^\{2/3\}|3\.6\s*k\^\{2/3\}"), ("1.009 (수)", r"(?<![0-9.])1\.009(?![0-9])"),
 # X1이 더한 토큰
 ("3131", r"3131"), ("3132", r"3132"), ("FL_n", r"mathrm\{FL\}_n"), ("KD_n (KD'_n 제외)", r"mathrm\{KD\}_n"), ("PAIR_n", r"mathrm\{PAIR\}_n"),
 ("다섯 몫", r"다섯 몫"), ("거대 나무", r"거대 나무"), ("창×창", r"창×창"), ("깊은 낙하", r"깊은 낙하"), ("대칭점", r"대칭점"), ("착지 행", r"착지 행"),
 ("SRC", r"SRC"), ("mathsf v(10^4)|1.629", r"mathsf v\(10\^4\)|1\.629"), ("11.3절", r"11\.3절"), (r"DDL^natural", r"DDL\}\^\\natural"),
]
out = [f"점검 X1 전수 검색 — 읽은 시각 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
texts = {f.name: f.read_text(encoding="utf-8").split("\n") for f in FILES}
for name, pat in TOKENS:
    rx = re.compile(pat)
    total = 0; per = []
    for fn, lines in texts.items():
        hits = [(i, L) for i, L in enumerate(lines, 1) if rx.search(L)]
        c = sum(len(rx.findall(L)) for _, L in hits)
        if c:
            total += c
            tag = " [부록 A·B·C]" if fn.startswith("부록") and not fn.startswith("부록D") else ""
            per.append(f"    {fn}{tag}: {c}회, 행 {', '.join(str(i) for i, _ in hits[:12])}{' …' if len(hits) > 12 else ''}")
    out.append(f"[{name}] 총 {total}")
    out.extend(per)
Path(__file__).with_name(Path(__file__).stem + "_out.txt").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print("\n".join(out))
