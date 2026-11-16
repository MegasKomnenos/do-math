import re
ch = open('장v2/장10.md', encoding='utf-8').read()
led = open('장부_v2.md', encoding='utf-8').read()
appA = open('장v2/부록A.md', encoding='utf-8').read()
BS = chr(92)
pat = re.compile(BS + BS + r"(?:mathfrak|mathsf|mathcal|mathrm) ?(?:\{[^{}]*\}|[A-Za-z])(?:\^\{[^{}]*\}|\^[A-Za-z0-9]|\^" + BS + BS + r"[A-Za-z]+|_\{[^{}]*\}|_[A-Za-z0-9]|_" + BS + BS + r"[A-Za-z]+)*")
toks = set(m.group(0) for m in pat.finditer(ch))
missing = [t for t in sorted(toks) if t not in led]
missA = [t for t in sorted(toks) if t not in appA]
print(len(toks), "tokens; not verbatim in ledger:", len(missing))
print(" | ".join(missing))
print("not in appendix A:", len(missA))
print(" | ".join(missA))
