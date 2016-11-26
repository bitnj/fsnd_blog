# Defines the Google App Engine Datastore Entity "Post", which stores the data
# relevent to to an individual Post such as the Author, Subject, Content
# Author: Neil Seas (2016)


# system packages
import os

# packages for Google App Engine
from google.appengine.ext import db
import jinja2


# User defined packages
from models import user


# call os.path.dirname twice because templates is up one directory
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    t = JINJA_ENV.get_template(template)
    return t.render(params)


class Post(db.Model):
    """defines Post Kind in GAE datastore"""
    user = db.ReferenceProperty(user.User, collection_name='posts')
    author = db.StringProperty(required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    likes = db.IntegerProperty(default=0)

    def render(self):
        """replaces plain text line breaks with proper HTML breaks"""
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", post=self)
