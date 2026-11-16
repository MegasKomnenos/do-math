import sys, re, html as H
sys.path.insert(0, r"C:\math\도구"); import md2pdf
text = open(r"C:\math\임시\주차함수_증명\원고.md", encoding="utf-8").read()
t2 = md2pdf.escape_stray_asterisks(text)
print("chars changed:", sum(1 for a,b in zip(text,t2) if a!=b), "len diff", len(t2)-len(text))
md = md2pdf.build_markdown(); env={"math":[]}
body, title, headings = md2pdf.convert_markdown(md, t2, env)
body = md2pdf.decorate(body)
ems = re.findall(r"<em>(.*?)</em>", body, flags=re.S)
print("em count", len(ems))
import collections
print(collections.Counter(re.sub(r"\x00D?MATH\d+\x00","$",re.sub(r"<[^>]+>","",e))[:40] for e in ems).most_common(20))
plain = re.sub(r"<[^>]+>","",body)
stars = re.findall(r".{0,25}\*.{0,25}", plain)
print("literal * in text:", len(stars))
for s in stars[:40]: print("   ", repr(s))
print("para divs:", body.count('<div class="para'), " dmath:", body.count('<div class="dmath">'), " nested p in p:", len(re.findall(r"<p[^>]*>[^<]*<p", body)))
print("thm:", body.count('class="para thm"') + body.count('<p class="thm"'), " proof:", body.count('class="para proof"') + body.count('<p class="proof"'))
print("headings with math:")
for h in headings:
    if "\x00" in h["html"]: print("   ", h["level"], repr(h["text"]), "| key:", repr(h["key"]))
# sample of a para split
m = re.search(r'<div class="para[^"]*">.*?</div>', body, flags=re.S); print("sample:", m.group(0)[:400])
