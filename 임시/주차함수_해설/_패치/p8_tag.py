# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
P = r'임시/주차함수_해설/원고.md'
t = open(P, encoding='utf-8').read()
found = re.findall(r'\\tag\{[^}]*\}', t)
print('before:', found)
t2 = re.sub(r'\\tag\{R[^}]*\}', lambda m: r'\tag{$R_0$}', t)
t2 = re.sub(r'\\tag\{CF[^}]*\}', lambda m: r"\tag{$CF'_0$}", t2)
open(P, 'w', encoding='utf-8', newline='\n').write(t2)
print('after:', re.findall(r'\\tag\{[^}]*\}', t2))
