from flask import request, redirect, url_for, jsonify
from flask.templating import render_template

import logging
import auth


class PackagesListView(auth.UserAwareView):

    def get(self):
        context = self.get_context()

        #testing
        import requests
        from xml.etree import ElementTree


        xml_req = """<?xml version="1.0" ?>
                        <AccessRequest xml:lang='en-US'>
                            <AccessLicenseNumber>FCAA2A0B2F22BF30</AccessLicenseNumber>
                            <UserId>computmaxer</UserId>
                            <Password>N3wpsw3d</Password>
                        </AccessRequest>
                    <?xml version="1.0" ?>
                        <TrackRequest>
                            <Request>
                                <TransactionReference>
                                    <CustomerContext>guidlikesubstance</CustomerContext>
                                </TransactionReference>
                                <RequestAction>Track</RequestAction>
                            </Request>
                            <TrackingNumber>1Z9999999999999999</TrackingNumber>
                        </TrackRequest>"""

        path = "https://wwwcie.ups.com/ups.app/xml/Track"

        #this url connects to the test server of fedex
        # for live server url is:"https://gateway.fedex.com:443/xml"

        r = requests.post(path, data=xml_req)

        tree = ElementTree.fromstring(r.text)
        context['tree'] = r.text


        return render_template('shipping/package_list.html', **context)