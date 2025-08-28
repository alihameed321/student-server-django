import os
import sys

# Add your project directory to Python path
# This should be the directory containing manage.py
path = '/home/emmanalhedad/student-server-django'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univ_services.settings')

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Debug information (remove in production)
# Uncomment these lines to debug path issues:
# print("Python path:", sys.path)
# print("Current working directory:", os.getcwd())
# print("Project path exists:", os.path.exists(path))
# print("univ_services directory exists:", os.path.exists(os.path.join(path, 'univ_services')))