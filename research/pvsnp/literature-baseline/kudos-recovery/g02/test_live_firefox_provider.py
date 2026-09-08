import json
from playwright.sync_api import sync_playwright
import resume
from firefox_provider import FirefoxProvider
with sync_playwright() as pw:
 provider=FirefoxProvider(pw,resume.ASSIGN['browser_state'])
 context,proof=provider.get()
 assert proof['authenticated'] and proof['ready'] and 'sciencedirect' in proof['url']
 resume.capture('fixtures','firefox-provider-ready.json',json.dumps(proof,ensure_ascii=False,indent=2),proof['url'],'authenticated-provider-ui')
 print(json.dumps(proof,ensure_ascii=False));provider.close()
