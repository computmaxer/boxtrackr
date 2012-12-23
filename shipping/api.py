#TODO: Create a flask extension/library out of this?
from xml.etree import ElementTree as ET

from flask.templating import render_template

import requests
import settings
import logging


NO_INFO = -1
RECEIVED_NOTICE = 0
IN_TRANSIT = 1
OUT_FOR_DELIVERY = 2
DELIVERED = 3

STATUS_LIST = [(NO_INFO, "Carrier has no information"),
               (RECEIVED_NOTICE, "Carrier has been notified of the shipment"),
               (IN_TRANSIT, "In Transit"),
               (OUT_FOR_DELIVERY, "Out for Delivery"),
               (DELIVERED, "Delivered")
]
STATUS_DICT = {
    NO_INFO: "Carrier has no information",
    RECEIVED_NOTICE: "Carrier has been notified of the shipment",
    IN_TRANSIT: "In Transit",
    OUT_FOR_DELIVERY: "Out for Delivery",
    DELIVERED: "Delivered",
}


def determine_carrier(tracking_number):
    #TODO: regex matching to return the proper carrier.
    #return 'fedex'
    #return 'usps'
    return 'ups'  # TODO: Temporary, obviously.


def query_tracking(tracking_number):
    carrier = determine_carrier(tracking_number)
    method = locals["query_%s_tracking" % carrier]
    return method(tracking_number)


def _determine_status(status_text):
    low_text = status_text.lower()
    #TODO: Finish this.
    if 'no' in low_text:  # TODO: figure out what this needs to be
        return NO_INFO
    elif 'received' in low_text:  # TODO: figure out what this needs to be
        return RECEIVED_NOTICE
    elif 'transit' in low_text:  # TODO: figure out what this needs to be
        return IN_TRANSIT
    elif 'out' in low_text:  # TODO: figure out what this needs to be
        return OUT_FOR_DELIVERY
    elif 'delivered' in low_text:  # TODO: figure out what this needs to be
        return DELIVERED


# UPS Tracking API
####################################################################################################
def query_ups_tracking(tracking_number):
    """
    Check shipment status with a UPS tracking number.  Queries the UPS API for the results in XML,
    and then parses the XML to return the shipment information.
    :param tracking_number: The UPS tracking number of the shipment being tracked.
    :return: A list of lists of dictionaries.  Shipments:Packages:InfoDict
    """
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
                status_text = activity.find('Status').find('StatusType').find('Description').text
                info = {
                    'tracking_number': package.find('TrackingNumber').text,
                    'status': _determine_status(status_text),
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
        'tracking_number': tracking_number,
        'password': settings.UPS_API_PASSWORD,
    }
    xml_req = render_template("xml/ups_tracking_request.html", **ctx)

    r = requests.post(path, data=xml_req)
    return r.text


# FedEx Tracking API
####################################################################################################
def query_fedex_tracking(tracking_number):
    """
    Check shipment status with a FedEx tracking number.  Queries the FedEX API for the results in
    XML, and then parses the XML to return the shipment information.
    :param tracking_number: The FedEx tracking number of the shipment being tracked.
    :return: A list of lists of dictionaries.  Shipments:Packages:InfoDict
    """
    response = _get_fedex_tracking_xml(tracking_number)
    tree = ET.XML(response)
    return _parse_fedex_tracking_response_xml(tree)


def _parse_fedex_tracking_response_xml(root):
    #TODO: Do this.
    return root


def _get_fedex_tracking_xml(tracking_number):
    path = "https://gatewaybeta.fedex.com:443/xml" #TODO: change to live url
    #path = "https://gateway.fedex.com:443/xml"
    ctx = {
        'tracking_number': tracking_number,
        'password': settings.FEDEX_API_PASSWORD,
    }
    xml_req = render_template("xml/fedex_tracking_request.html", **ctx)

    r = requests.post(path, data=xml_req)
    return r.text


# USPS Tracking API
####################################################################################################
def query_usps_tracking(tracking_number):
    """
    Check shipment status with a USPS tracking number.  Queries the USPS API for the results in
    XML, and then parses the XML to return the shipment information.
    :param tracking_number: The USPS tracking number of the shipment being tracked.
    :return: A list of lists of dictionaries.  Shipments:Packages:InfoDict
    """
    response = _get_usps_tracking_xml(tracking_number)
    tree = ET.XML(response)
    return _parse_usps_tracking_response_xml(tree)


def _parse_usps_tracking_response_xml(root):
    #TODO: Do this.
    return root


def _get_usps_tracking_xml(tracking_number):
    path = "" #TODO: find url
    ctx = {
        'tracking_number': tracking_number,
        'password': settings.USPS_API_PASSWORD,
    }
    xml_req = render_template("xml/usps_tracking_request.html", **ctx)

    r = requests.post(path, data=xml_req)
    return r.text
