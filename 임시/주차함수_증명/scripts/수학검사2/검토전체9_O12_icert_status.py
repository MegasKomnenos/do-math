# icert_py_full 폴더의 진행 상태를 센다: 끝난 열, 빠진 열, CPU 초, 불일치. (보고 (4-1)의 근거)
import glob, json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = "C:/math/임시/주차함수_증명/원고_자료/세션_재계산/icert_py_full/"
ks = set(); secs = 0.0; bad = 0
for f in glob.glob(base + 'out_*.txt') + glob.glob(base + 'out_*.part'):
    for line in open(f, encoding='utf-8'):
        line = line.strip()
        if not line: continue
        d = json.loads(line); ks.add(d['k']); secs += float(d.get('sec', 0))
        if not d.get('bit_identical_to_C', True) or d.get('ok') != [True, True]: bad += 1; print('PROBLEM', d)
missing = [k for k in range(1001, 10001) if k not in ks]
print('columns done', len(ks), '| missing', len(missing), '| first missing', missing[:3], '| cpu hours', round(secs/3600, 1), '| problems', bad)
print('txt files', len(glob.glob(base + 'out_*.txt')), '| part files', len(glob.glob(base + 'out_*.part')))
