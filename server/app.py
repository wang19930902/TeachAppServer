import os

from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.options import define
from tornado.options import options
from tornado.web import Application
from tornado.web import RequestHandler
from tornado.web import StaticFileHandler
from tornado_sqlalchemy import SessionMixin
from tornado_sqlalchemy import make_session_factory

from server.fake import insert_fake_data
from server.handlers.admin import admin_handers
from server.handlers.api import api_handers
from server.models import DeclarativeBase

define("database_url",
       default="mysql+pymysql://root:aaaaaa@localhost/my_db?charset=utf8",
       help="Main user DB")

define("enable_fake_data",
       type=bool,
       default=False,
       help="enable fake data")

static_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), "static")
web_app_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), "app")

class IndexHandler(RequestHandler, SessionMixin):
    @coroutine
    def get(self):
        self.redirect("/app/index.html")


def make_app():
    session_factory = make_session_factory(options.database_url)
    DeclarativeBase.metadata.create_all(session_factory.engine)
    if options.enable_fake_data:
        insert_fake_data(session_factory)

    handlers = [
        (r'/', IndexHandler),
        (r"/static/(.*)", StaticFileHandler, {"path": static_path}),
        (r"/app/(.*)", StaticFileHandler, {"path": web_app_path}),
        (r"/(config\.xml)", StaticFileHandler, {"path": web_app_path}),
    ]
    handlers.extend(api_handers)
    handlers.extend(admin_handers)
    return Application(
        handlers,
        session_factory=session_factory,
        static_path=static_path,
        cookie_secret="61oETzKXQAGaYdghdhgfhfhfg",
    )


if __name__ == '__main__':
    options.parse_config_file("server.ini", final=False)
    options.parse_command_line()

    make_app().listen(8888)

    IOLoop.current().start()
