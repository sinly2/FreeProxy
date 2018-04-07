# -*- coding: utf-8 -*-
"""
Created on Apr 7, 2018

@author: guxiwen
"""
from flask import Flask, request
import redis, sqlite3
app = Flask(__name__)
REDIS_POOL = None


@app.route("/getProxy")
def get_proxy():
    redis_conn = get_db("redis")
    sqlite_conn = get_db("sqlite")
    result = redis_conn.randomkey()
    ip = request.remote_addr
    sql = "insert into visit_log (ip,uri,create_time) values (%s,%s,%s)" % (ip, "/getProxy", "")
    sqlite_conn.execute(sql)
    sqlite_conn.commit()
    return result


def get_redis_conn():
    return redis.Redis(host="127.0.0.1", db=0)


def get_db(db_type):
    if db_type.upper() == "SQLITE":
        return sqlite3.connect("data.db")
    elif db_type.upper() == "REDIS":
        return redis.Redis(connection_pool=get_redis_pool())


def get_redis_pool():
    global REDIS_POOL
    if not REDIS_POOL:
        REDIS_POOL = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
    return REDIS_POOL


if __name__ == "__main__":
    app.run(host="127.0.0.1",port=50000,debug=True)