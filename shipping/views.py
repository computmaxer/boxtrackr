from flask.templating import render_template

from shipping import api

import auth


class PackagesListView(auth.UserAwareView):

    def get(self):
        context = self.get_context()

        context['tree'] = api._get_ups_tracking_xml("1Z12345E1512345676")
        return render_template('shipping/package_list.html', **context)