from functools import wraps

from tornado.web import RequestHandler
from tornado_sqlalchemy import SessionMixin

from server.models import User


class BaseAPIHandler(SessionMixin, RequestHandler):
    user = None

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        "x-requested-with, Content-Type, token-id")
        self.set_header('Access-Control-Allow-Methods',
                        'POST, GET, OPTIONS, PUT, DELETE')

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def bad_request(self, msg):
        self.set_status(400)
        self.write({"error": msg})

    def get_current_user(self):
        token_id = self.request.headers.get('token-id')
        if not token_id:
            return None
        user = self.session.query(User).filter_by(token_id=token_id).first()
        if not user:
            return None
        return user

    def initialize(self):
        super(BaseAPIHandler, self).initialize()
        self._session = self._make_session()


def auth_require(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            self.set_status(401)
            self.write({"error": "Auth invalid!"})
            return
        return f(self, *args, **kwargs)
    return wrapper


def admin_require(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        user = self.current_user
        if not user or user.role != 'admin':
            self.set_status(401)
            self.write({"error": "Auth invalid!"})
            return
        return f(self, *args, **kwargs)
    return wrapper
