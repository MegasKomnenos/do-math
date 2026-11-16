# -*- coding: utf-8 -*-
"""K14-11·K14-12: 의존지도 생성기의 옛 칸 처리를 고친다.
(1) `{{7:supermultiplicative}}` 행 — 11-12 판에서 이어받는 주장 칸의 「; Fekete 적용은 rb7effe0 §3.3 199행」과 문헌 칸 「Fekete 보조정리(표준)」을 뺀다(현행 증명은 Fekete를 쓰지 않는다; 구조표 7.2 행·장부 8절 규칙 8).
(2) 표기 문단 — 정의의 머리처럼 대괄호에 식별자만 있으면 그 식별자를 기록 열에 적는다는 사실을 밝힌다(생성기 148행의 실제 동작).
"""
import io, sys
P = r"C:\math\임시\주차함수_증명\scripts\_gen_의존지도_1절.py"
with io.open(P, encoding="utf-8") as f:
    s = f.read()
if "K14-11" in s:
    print("이미 패치됨"); sys.exit(0)
anchor = 'old_tail = old_text[i2:]  # "\\n## 2. ..." 끝까지\n'
if anchor not in s:
    print("앵커 1 없음"); sys.exit(1)
ins = anchor + (
    "\n# 2026-11-15 K14-11: 현행 7.2절 보조정리 supermultiplicative의 증명은 귀류와 초승법성만 쓰고 Fekete를 부르지 않는다\n"
    "# (구조표 7.2 행, 장부 8절 규칙 8, 11.4절 표에 Fekete 없음). 11-12 판의 주장·문헌 칸에서 그 흔적을 뺀다.\n"
    "if \"7:supermultiplicative\" in old_rows:\n"
    "    _o = old_rows[\"7:supermultiplicative\"]\n"
    "    _o[\"claims\"] = re.sub(r\";\\s*Fekete 적용은[^|]*$\", \"\", _o[\"claims\"]).strip()\n"
    "    if _o[\"lit\"].startswith(\"Fekete\"):\n"
    "        _o[\"lit\"] = \"—\"\n"
)
s = s.replace(anchor, ins, 1)
old2 = "「기록 주장」은 머리 대괄호의 `;` 뒤 기록 식별자(11-12 판이"
new2 = "「기록 주장」은 머리 대괄호의 `;` 뒤 기록 식별자(정의의 머리처럼 대괄호에 식별자만 있으면 그 식별자; 11-12 판이"
if old2 not in s:
    print("앵커 2 없음"); sys.exit(1)
s = s.replace(old2, new2, 1)
with io.open(P, "w", encoding="utf-8", newline="\n") as f:
    f.write(s)
print("패치 완료")
