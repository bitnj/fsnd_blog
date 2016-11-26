# Defines the handler for validating user input to the sign-up form

# Author: Neil Seas (2016)

import re
from handlers import bloghandler
from models import user

# helper functions to the signup handler to check for valid user input

def valid_username(username):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return USER_RE.match(username)


def valid_password(password):
    PWORD_RE = re.compile(r"^.{3,20}$")
    return PWORD_RE.match(password)


def valid_email(email):
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
    return not email or EMAIL_RE.match(email)


class SignupHandler(bloghandler.BlogHandler):

    def get(self):
        self.render("signup-form.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        params = dict(username=username, email=email)

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
        u = user.User.by_name(username)
        if u:
            params['error_username'] = "Username already exists."
            any_error = True

        if any_error:
            self.render("signup-form.html", **params)
        else:
            u = user.User.register(username, password, email)
            u.put()

            self.login(u)
            self.redirect('/welcome')
