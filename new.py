from collections import namedtuple

PRIVACY_CHOICES = namedtuple('PRIVACY_CHOICES', ['PUBLIC', 'PRIVATE', 'FRIENDS', 'CUSTOM'])(
    PUBLIC='PUBLIC',
    PRIVATE='PRIVATE',
    FRIENDS='FRIENDS',
    CUSTOM='CUSTOM'
    )

print(PRIVACY_CHOICES.PUBLIC)
