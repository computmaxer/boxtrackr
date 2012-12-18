from flask import request, redirect, url_for, jsonify
from flask.templating import render_template

import logging
import auth


class PackagesListView(auth.UserAwareView):

    def get(self):
        context = self.get_context()

        return render_template('shipping/package_list.html', **context)