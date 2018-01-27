# -*- coding: utf-8 -*-
"""
Created on Jan 28, 2018

@author: guxiwen
"""

from pyvirtualdisplay import Display
from selenium import webdriver
import time

display = Display(visible=0, size=(800,600))
display.start()
driver = webdriver.Chrome()
driver.get("http://www.xicidaili.com/nt/")
time.sleep(5)
page_source = driver.page_source
driver.quit()
display.stop()