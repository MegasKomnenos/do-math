# -*- coding: utf-8 -*-
import re, sys, io, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r"C:\math\임시\주차함수_증명")
heads = json.load(open(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_heads.json", encoding="utf-8"))
hl = {h["label"]: h for h in heads}
out = []
# --- 대응표 15:52 column permutation check per chapter
tbl = []
for line in (ROOT/"대조v2"/"라벨_번호_대응표_1114.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("| `"):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        tbl.append(c)
from collections import defaultdict
nums = defaultdict(list)
for c in tbl:
    v = c[4]
    if re.match(r"^\d+\.\d+$", v):
        ch, n = v.split("."); nums[ch].append(int(n))
for ch in sorted(nums, key=int):
    s = sorted(nums[ch]); miss = sorted(set(range(1, max(s)+1)) - set(s)); dup = sorted({x for x in s if s.count(x) > 1})
    out.append("15:52 ch%s: max=%d n=%d missing=%s dup=%s" % (ch, max(s), len(s), miss, dup))
# --- 의존지도 기록 주장 column vs head bracket identifiers
dep = {}
in1 = False
for line in (ROOT/"의존지도_v2.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("## 1."): in1 = True; continue
    if line.startswith("### 1.1"): in1 = False
    if in1 and line.startswith("| `{{"):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        dep[c[0].strip("`")] = c
out.append("== 기록 주장 열(/ 앞) vs 머리 대괄호 ; 뒤 식별자")
for h in heads:
    c = dep.get(h["label"]); st = h["status"] or ""
    ids_head = set(re.findall(r"r[0-9a-f]{7}", st.split(";", 1)[1])) if ";" in st else set(re.findall(r"r[0-9a-f]{7}", st))
    col = c[6]
    ids_col = set(re.findall(r"r[0-9a-f]{7}", col.split(" / ")[0])) if col != "—" else set()
    if ids_head != ids_col:
        out.append("  %s: 머리=%s 지도=%s" % (h["label"], sorted(ids_head), sorted(ids_col)))
# --- 첫 판 번호 column
out.append("== 의존지도 첫 판 번호 열 vs 라벨")
for lab, c in dep.items():
    v = c[2]; m = re.match(r"\{\{\d+:old-(\d+)-(\d+)\}\}", lab)
    if m:
        exp = "%s.%s" % m.groups()
        if not v.endswith(" " + exp): out.append("  %s: %r" % (lab, v))
    elif v != "새 진술": out.append("  %s: %r" % (lab, v))
# --- grep checks from 구조표 annotations
checks = {
 "첫 층 나무": ["장2.md"], "\mathsf S_R": None, "(5.50)": None, "(5.51)": None, "(5.52)": None, "(5.53)": None,
 "Fekete": None, "1.446": None, "0.44k": None, "0.44 k": None, "0.53k": None, "\Psi^{\mathrm{lb}}": None,
 "\mathcal I_4": ["장9.md"], "\mathsf{UL}": None, "UL": ["장6.md"], "(Diag)": None, "경계 응답 부등식": None,
 "첫째 범위": None, "둘째 범위": None, "\mathrm{dip}": None, "error-induction": None, "H^*_+": None, "H^\ast_+": None,
 "\mathsf H^\ast_+": None, "\mathsf H^*_+": None, "x_t(y)": None, "\mathsf z_{1/2}": None,
}
files = {p.name: p.read_text(encoding="utf-8").splitlines() for p in (ROOT/"장v2").glob("*.md")}
out.append("== 고정 문자열 검색(건수: 파일별)")
for tok, only in checks.items():
    res = []
    for fn, ls in sorted(files.items()):
        if only and fn not in only: continue
        n = sum(l.count(tok) for l in ls)
        if n: res.append("%s=%d" % (fn, n))
    out.append("  %-28s %s" % (tok, " ".join(res) if res else "0"))
# 부록 B identifiers
b = "\n".join(files["부록B.md"])
ids_B = set(re.findall(r"r[0-9a-f]{7}", b))
ids_text = set()
for fn, ls in files.items():
    if fn == "부록B.md": continue
    for l in ls: ids_text |= set(re.findall(r"\[(r[0-9a-f]{7})\]", l))
out.append("== 부록 B 식별자 %d; 본문·부록 D 대괄호 식별자 %d; B에만=%s; 본문에만=%s" % (len(ids_B), len(ids_text), sorted(ids_B-ids_text), sorted(ids_text-ids_B)))
for x in ["r801ec22","r0af7f41","r5c20a94","r77d0f73","rb1d8cd5","r1b79fab","rba2ecf4","rbeae3a3","rda45d0e","r9e782f5","r7798355","rc391829","rfc69320","r4daca3d","ra7615a0","rb4b7771"]:
    out.append("  %s: B=%s 본문=%s" % (x, x in ids_B, x in ids_text))
(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_misc_out.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
