import os
import sys

# Add your project directory to Python path
path = '/home/emmanalhedad/student-server-django'
if path not in sys.path:
    sys.path.append(path)

# Add your virtual environment site-packages
venv_path = '/home/emmanalhedad/student-server-django/venv/lib/python3.13/site-packages'
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'univ_services.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()