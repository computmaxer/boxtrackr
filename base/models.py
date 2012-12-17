from google.appengine.ext import db


class ModelMixin(object):
    """
    Base class used to create mix-in classes for L{db.Model} classes.
    """

    __metaclass__ = db.PropertiedClass

    @classmethod
    def kind(self):
        """
        Need to implement this because it is called by PropertiedClass
        to register the kind name in _kind_map. We just return a dummy name.
        """
        return '__model_mixin__'


class Timestamped(ModelMixin):
    create_date = db.DateTimeProperty(auto_now_add=True, indexed=True)
    modified_date = db.DateTimeProperty(auto_now=True, indexed=False)
