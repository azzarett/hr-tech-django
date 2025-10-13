"""
WSGI config for hrtech project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from hrtech.conf import ENV_ID, ENV_POSSIBLE_OPTIONS

assert ENV_ID in ENV_POSSIBLE_OPTIONS, f"Invalid env id. Possible options: {ENV_POSSIBLE_OPTIONS}"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'hrtech.env.{ENV_ID}')

application = get_wsgi_application()
