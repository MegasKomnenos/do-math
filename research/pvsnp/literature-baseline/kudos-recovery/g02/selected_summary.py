"""Exact DB-selected quotation boundaries, qualified by recorded direct reading."""
import hashlib,re

def extract(body):
 if len(re.findall(r'(?m)^MR\d+',body))!=1:return None
 match=re.search(r"(?s)\n(Review|Summary)\s*\nFrom the (text|preface|introduction):\s*``(.*?)''(.*)$",body)
 if not match:return None
 text=match[3];following=match[4].strip()
 # The whole quotation must close before any separate database apparatus.
 # Independent review prose after the quotation is never part of this class.
 if following and not (following.startswith('Contents:') or re.fullmatch(r'\{.*\}',following,re.S) or following.startswith('References\n')):return None
 if not text.strip() or not re.search(r'[.!?]$',text.rstrip()):return None
 return {'text':text,'section_heading':match[1],'wording_source':'From the '+match[2],'quotation_open':'``','quotation_close':"''",'following':following,'author_abstract_verified':False}

def approved(paper_id,data,decisions):
 try:parsed=extract(data.decode('utf-8-sig'))
 except UnicodeError:return None
 if not parsed:return None
 source_sha=hashlib.sha256(data).hexdigest();quote_sha=hashlib.sha256(parsed['text'].encode()).hexdigest()
 decision=next((d for d in decisions if d['paper_id']==paper_id and d['source_sha256']==source_sha and d['quote_sha256']==quote_sha and d['decision']=='database_selected_summary'),None)
 if not decision:return None
 return {**parsed,'reason':decision['reason'],'source_sha256':source_sha,'quote_sha256':quote_sha}
