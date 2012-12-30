from flask import render_template

from google.appengine.api import mail
from google.appengine.ext import deferred


def send_email(email, subject, body):
    import logging
    logging.warning(body)

    #TODO: Get @boxtrackr.com email set up and use one of those emails
    sender="Michael Davis <mike.philip.davis@gmail.com>"
    deferred.defer(mail.send_mail, sender=sender, to=email, subject=subject, body=body)


def generate_email_body(template, context=None, **kwargs):
    ctx = {}
    if context:
        ctx.update(context)
    ctx.update(kwargs)

    return render_template(template, **ctx)

