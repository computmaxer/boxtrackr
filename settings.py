FACEBOOK_APP_ID = '406278252776612'
FACEBOOK_APP_SECRET = 'e1490a8ce6200c7ff938d7f273087fbc'

GOOGLE_CLIENT_ID = '593910760953.apps.googleusercontent.com'
GOOGLE_SECRET = 'F2ngZOaKzAgUbhe3xVUqgYYj'

DEBUG = False
SECRET_KEY = 'dev_key_h8hfne89vm'
CSRF_ENABLED = True
CSRF_SESSION_LKEY = 'dev_key_h8asSNJ9s9=+'

# 1 day = 60s * 60m * 24h = 86400
TOKEN_SIGNING_TIMELIMIT = 86400

MEDIA_MERGED = True

UPS_API_USERNAME = 'username'
UPS_API_PASSWORD = 'password'
FEDEX_API_USERNAME = 'username'
FEDEX_API_PASSWORD = 'password'
USPS_API_USERNAME = 'username'
USPS_API_PASSWORD = 'password'
DHL_API_USERNAME = 'username'
DHL_API_PASSWORD = 'password'

try:
    from settingslocal import *
except ImportError:
    pass
