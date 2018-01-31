# -*- coding: utf-8 -*-
"""
Created on Jan 28, 2018

@author: guxiwen
"""

from base import Base,verify_ip_status,store_proxy,parse_func_1,clear_ip,get_random_proxy
from Queue import Queue
import threading,time,redis

lock = threading.Lock()

class MyQueue(Queue):
    def __init__(self):
        Queue.__init__(self,0)

    def _put(self,item):
        if item not in self.queue:
            self.queue.append(item)


class ProxyProduct(threading.Thread):
    num = 1
    def __init__(self, queue_to_filter, redis_conn,max_num,func=None):
        threading.Thread.__init__(self)
        self.data_to_filter = queue_to_filter
        self.time_delay = 30
        self.func = func
        self.redis_conn = redis_conn
        self.max_num = max_num

    def run(self):
        if self.func:
            while True:
                print "Queue_to_filter size is %s" %(self.data_to_filter.qsize())
                try:
                    lock.acquire()
                    ProxyProduct.num = ProxyProduct.num + 1
                    if ProxyProduct.num > self.max_num:
                        print "Provide proxy job is over...Finishing..."
                        return
                    page = ProxyProduct.num
                except:
                    print "[ERROR]Get lock failed..."
                finally:
                    lock.release()
                proxies = self.func(self.redis_conn,page)
                if proxies:
                    for proxy in proxies:
                        self.data_to_filter.put(proxy)
                time.sleep(self.time_delay)
        else:
            print "[ERROR]No func!"


class ProxyConsumer(threading.Thread):
    def __init__(self,queue_to_filter, queue_to_save):
        threading.Thread.__init__(self)
        self.data = queue_to_filter
        self.data_to_save = queue_to_save
        self.dic_url = {"item":"taobao","url":"https://www.taobao.com/"}

    def run(self):
        while True:
            if self.data.qsize() == 0:
                time.sleep(3)
            else:
                proxy = self.data.get()
                proxy_convert = verify_ip_status(proxy,self.dic_url)
                if proxy_convert:
                    self.data_to_save.put(proxy_convert)
                else:
                    continue


class ProxySave(threading.Thread):
    def __init__(self, queue_to_save):
        threading.Thread.__init__(self)
        self.data = queue_to_save
        self.redis_conn = redis.Redis(host="127.0.0.1",db=0)

    def run(self):
        while True:
            print "Save queue size %d" % self.data.qsize()
            if self.data.qsize() == 0:
                time.sleep(60)
            else:
                proxy = self.data.get()
                store_proxy(proxy,self.redis_conn)


class ProxyClearProduct(threading.Thread):
    def __init__(self, queue_to_clear):
        threading.Thread.__init__(self)
        self.data = queue_to_clear
        self.redis_conn = redis.Redis(host="127.0.0.1",db=0)
        self.time_delay = 1800
        self.dic_url = {"item":"taobao","url":"https://www.taobao.com/"}

    def run(self):
        while True:
            keys = self.redis_conn.keys(self.dic_url["item"]+"*")
            for key in keys:
                self.data.put(key)
            time.sleep(self.time_delay)


class ProxyClear(threading.Thread):
    def __init__(self, queue_to_clear):
        threading.Thread.__init__(self)
        self.redis_conn = redis.Redis(host="127.0.0.1", db=0)
        self.data = queue_to_clear
        self.time_delay = 2

    def run(self):
        while True:
            proxy = self.data.get()
            clear_ip(proxy,self.redis_conn)
        time.sleep(self.time_delay)


def get_xici_ip(redis_conn,page):
    url = "http://www.xicidaili.com/nt/" + str(page)
    ip_list = Base.get_dynamic_source(url, parse_func_1)
    if ip_list == "1010":
        proxy = get_random_proxy(redis_conn)
        print "[INFO]Get proxy %s ..." % (proxy)
        if not proxy:
            selenium_proxy = proxy.split(":")
            del selenium_proxy[0]
            ip_list = Base.get_dynamic_source(url, parse_func_1, selenium_proxy)
            return ip_list
    return ip_list if ip_list else None

if __name__ == "__main__":
    queue_to_filter = MyQueue()
    queue_to_save = MyQueue()
    queue_to_clear = MyQueue()
    redis_conn = redis.Redis(host="127.0.0.1", db=0)
    for i in range(2):
        proxy_p = ProxyProduct(queue_to_filter,redis_conn,630,get_xici_ip)
        proxy_p.start()
    for i in range(8):
        proxy_c = ProxyConsumer(queue_to_filter,queue_to_save)
        proxy_c.start()
    proxy_save = ProxySave(queue_to_save)
    proxy_save.start()
    proxy_c_p = ProxyClearProduct(queue_to_clear)
    proxy_c_p.start()
    for i in range(2):
        proxy_clear = ProxyClear(queue_to_clear)
        proxy_clear.start()

