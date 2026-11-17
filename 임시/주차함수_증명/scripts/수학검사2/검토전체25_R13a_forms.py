# -*- coding: utf-8 -*-
# R13a: for TOKEN in chapter CH, print distinct forms (token + following chars) with counts and first location.
# Usage: python -I ... CH[,CH..] TOKEN [TOKEN..]   (aid for locating places to read)
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
F = importlib.import_module('검토전체25_R13a_find')
data = F.load()
chs = sys.argv[1].split(',')
W = 16
for t in sys.argv[2:]:
    for c in chs:
        forms = {}
        for ch, b, i, sec, l in data:
            if ch != c: continue
            st = 0
            while True:
                p = l.find(t, st)
                if p < 0: break
                st = p + len(t)
                f = l[max(0, p-10):p+len(t)+W]
                key = l[p:p+len(t)+6]
                if key not in forms: forms[key] = [0, b, i, sec, f]
                forms[key][0] += 1
        items = sorted(forms.items(), key=lambda kv: -kv[1][0])
        print('== %s in ch %s: %d forms' % (t, c, len(items)))
        for kf, (n, b, i, sec, f) in items[:int(os.environ.get('TOP', '7'))]:
            print('   %3d  %-28s first %s:%d [%s]  ..%s..' % (n, kf, b, i, sec, f))
