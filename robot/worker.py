# -*- coding:utf-8 -*-
import sys, os, ujson
import base64, time
from lib.ItChat import itchat
from lib import log
from lib import mongo, db
from service import wechat_service
import random

reload(sys)
sys.setdefaultencoding('utf8')

msg_send = 0


def robot_processor(param):
    chat_room_list = []
    _id = param['_id']
    weChatInstance = itchat.new_instance()
    weChatInstance.get_chatrooms()
    def qr_callback(uuid, status, qrcode):
        log.info("qr_callback for _id:%s" % _id)
        col_account = db.get_col_wechat_account_sync()
        doc = mongo.mongo_find_one(col_account, {'_id': _id})
        if not doc:
            log.error("qr_callback@check record _id:%s failed" % _id)
            return
        if doc['status'] != wechat_service.WECHAT_ACCOUNT_STATUS_WAIT_GEN_QR:
            log.warn("qr_already exists, but refresh it, _id:%s" % _id)

        datab64 = base64.b64encode(qrcode)
        ts_now = int(time.time())
        ret = mongo.mongo_update_one(col_account, {'_id': _id, 'status': wechat_service.WECHAT_ACCOUNT_STATUS_WAIT_GEN_QR},
                                     {'$set': {'qrcode': datab64, 'ut': ts_now,
                                               'status': wechat_service.WECHAT_ACCOUNT_STATUS_WAIT_SCAN,
                                               'uuid_wechat': uuid}})
        if not ret:
            log.error("qr_callback@update _id:%s data failed" % _id)
        log.info("qr_callback@update _id:%s data succeed" % _id)


    def login_process(_id):
        global chat_room_list
        weChatInstance.auto_login(qrCallback=qr_callback, exitCallback=log_out)
        log.info("login for _id:%s complete" % _id)
        col_account = db.get_col_wechat_account_sync()
        doc = mongo.mongo_find_one(col_account, {'_id': _id})
        if not doc:
            log.error("login process for _id:%s doc check failed, now logout" % _id)
            weChatInstance.logout()

        nickName = weChatInstance.storageClass.nickName
        ret = mongo.mongo_update_one(col_account, {'_id': _id},
                                     {'$set': {'status': wechat_service.WECHAT_ACCOUNT_STATUS_LOGIN_DONE,
                                               'nickName': nickName}})
        if not ret:
            log.error("login process for update done status failed: %s, now logout" % _id)
            weChatInstance.logout()
        chat_room_list = weChatInstance.get_chatrooms(update=True)
        log.info("chat-room-count: %s" % len(chat_room_list))
        for ch in chat_room_list:
            log.info("account_name:%s chat-room: %s" % (nickName, ujson.dumps(ch, ensure_ascii=False)))

    def log_out():
        # weChatInstance.logout()
        log.info("user logout done, now update db status")
        col_account = db.get_col_wechat_account_sync()
        ret = mongo.mongo_update_one(col_account, {'_id': _id},
                                     {'$set': {'status': wechat_service.WECHAT_ACCOUNT_STATUS_DONE_EXIT}})
        if not ret:
            log.error("log_out update db status failed")
        log.info("process with _id:%s exit now" % _id)
        os._exit(0)

    def get_chat_room(name):
        global chat_room_list
        for e in chat_room_list:
            nick_name = e['NickName']
            if nick_name == name:
                return e
        return None

    def send_task():
        col_account = db.get_col_wechat_account_sync()
        account = mongo.mongo_find_one(col_account, {"_id": _id})
        if not account:
            log.error("account not found for _id:%s" % _id)
            return

        ut = account['ut']
        ts_now = int(time.time())
        if ts_now < ut + random.randint(5, 10):
            log.info("ts_now:%s in 60 seconds of ut:%s, should not send_msg, return" % (ts_now, ut))
            return

        col_task = db.get_col_task_sync()
        task = mongo.mongo_find_and_modify(col_task,
                                           {'cnt_send': 0,
                                            "ut": {'$lt': ts_now - 10},
                                            "ct": {'$gt': ts_now - 3600 * 12}},
                                           {'$inc': {'cnt_send': 1},
                                            '$set': {"ut": ts_now}},
                                           upsert=False)
        if not task:
            log.info("no tasks, return")
            return

        task_id = task['_id']
        title = task['title']
        url = task['url']
        msg = "%s\n%s" % (title, url)
        # chat_room_name = '机器人测试'
        chat_room_name = task.get('chat_room_name', '机器人测试')
        chat_room = get_chat_room(chat_room_name)
        if not chat_room:
            log.error("nickName:%s. chat_room:%s not found" % (account.get('nickName'), chat_room_name))
            # reset back task cnt_send
            mongo.mongo_update_one(col_task, {'_id': task_id}, {'$inc': {'cnt_send': -1}})
            return

        ret = mongo.mongo_update_one(col_account, {'_id': _id}, {'$set': {'ut': ts_now}})
        if not ret:
            log.error("send_task, update _id:%s ut failed, return" % _id)
            mongo.mongo_update_one(col_task, {'_id': task_id}, {'$inc': {'cnt_send': -1}})
            return

        chat_room.send_msg(msg)
        log.info("_id:%s, send msg:%s" % (_id, msg))

    def work():
        global msg_send
        chat_room_name = '机器人测试'
        if not msg_send:
            log.info("robot try send msg now")
            n = random.randint(0, 100)
            if n == 0:
                chat_room = get_chat_room(chat_room_name)
                chat_room.send_msg("hi, i'm robot, random send msg")
            else:
                log.info("random num:%s != 0, will not send msg" % n)
        else:
            log.info("robot will not send msg")
        n_rooms = len(chat_room_list)
        # msg_send = 1
        log.info("task idle, try one work, n_rooms:%s" % n_rooms)
        return

    while True:
        time.sleep(0.5)
        col_account = db.get_col_wechat_account_sync()
        doc = mongo.mongo_find_one(col_account, {'_id': _id})
        if not doc:
            log.error("check _id:%s doc check failed, now exit" % _id)
            os._exit(0)

        status = doc['status']
        if status in [wechat_service.WECHAT_ACCOUNT_STATUS_INIT,
                      wechat_service.WECHAT_ACCOUNT_STATUS_WAIT_GEN_QR,
                      wechat_service.WECHAT_ACCOUNT_STATUS_WAIT_SCAN]:
            ct = doc['ct']
            ts_now = int(time.time())
            if ts_now > ct + 60 * 5:
                log.info("status:%s invalid. ts_now:%s already 300s after ct:%s. exit now" % (status, ts_now, ct))
                os._exit(0)
                return

        if status == wechat_service.WECHAT_ACCOUNT_STATUS_WAIT_GEN_QR:
            login_process(_id)
        elif status == wechat_service.WECHAT_ACCOUNT_STATUS_WAIT_EXIT:
            log_out()
        elif status == wechat_service.WECHAT_ACCOUNT_STATUS_LOGIN_DONE:
            # work()
            send_task()
