# -*- coding: utf-8 -*-
"""번역측_전달 10절에서 heredoc 이스케이프로 깨진 `\\nu`(백슬래시+줄바꿈+u)를 되돌린다."""
import io
p = r"C:\math\임시\주차함수_증명\대조v2\수학검사2\번역측_전달_1115.md"
s = io.open(p, encoding="utf-8").read()
bad = "\\" + "\n" + "u$·$t$·$y$·$r$·$d$·$q$ 행"
good = "\\nu$·$t$·$y$·$r$·$d$·$q$ 행"
n = s.count(bad)
assert n == 1, n
s = s.replace(bad, good)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("fixed", n)
