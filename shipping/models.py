from google.appengine.ext import db

from base import models as base_models
from auth import models as auth_models

from shipping import api as shapi

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

    #Possible example of a get helper TODO: Finish this.
    def get_estimated_arrival(self):
        if self.last_checked < self.api_update_time:
            #CALL SHIPPING API
            pass
        else:
            return self.estimated_arrival

    def get_status(self):
        if self.last_checked < self.api_update_time:
            self.update_values_from_api()
        return self.status

    def update_values_from_api(self):
        shipments = shapi.query_tracking(self.tracking_number)
        if shipments:
            #TODO: Currently only supporting one package/shipment being returned from api.
            packages = shipments[0]
            if packages:
                pkg = packages[0]
                self.status = pkg['status']
#                self.estimated_arrival =  # TODO: Figure this out
                self.last_checked = datetime.datetime.now()
                self.put()
                return True
        return False

    @property
    def api_update_time(self):
        return datetime.datetime.now() - datetime.timedelta(minutes=30)