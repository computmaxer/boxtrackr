from google.appengine.ext import db

from shipping import models as shipping_models


def create_package(data, user):
    p = shipping_models.Package(**data)
    p.owner = user
    p.put()
    return p


def get_user_packages(user):
    query = shipping_models.Package.all().filter('owner', user)
    packages = []
    for package in query:
        setattr(package, 'STATUS_TEXT', package.get_status_text())
        packages.append(package)
    return packages
