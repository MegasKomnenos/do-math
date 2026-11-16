# -*- coding: utf-8 -*-
"""검토 D: 보관 폴더 v1_binary64omega(둘)·v1_floatgrid의 파일이 README 파일 목록(옛 SHA)과 맞는지, README 행의 파일이 지금 폴더에 있는지."""
import hashlib, io, os, re
ROOT = r"C:\math\임시\주차함수_증명\원고_자료"
readme = io.open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
rows = dict(re.findall(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$", readme, flags=re.M))
print("README 표 행", len(rows))
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
for folder in ["세션_재계산/bprime_boxes", "세션_재계산/band_boxes"]:
    print("==", folder)
    listed = {k: v for k, v in rows.items() if k.startswith(folder + "/")}
    v1 = os.path.join(ROOT, folder, "v1_binary64omega")
    moved = sorted(os.listdir(v1))
    same = diff = unl = 0
    for f in moved:
        if f.endswith(".npy"):
            continue
        key = folder + "/" + f
        h = sha(os.path.join(v1, f))
        if key in listed:
            if listed[key] == h: same += 1
            else: diff += 1; print("  SHA 다름:", f)
        else:
            unl += 1; print("  README 표에 없는 보관 파일:", f)
    print(f"  v1 파일(.npy 제외) README 일치 {same}, 불일치 {diff}, 표에 없음 {unl}")
    # README 행 가운데 v1에 없는 것(출력 파일인데 안 옮긴 것)과 지금 top에 없는 것
    top = set(os.listdir(os.path.join(ROOT, folder)))
    for key, h in sorted(listed.items()):
        f = key[len(folder) + 1:]
        intop = f in top
        inv1 = f in moved
        tophash = sha(os.path.join(ROOT, folder, f)) if intop and os.path.isfile(os.path.join(ROOT, folder, f)) else None
        if not intop:
            print("  !! README 행의 파일이 폴더에 없음:", f, "(v1에 있음)" if inv1 else "(v1에도 없음)")
        elif tophash != h and not inv1:
            print("  README SHA와 다른데 v1에 보관 안 됨:", f)
    for f in sorted(top):
        p = os.path.join(ROOT, folder, f)
        if os.path.isfile(p) and not f.endswith(".npy") and (folder + "/" + f) not in listed:
            print("  표에 없는 현재 파일:", f)
# critical_window_rerun: README 표에 행이 있는지
cw = [k for k in rows if "critical_window_rerun" in k]
print("== critical_window_rerun README 행 수", len(cw))
cwv = [k for k in rows if k.startswith("세션_재계산/critical_window/")]
print("   critical_window(옛) README 행 수", len(cwv))
