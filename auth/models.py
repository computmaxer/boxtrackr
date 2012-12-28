from google.appengine.ext import db

from auth import utils as auth_utils


class WTUser(db.Model):
    username = db.StringProperty()
    name = db.StringProperty()
    password = db.StringProperty()
    salt = db.StringProperty()
    method = db.StringProperty()
    email = db.EmailProperty()
    created = db.DateTimeProperty(auto_now=True)
    facebook_id = db.StringProperty()
    has_logged_in = db.BooleanProperty(default=True)

    def get_display_name(self):
        if self.name:
            return self.name

        if self.username:
            return self.username

        return self.email

    def get_id(self):
        return self.key().id()

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def update_password(self, new_password):
        hash, salt = auth_utils.encode_password(new_password)
        self.password = hash
        self.salt = salt
        self.put()
        return

    @classmethod
    def get_user_by_facebook_id(cls, facebook_id):
        return WTUser.all().filter('facebook_id =', facebook_id).get()

    @classmethod
    def get_user_by_email(cls, email):
        return WTUser.all().filter('email =', email).get()

    @classmethod
    def create_placeholder_user(cls, email, name=None):
        user = WTUser(email=email, name=name, has_logged_in=False)
        db.put(user)
        return user