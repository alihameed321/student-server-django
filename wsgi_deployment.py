import os
import sys

# Add your project path
# For Windows environment - adjust this path to match your actual project location
path = r'c:\Users\Haidan\Desktop\service\student-server-django'  # Windows path format
if path not in sys.path:
    sys.path.append(path)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'univ_services.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()