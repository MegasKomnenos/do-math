# 보고 파일의 한 문장을 확인한 원문으로 바로잡는다(R10 자신의 보고만 고친다).
p = r'C:/math/임시/주차함수_증명/대조v2/수학검사2/검토전체24_R10.md'
s = open(p, encoding='utf-8').read()
old = "기록의 멈춤 확률은 사슬이 거기서 끝날 확률이고(`r696d62c` `exposition.md`: 「끝의 멈춤 확률 stop_κ(r_(L−1))를 곱하면 경로 확률이다」), 부록 A 72행이 그 글자 $\mathrm{stop}_N(h)$([rb1d8cd5])를 쪼개짐 확률 $\pi^0$에 맞세운다."
new = "기록의 멈춤 확률은 사슬이 거기서 끝날 확률이다(`r696d62c` `exposition.md` 77행: 「조각과 부류는 \"멈춤 확률 𝒩을 포함·배제로 펼쳤는가\"에서만 다르다」). 부록 A 72행은 바로 그 글자 $\mathcal N(L,c)$([r696d62c])와 $\mathrm{stop}_N(h)$([rb1d8cd5])를 쪼개짐 확률 $\pi^0_n(y)$에 맞세운다."
assert old in s, '옛 문장을 못 찾음'
s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('고침')
