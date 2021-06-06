from collections import namedtuple

TOKEN_EXPIRY_TIME = 48
DEFAULT_PROFILE_PIC = "profile_pics/default.png"
VERIFY_EMAIL_SUBJECT = "WeConnect: Email verification"
REQUEST_MAIL_SUBJECT = "WeConnect: New Friend Request"
FORGOT_PASSWORD_MAIL_SUBJECT = "WeConnect: Forgot Password"

URL = "http://localhost:3000/"

PROFILE_PIC_PATH = "profile_pics/"
POST_PIC_PATH = "posts/"

PRIVACY_CHOICES = namedtuple('PRIVACY_CHOICES', ['PUBLIC', 'PRIVATE', 'FRIENDS', 'CUSTOM'])(
    PUBLIC='PUBLIC',
    PRIVATE='PRIVATE',
    FRIENDS='FRIENDS',
    CUSTOM='CUSTOM'
    )
