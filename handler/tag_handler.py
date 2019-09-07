#!/usr/bin/env python
# coding:utf-8
import base64
from tornado import gen
from service import tag_service as s
from base_handler import BaseHandler


class TagCreateHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        name = self.params.get('tag')
        if not name:
            self.jsonify({'ret': -1, 'data': {'msg': 'tag empty'}})
            return
        ret = yield s.tag_create(name)
        self.jsonify(ret)
        return


class TagDelHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        name = self.params.get('tag')
        if not name:
            self.jsonify({'ret': -1, 'data': {'msg': 'tag empty'}})
            return
        ret = yield s.tag_del(name)
        self.jsonify(ret)
        return


class TagListHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        ret = yield s.tag_list()
        self.jsonify(ret)
        return


class ChatroomListHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        tag = self.params.get('tag')
        ret = yield s.chatroom_list(tag)
        self.jsonify(ret)
        return


class TagBindHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        tag = self.params.get('tag')
        nick = self.params.get('nick')
        chatroom_name = self.params.get('chatroom_name')
        if not tag or not nick or not chatroom_name:
            self.jsonify({'ret': -1, 'data': {'msg': 'tag, nick or chatroom_name empty'}})
            return

        ret = yield s.chatroom_bind_tag(chatroom_name, nick, tag)
        self.jsonify(ret)
        return


class TagUnBindHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        tag = self.params.get('tag')
        nick = self.params.get('nick')
        chatroom_name = self.params.get('chatroom_name')
        if not tag or not nick or not chatroom_name:
            self.jsonify({'ret': -1, 'data': {'msg': 'tag, nick or chatroom_name empty'}})
            return

        ret = yield s.chatroom_unbind_tag(chatroom_name, nick, tag)
        self.jsonify(ret)
        return


class TagUnSendMsgHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        tag = self.params.get('tag')
        title = self.params.get('title')
        content = self.params.get('content')
        if not tag or not title or not content:
            self.jsonify({'ret': -1, 'data': {'msg': 'tag, title or content empty'}})
            return

        ret = yield s.chatroom_send_msg(tag, title, content)
        self.jsonify(ret)
        return
