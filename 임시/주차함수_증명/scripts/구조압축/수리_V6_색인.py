# -*- coding: utf-8 -*-
# 수리 U17 — 장부·부록 A·B·C·구조표에 남은 라벨·식별자의 색인(읽기 전용 분석).
#  (1) 장 파일(장v2/장*.md·부록D_장*.md)의 진술 머리에서 정의된 라벨 집합.
#  (2) 장부 4절의 라벨 집합과의 차: 4절에 있으나 머리에 없는 것(뺌 후보), 머리에 있으나 4절에 없는 것(새 행 후보).
#  (3) 다섯 파일(장부·부록A·B·C·구조표)에 나오는 `{{라벨}}`·`라벨` 가운데 정의되지 않은 것(자리 포함).
#  (4) 식별자 [rXXXXXXX]: 장 파일·부록 D에 나오는 집합 대 부록 B 행 집합 — 소멸 후보.
import re, glob, os, sys, io
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
os.chdir(ROOT)
import subprocess
GIT_ROOT = os.path.abspath(os.path.join(ROOT, '..', '..'))
HEAD_REV = "fbf8a575"  # 9장 제거 물결 끝의 체크포인트(V6 기준)
FORCE_TREE = False
def read_chapter(path):
    """장 파일은 git HEAD 53c18619(물결 3 끝)에서 읽는다 — 병행 단위(H1·H3·U15·U16)가 쥔 파일은 작업 트리가 반쯤 바뀐 상태일 수 있다(파견문 1절). --tree 를 주면 작업 트리."""
    if '--tree' in sys.argv or FORCE_TREE:
        return io.open(path, encoding='utf-8').read()
    rel = os.path.relpath(os.path.abspath(path), GIT_ROOT).replace(os.sep, '/')
    out = subprocess.run(['git', 'show', f'{HEAD_REV}:{rel}'], cwd=GIT_ROOT, capture_output=True)
    if out.returncode != 0:
        return io.open(path, encoding='utf-8').read()
    return out.stdout.decode('utf-8')
HEAD = re.compile(r"\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}")
def _chapter_list():
    if '--tree' in sys.argv or FORCE_TREE:
        names = [os.path.basename(f) for f in glob.glob('장v2/*.md')]
    else:
        rel = os.path.relpath(os.path.abspath('장v2'), GIT_ROOT).replace(os.sep, '/')
        out = subprocess.run(['git', '-c', 'core.quotepath=false', 'ls-tree', '--name-only', f'{HEAD_REV}:{rel}'], cwd=GIT_ROOT, capture_output=True)
        names = out.stdout.decode('utf-8').splitlines()
    return sorted('장v2/' + n for n in names if n.endswith('.md') and not n.startswith('_') and n not in ('부록A.md','부록B.md','부록C.md'))
chap = _chapter_list()
defined = {}
for f in chap:
    for i, l in enumerate(read_chapter(f).split('\n'), 1):
        for m in HEAD.finditer(l):
            defined.setdefault(m.group(2), []).append((os.path.basename(f), i, m.group(1)))
# 부록 D 항목 라벨: `**D.{{D:...}}` 꼴? 확인
DLAB = re.compile(r"\{\{(D:[^}]+)\}\}")
dlabels = {}
for f in chap:
    if '부록D' in f:
        for i, l in enumerate(read_chapter(f).split('\n'), 1):
            if l.startswith('**') or l.startswith('### ') or l.startswith('- **'):
                for m in DLAB.finditer(l):
                    dlabels.setdefault(m.group(1), []).append((os.path.basename(f), i))
print('== (1) 진술 머리 라벨 수:', len(defined), '; 부록 D 항목 라벨 수(머리 줄):', len(dlabels))
dups = {k: v for k, v in defined.items() if len(v) > 1}
if dups:
    print('   중복 정의:', dups)
all_defined = set(defined) | set(dlabels)
# (2) 장부 4절
L = io.open('장부_v2.md', encoding='utf-8').read().split('\n')
s4 = next(i for i, l in enumerate(L) if l.startswith('## 4. '))
s5 = next(i for i, l in enumerate(L) if l.startswith('## 5. '))
rows4 = {}
for i in range(s4, s5):
    l = L[i]
    if l.startswith('| ') and not l.startswith('|---'):
        cells = [c.strip() for c in l.strip().strip('|').split(' | ')]
        labs = re.findall(r"\{\{([^}]+)\}\}", cells[-1]) if cells else []
        for lab in labs:
            rows4.setdefault(lab, []).append((i + 1, cells[0], cells[1] if len(cells) > 1 else ''))
print('\n== (2) 장부 4절 라벨 수:', len(rows4))
gone = sorted(k for k in rows4 if k not in all_defined)
print('   4절에 있으나 머리에 없는 라벨(뺌 후보):', len(gone))
for k in gone:
    print('     ', k, rows4[k])
new = sorted(k for k in defined if k not in rows4)
print('   머리에 있으나 4절에 없는 라벨(새 행 후보):', len(new))
for k in new:
    print('     ', k, defined[k])
# (3) 다섯 파일의 정의되지 않은 라벨 참조
print('\n== (3) 다섯 파일의 정의되지 않은 라벨 참조 ==')
REF = re.compile(r"\{\{([^}]+)\}\}|`((?:\d+|D):[A-Za-z0-9][^`\s]*)`")
for f in ['장부_v2.md', '장v2/부록A.md', '장v2/부록B.md', '장v2/부록C.md', '구조표_v2.md']:
    cnt = {}
    for i, l in enumerate(io.open(f, encoding='utf-8').read().split('\n'), 1):
        for m in REF.finditer(l):
            lab = m.group(1) or m.group(2)
            if lab not in all_defined:
                cnt.setdefault(lab, []).append(i)
    print(f'-- {f}: 정의되지 않은 라벨 {len(cnt)}종, 자리 {sum(len(v) for v in cnt.values())}')
    for lab in sorted(cnt):
        print(f'     {lab}: 행 {cnt[lab][:30]}{" ..." if len(cnt[lab])>30 else ""}')
# (4) 식별자
ID = re.compile(r"(?<![0-9a-zA-Z])r[0-9a-f]{7}(?![0-9a-zA-Z])")
body_ids = {}
for f in chap:
    for i, l in enumerate(read_chapter(f).split('\n'), 1):
        for m in ID.finditer(l):
            body_ids.setdefault(m.group(0), set()).add(os.path.basename(f))
B = io.open('장v2/부록B.md', encoding='utf-8').read().split('\n')
b_ids = {}
for i, l in enumerate(B, 1):
    if l.startswith('| r'):
        b_ids[l.split('|')[1].strip()] = i
print('\n== (4) 식별자: 본문·부록 D 출현', len(body_ids), '; 부록 B 행', len(b_ids))
print('   부록 B에 있으나 본문·부록 D에 없는 식별자(소멸 후보):')
for k in sorted(b_ids):
    if k not in body_ids:
        # 다섯 파일 안 출현
        where = {}
        for f in ['장부_v2.md', '장v2/부록A.md', '장v2/부록C.md']:
            n = io.open(f, encoding='utf-8').read().count(k)
            if n: where[f] = n
        print(f'     {k} (부록 B {b_ids[k]}행) — 장부/부록 A·C 출현 {where}')
print('   본문에 있으나 부록 B에 없는 식별자:')
for k in sorted(body_ids):
    if k not in b_ids:
        print('     ', k, sorted(body_ids[k]))
