# Defines the Google App Engine Datastore Entity "Liker", which establishes a
# one-to-many relationship between a Post and Liker
# Author: Neil Seas (2016)

# packages for Google App Engine
from google.appengine.ext import db

# User defined packages
from models import post


class Liker(db.Model):
    post = db.ReferenceProperty(post.Post, collection_name='likers')
    likerKey = db.StringProperty()
