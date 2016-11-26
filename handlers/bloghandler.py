# This is the main handler class that establishes the core functionality needed
# to render pages.  It was built by the instructor for the Udacity Full Stack
# Nanodegree program and several of the functions are conveniences to shorten
# some of the request syntax (e.g. write replaces self.response.out.write)

# system packages
import os

# packages for google app engine
import webapp2
import jinja2

# user defined packages
from models import *

# call os.path.dirname twice because templates is up one directory
template_dir = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)),
    'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    t = JINJA_ENV.get_template(template)
    return t.render(params)


class BlogHandler(webapp2.RequestHandler):
    """helper functions to shorten request calls"""

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user  # gets user into Base.html for logout text
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, unsecure_val):
        cookie_val = user.make_secure_val(unsecure_val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/'
                                         % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        """shorthand for return cookie_val if cookie_val exists and
        check_secure_val exists (i.e. doesn't return None"""
        return cookie_val and user.check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and user.User.by_id(int(uid))
