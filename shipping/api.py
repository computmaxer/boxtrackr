#TODO: Create a flask extension/library out of this?
from xml.etree import ElementTree as ET

from flask.templating import render_template

import requests
import settings
import logging


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
