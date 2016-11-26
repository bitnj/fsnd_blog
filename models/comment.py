# Defines the Google App Engine Datastore Entity "Comment", which establishes a
# one-to-many relationship between Comments and a Post
# Author: Neil Seas (2016)

# packages for Google App Engine
from google.appengine.ext import db

# User defined packages
from models import post


class Comment(db.Model):
    post = db.ReferenceProperty(post.Post, collection_name='comments')
    commenterKey = db.StringProperty()
    author = db.StringProperty()
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
