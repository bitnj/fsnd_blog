# This handler can login and logout an existing user
# Author: Neil Seas (2016)

# User defined packages
from handlers import bloghandler
from models import user


LOGIN_REDIRECT = '/login'
WELCOME_REDIRECT = '/welcome'
TEMPLATE = 'login-form.html'


class LoginHandler(bloghandler.BlogHandler):

    def get(self):
        self.render(TEMPLATE)

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        u = user.User.login(username, password)
        if u:
            self.login(u)
            self.redirect(WELCOME_REDIRECT)
        else:
            msg = "Invalid Login"
            self.render(TEMPLATE, error=msg)


class LogoutHandler(bloghandler.BlogHandler):

    def get(self):
        self.logout()
        self.redirect(LOGIN_REDIRECT)
