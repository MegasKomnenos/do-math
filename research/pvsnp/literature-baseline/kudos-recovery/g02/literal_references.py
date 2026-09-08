"""Recognize retained literal links only inside an explicit reference section."""
import re

def in_reference_section(body,url):
 start=re.search(r'(?im)^References\s*$',body)
 if not start:return False
 rest=body[start.end():]
 end=re.search(r'(?im)^(?:Author information|Authors and Affiliations|About this chapter|About this article|Copyright information|Rights and permissions|Editor information|Cite this chapter|Bibliographic Information|Related content|Recommended articles)\s*$',rest)
 section=rest[:end.start()] if end else rest
 return bool(re.search(re.escape(url)+r'(?=$|\s|[),;])',section))
