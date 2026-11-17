# 검토 22차 R8: 보고 파일의 LaTeX 토큰이 온전한지(역슬래시 탈락, 줄바꿈 끼어듦) 점검
import io, re, sys
BS = chr(92)
s = io.open(sys.argv[1], encoding='utf-8').read()
words = 'mathfrak|mathrm|mathcal|mathsf|frac|varepsilon|varsigma|sqrt|infty|lfloor|rfloor|lceil|rceil|dots|cdot|qquad|approx|times'
pat = re.compile('(' + words + ')(?![A-Za-z])')
n = 0
for i, line in enumerate(s.split(chr(10)), 1):
    for m in pat.finditer(line):
        prev = line[m.start()-1] if m.start() > 0 else ' '
        if prev != BS and not prev.isalpha():
            n += 1; print(i, line[max(0, m.start()-30):m.end()+30])
    if re.match('^[a-z]{1,4}[)$}]', line):
        print('줄 머리 의심', i, line[:60])
print('역슬래시 없는 토큰:', n)
print('달러 홀수 줄:', [i for i, line in enumerate(s.split(chr(10)), 1) if line.count('$') % 2])
