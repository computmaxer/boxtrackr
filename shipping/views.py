from flask.templating import render_template

from shipping import api

import auth


class PackagesListView(auth.UserAwareView):

    def get(self):
        context = self.get_context()

        context['query_result'] = api.query_ups_tracking("1Z12345E1512345676")
        return render_template('shipping/package_list.html', **context)