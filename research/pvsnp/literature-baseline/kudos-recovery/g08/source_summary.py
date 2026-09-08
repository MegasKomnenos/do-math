"""Quote-boundary extraction only; semantic eligibility still requires review."""
import re

def source_quote(text):
    match=re.match(r"^Review\s*\nFrom the text:\s*``",text.strip())
    if not match:return None
    quote,separator,tail=text.strip()[match.end():].partition("''")
    if not separator or tail.strip():return None
    return quote.replace('``','').strip()
