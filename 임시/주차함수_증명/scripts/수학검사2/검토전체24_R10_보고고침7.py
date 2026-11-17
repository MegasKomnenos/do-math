# 보고 [10.2-1]의 행 번호 하나를 바로잡는다(R10 자신의 보고만 고친다).
p = r'C:/math/임시/주차함수_증명/대조v2/수학검사2/검토전체24_R10.md'
s = open(p, encoding='utf-8').read()
old = "`장v2/부록D_장7B.md` 9행 「산술 등급」 줄 전문"
assert old in s
s = s.replace(old, "`장v2/부록D_장7B.md` 11행 「산술 등급」 줄 전문")
s = s.replace('(스물아홉 개; 그 가운데 `보고고침`이 붙은 여섯은', '(서른 개; 그 가운데 `보고고침`이 붙은 일곱은')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('고침')
