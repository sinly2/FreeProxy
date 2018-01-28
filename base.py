# -*- coding: utf-8 -*-
"""
Created on Jan 28, 2018

@author: guxiwen
"""

from pyvirtualdisplay import Display
from selenium import webdriver
import requests, lxml.html,telnetlib,redis
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# display = Display(visible=0, size=(800,600))
# display.start()
# driver = webdriver.Chrome()
# driver.get("http://www.xicidaili.com/nt/")
# time.sleep(5)
# page_source = driver.page_source
# driver.quit()
# display.stop()


class Base(object):
    def __init__(self):
        # self.display = Display(visible=0,size=(800,600))
        self.cookies = {}
        self.proxies = {}
        self.session = requests.Session()
        self.user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 " \
                          "Safari/537.36 SE 2.X MetaSr 1.0"
        self.headers = {"user-agent": self.user_agent, "accept-encoding": "gzip, deflate, sdch",
                        "accept-language": "zh-CN,zh;q=0.8", "content-type": "application/x-www-form-urlencoded",
                        "referer": "http://www.xicidaili.com/nt/", "Upgrade-Insecure-Requests": "1",
                        "host": "www.xicidaili.com"}

    @staticmethod
    def get_dynamic_source(seed_url, callback=None):
        try:
            display = Display(visible=0, size=(800, 600))
            display.start()
            driver = webdriver.Firefox()
            driver.get(seed_url)
            page_source = driver.page_source
            # for cookie in self.driver.get_cookies():
            #     self.cookies.update(dict(cookie["name"],cookie["value"]))
            # cookies = requests.utils.cookiejar_from_dict(self.cookies, cookiejar=None, overwrite=True)
            # self.session.cookies = cookies
            # cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
            # with open("a.txt","wb") as fp:
            #     fp.write(page_source)
            driver.quit()
            display.stop()
            if callback:
                return callback(page_source)
            else:
                return page_source

        except Exception, e:
            print "[ERROR]Selenium visit %s failed..." % (seed_url)
            print e
            return "1010"

    def get_source(self, seed_url, callback=None):
        try:
            result = self.session.get(seed_url, headers=self.headers)
            if result.status_code == 200:
                if callback:
                    return callback(result.text)
                else:
                    return result.text
            else:
                print "[ERROR]Visit %s http responsecode %d" % (seed_url, result.status_code)
                return "1001"
        except Exception, e:
            print "[ERROR]Visit %s failed..." % (seed_url)
            print e
            return "1010"

    def set_cookie(self, cookie):
        self.session.cookies = cookie

    def get_cookie(self):
        return self.session.cookies


def parse_func_1(page_source):
    # host http://www.xicidaili.com
    tree = lxml.html.fromstring(page_source)
    trs = tree.cssselect("table#ip_list")
    result = []
    for td in trs[0].getchildren()[0].getchildren():
        result.append([td[1].text_content(),td[2].text_content()])
    del result[0]
    return result

def verify_ip_status(ip):
        if isinstance(ip,list) and ip:
            proxy_convert = "%s:%s"%(ip[0],str(ip[1]))
            telnetlib.Telnet(ip[0], port=str(ip[1]), timeout=10)
            proxy = {"http":proxy_convert,"https":proxy_convert}
            r = requests.get("http://weixin.sogou.com/", timeout=10, proxies=proxy)
            try:
                r = requests.get("https://www.baidu.com", timeout=10, proxies=proxy)
                return "HTTPS:%s" % proxy_convert
            except:
                return "HTTP:%s" % proxy_convert
        else:
            print "[ERROR]Params %s is not a list or is null..."%(ip)
            return None

def store_proxy(proxy,redis_conn):
    if isinstance(proxy,str) and proxy:
        r = redis_conn
        if not r.exists(proxy):
            r.set(proxy,1)
            print "%s store in redis successfully..."
    else:
        print "[ERROR]Params %s is not a list or is null..."%(proxy)

def clear_ip(type="HTTP"):
    pass




if __name__ == "__main__":
    #tmp = Base()
    ip_list = Base.get_dynamic_source("http://www.xicidaili.com/nt/", parse_func_1)
    ip1,ip2 = verify_ip_status(ip_list)
    print ip1,ip2
    # tmp.get_source("http://www.xicidaili.com/wt/2")
    # page_source = ""
    # with open("a.txt", "r") as fp:
    #     for line in fp.readlines():
    #         page_source = page_source + line
    # parse_func_1(page_source)
