#TODO: Create a flask extension/library out of this?
from xml.etree import ElementTree as ET

from flask.templating import render_template

import requests
import settings
import logging


def query_ups_tracking(tracking_number):
    response = _get_ups_tracking_xml(tracking_number)
    tree = ET.XML(response)

    return _parse_ups_tracking_response_xml(tree)


def _parse_ups_tracking_response_xml(root):
    response = root.find('Response')
    status = response.find('ResponseStatusDescription')
    if status.text == "Success":
        shipments = []
        for shipment in root.findall('Shipment'):
            packages = []
            for package in shipment.findall('Package'):
                activity = package.find('Activity')
                status = activity.find('Status').find('StatusType').find('Description').text
                info = {
                    'tracking_number': package.find('TrackingNumber').text,
                    'status': status,
                }
                #TODO: Add more info to the dict?
                packages.append(info)
            shipments.append(packages)
        return shipments

    logging.error(root.items())
    # Query failed.  #TODO raise some kind of exception
    return None


def _get_ups_tracking_xml(tracking_number):
    path = "https://wwwcie.ups.com/ups.app/xml/Track"
    ctx = {
        'tracking_number':tracking_number,
        'password':settings.UPS_API_PASSWORD,
        }
    xml_req = render_template("xml/ups_tracking_request.html", **ctx)

    r = requests.post(path, data=xml_req)
    return r.text
