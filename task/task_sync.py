# -*- coding:utf-8 -*-
import time, sys
from lib import log
from lib import mongo, db
import urllib2
import ujson

reload(sys)
sys.setdefaultencoding('utf8')

TASKS = list()
TASKS.append(('https://www.7234.cn/api/v1/category/21/page/1', '机器人测试'))
url_ela = 'https://www.7234.cn/api/v1/category/21/page/1'
for room_name in ['亦来云Elastos社区23群', '亦来云Elastos社区26群',
                  '亦来云Elastos社区25群', '亦来云Elastos社区28群', '亦来云elastos社区1群', '亦来云Elastos社区29群',
                  '亦来云Elastos社区5群', '亦来云の链世界节点社区']:
    TASKS.append((url_ela, room_name))


def get_linkworld_posts(url):
    try:
        resp = urllib2.urlopen(url).read()
        posts = ujson.loads(resp)
        return [posts[0]]
    except Exception as e:
        log.error("get_linkworld_tasks except:%s" % str(e))
    return []


def load_post_to_db(posts, room_name):
    col_task = db.get_col_task_sync()
    n_suc, n_fail = 0, 0
    for post in posts:
        pid = post['url'].strip() + room_name
        if mongo.mongo_find_one(col_task, {'_id': pid}):
            log.info("task _id:%s dup. pass" % pid)
            continue

        post['_id'] = pid
        post['cnt_send'] = 0
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
        task_str = ujson.dumps(task, ensure_ascii=False)
        log.info("start download task:%s" % task_str)
        url = task[0]
        room_name = task[1]
        posts = get_linkworld_posts(url)
        n_succ, n_fail = load_post_to_db(posts, room_name)
        log.info("download task done:%s. suc:%s, fail:%s" % (task_str, n_succ, n_fail))


while True:
    time.sleep(10)
    try:
        task_download()
    except Exception as e:
        log.error("sleep 60s. task_download except:%s" % str(e))
        time.sleep(60)
