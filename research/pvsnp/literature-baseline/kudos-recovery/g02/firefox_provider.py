"""One sequential Firefox fallback for the observed institution provider path."""
class FirefoxProvider:
 def __init__(self,pw,state):self.pw=pw;self.state=state;self.browser=None;self.context=None;self.proof=None
 def get(self):
  if self.context:return self.context,self.proof
  browser=self.pw.firefox.launch(headless=True);context=browser.new_context(storage_state=self.state);context.set_default_timeout(20000)
  try:
   page=context.new_page();page.goto('https://kudos.knu.ac.kr/pages/index.htm',wait_until='domcontentloaded');page.get_by_role('link',name='로그아웃',exact=True).wait_for(state='visible')
   page.goto('https://kudos.knu.ac.kr/pages/sub.htm?nav_code=kud1641346542',wait_until='domcontentloaded');page.locator('#search_order').fill('ScienceDirect');page.locator('#search_order').press('Enter')
   with context.expect_page() as opened:page.get_by_text('바로가기',exact=True).first.click()
   provider=opened.value;provider.wait_for_function("() => location.hostname.includes('sciencedirect')",timeout=40000);provider.locator('#qs:visible').first.wait_for(state='visible',timeout=40000)
   proof={'engine':'Firefox headless default settings','authenticated':True,'ready':True,'url':provider.url,'search_selector':'#qs:visible','visible_inputs':provider.locator('input:visible').count()}
   page.close();provider.close();self.browser=browser;self.context=context;self.proof=proof
   return context,proof
  except Exception:browser.close();raise
 def close(self):
  if self.browser:self.browser.close()
