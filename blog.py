# system libraries
import os
import re
import time

# libraries for google app engine
import webapp2
import jinja2
from google.appengine.ext import db

# libraries used for storing user names and passwords
import hashlib
import hmac
import random
from string import letters

SECRET = 'foo'

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

# functions for validating cookies and encryption
def make_secure_val(unsecure_val):
    return '%s|%s' % (unsecure_val, hmac.new(SECRET, unsecure_val).hexdigest())

def check_secure_val(hash_val):
    val = hash_val.split('|')[0]
    if hash_val == make_secure_val(val):
        return val

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = cls.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return cls(parent = users_key(), name = name, pw_hash = pw_hash, email
                = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

def render_str(template, **params):
        t = JINJA_ENV.get_template(template)
        return t.render(params)

class BlogHandler(webapp2.RequestHandler):
    """helper functions to shorten request calls"""
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user # gets user into Base.html for logout text
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, unsecure_val):
        cookie_val = make_secure_val(unsecure_val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/'
                    % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        """shorthand for return cookie_val if cookie_val exists and
        check_secure_val exists (i.e. doesn't return None""" 
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

class MainPageHandler(BlogHandler):
    def get(self):
        self.write('Blog Welcome Page')

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    """defines Post Kind in GAE datastore"""
    user = db.ReferenceProperty(User, collection_name='posts')
    author = db.StringProperty(required = True)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    likes = db.IntegerProperty(default=0)

    def render(self):
        """replaces plain text line breaks with proper HTML breaks"""
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", post = self)

class Liker(db.Model):
    post = db.ReferenceProperty(Post, collection_name='likers')
    likerKey = db.StringProperty()

class BlogFrontHandler(BlogHandler):
    def get(self):
        """get the top 10 most recent blog posts"""
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created LIMIT 10")
        self.render("front.html", posts=posts)

class NewPostHandler(BlogHandler):
    def get(self):
        if self.user:
            self.render("post-form.html")
        else:
            self.redirect("/login")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        # if both the subject and content fields have data forward to a
        # permalink
        if subject and content:
            p = Post(user=self.user, author=self.user.name, subject=subject, content=content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "both subject and content are required"
            self.render("post-form.html", subject=subject, content=content,
                    error=error)
            
class PermaLinkHandler(BlogHandler):
    def get(self, postID):
        post = Post.get_by_id(int(postID))
        
        if not post:
            self.error(404)
            return
        
        self.render("permalink.html", post=post)

class EditPostHandler(BlogHandler, db.Model):
    def get(self, postKey):
        q = Post.all()       
        post = q.filter('__key__', db.Key(postKey)).get()
        
        self.render("edit-post.html", subject=post.subject, content=post.content)
    
    def post(self, postKey):
        subject = self.request.get("subject")
        content = self.request.get("content")

        # if both the subject and content fields have data forward to a
        # permalink
        if subject and content:
            q = Post.all()       
            post = q.filter('__key__', db.Key(postKey)).get()
            
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = "both subject and content are required"
            self.render("post-form.html", subject=subject, content=content,
                    error=error)
            
class DeletePostHandler(BlogHandler, db.Model):
    def get(self, postKey):
        db.delete(db.Key(postKey))
        time.sleep(1)
        self.redirect('/blog')

class LikePostHandler(BlogHandler, db.Model):
    def get(self, postKey):
        q = Post.all()       
        post = q.filter('__key__', db.Key(postKey)).get()
       
        # make sure this user hasn't already liked this post
        already_liked = False
        for liker in post.likers:
            if liker.likerKey == str(self.user.key()):
                already_liked = True

        if not already_liked:
            Liker(post=post, likerKey=str(self.user.key())).put()
            post.likes += 1
            post.put()
            time.sleep(1)

        self.redirect('/blog')

# set up regex for sign-up form fields
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

def valid_username(username):
    return USER_RE.match(username)

def valid_password(password):
    return PWORD_RE.match(password)

def valid_email(email):
    return not email or EMAIL_RE.match(email)

class SignupHandler(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        
        params = dict(username = username, email = email)

        # validate the user input against our regex
        any_error = False
        
        if not valid_username(username):
            params['error_username'] = "Invalid username."
            any_error = True

        if not valid_password(password):
            params['error_password'] = "Invalid password."
            any_error = True
        elif password != verify:
            params['error_verify'] = "Passwords do not match!"
            any_error = True

        if email and not valid_email(email):
            params['error_email'] = "Email address is not valid."
            any_error = True

        # check to see if this user name is already taken
        u = User.by_name(username)
        if u:
            params['error_username'] = "Username already exists."
            any_error = True
        
        if any_error:
            self.render("signup-form.html", **params)
        else:
            u = User.register(username, password, email)
            u.put()
            
            self.login(u)
            self.redirect('/welcome')

class LoginHandler(BlogHandler):
    def get(self):
        self.render("login-form.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/welcome')
        else:
            msg = "Invalid Login"
            self.render('login-form.html', error = msg)
            
class LogoutHandler(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/signup')

class WelcomeHandler(BlogHandler):
    def get(self):
        if self.user:
            self.render("welcome.html", username = self.user.name)
        else:
            self.redirect('/signup')

app = webapp2.WSGIApplication([('/', MainPageHandler),
    ('/signup', SignupHandler),
    ('/welcome', WelcomeHandler),
    ('/blog/?', BlogFrontHandler),
    ('/blog/newpost', NewPostHandler), 
    ('/blog/(\d+)', PermaLinkHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/editpost/([a-zA-Z0-9_-]+)', EditPostHandler),
    ('/deletepost/([a-zA-Z0-9_-]+)', DeletePostHandler),
    ('/likepost/([a-zA-Z0-9_-]+)', LikePostHandler)], 
    debug=True)
