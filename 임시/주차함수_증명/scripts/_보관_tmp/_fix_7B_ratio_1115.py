# -*- coding: utf-8 -*-
"""정리 theorem-W (나) 증명(장7B 627–631행)의 비 글자 \\mathfrak r(1.2 \\mathfrak r_N과 겹침)을 글자 없이 n/k로 풀어 적는다."""
import io
p = '장v2/장7B.md'
t = io.open(p, encoding='utf-8', newline='').read()
pairs = [
    (r'(나) $\mathfrak r:=n/k$로 두자. $n\ge2k+1\ge6263$이므로', r'(나) $n\ge2k+1\ge6263$이므로'),
    (r'$(n-k+1)^2/(n(n+1))\ge(1-1/\mathfrak r)^2$이고', r'$(n-k+1)^2/(n(n+1))\ge(1-k/n)^2$이고'),
    (r'\mathfrak G_k(n)\ge\frac{0.14}{\mathfrak r k}\bigl[2.38\cdot0.9999\,k^{3/2}(1-1/\mathfrak r)^2-301\bigr]$이며 $\mathfrak G_k(n)>1$은',
     r'\mathfrak G_k(n)\ge\frac{0.14}{n}\bigl[2.38\cdot0.9999\,k^{3/2}(1-k/n)^2-301\bigr]$이며, 비 $n/k$의 함수로 적은 $\mathfrak G_k(n)>1$은'),
    (r'\mathrm D_k(\mathfrak r):=0.33316\sqrt k\,(1-1/\mathfrak r)^2-\mathfrak r-42.14/k>0',
     r'\mathrm D_k(n/k):=0.33316\sqrt k\,(1-k/n)^2-n/k-42.14/k>0'),
    (r'$(1-1/\mathfrak r)^2$의 둘째 도함수는 $2(3-2\mathfrak r)/\mathfrak r^4$로 $\mathfrak r\ge2$에서 음이므로 $\mathrm D_k$는 $\mathfrak r\ge2$에서 오목하고',
     r'$(1-k/n)^2$을 비 $n/k$의 함수로 보면 둘째 도함수가 $2(3-2n/k)/(n/k)^4$로 $n/k\ge2$에서 음이므로 $\mathrm D_k$는 $n/k\ge2$에서 오목하고'),
    (r'왼쪽 끝 $\mathfrak r=2$에서', r'왼쪽 끝 $n/k=2$에서'),
    (r'오른쪽 끝 $\mathfrak r_{\max}:=n_{\mathrm{PD}}(k)/k\le k^{1/3}(1+1/k)^{4/3}+1+2/k\le1.0005k^{1/3}+1.001$이고 $\mathfrak r_{\max}\ge k^{1/3}$에서 $(1-1/\mathfrak r_{\max})^2\ge(1-k^{-1/3})^2$이므로, $\mathrm D_k(\mathfrak r_{\max})\ge',
     r'오른쪽 끝 $n/k=n_{\mathrm{PD}}(k)/k\le k^{1/3}(1+1/k)^{4/3}+1+2/k\le1.0005k^{1/3}+1.001$에서는 $n_{\mathrm{PD}}(k)/k\ge k^{1/3}$이므로 $(1-k/n_{\mathrm{PD}}(k))^2\ge(1-k^{-1/3})^2$이고, $\mathrm D_k(n_{\mathrm{PD}}(k)/k)\ge'),
    (r'$[2,\mathfrak r_{\max}]$ 전체에서 양수다', r'$[2,n_{\mathrm{PD}}(k)/k]$ 전체에서 양수다'),
]
for old, new in pairs:
    n = t.count(old)
    assert n == 1, (n, old[:60])
    t = t.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
left = t.count('\\mathfrak r')
print('ok; remaining mathfrak r in 7B:', left)
