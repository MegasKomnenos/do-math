# -*- coding: utf-8 -*-
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
NOTFONT = r'(?<!\\mathsf )(?<!\\mathfrak )(?<!\\mathcal )(?<!\\mathrm )(?<!\\mathbf )(?<!\\mathbb )(?<!\\mathscr )(?<![A-Za-z\\])'
def plain(letter): return NOTFONT + re.escape(letter) + r'(?![A-Za-z])'
p = plain('s')+r'\^\{?\\mathrm\{?F\b'
print(repr(p))
s = '4-3s^{\\mathrm F}(k,\\nu)'
print(s)
print(re.search(p, s))
print(re.search(r's\^\{?\\mathrm\{?F\b', s))
print(re.search(NOTFONT + 's', s))
print(re.search(plain('s'), s))
print(re.search(plain('s')+r'\^', s))
print(re.search(plain('s')+r'\^\{', s))
print(re.search(plain('s')+r'\^\{?\\mathrm', s))
