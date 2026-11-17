# 보고 1절(읽은 범위)을 끝까지 읽은 사실대로 고친다(R10 자신의 보고만 고친다).
import glob
p = r'C:/math/임시/주차함수_증명/대조v2/수학검사2/검토전체24_R10.md'
s = open(p, encoding='utf-8').read()
i = s.index('- `장v2/부록C.md` 1–496행 전부'); j = s.index('\n', i)
s = s[:i] + "- `장v2/부록C.md` 1–496행 전부(낱말 표 96행, 이름 표 164행, 글자 표 200행, 영어 병기 표 9행). 글자 표는 행마다 끝까지 읽었고, 따로 장부 7절의 같은 행과 기계로 맞대어 차이 난 자리를 원문으로 다시 읽었다." + s[j:]
old = "그리고 `r9bf2dc6`·`r13b0b8f`·`r7798355`·`r29c10cd`·`r5bbc534`·`rae1f209`·`re71a735`·`r3d0856b`·`r475ada3`·`r030ffae`·`r98fb348`의 `exposition.md`에서 글자·줄 번호 확인."
assert old in s
s = s.replace(old, "그리고 `r9bf2dc6`·`r13b0b8f`·`r7798355`·`r29c10cd`·`r5bbc534`·`rae1f209`·`re71a735`·`r3d0856b`·`r475ada3`·`r030ffae`·`r98fb348`·`r696d62c`·`rb1d8cd5`·`r3172894`·`r5f5cf73`·`r33475a7`·`r7c26b8b`의 `exposition.md`(와 일부 `evidence/`·`review/` 문서)에서 글자·낱말·줄 번호 확인. 75개 기록의 `.md`·`record.json` 전부를 낱말·글자 검색의 대상으로 썼다.")
n = len(glob.glob(r'C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체24_R10_*.py'))
num = {27: '스물일곱', 28: '스물여덟', 29: '스물아홉'}[n]
assert '(스물두 개)' in s
s = s.replace('(스물두 개)', f'({num} 개; 그 가운데 `보고고침`이 붙은 다섯은 이 보고의 문장을 바로잡은 것)')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('고침', n)
