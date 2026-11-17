# 보고 [C-1]의 근거 문장을 실제로 한 확인대로 적는다(R10 자신의 보고만 고친다). 끝에 줄 끝이 LF인지도 센다.
p = r'C:/math/임시/주차함수_증명/대조v2/수학검사2/검토전체24_R10.md'
s = open(p, encoding='utf-8').read()
old = "장 파일에는 그 뜻의 「경계」가 없다(「Stirling 경계」·「Robbins 경계」·「명시 경계」·「양측 경계」 등 여덟 꼴을 장 파일 전부에서 찾아 0건; 부록 B의 두 건은 기록의 제목이다)."
new = "장 파일과 부록 D에서 「경계」 앞에 오는 말을 모두 뽑아 훑으면 반감 경계·경계 다항식·경계 응답·경계항·경계점·절반과 층의 경계처럼 가장자리의 뜻뿐이고, 상계·하계의 뜻으로 쓴 자리는 찾지 못했다(「Stirling 경계」·「Robbins 경계」·「명시 경계」·「양측 경계」 등 여덟 꼴은 0건; 부록 B의 두 건은 기록의 제목이다)."
assert old in s
s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
b = open(p, 'rb').read()
print('고침; CR 수', b.count(b'\r'), '줄 수', b.count(b'\n'))
