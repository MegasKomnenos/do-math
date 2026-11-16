# -*- coding: utf-8 -*-
"""20차 독립 검토 파견문(태그 N)과 20차 수리 공통 안내(태그 Y) 1–3절을 19차 것에서 만든다. 2026-11-16.
파일 이름에 차례 번호가 있어 겹치지 않는 글자(N 검토·Y 수리)를 쓴다.
공통 안내의 C50·C20·C1′·(G1)(G2)와 「5차 V2 실측」은 작업자 태그가 아니므로 보호한다."""
import io, re
ROOT = r"C:\math\임시\주차함수_증명\파견"

s = io.open(ROOT + r"\전체_독립검토19_파견문_1116.md", encoding="utf-8").read()
print("파견문 안의 기존 N·Y 토큰", re.findall(r"(?<![A-Za-z가-힣])[NY](\d+[ab]?)(?=[^A-Za-z가-힣]|$)", s))
s = re.sub(r"^# .*$", lambda m: m.group(0).replace("19차", "20차").replace("18차 수리", "19차 수리"), s, count=1, flags=re.M)
s = s.replace("검토전체19_M", "검토전체20_N")
s = re.sub(r"\| M(\d+[ab]?) \|", lambda m: "| N" + m.group(1) + " |", s)
s = s.replace("M11·M12·M13", "N11·N12·N13").replace("M14", "N14").replace("M1–M14", "N1–N14")
s = s.replace("`scripts/수학검사2/검토전체19_<태그>_*.py`", "`scripts/수학검사2/검토전체20_<태그>_*.py`")
s = re.sub(r"(?<![A-Za-z가-힣])M(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "N" + m.group(1), s)
# 19차의 교훈 한 문장: 표의 셀을 기계로 쪼갠 값은 원문 행으로 확인(N11 선례) — 글리프 교훈 문장 바로 뒤
pat = re.compile(r"(문헌 원문을 PDF에서[^\n]*?오독한 선례가 있다\)\.)")
assert len(pat.findall(s)) == 1, pat.findall(s)
s = pat.sub(lambda m: m.group(1) + " 장부·부록 A의 표에서 셀을 기계로 쪼개어 뽑은 값(기호의 핵·정의 절 번호)은 그 행의 원문을 열어 확인한 뒤에야 지적으로 적는다(19차에 부록 A 기호 셀을 쉼표에서 쪼개 다른 행의 절 번호를 읽어 세 기호의 정의 절이 틀렸다고 적은 선례가 있다).", s, count=1)
io.open(ROOT + r"\전체_독립검토20_파견문_1116.md", "w", encoding="utf-8", newline="\n").write(s)
print("파견문 ok", len(s), "M 잔존", re.findall(r"(?<![A-Za-z가-힣])M\d", s), "19차 잔존", [s[max(0,m.start()-15):m.start()+10] for m in re.finditer("19차", s)])

c = io.open(ROOT + r"\전체검토19_수리_공통_1116.md", encoding="utf-8").read()
print("공통 안내 안의 기존 N·Y 토큰", re.findall(r"(?<![A-Za-z가-힣])[NY](\d+|D|L)(?=[^A-Za-z가-힣]|$)", c))
i = c.find("## 4. ")
assert i > 0
c = c[:i] + "## 4. 이번 차례의 배정 메모(세션이 보고를 훑어 적은 임자와 주의; 판정이 아니다)\n\n(N1–N14 보고 회수 뒤 작성)\n"
c = c.replace("전체 독립 검토 19차(M1–M14) 뒤의 수리", "전체 독립 검토 20차(N1–N14) 뒤의 수리")
c = c.replace("이 문서는 19차 전체 검토의 지적을 반영하는", "이 문서는 20차 전체 검토의 지적을 반영하는")
c = c.replace("검토전체19_", "검토전체20_").replace("수리_전체19_", "수리_전체20_").replace("인계_전체19_", "인계_전체20_")
PROT = {"C50": "\u0001", "C20": "\u0002", "C1′": "\u0003", "(G1)(G2)": "\u0004", "5차 V2 실측": "\u0005"}
for k, v in PROT.items():
    c = c.replace(k, v)
c = re.sub(r"(?<![A-Za-z가-힣])X(\d+|D|L)(?=[^A-Za-z가-힣]|$)", lambda m: "Y" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])X(\d+|D|L)(?=[가-힣·])", lambda m: "Y" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])M(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "N" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])M(\d+[ab]?)(?=[가-힣·])", lambda m: "N" + m.group(1), c)
for k, v in PROT.items():
    c = c.replace(v, k)
c = c.replace("6차부터 18차까지", "6차부터 19차까지")
io.open(ROOT + r"\전체검토20_수리_공통_1116.md", "w", encoding="utf-8", newline="\n").write(c)
print("공통 ok", len(c), "X 잔존", re.findall(r"(?<![A-Za-z가-힣])X(\d+|D|L)\b", c), "M 잔존", len(re.findall(r"(?<![A-Za-z가-힣])M\d", c)),
      "19차 잔존", [c[max(0,m.start()-15):m.start()+10] for m in re.finditer("19차", c)], "Y 토큰", sorted(set(re.findall(r"(?<![A-Za-z가-힣])Y(\d+|D|L)\b", c))))
