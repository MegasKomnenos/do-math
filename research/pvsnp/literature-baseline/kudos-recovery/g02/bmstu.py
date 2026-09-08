"""Boundary extraction for the observed BMSTU catalog annotation block."""
import re
def abstract_field(body,year,pages):
 if '\nАннотация\n' not in body:return None
 header,tail=body.split('\nАннотация\n',1)
 if 'Подробное описание документа' not in header:return None
 header=header.split('Подробное описание документа',1)[1]
 if not re.search(r'\b'+str(year)+r'\b',header) or not re.search(r'\b'+str(pages)+r'\s*с\.',header):return None
 if '\nУДК\n' not in tail:return None
 value=tail.split('\nУДК\n',1)[0].strip()
 return value or None
