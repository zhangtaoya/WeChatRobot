#!/usr/bin/env python
# coding:utf-8

import os.path
import tornado.web
import sys
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options

from handler.index_handler import *
from handler.tag_handler import *


tornado.options.define("port", default=8000, help="run on the given port", type=int)

reload(sys)
sys.setdefaultencoding('utf8')
url = 'https://www.7234.cn/api/v1/category/1/page/10'

handlers = [
    (r"/", IndexHandler),
    (r"/lsj", LSJHandler),
    (r"/wechat_login", WechatLoginHandler),
    (r"/robot_tag/create", TagCreateHandler),
    (r"/robot_tag/del", TagDelHandler),
    (r"/robot_tag/tag_list", TagListHandler),
    (r"/robot_tag/chatroom_list", ChatroomListHandler),
    (r"/robot_tag/bind", TagBindHandler),
    (r"/robot_tag/unbind", TagUnBindHandler),
    (r"/robot_tag/send_msg", TagUnSendMsgHandler),
]

template_path = os.path.join(os.path.dirname(__file__),"template")

if __name__ == "__main__":
    options.parse_command_line()
    app = tornado.web.Application(handlers, template_path)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
