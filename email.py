import logging
import webapp2
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from email.utils import parseaddr

from shipping import actions as shipping_actions

from mail import utils as mail_utils

from auth import models as auth_models


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

            tracking_num = mail_utils.check_message_for_tracking_number(message_body)
            logging.info("Tracking number found: %s" % tracking_num)

        if not tracking_num:
            logging.debug("No tracking number found.")
            #TODO: This should raise a specific exception that we can catch.
            raise Exception("Email parsing - No tracking number found")

        if tracking_num:
            data = {
                'tracking_number': tracking_num,
                'site': from_name
            }

            #TODO: Send the user an email back with the info we parsed out.
            #TODO: If it is a new user we could also tell them how to claim their account.
            shipping_actions.create_package(data, user)


app = webapp2.WSGIApplication([EmailHandler.mapping()], debug=True)


def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()