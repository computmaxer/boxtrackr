#TODO: Create a flask extension/library out of this?
from xml.etree import ElementTree as ET

from flask.templating import render_template

import sys
import requests
import datetime
import random
import uuid
import settings
import logging


API_UNAVAILABLE = -3
INVALID_NUMBER = -2
NO_INFO = -1
RECEIVED_NOTICE = 0
IN_TRANSIT = 1
OUT_FOR_DELIVERY = 2
DELIVERED = 3

STATUS_LIST = [(INVALID_NUMBER, "Invalid Tracking Number"),
               (API_UNAVAILABLE, "Carrier service unavailable"),
               (NO_INFO, "Carrier has no information"),
               (RECEIVED_NOTICE, "Carrier has been notified of the shipment"),
               (IN_TRANSIT, "In Transit"),
               (OUT_FOR_DELIVERY, "Out for Delivery"),
               (DELIVERED, "Delivered")
]
STATUS_DICT = {
    API_UNAVAILABLE: "Carrier service unavailable",
    INVALID_NUMBER: "Invalid Tracking Number",
    NO_INFO: "Carrier has no information",
    RECEIVED_NOTICE: "Carrier has been notified of the shipment",
    IN_TRANSIT: "In Transit",
    OUT_FOR_DELIVERY: "Out for Delivery",
    DELIVERED: "Delivered",
}

CARRIER_LIST = [('ups', "UPS"),
                ('fedex', 'FedEx'),
                ('usps', 'USPS'),
                ('dhl', 'DHL')]


def determine_carrier(tracking_number):
    #TODO: regex matching to return the proper carrier.
    #return 'fedex'
    if len(tracking_number) < 12:
        return 'dhl'
    elif '1Z' in tracking_number:
        return 'ups'  # TODO: Temporary, obviously.
    else:
        return 'usps'


def query_tracking(tracking_number, carrier=None):
    """
    Query a tracking number without knowing the carrier.  Function will determine the proper carrier
    based on the tracking number and then call the appropriate shipping API function.
    :param tracking_number: The tracking number to query for.
    :keyword carrier: Optionally specify the carrier to query.
    :return: The result list from the API function if the query was successful.
    """
    if not carrier:
        carrier = determine_carrier(tracking_number)
    logging.info("Querying %s tracking API.  Tracking number: %s" % (carrier, tracking_number))
    this = sys.modules[__name__]
    method = getattr(this, "query_%s_tracking" % carrier)
    return method(tracking_number)


def _determine_status(status_text):
    low_text = status_text.lower()
    #TODO: Finish this.
    if 'no' in low_text:  # TODO: figure out what this needs to be
        return NO_INFO
    elif 'received' in low_text:  # TODO: figure out what this needs to be
        return RECEIVED_NOTICE
    elif 'transit' in low_text or low_text == 'pu':  # TODO: figure out what this needs to be
        return IN_TRANSIT
    elif 'out' in low_text or low_text == 'wc':  # TODO: figure out what this needs to be
        return OUT_FOR_DELIVERY
    elif 'delivered' or 'ok' in low_text:  # TODO: figure out what this needs to be
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
    if response and 200 <= response.status_code < 300:
        logging.info(response.text)  # TODO: Remove?
        tree = ET.XML(response.text)
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
                #TODO: Add more info to the dict
                packages.append(info)
            shipments.append(packages)
        return shipments
    elif status.text == "Failure":
        error = response.find('Error').find('ErrorDescription')
        if error.text == "Invalid tracking number":
            shipments = []
            packages = [{'status': INVALID_NUMBER}]
            shipments.append(packages)
            return shipments
        elif error.text == "Tracking service unavailable":
            shipments = []
            packages = [{'status': API_UNAVAILABLE}]
            shipments.append(packages)
            return shipments
        else:
            logging.error(str(root) + " ,".join(root.items()))
    else:
        logging.error(str(root) + " ,".join(root.items()))
    # Query failed.  #TODO raise some kind of exception
    return None


def _get_ups_tracking_xml(tracking_number):
    path = "https://wwwcie.ups.com/ups.app/xml/Track"
    ctx = {
        'tracking_number': tracking_number,
        'guid': uuid.uuid4(),
        'username': settings.UPS_API_USERNAME,
        'password': settings.UPS_API_PASSWORD,
    }
    xml_req = render_template("xml/ups_tracking_request.html", **ctx)

    try:
        r = requests.post(path, data=xml_req)
        return r
    except requests.ConnectionError, e:
        logging.error("Error connecting to UPS: %s" % e)


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
    if response and 200 <= response.status_code < 300:
        logging.info(response.text)
        tree = ET.XML(response.text)
        return _parse_fedex_tracking_response_xml(tree)


