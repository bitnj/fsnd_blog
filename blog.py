# This module simply sets up the mapping from request to request handler.  All
# handlers are contained in the handlers package directory.

# Author: Neil Seas (2016)

import webapp2
from handlers import *

app = webapp2.WSGIApplication([('/', blogfront.MainPageHandler),
                               ('/signup', signup.SignupHandler),
                               ('/welcome', blogfront.WelcomeHandler),
                               ('/blog/?', blogfront.BlogFrontHandler),
                               ('/blog/newpost', post.NewPostHandler),
                               ('/blog/(\d+)', post.PermaLinkHandler),
                               ('/login', userauth.LoginHandler),
                               ('/logout', userauth.LogoutHandler),
                               ('/editpost/([a-zA-Z0-9_-]+)', post.EditPostHandler),
                               ('/deletepost/([a-zA-Z0-9_-]+)', post.DeletePostHandler),
                               ('/likepost/([a-zA-Z0-9_-]+)', post.LikePostHandler),
                               ('/comment/([a-zA-Z0-9_-]+)', comment.CommentHandler),
                               ('/editcomment/([a-zA-Z0-9_-]+)', comment.EditCommentHandler),
                               ('/deletecomment/([a-zA-Z0-9_-]+)',
                                   comment.DeleteCommentHandler)],
                              debug=True)
