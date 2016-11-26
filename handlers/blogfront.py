# This is the handler for '/welcome', '/', and '/blog/?' requests.

# Neil Seas (2016)


from handlers import bloghandler
from google.appengine.ext import db


FRONT_TEMPLATE = "front.html"
SIGNUP_REDIRECT = '/signup'
WELCOME_TEMPLATE = 'welcome.html'


class BlogFrontHandler(bloghandler.BlogHandler):
    
    def get(self):
        """get the top 10 most recent blog posts"""
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created LIMIT 10")
        self.render(FRONT_TEMPLATE, posts=posts)

    
class MainPageHandler(bloghandler.BlogHandler):

    def get(self):
        self.redirect(SIGNUP_REDIRECT)

    
class WelcomeHandler(bloghandler.BlogHandler):

    def get(self):
        if self.user:
            self.render(WELCOME_TEMPLATE, username=self.user.name)
        else:
            self.redirect(SIGNUP_REDIRECT)

