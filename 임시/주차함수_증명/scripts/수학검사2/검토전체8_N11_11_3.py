# 검토전체8 N11: 11.3절 세 표의 "직접 인용하는 자리" 주장을 진술 블록으로 검사한다.
import re, json, os
blocks = json.load(open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\_N11_blocks.json", encoding="utf-8"))
root = r"C:\math\임시\주차함수_증명\장v2"
ch11 = open(os.path.join(root, "장11.md"), encoding="utf-8").read().split("\n")
# 표 구간 찾기
tables = {}
cur = None
for ln in ch11:
    if ln.startswith("**공유 입력.**"): cur = "공유"
    elif ln.startswith("**첫째 증명의 고유 입력.**"): cur = "첫째"
    elif ln.startswith("**둘째 증명의 고유 입력.**"): cur = "둘째"
    elif ln.startswith("### 11.4"): cur = None
    if cur and ln.startswith("| ") and not ln.startswith("| 입력") and not ln.startswith("|---"):
        tables.setdefault(cur, []).append([c.strip() for c in ln.strip().strip("|").split(" | ")])
missing = set()
def labels(s): return re.findall(r"\{\{(\d+[A-Za-z]*:[^}]+)\}\}", s)
for name, rows in tables.items():
    print("=====", name, len(rows), "행")
    for cells in rows:
        inputs = labels(cells[0])
        for l in inputs + labels(cells[1]):
            if l not in blocks: missing.add(l)
        cite_cols = cells[2:]
        for col in cite_cols:
            # "직접 인용 없음" 처리
            direct_none = "직접 인용 없음" in col
            citing = labels(col)
            for c in citing:
                if c not in blocks: missing.add(c)
            # 각 인용 자리(진술)에 대해 입력 라벨 중 하나라도 본문(머리+증명)에 있는지
            for c in citing:
                if c in inputs: continue
                b = blocks.get(c)
                if not b: continue
                found = [l for l in inputs if "{{"+l+"}}" in b["text"]]
                if not found and not direct_none:
                    print(f"  [{cells[0][:40]}] 인용 자리 {c}({b['file']}) 블록에 입력 라벨 없음 (입력={inputs})")
        # "직접 인용 없음" 주장의 검사: 9장·10장 진술과 7:old-6-22 블록에 그 라벨이 나타나는지
        for col_i, col in enumerate(cite_cols):
            for m in re.finditer(r"((?:정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}[^;]*?직접 인용 없음|직접 인용 없음)", col):
                pass
        if "직접 인용 없음" in " ".join(cite_cols):
            # 어느 입력이 직접 인용 없음인지: 간단히 모든 입력 라벨에 대해 9·10장 블록 + 7:old-6-22에서의 출현을 보고
            for l in inputs:
                where = []
                for k, b in blocks.items():
                    if k == l: continue
                    if (b["file"] in ("장9", "장10") or k == "7:old-6-22") and "{{"+l+"}}" in b["text"]:
                        where.append(f"{b['file']}:{k}")
                print(f"  [{cells[0][:40]}] 입력 {l} 이 9·10장/7:old-6-22 블록에 나타나는 자리: {where}")
print("없는 라벨:", missing)
