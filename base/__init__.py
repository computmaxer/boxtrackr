from flask import request, redirect, abort
from flask.views import MethodView


# Did not want to put this here, but was having problems with circular imports in base/views.py
class BaseMultiMethodView(MethodView):
    active_nav = None

    def post(self):
        id = request.form.get('id', None)
        if id:
            attr = getattr(self, 'post_%s' % id, None)
            if attr and callable(attr):
                response = attr()
                if response:
                    return response
        return abort(404, "Post method not found on view.")
