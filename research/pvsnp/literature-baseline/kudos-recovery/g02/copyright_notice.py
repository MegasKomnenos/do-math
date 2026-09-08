"""Match an unambiguous year on an explicit copyright notice line."""
import re

def matches_year(front,year):
 observed=set()
 for line in front.splitlines():
  if not re.match(r'^\s*(?:©|Copyright\b)',line,re.I):continue
  years=set(re.findall(r'\b(?:18|19|20)\d{2}\b',line))
  observed.update(years)
 return observed=={str(year)}
