"""
WSGI config for sprinter project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""
# wsgi.py

import os
from django.core.wsgi import get_wsgi_application  # Correct import

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sprinter.settings')
app = get_wsgi_application()
