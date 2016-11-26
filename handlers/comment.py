# This handler is for comment related requests.  It handles creating, editing,
# and deleting comments.  Any user can comment on any post, but only the author
# of a particular post can edit or delete it.

# Author: Neil Seas (2016)


import time
from handlers import bloghandler
from models import post
from models import comment
from google.appengine.ext import db


BLOG_REDIRECT = '/blog'
LOGIN_REDIRECT = '/login'
COMMENT_TEMPLATE = 'comment-form.html'
EDIT_TEMPLATE = 'edit-comment.html'


class CommentHandler(bloghandler.BlogHandler, db.Model):

    def get(self, postKey):
        if self.user:
            self.render(COMMENT_TEMPLATE)
        else:
            self.redirect(LOGIN_REDIRECT)

    def post(self, postKey):
        if self.user:
            newcomment = self.request.get("comment")

            q = post.Post.all()
            newpost = q.filter('__key__', db.Key(postKey)).get()

            comment.Comment(
                post=newpost,
                author=self.user.name,
                commenterKey=str(
                    self.user.key()),
                content=newcomment).put()
            newpost.put()
            time.sleep(1)

            self.redirect(BLOG_REDIRECT)
        else:
            self.redirect(LOGIN_REDIRECT)


class EditCommentHandler(bloghandler.BlogHandler, db.Model):

    def get(self, commentKey):
        if self.user:
            q = comment.Comment.all()
            newcomment = q.filter('__key__', db.Key(commentKey)).get()

            # users can only edit comments they created
            if self.user.name == newcomment.author:
                self.render(EDIT_TEMPLATE, content=newcomment.content)
            else:
                self.redirect(BLOG_REDIRECT)
        else:
            self.redirect(LOGIN_REDIRECT)

    def post(self, commentKey):
        if self.user:
            content = self.request.get("comment")
            q = comment.Comment.all()
            newcomment = q.filter('__key__', db.Key(commentKey)).get()

            # user can only edit comments they created
            if self.user.name == newcomment.author:
                newcomment.content = content
                newcomment.put()
                time.sleep(1)
            self.redirect(BLOG_REDIRECT)
        else:
            self.redirect(LOGIN_REDIRECT)


class DeleteCommentHandler(bloghandler.BlogHandler, db.Model):

    def get(self, commentKey):
        if self.user:
            q = comment.Comment.all()
            newcomment = q.filter('__key__', db.Key(commentKey)).get()

            # users can only delete comments they created
            if self.user.name == newcomment.author:
                db.delete(db.Key(commentKey))
                time.sleep(1)

            self.redirect(BLOG_REDIRECT)
        else:
            self.redirect(LOGIN_REDIRECT)
