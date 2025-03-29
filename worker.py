from seleniumbase import Driver
import time
from lxml import html
from starlette.types import ExceptionHandler

class SeleniumWorker:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.uses = 0
        self.start_time = time.time()
        self.driver = self._start_driver()

    def _start_driver(self):
        return Driver(uc=True,multi_proxy=True,uc_cdp=True,log_cdp=True,ad_block=True,headless2=True)

    def fetch(self, url):
        try:
            self.driver.open(url)
            self.driver.sleep(1)
            page_source =self.driver.get_page_source()
            tree = html.fromstring(page_source)
            
            if tree.xpath("//iframe[@title='recaptcha challenge']") or tree.xpath("//div[contains(@class, 'g-recaptcha')]") or \
            tree.xpath("//iframe[contains(@src, 'hcaptcha.com')]") or tree.xpath('//h2[contains(text(),"You are being rate limited")]') or \
            tree.xpath('//*[contains(text(),"Verifying you are human. This may take a few seconds.")]'):
                return page_source,True    

            else:
                return self.driver.get_page_source(), False
        
        
        except Exception:
            return None, True



    def restart(self, new_proxy=None):
        try:
            self.driver.quit()
        except:
            print('driver.quit error')
            try:
                self.driver.close()
            except:
                print('driver.close error')
                
        self.proxy = new_proxy
        self.uses = 0
        self.start_time = time.time()
        self.driver = self._start_driver()

    

    def quit(self):
        self.driver.quit()
      
    def is_stale(self, max_uses=10, max_age=300):
        return self.uses >= max_uses or (time.time() - self.start_time) > max_age

