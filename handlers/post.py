# This module contains the handlers for all post related requests.  It handles
# creating, editing, deleting, and liking a post.  It makes sure that we have a
# logged in user.  If not, redirects to '/login'
# Author: Neil Seas (2016)


# system modules
import time

# modules for Google App Engine
from google.appengine.ext import db

# user defined modules
from handlers import bloghandler
from models import post
from models import liker

POST_TEMPLATE = 'post-form.html'
EDIT_TEMPLATE = 'edit-post.html'
PERMALINK_TEMPLATE = 'permalink.html'
LOGIN_REDIRECT = '/login'
BLOG_REDIRECT = '/blog'


class NewPostHandler(bloghandler.BlogHandler):

    def get(self):
        if self.user:
            self.render(POST_TEMPLATE)
        else:
            self.redirect(LOGIN_REDIRECT)

    def post(self):
        # make sure we have a logged in user by checking self.user
        if self.user:
            subject = self.request.get("subject")
            content = self.request.get("content")

            # if both the subject and content fields have data forward to a
            # permalink
            if subject and content:
                p = post.Post(
                    user=self.user,
                    author=self.user.name,
                    subject=subject,
                    content=content)
                p.put()
                self.redirect('/blog/%s' % str(p.key().id()))
            else:
                error = "both subject and content are required"
                self.render(POST_TEMPLATE, subject=subject, content=content,
                            error=error)
        else:
            self.redirect(LOGIN_REDIRECT)


class PermaLinkHandler(bloghandler.BlogHandler):

    def get(self, postID):
        newpost = post.Post.get_by_id(int(postID))

        if not post:
            self.error(404)
            return

        self.render(PERMALINK_TEMPLATE, post=newpost)


class EditPostHandler(bloghandler.BlogHandler, db.Model):

    def get(self, postKey):
        if self.user:
            q = post.Post.all()
            newpost = q.filter('__key__', db.Key(postKey)).get()
            self.render(
                EDIT_TEMPLATE,
                subject=newpost.subject,
                content=newpost.content)
        else:
            self.redirect(LOGIN_REDIRECT)

    def post(self, postKey):
        if self.user:
            subject = self.request.get("subject")
            content = self.request.get("content")

            # if both the subject and content fields have data forward to a
            # permalink
            if subject and content:
                q = post.Post.all()
                newpost = q.filter('__key__', db.Key(postKey)).get()

                # only the author of a post can edit it
                if self.user.key() == newpost.user.key():
                    newpost.subject = subject
                    newpost.content = content
                    newpost.put()
                    self.redirect('/blog/%s' % str(newpost.key().id()))
                else:
                    self.redirect(BLOG_REDIRECT)
            else:
                error = "both subject and content are required"
                self.render(POST_TEMPLATE, subject=subject, content=content,
                            error=error)
        else:
            self.redirect(LOGIN_REDIRECT)


class LikePostHandler(bloghandler.BlogHandler, db.Model):

    def get(self, postKey):
        if self.user:
            q = post.Post.all()
            newpost = q.filter('__key__', db.Key(postKey)).get()

            # make sure this user hasn't already liked this post
            already_liked = False
            for myliker in newpost.likers:
                if myliker.likerKey == str(self.user.key()):
                    already_liked = True

            if not already_liked and newpost.user.key() != self.user.key():
                liker.Liker(post=newpost, likerKey=str(self.user.key())).put()
                newpost.likes += 1
                newpost.put()
                time.sleep(1)

            self.redirect(BLOG_REDIRECT)
        else:
            self.redirect(LOGIN_REDIRECT)


class DeletePostHandler(bloghandler.BlogHandler, db.Model):

    def get(self, postKey):
        if self.user:
            q = post.Post.all()
            newpost = q.filter('__key__', db.Key(postKey)).get()
            if self.user.key() == newpost.user.key():
                db.delete(db.Key(postKey))
                time.sleep(1)
            self.redirect(BLOG_REDIRECT)
        else:
            self.redirect(LOGIN_REDIRECT)
