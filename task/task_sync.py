# -*- coding:utf-8 -*-
import time, sys
from lib import log
from lib import mongo, db
import urllib2
import ujson

reload(sys)
sys.setdefaultencoding('utf8')
log.init_logger("task_sync")
TASKS = list()
url_ela = 'https://www.7234.cn/api/v1/category/21/page/1'
url_nuls = 'https://www.7234.cn/api/v1/category/24/page/1'
url_bottos = 'https://www.7234.cn/api/v1/category/22/page/1'

TASKS.append((url_ela, ["机器人测试"]))

rlist = []
for rid in range(1, 30):
    room_name = '亦来云Elastos社区%d群' % rid
    rlist.append(room_name)
TASKS.append((url_ela, rlist))

rlist = []
for rid in range(1, 100):
    room_name = "NULS中文社区%d群" % rid
    rlist.append(room_name)
TASKS.append((url_nuls, rlist))

rlist = []
for rid in range(1, 100):
    room_name = "铂链-人工智能第一公链%03d群" % rid
    rlist.append(room_name)
for rid in range(1, 10):
    room_name = "Bottos社区活动%d群" % rid
    rlist.append(room_name)
TASKS.append((url_bottos, rlist))


def get_linkworld_posts(url):
    try:
        resp = urllib2.urlopen(url).read()
        posts = ujson.loads(resp)
        return [posts[0]]
    except Exception as e:
        log.error("get_linkworld_tasks except:%s" % str(e))
    return []


def load_post_to_db(posts, rlist):
    col_task = db.get_col_task_sync()
    n_suc, n_fail = 0, 0
    for post in posts:
        for room_name in rlist:
            pid = str(post['url'].strip() + room_name.strip())
            if mongo.mongo_find_one(col_task, {'_id': pid}):
                log.info("task _id:%s dup. pass" % pid)
                continue

            ts_now = int(time.time())
            post['_id'] = pid
            post['cnt_send'] = 0
            post['ct'] = ts_now
            post['ut'] = ts_now
            post['chat_room_name'] = room_name
            ret = mongo.mongo_insert(col_task, post)
            if ret:
                n_suc += 1
                log.info("one task added, task_id:%s" % pid)
            else:
                n_fail += 1
                log.error("add task failed for task_id:%s" % pid)
    return n_suc, n_fail


def task_download():
    for task in TASKS:
        url = task[0]
        log.info("start download task:%s" % url)

        rlist = task[1]
        posts = get_linkworld_posts(url)
        n_succ, n_fail = load_post_to_db(posts, rlist)
        log.info("download task done:%s. suc:%s, fail:%s" % (url, n_succ, n_fail))


while True:
    time.sleep(10)
    try:
        task_download()
    except Exception as e:
        log.error("sleep 60s. task_download except:%s" % str(e))
        time.sleep(60)
