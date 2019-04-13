# -*- coding:utf-8 -*-
import sys
import base64, time
from lib.ItChat import itchat
from lib import log
from lib import mongo, db
from service import wechat_service


def robot_processor(param):
    _id = param['_id']
    weChatInstance = itchat.new_instance()
    weChatInstance.get_chatrooms()
    chat_room_list = []
    msg_send = 0
    def qr_callback(uuid, status, qrcode):
        log.info("qr_callback for _id:%s" % _id)
        col_account = db.get_col_wechat_account_sync()
        doc = mongo.mongo_find_one(col_account, {'_id': _id})
        if not doc:
            log.error("qr_callback@check record _id:%s failed" % _id)
            return
        if doc['status'] != wechat_service.WECHAT_ACCOUNT_STATUS_WAIT_GEN_QR:
            log.warn("qr_already exists, no need update, _id:%s" % _id)
            return

        datab64 = base64.b64encode(qrcode)
        ts_now = int(time.time())
        ret = mongo.mongo_update_one(col_account, {'_id': _id, 'status': wechat_service.WECHAT_ACCOUNT_STATUS_WAIT_GEN_QR},
                                     {'$set': {'qrcode': datab64, 'ut': ts_now,
                                               'status': wechat_service.WECHAT_ACCOUNT_STATUS_WAIT_SCAN}})
        if not ret:
            log.error("qr_callback@update _id:%s data failed" % _id)
        log.info("qr_callback@update _id:%s data succeed" % _id)

    def login_process(_id):
        global chat_room_list
        weChatInstance.auto_login(qrCallback=qr_callback)
        log.info("login for _id:%s complete" % _id)
        col_account = db.get_col_wechat_account_sync()
        doc = mongo.mongo_find_one(col_account, {'_id': _id})
        if not doc:
            log.error("login process for _id:%s doc check failed, now logout" % _id)
            weChatInstance.logout()

        ret = mongo.mongo_update_one(col_account, {'_id': _id},
                                     {'$set': {'status': wechat_service.WECHAT_ACCOUNT_STATUS_LOGIN_DONE}})
        if not ret:
            log.error("login process for update done status failed: %s, now logout" % _id)
            weChatInstance.logout()
        chat_room_list = weChatInstance.get_chatrooms(update=True)

    def log_out(_id):
        weChatInstance.logout()
        log.info("user logout done, now update db status")
        col_account = db.get_col_wechat_account_sync()
        ret = mongo.mongo_update_one(col_account, {'_id': _id},
                                     {'$set': {'status': wechat_service.WECHAT_ACCOUNT_STATUS_DONE_EXIT}})
        if not ret:
            log.error("log_out update db status failed")

    def get_chat_room(name):
        for e in chat_room_list:
            if e['NickName'] == name:
                return e
        return None

    def work():
        global msg_send
        chat_room_name = '机器人测试'
        if not msg_send:
            log.info("robot send msg now")
            chat_room = get_chat_room(chat_room_name)
            chat_room.send_msg("hi, i'm robot")
        else:
            log.info("robot will not send msg")
        n_rooms = len(chat_room_list)
        msg_send = 1
        log.info("task idle, try one work, n_rooms:%s" % n_rooms)
        return

    while True:
        time.sleep(0.5)
        col_account = db.get_col_wechat_account_sync()
        doc = mongo.mongo_find_one(col_account, {'_id': _id})
        if not doc:
            log.error("check _id:%s doc check failed, now exit" % _id)
            sys.exit(0)
        status = doc['status']

        if status == wechat_service.WECHAT_ACCOUNT_STATUS_WAIT_GEN_QR:
            login_process(_id)
        elif status == wechat_service.WECHAT_ACCOUNT_STATUS_WAIT_EXIT:
            log_out(_id)
            sys.exit(0)
        elif status == wechat_service.WECHAT_ACCOUNT_STATUS_LOGIN_DONE:
            work()
