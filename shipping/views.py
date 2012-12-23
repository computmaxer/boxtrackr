from flask import request
from flask.templating import render_template

from shipping import api, forms, actions

import auth
import logging


class PackagesListView(auth.UserAwareView):

    def get(self, form=None):
        context = self.get_context()
        context['add_package_open'] = request.args.get('add', None)
        context['form'] = form or forms.AddPackageForm()
        context['packages'] = actions.get_user_packages(self.user)
        return render_template('shipping/package_list.html', **context)

    def post_add_package(self):
        form = forms.AddPackageForm(request.form)
        if form.validate():
            actions.create_package(form.data, self.user)
            return self.get()
        return self.get(form)
