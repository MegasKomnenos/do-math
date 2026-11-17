# -*- coding: utf-8 -*-
"""X2 전수 검색 — 파견문 1.6의 토큰 목록을 장 파일과 부록 D 조각(그리고 참고로 부록 A·B·C)에서 센다.
실행: python -I scripts/구조압축/점검_X2_토큰.py > scripts/구조압축/점검_X2_토큰_out.txt
읽기 전용. 원고는 고치지 않는다."""
import re, sys, os, glob, io, datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
ROOT = os.path.abspath(ROOT)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')

TOKENS = [
    ('「9장」',            re.compile(r'(?<![0-9])9장')),
    ('`{{9:`',            re.compile(r'\{\{9:')),
    ('`9:`',              re.compile(r'(?<![0-9A-Za-z.\-])9:')),
    ('「첫째 증명」',      re.compile(r'첫째 증명')),
    ('「둘째 증명」',      re.compile(r'둘째 증명')),
    ('「두 증명」',        re.compile(r'두 증명')),
    ('「두 길」',          re.compile(r'두 길')),
    ('「두 마무리」',      re.compile(r'두 마무리')),
    ('「공유 입력」',      re.compile(r'공유 입력')),
    ('「고유 입력」',      re.compile(r'고유 입력')),
    ('LRP',               re.compile(r'LRP')),
    ('regen',             re.compile(r'regen')),
    ('FS',                re.compile(r'(?<![A-Za-z])FS(?![A-Za-z])')),
    ('lk',                re.compile(r'(?<![A-Za-z])lk(?![A-Za-z])')),
    ('P◇ (Diamond)',     re.compile(r'\\Diamond|◇')),
    ('`7:old-6-22`',      re.compile(r'7:old-6-22')),
    ('`2:old-2-39`',      re.compile(r'2:old-2-39')),
    ('`2:old-2-41`',      re.compile(r'2:old-2-41')),
    ('`6:increment-bounds`', re.compile(r'6:increment-bounds')),
    ('`6:D-bound`',       re.compile(r'6:D-bound')),
    ('`6:pair-rearrange`', re.compile(r'6:pair-rearrange')),
    ('`10:regen-vs-ledger`', re.compile(r'10:regen-vs-ledger')),
    ('「11.4절」',         re.compile(r'11\.4절')),
    ('「둘째 문턱」',      re.compile(r'둘째 문턱')),
    ('1.05',              re.compile(r'(?<![0-9.])1\.05(?![0-9])')),
    ('3.6k^{2/3}',        re.compile(r'3\.6\s*k')),
    ('1.009',             re.compile(r'(?<![0-9.])1\.009(?![0-9])')),
]

GROUPS = [
    ('장 파일', sorted(glob.glob(os.path.join(ROOT, '장v2', '장*.md')))),
    ('부록 D 조각', sorted(glob.glob(os.path.join(ROOT, '장v2', '부록D_*.md')))),
    ('부록 A·B·C(참고; V6 영역)', sorted(glob.glob(os.path.join(ROOT, '장v2', '부록[ABC].md')))),
]

def ctx(line, m, w=70):
    a = max(0, m.start() - w); b = min(len(line), m.end() + w)
    s = line[a:b].replace('\n', ' ')
    return ('…' if a > 0 else '') + s + ('…' if b < len(line) else '')

print('X2 전수 검색 — 실행 시각', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print('뿌리:', ROOT)
grand = {}
for gname, files in GROUPS:
    print('\n' + '=' * 78)
    print('묶음:', gname, '(파일 %d)' % len(files))
    for f in files:
        st = os.stat(f)
        print('  파일 %s  크기 %d B  수정 %s' % (os.path.relpath(f, ROOT), st.st_size,
              datetime.datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M:%S')))
    counts = {}
    hits = []
    for f in files:
        with open(f, encoding='utf-8', newline='') as fh:
            data = fh.read()
        cr = data.count('\r')
        lines = data.split('\n')
        for ln, line in enumerate(lines, 1):
            for name, rx in TOKENS:
                for m in rx.finditer(line):
                    counts[name] = counts.get(name, 0) + 1
                    hits.append((name, os.path.relpath(f, ROOT), ln, ctx(line, m)))
    print('\n  토큰별 수:')
    for name, _ in TOKENS:
        c = counts.get(name, 0)
        print('    %-22s %d' % (name, c))
        grand.setdefault(gname, {})[name] = c
    print('\n  자리(토큰 / 파일:행 / 문맥):')
    if not hits:
        print('    (없음)')
    for name, rel, ln, c in hits:
        print('    [%s] %s:%d\n        %s' % (name, rel, ln, c))
print('\n' + '=' * 78)
print('끝.')
