# -*- coding: utf-8 -*-
# R13a: ledger section 5 (rows per chapter, column "이 장이 처음 정의하는 전역 기호") vs section 1.2
# (first definition section of each row). Also checks the spare-letter column against the base
# letters of 1.2 rows whose "쓰이는 장" contains the chapter (letters only; aid for reading).
import io, os, re, sys
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
led = io.open(os.path.join(base, '장부_v2.md'), encoding='utf-8').read().split('\n')
rows = {}
for n in range(49, 288):
    c = led[n-1].split(' | ')
    head = c[0][2:].strip()
    secs = re.findall(r'(\d+)\.\d+', c[3])
    first = c[3].strip()
    m = re.match(r'(\d+)\.(\d+)', first)
    rows[head] = dict(line=n, defch=m.group(1), defcell=c[3].strip(), used=[x.strip() for x in c[4].split(',')], font=c[1].strip())
sec5 = {}
for n in range(1191, 1201):
    c = led[n-1].split(' | ')
    ch = c[0][2:].strip()
    syms = [s.strip() for s in c[1].split('; ')]
    sec5[ch] = (n, syms, c[3])
for ch in sorted(sec5, key=int):
    n, syms, spare = sec5[ch]
    want = [h for h in rows if rows[h]['defch'] == ch]
    miss = [h for h in want if h not in syms]
    extra = [s for s in syms if s not in want]
    print('ch %s (L%d): listed %d, expected %d' % (ch, n, len(syms), len(want)))
    for h in miss: print('   in 1.2 (def %s, L%d) but not in section 5 row: %s' % (rows[h]['defcell'], rows[h]['line'], h))
    for s in extra:
        info = rows.get(s)
        print('   in section 5 row but 1.2 says: %s  -> %s' % (s, (info['defcell'] + ' L%d' % info['line']) if info else 'NO SUCH 1.2 ROW'))
    # spare letters vs used globals: font classes
    used = [h for h in rows if ch in rows[h]['used']]
    for h in used:
        f = rows[h]['font']
        m = re.match(r'(\\?[A-Za-z]+)·(.*)', f)
        if not m: continue
        letter, cls = m.group(1), m.group(2)
        if '일반' in cls: tok = '$' + letter + '$'
        elif '필기체' in cls: tok = '$\\mathcal ' + letter + '$'
        elif '프락투어' in cls: tok = '$\\mathfrak ' + letter + '$'
        elif '산세리프' in cls: tok = '$\\mathsf ' + letter + '$'
        else: continue
        if tok in spare:
            print('   SPARE LIST contains base letter of a global used in ch %s: %s  (row L%d %s)' % (ch, tok, rows[h]['line'], h))
