"""Classify actual source outcomes without copying one failure across sources."""
import re
def assess(text,status):
 if not text.strip():return 'retry'
 if 'The handle you requested' in text and 'cannot be found' in text:return 'link_not_found'
 if re.search(r'Unusual Traffic Detected \(Error 418\)|preview of subscription content|이용가능한 전자자료가 없습니다|보안 확인 수행 중',text,re.I):return 'restricted'
 if status==429 or (status and status>=500):return 'retry'
 return 'content'
