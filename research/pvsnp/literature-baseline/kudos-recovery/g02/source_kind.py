"""Classify actual source outcomes without copying one failure across sources."""
import re
def assess(text,status):
 if not text.strip():return 'retry'
 if re.fullmatch(r'(?:Loading|Please wait)[.\s…]*',text.strip(),re.I):return 'retry'
 if re.fullmatch(r'Skip to main content\s+For Authors\s+For Librarians',text.strip(),re.I):return 'retry'
 if text.lstrip().startswith('There was a problem providing the content you requested') and 'CPE00001' in text:return 'provider_failure'
 if 'The handle you requested' in text and 'cannot be found' in text:return 'link_not_found'
 if re.search(r'Unusual Traffic Detected \(Error 418\)|preview of subscription content|보안 확인 수행 중',text,re.I):return 'restricted'
 if '이용가능한 전자자료가 없습니다' in text:return 'no_resource'
 if status==429 or (status and status>=500):return 'retry'
 return 'content'
