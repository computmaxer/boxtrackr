from flask import request, redirect, url_for
from flask.templating import render_template

from flask_login import login_required

from shipping import api, forms, actions

import auth
import json
import logging


class MainHandler(auth.UserAwareView):
    active_nav = 'home'

    def get(self):
        context = self.get_context()
        context['remove_header'] = True

        if self.user and request.path != '/home/':
            return redirect(url_for('package-list'))

        context['login_mode'] = request.args.get('login_mode', None)
        return render_template('home.html', **context)


class PackagesListView(auth.UserAwareView):
    decorators = [login_required]

    def get(self, form=None):
        context = self.get_context()
        context['add_package_open'] = request.args.get('add', None)
        context['form'] = form or forms.AddPackageForm()
        context['packages'] = actions.get_user_packages(self.user)
        context['num_packages'] = len(context['packages'])
        return render_template('shipping/package_list.html', **context)

    def post_add_package(self):
        form = forms.AddPackageForm(request.form)
        if form.validate():
            actions.create_package(form.data, self.user)
            return self.get()
        return self.get(form)

    def post_edit_package(self):
        package_key = request.form.get('package-key')
        package = actions.get_package(package_key)
        form = forms.AddPackageForm(request.form)
        if form.validate():
            actions.edit_package(package, form.data)
            return self.get()
        return self.get(form)

    def post_delete_package(self):
        package_key = request.form.get('package-key')
        package = actions.get_package(package_key)
        actions.delete_package(package, self.user)
        #TODO: Notify user if delete fails.
        return self.get()

    def post_refresh_package(self):
        package_key = request.form.get('key')
        package = actions.get_package(package_key)
        package.update_values_from_api()
        setattr(package, 'STATUS_TEXT', package.get_status_text())
        row = render_template("shipping/package_row.html", **{'package': package})
        return json.dumps({'key': package_key, 'row': row})
