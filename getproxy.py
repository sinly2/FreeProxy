# -*- coding: utf-8 -*-
"""
Created on Jan 28, 2018

@author: guxiwen
"""

from base import Base,verify_ip_status,store_proxy,parse_func_1,clear_ip
from Queue import Queue
import threading,time,redis


class MyQueue(Queue):
    def __init__(self):
        Queue.__init__(self,0)

    def _put(self,item):
        if item not in self.queue:
            self.queue.append(item)

class ProxyConsumer(threading.Thread):
    def __init__(self,queue,queue_to_save):
        threading.Thread.__init__(self)
        self.data = queue
        self.data_to_save = queue_to_save

    def run(self):
        while True:
            if self.data.qsize() == 0:
                time.sleep(3)
            else:
                proxy = self.data.get()
                proxy_convert = verify_ip_status(proxy)
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
                time.sleep(10)
            else:
                proxy = self.data.get()
                store_proxy(proxy,self.redis_conn)


class ProxyClearProduct(threading.Thread):
    def __init__(self, queue_to_clear):
        threading.Thread.__init__(self)
        self.data = queue_to_clear
        self.redis_conn = redis.Redis(host="127.0.0.1",db=0)
        self.time_delay = 1800

    def run(self):
        while True:
            keys = self.redis_conn.keys("HTTP*")
            for key in keys:
                self.data.put(key)
            time.sleep(self.time_delay)


class ProxyClear(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self,queue_to_clear)
        self.redis_conn = redis.Redis(host="127.0.0.1", db=0)
        self.data = queue_to_clear
        self.time_delay = 2

    def run(self):
        while True:
            proxy = self.data.get()
            clear_ip(proxy,self.redis_conn)
        time.sleep(self.time_delay)

if __name__ == "__main__":
    queue_to_filter = MyQueue()
    queue_to_save = MyQueue()
    queue_to_clear = MyQueue()
    ip_list = Base.get_dynamic_source("http://www.xicidaili.com/nt/", parse_func_1)
    for ip in ip_list:
        queue_to_filter.put(ip)
    for i in range(6):
        proxy_c = ProxyConsumer(queue_to_filter,queue_to_save)
        proxy_c.start()
    proxy_save = ProxySave(queue_to_save)
    proxy_save.start()
    proxy_c_p = ProxyClearProduct(queue_to_clear)
    proxy_c_p.start()
    for i in range(2):
        proxy_clear = ProxyClear(queue_to_clear)
        proxy_clear.start()

