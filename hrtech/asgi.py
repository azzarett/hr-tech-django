"""
ASGI config for hrtech project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from hrtech.conf import ENV_ID, ENV_POSSIBLE_OPTIONS

assert ENV_ID in ENV_POSSIBLE_OPTIONS, f"Invalid env id. Possible options: {ENV_POSSIBLE_OPTIONS}"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'hrtech.env.{ENV_ID}')

application = get_asgi_application()