def _parse_fedex_tracking_response_xml(root):
    #TODO: Do this.
    return root


def _get_fedex_tracking_xml(tracking_number):
    path = "https://gatewaybeta.fedex.com:443/xml" #TODO: change to live url
    #path = "https://gateway.fedex.com:443/xml"
    ctx = {
        'tracking_number': tracking_number,
        'username': settings.FEDEX_API_USERNAME,
        'password': settings.FEDEX_API_PASSWORD,
    }
    xml_req = render_template("xml/fedex_tracking_request.html", **ctx)

    try:
        r = requests.post(path, data=xml_req)
        return r
    except requests.ConnectionError, e:
        logging.error("Error connecting to FedEx: %s" % e)


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
    if response and 200 <= response.status_code < 300:
        logging.info(response.text)
        tree = ET.XML(response.text)
        return _parse_usps_tracking_response_xml(tree)


def _parse_usps_tracking_response_xml(root):
    shipments = []
    if root.tag == 'TrackResponse':
        logging.warning("root.tag is a TrackResponse")
        packages = []
        for package in root.findall('TrackInfo'):
            summary = package.find('TrackSummary')
            status = summary.find('Event').text
            info = {
                'tracking_number': package.get('ID'),
                'status': _determine_status(status),
            }
            #TODO: Add more info to the dict
            packages.append(info)
        shipments.append(packages)
        return shipments

    #TODO: Handle error
    if root.tag == 'Error':
        logging.error("USPS Error: %s" % root.find('Description').text)
    else:
        logging.error("Error parsing USPS root response.")
    return None


def _get_usps_tracking_xml(tracking_number):
    ctx = {
        'tracking_number': tracking_number,
        'username': settings.USPS_API_USERNAME,
        'password': settings.USPS_API_PASSWORD,
    }
    xml_req = render_template("xml/usps_tracking_request.html", **ctx)
    path = "http://testing.shippingapis.com/ShippingAPITest.dll?API=TrackV2&XML=%s" % xml_req
    try:
        r = requests.get(path)
        return r
    except requests.ConnectionError, e:
        logging.error("Error connecting to USPS: %s" % e)


# DHL Tracking API
####################################################################################################
def query_dhl_tracking(tracking_number):
    """
    Check shipment status with a USPS tracking number.  Queries the USPS API for the results in
    XML, and then parses the XML to return the shipment information.
    :param tracking_number: The USPS tracking number of the shipment being tracked.
    :return: A list of lists of dictionaries.  Shipments:Packages:InfoDict
    """
    response = _get_dhl_tracking_xml(tracking_number)
    if response and 200 <= response.status_code < 300:
        logging.info(response.text)
        tree = ET.XML(response.text)
        return _parse_dhl_tracking_response_xml(tree)


def _parse_dhl_tracking_response_xml(root):
    shipments = []
    if root.tag == '{http://www.dhl.com}TrackingResponse':
        logging.warning("root.tag is a TrackResponse")
        packages = []
        for package in root.findall('AWBInfo'):
            status = ''
            for shipment_event in package.findall('ShipmentEvent'):
                #TODO: This is silly.
                status = shipment_event.find('ServiceEvent').find('EventCode').text
                logging.warning(status)
            info = {
                'tracking_number': package.find('AWBNumber').text,
                'status': _determine_status(status),
            }
            #TODO: Add more info to the dict
            packages.append(info)
        shipments.append(packages)
        return shipments

    #TODO: Handle error
    if root.tag == '{http://www.dhl.com}ShipmentTrackingErrorResponse':
        error = root.find('Response').find('Status').find('Condition').find('ConditionData')
        logging.error("DHL Error: %s" % error.text)
    else:
        logging.error("Error parsing DHL root response.")
    return None


def _get_dhl_tracking_xml(tracking_number):
    ctx = {
        'tracking_number': tracking_number,
        'time': datetime.datetime.now().isoformat(),
        'guid': random.randint(1000000000000000000000000000, 1999999999999999999999999999),
        'username': settings.DHL_API_USERNAME,
        'password': settings.DHL_API_PASSWORD
    }
    xml_req = render_template("xml/dhl_tracking_request.html", **ctx)
    path = "http://xmlpitest-ea.dhl.com/XMLShippingServlet"
    try:
        r = requests.post(path, data=xml_req)
        return r
    except requests.ConnectionError, e:
        logging.error("Error connecting to DHL: %s" % e)
