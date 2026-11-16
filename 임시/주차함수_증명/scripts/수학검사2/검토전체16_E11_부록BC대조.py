# (1) 부록 B의 식별자·폴더와 본문·부록이 인용한 식별자, 기록 폴더의 실존을 견준다.
# (2) 부록 C 「기록이 결과에 붙인 이름과 이 글의 번호」 표를 본문 진술 머리의 괄호(이름; 기록 [r…]의 …)와 견준다.
import re, glob, os
root = r"C:\math\임시\주차함수_증명"
rec_dir = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
B = open(os.path.join(root, "장v2", "부록B.md"), encoding="utf-8").read()
brow = re.findall(r"^\| (r[0-9a-f]{7}) \| ([^|]+) \| ([^|]+) \| `(r[0-9a-f]{32})` \|", B, flags=re.M)
bids = {r[0]: r for r in brow}
print("부록 B 행 수", len(brow))
folders = set(os.listdir(rec_dir)) if os.path.isdir(rec_dir) else set()
print("기록 폴더 수", len(folders))
for rid, t, title, folder in brow:
    if folder not in folders: print("[폴더 없음]", rid, folder)
    if not folder.startswith(rid): print("[식별자≠폴더 앞 8글자]", rid, folder)
# 본문 인용 식별자
cited = {}
for f in sorted(glob.glob(os.path.join(root, "장v2", "*.md"))):
    if os.path.basename(f) == "부록B.md": continue
    txt = open(f, encoding="utf-8").read()
    for m in re.finditer(r"\[(r[0-9a-f]{7})\]|; (r[0-9a-f]{7}(?:, r[0-9a-f]{7})*)\]", txt):
        ids = [m.group(1)] if m.group(1) else m.group(2).split(", ")
        for i in ids: cited.setdefault(i, set()).add(os.path.basename(f))
print("본문·부록 인용 식별자 수", len(cited))
print("인용되었으나 B에 없음:", sorted(set(cited) - set(bids)))
print("B에 있으나 어디에도 인용 안 됨:", sorted(set(bids) - set(cited)))
# 시각 순서 점검
times = [r[1].strip() for r in brow]
print("시각 순서가 깨진 자리:", [(times[i], times[i+1]) for i in range(len(times)-1) if times[i] > times[i+1]])
# (2) 부록 C 이름표
C = open(os.path.join(root, "장v2", "부록C.md"), encoding="utf-8").read()
sec = C[C.index("### 기록이 결과에 붙인 이름"): C.index("### 기록의 글자와 이 글의 글자")]
crow = re.findall(r"^\| (.+?) \| (정리|명제|보조정리|따름정리) \{\{(\d+:[a-zA-Z0-9-]+)\}\} \| (.+?) \|$", sec, flags=re.M)
cmap = {}
for src, kind, lab, name in crow: cmap.setdefault(lab, []).append((src, kind, name))
print("\n부록 C 이름표 행 수", len(crow))
heads = {}
for f in sorted(glob.glob(os.path.join(root, "장v2", "장*.md"))):
    for line in open(f, encoding="utf-8"):
        m = re.match(r"^\*\*(정리|명제|보조정리|따름정리)\s+\{\{(\d+[AB]?:[a-zA-Z0-9-]+)\}\}\s*(?:\((.*?)\)\s*)?\[", line)
        if m and "의 증명" not in line[:60]:
            lab = m.group(2).replace("5A:","5:").replace("5B:","5:").replace("7A:","7:").replace("7B:","7:")
            heads[lab] = (m.group(1), m.group(3) or "")
# 머리에 「기록 [r…]의 …」가 있는 진술
for lab, (kind, par) in sorted(heads.items()):
    if "기록 [" in par:
        name, _, src = par.partition("; ")
        if lab not in cmap:
            print("[C 이름표에 없음]", kind, lab, "|", par); continue
        for csrc, ckind, cname in cmap[lab]:
            if ckind != kind: print("[종류 다름]", lab, "머리:", kind, "C:", ckind)
            if cname.strip() != name.strip(): print("[이름 다름]", lab, "머리:", name, "| C:", cname)
            if csrc.strip() != src.strip(): print("[출처 다름]", lab, "\n   머리:", src, "\n   C  :", csrc)
for lab, rows in cmap.items():
    if lab not in heads: print("[C에 있으나 머리 없음]", lab, rows)
    elif "기록 [" not in heads[lab][1]: print("[C에 있으나 머리에 기록 이름 없음]", lab, "머리 괄호:", heads[lab][1][:80], "| C:", rows)
