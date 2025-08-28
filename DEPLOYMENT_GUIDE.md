# Django Deployment Guide

This guide explains how to deploy your Django student services application in different environments.

## Files Created

1. **`wsgi_deployment.py`** - WSGI configuration for Windows deployment
2. **`settings_production.py`** - Production settings configuration

## Deployment Options

### 1. Local Development (Windows)

For local development, continue using:
```bash
python manage.py runserver
```

### 2. Windows Server Deployment

Use the `wsgi_deployment.py` file with IIS or other Windows web servers:

```python
# wsgi_deployment.py is configured for Windows paths
# Update the path variable to match your server location
path = r'c:\path\to\your\student-server-django'
```

### 3. Linux Server Deployment (PythonAnywhere, etc.)

For Linux servers, create a similar WSGI file with Linux paths:

```python
import os
import sys

# Linux path format
path = '/home/emmanalhedad/student-server-django'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'univ_services.settings_production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## Production Settings

### Using Production Settings

To use production settings, update your WSGI configuration:

```python
# Change this line in your WSGI file
os.environ['DJANGO_SETTINGS_MODULE'] = 'univ_services.settings_production'
```

### Important Production Configurations

1. **Debug Mode**: Set to `False` in production
2. **Allowed Hosts**: Add your domain/IP addresses
3. **Database**: Consider using PostgreSQL or MySQL for production
4. **Static Files**: Configure proper static file serving
5. **Security**: Enable security headers and HTTPS

## Environment Variables

For better security, consider using environment variables:

```python
# In your settings file
import os
from decouple import config  # pip install python-decouple

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
DATABASE_URL = config('DATABASE_URL')
```

## Static Files Collection

Before deployment, collect static files:

```bash
python manage.py collectstatic --noinput
```

## Database Migration

Ensure database is migrated:

```bash
python manage.py migrate
```

## CORS Configuration

Update CORS settings in production:

- Set `CORS_ALLOW_ALL_ORIGINS = False`
- Add specific domains to `CORS_ALLOWED_ORIGINS`
- Remove development URLs from allowed origins

## Security Checklist

- [ ] DEBUG = False
- [ ] Proper ALLOWED_HOSTS configuration
- [ ] Secure database credentials
- [ ] HTTPS enabled
- [ ] Static files properly served
- [ ] CORS properly configured
- [ ] Security headers enabled
- [ ] Regular backups configured

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure project path is correctly added to sys.path
2. **Static Files**: Run collectstatic and configure web server to serve static files
3. **Database**: Ensure database file permissions are correct
4. **CORS**: Check that frontend domains are in CORS_ALLOWED_ORIGINS

### Logs

Check Django logs for errors:
- Development: Console output
- Production: Check log files configured in LOGGING settings

## PythonAnywhere Specific

For PythonAnywhere deployment:

1. Upload your code to `/home/yourusername/student-server-django`
2. Create a WSGI file in the Web tab
3. Use the Linux path format in your WSGI configuration
4. Set environment variables in the Files tab
5. Configure static files mapping in the Web tab

## Next Steps

1. Test the deployment in a staging environment
2. Set up monitoring and logging
3. Configure automated backups
4. Set up SSL/HTTPS
5. Configure domain and DNS