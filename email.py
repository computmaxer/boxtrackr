import logging
import webapp2
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app

from shipping import actions as shipping_actions

from mail import utils as mail_utils

from auth import models as auth_models


class EmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: %s" % mail_message.sender)

        for content_type, body in mail_message.bodies('text/plain'):
            message_body = body.decode()
            logging.info(message_body)

            tracking_num = mail_utils.check_message_for_tracking_number(message_body)
            logging.info("Tracking number found: %s" % tracking_num)

        if tracking_num:
            data = {
                'tracking_number': tracking_num,
                'site': mail_message.sender
            }

            #TODO Correctly check for user
            user = auth_models.WTUser.get_user_by_email(mail_message.sender)

            shipping_actions.create_package(data, user)


app = webapp2.WSGIApplication([EmailHandler.mapping()], debug=True)


def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()