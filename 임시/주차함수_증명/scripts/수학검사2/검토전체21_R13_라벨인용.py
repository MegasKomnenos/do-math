# R13: 장부·구조표·의존지도가 {{…}}로 부르는 라벨이 장 파일의 현행 머리에 있는지 본다.
# 구조표는 죽은 라벨을 중괄호 없이 적는다고 머리말이 밝히므로, 중괄호 라벨은 모두 살아 있어야 한다.
import re, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
heads = json.load(open(os.path.join(ROOT, '대조v2', '수학검사2', '_R13_heads.json'), encoding='utf-8'))
live = {h['label'] for h in heads}
lab_re = re.compile(r'\{\{(\d+:[^}]+)\}\}')
bare_re = re.compile(r'`(\d+:[a-zA-Z][^`\s]*)`')
# 부록 D 라벨 {{D:…}}는 부록 D 조각의 머리에서 모은다
D_re = re.compile(r'\{\{(D:[^}]+)\}\}')
dlabels = set()
import glob
for f in glob.glob(os.path.join(ROOT, '장v2', '부록D_*.md')):
    for line in open(f, encoding='utf-8'):
        if line.startswith('**') or line.startswith('#') or line.startswith('- **') or line.startswith('### '):
            for m in D_re.findall(line):
                dlabels.add(m)
print('부록 D 라벨(머리)', sorted(dlabels))
for name in ['장부_v2.md', '구조표_v2.md', '의존지도_v2.md', os.path.join('대조v2', '라벨_번호_대응표_1114.md')]:
    path = os.path.join(ROOT, name)
    print('\n==', name)
    bad = {}
    badD = {}
    for ln, line in enumerate(open(path, encoding='utf-8'), 1):
        for m in lab_re.findall(line):
            if m not in live:
                bad.setdefault(m, []).append(ln)
        for m in D_re.findall(line):
            if m not in dlabels:
                badD.setdefault(m, []).append(ln)
    for m, lns in sorted(bad.items()):
        print('  죽은/없는 라벨을 중괄호로:', m, '행', lns[:12], ('…' if len(lns) > 12 else ''))
    for m, lns in sorted(badD.items()):
        print('  없는 부록 D 라벨:', m, '행', lns[:12])
    if name == '구조표_v2.md':
        # 중괄호 없이 적은 라벨 가운데 실제로 살아 있는 것(머리말과 어긋남)
        alive_bare = {}
        for ln, line in enumerate(open(path, encoding='utf-8'), 1):
            for m in bare_re.findall(line):
                if m in live:
                    alive_bare.setdefault(m, []).append(ln)
        for m, lns in sorted(alive_bare.items()):
            print('  살아 있는 라벨을 중괄호 없이:', m, '행', lns[:12])
