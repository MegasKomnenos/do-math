# -*- coding: utf-8 -*-
# _JL_수리_1116.py의 줄끝 처리를 CRLF에서 LF로 바꾼다(세 파일은 LF — 파이썬 실측).
p = r"C:\math\임시\주차함수_증명\scripts\_보관_tmp\_JL_수리_1116.py"
s = open(p, encoding="utf-8").read()
n0 = s.count('"\\r\\n"')
s = s.replace('"\\r\\n"', '"\\n"')
s = s.replace('assert "\\r\\n" in s and "\\n" not in s.replace("\\r\\n", ""), p',
              'assert "\\r" not in s, p  # 세 파일은 LF 줄끝(파이썬 실측)')
s = s.replace('assert "\\n" not in s.replace("\\r\\n", ""), p', 'assert "\\r" not in s, p')
s = s.replace('print("written", p, "lines", s.count("\\r\\n"))', 'print("written", p, "lines", s.count("\\n"))')
s = s.replace('CRLF를 그대로 둔다', '줄끝(세 파일 모두 LF — 파이썬 실측)을 그대로 둔다')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("replaced", n0, "CRLF literals; remaining", s.count('\\r\\n'))
