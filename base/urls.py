from base import views as base_views
from flask import render_template
import logging


def setup_urls(app):
    """URLs for the base module"""

    @app.errorhandler(404)
    def page_not_found(e):
        logging.error(e)
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        logging.error(e)
        return render_template('500.html'), 500
