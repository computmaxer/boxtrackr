from shipping import views as shipping_views
from flask import render_template


def setup_urls(app):
    """URLs for the base module"""
    app.add_url_rule('/shipping/package_list/',
                     view_func=shipping_views.PackagesListView.as_view('package-list'))
    app.add_url_rule('/', view_func=shipping_views.MainHandler.as_view('home'))
    app.add_url_rule('/home/', view_func=shipping_views.MainHandler.as_view('force-home'))
