# -*- coding: utf-8 -*-
"""장부 1.3 399행: 세션이 걷은 7B 비 글자 \\mathfrak r의 임시 등록을 지우고, D_k의 변수 표기를 n/k로 맞춘다."""
import io, re
p = '장부_v2.md'
lines = io.open(p, encoding='utf-8', newline='').read().split('\n')
idx = [i for i, l in enumerate(lines) if l.startswith('| 7.6의 양(7B 집필자의 최종 글자')]
assert len(idx) == 1, idx
l = lines[idx[0]]
start = l.find('$\\mathfrak r=n/k$(정리')
end = l.find('$\\mathrm D_k(\\mathfrak r)=')
assert 0 < start < end, (start, end)
# 「…, $\mathfrak r=n/k$(… 인계_전체3_SL), $\mathrm D_k(…」 → 「…, $\mathrm D_k(…」
l = l[:start] + l[end:]
old_D = '$\\mathrm D_k(\\mathfrak r)=0.33316\\sqrt k(1-1/\\mathfrak r)^2-\\mathfrak r-42.14/k$(기록 $D_k(z)$;'
new_D = '$\\mathrm D_k(n/k)=0.33316\\sqrt k(1-k/n)^2-n/k-42.14/k$(비 $n/k$의 함수; 글자 없이 적음; 기록 $D_k(z)$;'
assert l.count(old_D) == 1
l = l.replace(old_D, new_D)
lines[idx[0]] = l
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('ok; remaining mathfrak r in line:', l.count('\\mathfrak r'))
