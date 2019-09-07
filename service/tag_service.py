# -*- coding:utf-8 -*-
import sys
import time
from tornado import gen
from lib.db import *

reload(sys)
sys.setdefaultencoding('utf-8')


@gen.coroutine
def tag_create(name):
    col = get_col_tag_tag()
    doc = yield motordb.mongo_find_one(col, {'_id': name})
    if doc:
        raise gen.Return({'ret': -1, 'data': {'msg': 'tag already exists'}})
    ts_now = int(time.time())
    ret = yield motordb.mongo_insert_one(col, {'_id': name, 'ct': ts_now})
    if not ret:
        raise gen.Return({'ret': -1, 'data': {'msg': 'tag:%s create failed' % name}})
    raise gen.Return({'ret': 1})


@gen.coroutine
def tag_del(name):
    col = get_col_tag_tag()
    doc = yield motordb.mongo_find_one(col, {'_id': name})
    if doc is False:
        raise gen.Return({'ret': -1, 'data': {'msg': 'service db error'}})
    if not doc:
        raise gen.Return({'ret': -1, 'data': {'msg': 'tag not exists'}})

    col_chat_room = get_col_tag_chatroom()
    ret = yield motordb.mongo_update_many(col_chat_room, {'tag': name}, {'$unset': {'tag': 1}})
    if not ret:
        raise gen.Return({'ret': -1, 'data': {'msg': 'tag:%s delete chatroom failed' % name}})

    ret = yield motordb.mongo_delete_one(col, {'_id': name})
    if not ret:
        raise gen.Return({'ret': -1, 'data': {'msg': 'tag:%s delete failed' % name}})

    raise gen.Return({'ret': 1})


@gen.coroutine
def tag_list():
    col = get_col_tag_tag()
    docs = yield motordb.mongo_find(col, {})
    if docs is False:
        raise gen.Return({'ret': -1, 'data': {'msg': 'service db error'}})
    if not docs:
        docs = []
    col_chat_room = get_col_tag_chatroom()
    docs_chatroom = yield motordb.mongo_find(col_chat_room, {'tag': {'$exists': False}})
    if not docs_chatroom:
        docs_chatroom = []
    raise gen.Return({'ret': 1, 'data': {'tag_list': docs, 'chatroom_list': docs_chatroom}})


@gen.coroutine
def chatroom_list(tag):
    col_chat_room = get_col_tag_chatroom()
    docs_chatroom = yield motordb.mongo_find(col_chat_room, {'tag': tag})
    if not docs_chatroom:
        docs_chatroom = []
    raise gen.Return({'ret': 1, 'data': {'chatroom_list': docs_chatroom}})


@gen.coroutine
def chatroom_bind_tag(chatroom_name, nick, tag):
    col_chat_room = get_col_tag_chatroom()
    doc = yield motordb.mongo_find_one(col_chat_room, {'chatroom_name': chatroom_name, 'nick': nick})
    if doc is False:
        raise gen.Return({'ret': -1, 'data': {'msg': 'chatroom_name:%s, nick:%s. db error' % (chatroom_name, nick)}})
    if not doc:
        raise gen.Return({'ret': -1, 'data': {'msg': 'chatroom_name:%s, nick:%s not exists' % (chatroom_name, nick)}})
    ts_now = int(time.time())
    ret = yield motordb.mongo_update_one(col_chat_room, {'chatroom_name': chatroom_name, 'nick': nick},
                                         {'$set': {'tag': tag, 'ut': ts_now}}, up=True)
    if not ret:
        raise gen.Return(
            {'ret': -1, 'data': {'msg': 'chatroom_name:%s, nick:%s tag:%s bind failed' % (chatroom_name, nick, tag)}})

    raise gen.Return({'ret': 1})


@gen.coroutine
def chatroom_unbind_tag(chatroom_name, nick, tag):
    col_chat_room = get_col_tag_chatroom()
    doc = yield motordb.mongo_find_one(col_chat_room, {'chatroom_name': chatroom_name, 'nick': nick})
    if doc is False:
        raise gen.Return({'ret': -1, 'data': {'msg': 'chatroom_name:%s, nick:%s. db error' % (chatroom_name, nick)}})
    if not doc:
        raise gen.Return({'ret': -1, 'data': {'msg': 'chatroom_name:%s, nick:%s not exists' % (chatroom_name, nick)}})

    ret = yield motordb.mongo_update_one(col_chat_room, {'chatroom_name': chatroom_name, 'nick': nick},
                                         {'$unset': {'tag': 1}})
    if not ret:
        raise gen.Return(
            {'ret': -1, 'data': {'msg': 'chatroom_name:%s, nick:%s tag:%s bind failed' % (chatroom_name, nick, tag)}})

    raise gen.Return({'ret': 1})


@gen.coroutine
def chatroom_send_msg(tag, title, content):
    col_chat_room = get_col_tag_chatroom()
    docs = yield motordb.mongo_find(col_chat_room, {'tag': tag})
    if docs is False:
        raise gen.Return({'ret': -1, 'data': {'msg': 'tag:%s, title:%s. db error' % (tag, title)}})
    if not docs:
        raise gen.Return({'ret': -1, 'data': {'msg': 'tag:%s not exists' % tag}})
    raise gen.Return({'ret': 1})
