import sys, re, html as H
sys.path.insert(0, r"C:\math\도구")
import md2pdf
text = open(sys.argv[1], encoding="utf-8").read()
md = md2pdf.build_markdown()
env = {"math": []}
text2 = md2pdf.escape_intraword_asterisks(text)
body, title, headings = md2pdf.convert_markdown(md, text2, env)
body = md2pdf.decorate(body)
open(sys.argv[2], "w", encoding="utf-8").write(body)
ems = re.findall(r"<em>(.*?)</em>", body, flags=re.S)
print("em count", len(ems))
for e in ems:
    t = re.sub(r"<[^>]+>", "", e); t = re.sub(r"\x00MATH\d+\x00", "$", t)
    print("  EM:", repr(H.unescape(t)[:100]), "len", len(t))
codes = re.findall(r"<code>(.*?)</code>", body, flags=re.S)
hang = [c for c in codes if re.search(r"[가-힣]", c)]
print("code spans", len(codes), "with hangul", len(hang))
for c in hang[:20]: print("  CODE:", H.unescape(c)[:80])
# literal asterisks remaining in text (outside math placeholders)
stars = re.findall(r"[^\x00]{0,30}\*[^\x00]{0,30}", re.sub(r"<[^>]+>", "", body))
print("literal * occurrences", len(stars))
for s in stars[:30]: print("  *:", repr(s))
