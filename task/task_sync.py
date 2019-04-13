# -*- coding:utf-8 -*-
import sys
import base64, time
from lib.ItChat import itchat
from lib import log
from lib import mongo, db
from service import wechat_service
import random
import urllib2
import ujson

URL_LINK_WORL = 'https://www.7234.cn/api/v1/category/1/page/10'


def get_linkworld_tasks():
    try:
        resp = urllib2.urlopen(URL_LINK_WORL).read()
        jv = ujson.loads(resp)
        return jv
    except Exception as e:
        log.error("get_linkworld_tasks except:%s" % str(e))
    return []


while True:
    time.sleep(10)
    tasks = get_linkworld_tasks()
    col_task = db.get_col_task_sync()
    for task in tasks:
        task_id = task['url'].strip()
        if mongo.mongo_find_one(col_task, {'_id': task_id}):
            continue
        task['_id'] = task_id
        ret = mongo.mongo_insert(col_task, task)
        if ret:
            log.info("one task added, task_id:%s" % task_id)
        else:
            log.error("add task failed for task_id:%s" % task_id)
