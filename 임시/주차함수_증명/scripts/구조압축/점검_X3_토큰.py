# -*- coding: utf-8 -*-
"""점검 X3 (수·문턱·계산의 여파) — 9장 제거 토큰과 수치 고아 후보의 전수 검색.

읽기만 한다. 장v2/장*.md, 장v2/부록D_*.md 를 주 대상으로, 부록A·B·C는 참고(편집 중)로 따로 센다.
출력: 같은 폴더의 점검_X3_토큰_out.txt (UTF-8, LF).
실행: python -I scripts/구조압축/점검_X3_토큰.py   (어느 작업 폴더에서든 된다; 경로는 파일 위치에서 잡는다)
"""
import os, re, sys, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CH = os.path.join(ROOT, '장v2')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '점검_X3_토큰_out.txt')

MAIN = ['장1.md', '장2.md', '장3.md', '장4.md', '장5A.md', '장5B.md', '장6.md', '장7A.md', '장7B.md', '장8.md', '장10.md', '장11.md',
        '부록D_장2.md', '부록D_장3.md', '부록D_장4.md', '부록D_장5A.md', '부록D_장5B.md', '부록D_장6.md', '부록D_장7A.md', '부록D_장7B.md', '부록D_장8.md', '부록D_장10.md']
REF = ['부록A.md', '부록B.md', '부록C.md']

# (표시 이름, 정규식, 문맥 출력 여부)
REMOVAL = [
    ('「9장」', r'(?<![0-9])9장', True),
    ('{{9:', r'\{\{9:', True),
    ('9: (숫자 앞 아님)', r'(?<![0-9])9:', True),
    ('「첫째 증명」', r'첫째 증명', True),
    ('「둘째 증명」', r'둘째 증명', True),
    ('「두 증명」', r'두 증명', True),
    ('「두 길」', r'두 길', True),
    ('「두 마무리」', r'두 마무리', True),
    ('「공유 입력」', r'공유 입력', True),
    ('「고유 입력」', r'고유 입력', True),
    ('LRP', r'LRP', True),
    ('regen', r'regen', True),
    ('FS (낱말)', r'(?<![A-Za-z\\])FS(?![A-Za-z])', True),
    ('lk (낱말)', r'(?<![A-Za-z\\])lk(?![A-Za-z])', True),
    ('P◇ / P\\diamond', r'P\^?\\diamond|P◇', True),
    ('7:old-6-22', r'7:old-6-22', True),
    ('2:old-2-39', r'2:old-2-39', True),
    ('2:old-2-41', r'2:old-2-41', True),
    ('6:increment-bounds', r'6:increment-bounds', True),
    ('6:D-bound', r'6:D-bound', True),
    ('6:pair-rearrange', r'6:pair-rearrange', True),
    ('10:regen-vs-ledger', r'10:regen-vs-ledger', True),
    ('D:H-star-plus-interval', r'D:H-star-plus-interval', True),
    ('D:band-LP', r'D:band-LP', True),
    ('D:pair-one-variable', r'D:pair-one-variable', True),
    ('「11.4절」', r'11\.4절', True),
    ('「둘째 문턱」', r'둘째 문턱', True),
    ('1.05 (상수)', r'(?<![0-9.])1\.05(?![0-9])', True),
    ('3.6k^{2/3}', r'3\.6\s*\\?,?\s*k', True),
    ('1.009', r'(?<![0-9.])1\.009(?![0-9])', True),
    ('「입력 표」', r'입력 표', True),
    ('첫째/둘째 … 증명 (변형)', r'첫째[^。.\n]{0,6}증명|둘째[^。.\n]{0,6}증명', True),
]

ORPHAN = [
    ('3131', r'(?<![0-9.])3131(?![0-9])', True),
    ('3132', r'(?<![0-9.])3132(?![0-9])', True),
    ('19404', r'(?<![0-9.])19404(?![0-9])', True),
    ('48966', r'(?<![0-9.])48966(?![0-9])', True),
    ('38887', r'(?<![0-9.])38887(?![0-9])', True),
    ('1.149', r'(?<![0-9.])1\.149(?![0-9])', True),
    ('0.0536 / 0.0537', r'(?<![0-9.])0\.053[67](?![0-9])', True),
    ('1.198', r'(?<![0-9.])1\.198(?![0-9])', True),
    ('1.629', r'(?<![0-9.])1\.629(?![0-9])', True),
    ('1.549', r'(?<![0-9.])1\.549(?![0-9])', True),
    ('0.3951', r'(?<![0-9.])0\.3951(?![0-9])', True),
    ('0.2244', r'(?<![0-9.])0\.2244(?![0-9])', True),
    ('0.4193', r'(?<![0-9.])0\.4193(?![0-9])', True),
    ('0.4944', r'(?<![0-9.])0\.4944(?![0-9])', True),
    ('k+103', r'k\s*\+\s*103(?![0-9])', True),
    ('4k^{2/3}', r'(?<![0-9.])4\s*k\^\{2/3\}', True),
    ('6/5 (분수)', r'\\frac\s*65|\\frac\{6\}\{5\}|6/5(?![0-9])', True),
    ('8065', r'(?<![0-9.])8065(?![0-9])', True),
    ('9551', r'(?<![0-9.])9551(?![0-9])', True),
    ('9705', r'(?<![0-9.])9705(?![0-9])', True),
    ('3999', r'(?<![0-9.])3999(?![0-9])', True),
    ('1.3k^{2/3}', r'1\.3\s*k\^\{2/3\}', True),
    ('2k^{2/3}', r'(?<![0-9.])2\s*k\^\{2/3\}', True),
    ('0.976 / 0.98% (띠 여유)', r'0\.976|0\.98\\?%', True),
    ('1.0097', r'1\.0097', True),
    ('0.168 (1a 여유)', r'(?<![0-9.])0\.168(?![0-9])', True),
    ('0.0856', r'0\.0856', True),
    ('1.3195 / 1.1507', r'1\.3195|1\.1507', True),
]

