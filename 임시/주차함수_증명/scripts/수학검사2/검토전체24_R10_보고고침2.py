# 보고 파일의 한 구절을 확인한 원문대로 바로잡는다(R10 자신의 보고만 고친다).
p = r'C:/math/임시/주차함수_증명/대조v2/수학검사2/검토전체24_R10.md'
s = open(p, encoding='utf-8').read()
old = "기록 75개에서 「식별자」는 세 기록에 「프로세스 식별자」로만 나오고"
new = "기록 75개에서 「식별자」는 세 기록에 계산 실행을 가리키는 말(`rf09e7ef` 「프로세스 식별자」, `rc9aee43` 「실행 식별자」)로만 나오고"
assert old in s
open(p, 'w', encoding='utf-8', newline='\n').write(s.replace(old, new))
print('고침')
