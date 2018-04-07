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
    def get_dynamic_source(seed_url, callback=None, proxy=None):
        try:
            display = Display(visible=0, size=(800, 600))
            display.start()
            if proxy:
                profile = webdriver.FirefoxProfile()
                profile.set_preference('network.proxy.type', 1)
                profile.set_preference('network.proxy.http', proxy[0])
                profile.set_preference('network.proxy.http_port', proxy[1])
                profile.set_preference('network.proxy.ssl', proxy[0])
                profile.set_preference('network.proxy.ssl_port', proxy[1])
                profile.update_preferences()
                driver = webdriver.Firefox(profile)
            else:
                driver = webdriver.Firefox()
            driver.get(seed_url)
            page_source = driver.page_source
            driver.quit()
            display.stop()
            if callback:
                return callback(page_source)
            else:
                return page_source
        except Exception, e:
            print e
            print "[ERROR]Selenium visit %s failed..." % (seed_url)
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

    def set_firefox_proxy(self):
        pass



def parse_func_1(page_source):
    # host http://www.xicidaili.com
    #Return None or a list
    tree = lxml.html.fromstring(page_source)
    trs = tree.cssselect("table#ip_list")
    result = []
    for td in trs[0].getchildren()[0].getchildren():
        #速度<1秒且存活时间>1小时
        if u"速度" not in td[6].text_content():
            speed = td[6].getchildren()[0].attrib["title"].strip().replace(u"秒","")
            sur_time = td[8].text_content()
            if float(speed) < 1 and u"分钟" not in sur_time:
                result.append([td[1].text_content(),td[2].text_content()])
    return result if result else None


def verify_ip_status(ip, dic_url):
    dic_url = {"item":"taobao","url":"https://www.jqian.com/hehuoren-350449.html"}
    timeout = 3
    if isinstance(ip,list) and ip:
        proxy_convert = "%s:%s"%(ip[0],str(ip[1]))
        proxy = {"http":proxy_convert,"https":proxy_convert}
        # try:
        #     #telnetlib.Telnet(ip[0], port=str(ip[1]), timeout=timeout)
        #     r = requests.get("http://weixin.sogou.com/", timeout=timeout, proxies=proxy)
        # except:
        #     return None
        try:
            r = requests.get(dic_url["url"], timeout=timeout, proxies=proxy)
            return "%s:%s" % (dic_url["item"],proxy_convert)
        except:
            #return "HTTP:%s" % proxy_convert
            return None
    else:
        print "[ERROR]Params %s is not a list or is null..."%(ip)
        return None


def store_proxy(proxy,redis_conn):
    if isinstance(proxy,str) and proxy:
        r = redis_conn
        if not r.exists(proxy):
            r.set(proxy,1)
            print "%s store in redis successfully..." % (proxy)
    else:
        print "[ERROR]Params %s is not a list or is null..." %(proxy)


def clear_ip(proxy, redis_conn,dic_url):
    item = proxy.split(":")
    del item[0]
    if item:
        if verify_ip_status(item,dic_url):
            print "[INFO]Proxy %s will be cleared..." % (proxy)
            redis_conn.delete(proxy)


def get_random_proxy(redis_conn):
    try:
        result = redis_conn.randomkey()
    except:
        return None
    return result



if __name__ == "__main__":
    #tmp = Base()
    ip_list = Base.get_dynamic_source("http://www.xicidaili.com/nt/", parse_func_1)
    dic_url = {"item": "taobao", "url": "https://www.taobao.com/"}
    ip1,ip2 = verify_ip_status(ip_list,dic_url)
    print ip1,ip2
    # tmp.get_source("http://www.xicidaili.com/wt/2")
    # page_source = ""
    # with open("a.txt", "r") as fp:
    #     for line in fp.readlines():
    #         page_source = page_source + line
    # parse_func_1(page_source)
