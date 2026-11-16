# -*- coding: utf-8 -*-
"""_gen_재실행표.py CONFIG에 stored-table-check 항목(이 글의 check_table_iv.py 재확인)을 더한다 — 9차 ZD 인계. 2026-11-16."""
import io
p = r"C:\math\임시\주차함수_증명\scripts\_gen_재실행표.py"
s = io.open(p, encoding="utf-8").read()
anchor = '    "band-check": dict('
assert s.count(anchor) == 1 and '"stored-table-check"' not in s
entry = ('    "stored-table-check": dict(\n'
         '        scripts=[S + "window_mass_env/check_table_iv.py"],\n'
         '        cmd=["python -I check_table_iv.py"],\n'
         '        expect="위반 $0$; 가장 작은 여유 $4.7447\\\\cdot10^{-13}$($i=0$); 엄격 감소, 최소 감소 $6.643869\\\\cdot10^{-6}$($i=11999$)",\n'
         '        outputs=[S + "window_mass_env/check_table_iv_out.txt"],\n'
         '        time="약 14초(`check_table_iv_out.txt`의 time 줄)"),\n')
s = s.replace(anchor, entry + anchor)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("added")
