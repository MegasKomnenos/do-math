# 보고 1절의 부록 B 줄에 읽은 방식을 밝힌다(R10 자신의 보고만 고친다).
p = r'C:/math/임시/주차함수_증명/대조v2/수학검사2/검토전체24_R10.md'
s = open(p, encoding='utf-8').read()
old = "- `장v2/부록B.md` 1–82행 전부(머리 문단과 75행)."
assert old in s
s = s.replace(old, "- `장v2/부록B.md` 1–82행 전부(머리 문단과 75행; 330자를 넘는 긴 제목의 뒷부분은 눈으로 읽지 않고 `record.json`의 `title`과 글자 단위로 맞대어 같음을 확인).")
s = s.replace('(스물여덟 개; 그 가운데 `보고고침`이 붙은 다섯은', '(스물아홉 개; 그 가운데 `보고고침`이 붙은 여섯은')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
b = open(p, 'rb').read(); print('CR', b.count(b'\r'), '줄', b.count(b'\n'), '바이트', len(b))
