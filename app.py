# -*- coding: utf-8 -*-
"""
Created on Apr 7, 2018

@author: guxiwen
"""
from flask import Flask
import redis
app = Flask(__name__)


@app.route("/getProxy")
def get_proxy():
    redis_conn = get_redis_conn()
    result = redis_conn.randomkey()
    return result


def get_redis_conn():
    return redis.Redis(host="127.0.0.1", db=0)

if __name__ == "__main__":
    app.run(host="127.0.0.1",port=50000,debug=True)