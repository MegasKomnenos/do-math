# R11: 자료 묶음의 기록 폴더 파일과 README 「파일 목록」 표의 대조 (목록에 없는 파일, 목록에만 있는 파일)
import os, re, io, sys
root = '원고_자료'
readme = io.open(os.path.join(root, 'README.md'), encoding='utf-8').read().split('## 파일 목록', 1)[1]
listed = {}
for line in readme.splitlines():
    m = re.match(r'\|\s*`([^`]+)`\s*\|\s*(.*?)\|\s*([^|]*?)\s*\|', line)
    if m:
        listed.setdefault(m.group(1), set()).add(m.group(3).strip())
actual = set()
for d in sorted(os.listdir(root)):
    p = os.path.join(root, d)
    if os.path.isdir(p) and re.fullmatch(r'r[0-9a-f]{7}', d):
        for dp, dn, fn in os.walk(p):
            for f in fn:
                actual.add(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/'))
only_fs = sorted(actual - set(listed))
only_rd = sorted(k for k in listed if re.match(r'r[0-9a-f]{7}/', k) and k not in actual)
print("files in record folders:", len(actual), " listed paths:", len([k for k in listed if re.match(r'r[0-9a-f]{7}/', k)]))
print("in folder but not in README list:", len(only_fs))
by = {}
for f in only_fs: by.setdefault(f.split('/')[0], []).append(f)
for k, v in by.items(): print(" ", k, len(v), v[:12])
print("in README list but not in folder:", len(only_rd), only_rd[:20])

# 목록에 없는 파일이 같은 폴더의 목록 파일과 바이트 동일한 사본인지
import hashlib
def h(p):
    return hashlib.sha256(open(os.path.join(root, p), 'rb').read()).hexdigest()
lh = {}
for k in listed:
    if k in actual: lh.setdefault((k.split('/')[0], h(k)), []).append(k)
print()
for f in only_fs:
    key = (f.split('/')[0], h(f))
    print(f, '-> duplicate of', lh[key][0] if key in lh else None)
