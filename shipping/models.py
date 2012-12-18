from google.appengine.ext import db

from base import models as base_models
from auth import models as auth_models

import datetime


class Package(db.Model, base_models.Timestamped):
    name = db.StringProperty()                   # Name this package
    tracking_number = db.StringProperty()        # Tracking number on the shipment
    site = db.StringProperty()                   # Website/store purchased from
    description = db.StringProperty()            # A field for describing the package

    owner = db.ReferenceProperty(auth_models.WTUser)

    #Info for caching information from UPS/USPS/FedEx
    last_checked = db.DateTimeProperty()
    estimated_arrival = db.DateTimeProperty()
    status = db.IntegerProperty()

    #Possible example of a get helper
    def get_estimated_arrival(self):
        time_diff = datetime.datetime.now() - datetime.timedelta(minutes=30)
        if self.last_checked < time_diff:
            #CALL SHIPPING API
            pass
        else:
            return self.estimated_arrival
