# -*- coding: utf-8 -*-
import io
P = r"C:\math\임시\주차함수_증명\작업_장부.md"
s = io.open(P, encoding="utf-8", newline="").read()
old = "`\t`·`\\r`·`\\b`"
new = "`\\t`·`\\r`·`\\b`"
print("count:", s.count(old))
s = s.replace(old, new)
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tabs remaining:", s.count("\t"))
