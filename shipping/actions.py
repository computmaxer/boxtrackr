from google.appengine.ext import db

from shipping import models as shipping_models

from datetime import datetime, timedelta


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


def get_package(keystr=None, key=None):
    if keystr:
        return shipping_models.Package.get(db.Key(keystr))
    elif key:
        return shipping_models.Package.get(key)


def edit_package(package, data):
    package.name = data.get('name')
    package.tracking_number = data.get('tracking_number')
    package.site = data.get('site')
    package.description = data.get('description')

    # Set the last_checked time so that it will refresh from the api on next load
    new_time = datetime.now() - timedelta(minutes=shipping_models.Package.UPDATE_INTERVAL_MINUTES)
    package.last_checked = new_time
    package.put()


def delete_package(package, user):
    if package.owner.key() == user.key():
        package.delete()
        return True
    return False
