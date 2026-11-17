# R3: survey Korean particles directly after a math span that ends in a (possibly sub/superscripted) named symbol.
# Used only to locate candidate spots; every reported spot was read in context.
import re, sys, collections
path = sys.argv[1]
t = open(path, encoding='utf-8').read()
BS = chr(92)
sym = BS + BS + r'(?:mathrm|mathfrak|mathcal|mathsf|hat)' + BS + r'{[A-Za-z]{1,4}' + BS + r'}'
subsup = r'(?:_[A-Za-z0-9]|_' + BS + r'{[^}]{1,8}' + BS + r'}|' + BS + r'^[A-Za-z0-9+' + BS + r'-]|' + BS + r'^' + BS + r'{[^}]{1,8}' + BS + r'}|' + "'" + r')*'
pat = re.compile('(' + sym + subsup + ')' + BS + r'$(은|는|이|가|을|를|과|와|로|으로|라|이라)(?=[ ,.)])')
c = collections.Counter((m.group(1), m.group(2)) for m in pat.finditer(t))
out = []
for (s, p), n in sorted(c.items()):
    out.append('%s|%s|%d' % (s, p, n))
sys.stdout.write(' ;; '.join(out) + '\n')
