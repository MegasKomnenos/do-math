"""Distinguish source abstract fields from observed non-abstract material."""
import re

def classify(text):
 t=text.strip()
 key=re.sub(r'[^a-z]','',t.lower())
 if not t or key in {'abstract','noabstract','noabstractavailable','noabstractprovided','na'}:return 'placeholder'
 if '\ufffd' in t or re.search(r'[A-Za-z]\?[A-Za-z]',t):return 'damaged_text'
 if re.search(r'\bI (?:earnestly )?recommend this book\b|\bI have always considered this book\b',t,re.I):return 'review_excerpt'
 if re.match(r'\s*(?:from\s+the\s+reviews?|reviewed\s+by|book\s+review\s*:)',t,re.I):return 'review_excerpt'
 if re.match(r'\s*(?:from\s+(?:the\s+)?(?:preface|introduction|text)|preface\s*:)',t,re.I):return 'source_excerpt'
 if re.match(r'\s*(?:table\s+of\s+)?contents\s*[:\n]',t,re.I):return 'table_of_contents'
 if re.search(r'(?:\.\.\.|…)\s*(?:["”\']\s*)?$',t):return 'truncated_snippet'
 pages=re.search(r'\bpp?\.\s*\d+(?:\s*[-–]\s*\d+)?',t,re.I)
 year=re.search(r'\b[12]\d{3}\b',t)
 summary=re.search(r'\b(?:we|this\s+(?:book|paper|article|chapter|volume|work)|is|are|was|were|presents?|provides?|describes?|proposes?|discusses?|shows?|proves?|investigates?)\b',t,re.I)
 if pages and year and t.count(',')>=4 and not summary:return 'bibliographic_citation'
 if re.match(r'\s*references\s*[:\n]',t,re.I):return 'bibliographic_citation'
 return 'database_indexing_abstract'

def database_abstract(text,artifact,content_type=None,attribution=''):
 if classify(text)!='database_indexing_abstract':raise ValueError('Source field does not function as an abstract')
 result={'status':'found','source_kind':'database_indexing_abstract','provided_by':'Summon','wording_author_status':'not_verified','printed_abstract_comparison':'not_yet_checked','artifacts':[artifact],'attribution':attribution}
 if content_type:result['source_content_type']=content_type
 if re.search(r'<(?:mml:)?math\b|<mml:',text,re.I):result['raw_format']='database_text_with_MathML_preserved'
 return result
