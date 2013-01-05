import logging
import webapp2

import sys
import os

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
LIB_PATH = os.path.join(ROOT_PATH, 'lib')
sys.path.insert(0, LIB_PATH)

from webapp2_extras import jinja2

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app

from email.utils import parseaddr

from shipping import actions as shipping_actions

from mail import utils as mail_utils

from auth import models as auth_models

from base import mail as base_mail


class EmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.debug("Received a message from: %s" % mail_message.sender)

        #TODO: Perhaps we could build a database of email addresses for common package senders
        #TODO: and then we could auto detect who the package is from.  (Amazon, Newegg, etc)
        #TODO: Heck, for common ones, we could even try to parse even more info.  Things like
        #TODO: what was in the package and whatnot.
        from_name, from_addr = parseaddr(mail_message.sender)

        if not from_addr:
            logging.debug("No from address found. Aborting.")
            return

        user = auth_models.WTUser.get_user_by_email(from_addr)

        new_user = None
        if not user:
            logging.debug("No user found for %s.  Creating new account." % from_addr)
            new_user = auth_models.WTUser.create_placeholder_user(email=from_addr, name=from_name)
            if new_user:
                logging.debug("New placeholder user created for %s" % from_addr)
                user = new_user

        if not user:
            logging.debug("Whoops. User needed to go forward. Something went wrong.")
            raise Exception("Email parsing - Missing user entity.")

        for content_type, body in mail_message.bodies('text/plain'):
            message_body = body.decode()
            logging.info(message_body)

            tracking_nums = mail_utils.check_message_for_tracking_number(message_body)
            for tracking_num in tracking_nums:
                logging.info("Tracking number found: %s" % tracking_num)

        if not tracking_nums:
            subject = "BoxTrackr - No Tracking Number Found"
            missing_body = self.render_email('email/responses/missing_tracking_num.html')
            base_mail.send_email(from_addr, subject, missing_body)
            logging.debug("No tracking number found.")
            return

        if tracking_nums:
            #TODO: Add more info to the email response.
            subject = "BoxTrackr - Tracking Number Found"
            body = self.render_email('email/responses/found_tracking_num.html', nums=tracking_nums)
            base_mail.send_email(from_addr, subject, body)

            for tracking_num in tracking_nums:
                data = {
                    'tracking_number': tracking_num,
                    'site': from_name,
                    'new_user': True if new_user else False
                }

                shipping_actions.create_package(data, user)
            return

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_email(self, _template, **context):
        return self.jinja2.render_template(_template, **context)


app = webapp2.WSGIApplication([EmailHandler.mapping()], debug=True)


def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()