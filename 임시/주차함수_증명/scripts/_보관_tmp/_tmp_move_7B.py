import io, sys
p = sys.argv[1]
with io.open(p, encoding='utf-8', newline='') as f:
    lines = f.read().split('\n')
# 1-indexed: head of 정리 old-6-21 at 829; 따름정리 block 849..871 (incl. trailing blank)
assert lines[828].startswith('**정리 {{7:old-6-21}}'), lines[828][:40]
assert lines[848].startswith('**따름정리 {{7:threshold-unit-ratio}}'), lines[848][:40]
assert lines[870] == '', repr(lines[870][:40])
assert lines[871].startswith('층의 꼭대기'), lines[871][:40]
assert lines[827] == '', repr(lines[827][:40])
block = lines[848:871]
new = lines[:828] + block + lines[828:848] + lines[871:]
assert len(new) == len(lines)
with io.open(p, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(new))
print('moved', len(block), 'lines; new head positions:',
      [i + 1 for i, l in enumerate(new) if l.startswith('**정리 {{7:old-6-21}}') or l.startswith('**따름정리 {{7:threshold-unit-ratio}}')])