REGISTRY = [
    ('16', r'(?<![0-9.,$^{_-])16(?![0-9])'),
    ('20000', r'(?<![0-9.])20000(?![0-9])'), ('20001', r'(?<![0-9.])20001(?![0-9])'),
    ('50000', r'(?<![0-9.])50000(?![0-9])'), ('50001', r'(?<![0-9.])50001(?![0-9])'),
    ('6667', r'(?<![0-9.])6667(?![0-9])'), ('6668', r'(?<![0-9.])6668(?![0-9])'),
    ('25000', r'(?<![0-9.])25000(?![0-9])'), ('25001', r'(?<![0-9.])25001(?![0-9])'),
    ('10000', r'(?<![0-9.])10000(?![0-9])'), ('10001', r'(?<![0-9.])10001(?![0-9])'),
    ('2000', r'(?<![0-9.])2000(?![0-9])'), ('2001', r'(?<![0-9.])2001(?![0-9])'),
    ('140', r'(?<![0-9.])140(?![0-9])'), ('141', r'(?<![0-9.])141(?![0-9])'),
    ('500', r'(?<![0-9.])500(?![0-9])'), ('501', r'(?<![0-9.])501(?![0-9])'),
    ('840', r'(?<![0-9.])840(?![0-9])'), ('841', r'(?<![0-9.])841(?![0-9])'),
    ('102', r'(?<![0-9.])102(?![0-9])'), ('103', r'(?<![0-9.])103(?![0-9])'),
    ('0.48k', r'0\.48\s*k'), ('0.49k', r'0\.49\s*k'),
    ('6600', r'(?<![0-9.])6600(?![0-9])'),
    ('4000', r'(?<![0-9.])4000(?![0-9])'),
    ('43', r'(?<![0-9.])43(?![0-9])'), ('50 (용량)', r'(?<![0-9.])50(?![0-9])'), ('301', r'(?<![0-9.])301(?![0-9])'),
    ('170', r'(?<![0-9.])170(?![0-9])'), ('64', r'(?<![0-9.])64(?![0-9])'), ('1.4 (창)', r'(?<![0-9.])1\.4(?![0-9])'),
    ('6k^{2/3}', r'(?<![0-9.])6\s*k\^\{2/3\}'), ('m^{2/3}/2', r'm\^\{2/3\}/2'),
    ('1.15', r'(?<![0-9.])1\.15(?![0-9])'),
]


def load(fn):
    p = os.path.join(CH, fn)
    if not os.path.exists(p):
        return None
    with open(p, 'rb') as f:
        b = f.read()
    return b.decode('utf-8'), b.count(b'\r'), len(b)


def scan(files, toks, ctx_limit=14, show_ctx=True):
    lines_out = []
    texts = {fn: load(fn) for fn in files}
    for name, rx, ctx in toks:
        r = re.compile(rx)
        per = []
        hits = []
        total = 0
        for fn in files:
            t = texts[fn]
            if t is None:
                continue
            txt = t[0]
            c = 0
            for ln, line in enumerate(txt.split('\n'), 1):
                for m in r.finditer(line):
                    c += 1
                    hits.append((fn, ln, m.start(), line))
            if c:
                per.append('%s:%d' % (fn, c))
            total += c
        lines_out.append('%-40s 합계 %4d   %s' % (name, total, ', '.join(per) if per else '(없음)'))
        if show_ctx and ctx and 0 < total <= ctx_limit:
            for fn, ln, pos, line in hits:
                a = max(0, pos - 70)
                b = min(len(line), pos + 90)
                snip = line[a:b].replace('\t', ' ')
                lines_out.append('      %s:%d  …%s…' % (fn, ln, snip))
    return lines_out


def main():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    out = []
    out.append('# 점검 X3 토큰 전수 검색 — 실행 %s' % now)
    out.append('# 대상 폴더: %s' % CH)
    out.append('')
    out.append('## 0. 읽은 파일 (크기 바이트, CR 수, 수정 시각)')
    for fn in MAIN + REF:
        p = os.path.join(CH, fn)
        if os.path.exists(p):
            t = load(fn)
            mt = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%H:%M:%S')
            out.append('  %-16s %8d B  CR=%d  mtime %s' % (fn, t[2], t[1], mt))
        else:
            out.append('  %-16s (없음)' % fn)
    out.append('')
    out.append('## 1. 제거 토큰 (장·부록D)')
    out += scan(MAIN, REMOVAL)
    out.append('')
    out.append('## 2. 수치 고아 후보 (장·부록D)')
    out += scan(MAIN, ORPHAN, ctx_limit=16)
    out.append('')
    out.append('## 3. 등록부 수의 분포 (장·부록D; 수만 센다)')
    out += scan(MAIN, [(n, r, False) for n, r in REGISTRY], show_ctx=False)
    out.append('')
    out.append('## 4. 참고 — 부록 A·B·C (U17 편집 중; 제거 토큰만)')
    out += scan(REF, REMOVAL, ctx_limit=10)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    sys.stdout.buffer.write(('\n'.join(out) + '\n').encode('utf-8'))


if __name__ == '__main__':
    main()
