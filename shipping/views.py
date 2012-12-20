from flask.templating import render_template

from shipping import api

import auth


class PackagesListView(auth.UserAwareView):

    def get(self):
        context = self.get_context()
                
        return render_template('shipping/package_list.html', **context)