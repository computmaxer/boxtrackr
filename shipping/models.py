from google.appengine.ext import db

from base import models as base_models


class Package(db.Model, base_models.Timestamped):
    name = db.StringProperty()                   # Name this package
    tracking_number = db.StringProperty()        # Tracking number on the shipment
    site = db.StringProperty()                   # Website/store purchased from
    description = db.StringProperty()            # A field for describing the package
