#TODO: Create a flask extension/library out of this?
from flask.templating import render_template

import requests
import settings


def _get_ups_tracking_xml(tracking_number):
    path = "https://wwwcie.ups.com/ups.app/xml/Track"
    ctx = {
        'tracking_number':tracking_number,
        'password':settings.UPS_API_PASSWORD,
        }
    xml_req = render_template("xml/ups_tracking_request.html", **ctx)

    r = requests.post(path, data=xml_req)
    return r.text
