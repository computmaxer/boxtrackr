from google.appengine.ext import db

from base import models as base_models
from auth import models as auth_models

from shipping import api as shapi

import datetime
import logging


class Package(db.Model, base_models.Timestamped):
    name = db.StringProperty()                   # Name this package
    tracking_number = db.StringProperty()        # Tracking number on the shipment
    carrier = db.StringProperty()                # Shipping carrier. Determined by us or by user
    site = db.StringProperty()                   # Website/store purchased from
    description = db.StringProperty()            # A field for describing the package

    owner = db.ReferenceProperty(auth_models.WTUser)

    #Info for caching information from UPS/USPS/FedEx
    last_checked = db.DateTimeProperty()
    estimated_arrival = db.DateTimeProperty()
    status = db.IntegerProperty()

    UPDATE_INTERVAL_MINUTES = 30

    def get_estimated_arrival(self):
        if self.last_checked and self.estimated_arrival:
            if self.last_checked < self.api_update_time:
                self.update_values_from_api()
            return self.estimated_arrival.strftime("%x")

    def get_last_checked(self):
        if self.last_checked:
            return self.last_checked.strftime("%m/%d/%y %H:%M:%S")

    def get_status(self):
        if not self.last_checked or self.last_checked < self.api_update_time:
            self.update_values_from_api()
        return self.status

    def get_status_text(self):
        status = self.get_status()
        return shapi.STATUS_DICT.get(status, "An error has occured")

    def update_values_from_api(self):
        if not self.carrier:
            self.carrier = shapi.determine_carrier(self.tracking_number)
        shipments = shapi.query_tracking(self.tracking_number, self.carrier)
        if shipments:
            #TODO: Currently only supporting one package/shipment being returned from api.
            packages = shipments[0]
            if packages:
                pkg = packages[0]
                self.status = pkg.get('status')
                self.estimated_arrival = pkg.get('eta')
                self.last_checked = datetime.datetime.now()
                self.put()
                return True
        logging.error("An error occured while retrieving fresh values from the shipping API")
        return False

    @property
    def api_update_time(self):
        return datetime.datetime.now() - datetime.timedelta(minutes=self.UPDATE_INTERVAL_MINUTES)
