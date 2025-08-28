# PythonAnywhere Deployment Troubleshooting Guide

## Current Error Analysis

You're encountering: `ModuleNotFoundError: No module named 'univ_services'`

This error occurs because Django cannot locate your project's main module. Here's how to fix it:

## Step-by-Step Solution

### 1. Verify Project Structure on PythonAnywhere

First, check your project structure on PythonAnywhere:

```bash
# In a PythonAnywhere console, navigate to your project
cd /home/emmanalhedad/student-server-django
ls -la
```

You should see:
```
├── manage.py
├── univ_services/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
├── student_portal/
├── staff_panel/
├── financial/
└── other_apps/
```

### 2. Update Your WSGI Configuration

Use the corrected WSGI file (`pythonanywhere_wsgi.py`) I created:

```python
import os
import sys

# Add your project directory to Python path
path = '/home/emmanalhedad/student-server-django'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univ_services.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 3. Common Path Issues and Solutions

#### Issue A: Wrong Project Path
**Problem**: The path `/home/emmanalhedad/student-server-django` doesn't exist

**Solution**: Check your actual project location:
```bash
find /home/emmanalhedad -name "manage.py" -type f
```

#### Issue B: Missing __init__.py Files
**Problem**: Python can't recognize directories as modules

**Solution**: Ensure all app directories have `__init__.py` files:
```bash
find /home/emmanalhedad/student-server-django -name "__init__.py"
```

#### Issue C: Incorrect Directory Structure
**Problem**: Project uploaded to wrong location

**Expected Structure**:
```
/home/emmanalhedad/student-server-django/
├── manage.py
└── univ_services/
    └── settings.py
```

**If you have**:
```
/home/emmanalhedad/student-server-django/student-server-django/
├── manage.py
└── univ_services/
```

**Fix**: Update WSGI path to:
```python
path = '/home/emmanalhedad/student-server-django/student-server-django'
```

### 4. Debug Your WSGI File

Temporarily add debug information to your WSGI file:

```python
import os
import sys

# Debug information
print("=== WSGI DEBUG INFO ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Python version: {sys.version}")

path = '/home/emmanalhedad/student-server-django'
print(f"Project path: {path}")
print(f"Path exists: {os.path.exists(path)}")

if path not in sys.path:
    sys.path.insert(0, path)

print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries

# Check if univ_services directory exists
univ_services_path = os.path.join(path, 'univ_services')
print(f"univ_services path: {univ_services_path}")
print(f"univ_services exists: {os.path.exists(univ_services_path)}")

# Check if settings.py exists
settings_path = os.path.join(univ_services_path, 'settings.py')
print(f"settings.py exists: {os.path.exists(settings_path)}")
print("=== END DEBUG INFO ===")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univ_services.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 5. PythonAnywhere Web App Configuration

1. **Go to Web tab** in PythonAnywhere dashboard
2. **Source code**: Set to `/home/emmanalhedad/student-server-django`
3. **WSGI configuration file**: Point to your corrected WSGI file
4. **Virtualenv**: If using one, set the correct path

### 6. Install Dependencies

Ensure all required packages are installed:

```bash
# If using virtualenv
workon your-virtualenv-name

# Install requirements
cd /home/emmanalhedad/student-server-django
pip install -r requirements.txt
```

### 7. Static Files Configuration

Collect static files:

```bash
cd /home/emmanalhedad/student-server-django
python manage.py collectstatic --noinput
```

In PythonAnywhere Web tab, add static files mapping:
- **URL**: `/static/`
- **Directory**: `/home/emmanalhedad/student-server-django/staticfiles/`

### 8. Database Setup

Run migrations:

```bash
cd /home/emmanalhedad/student-server-django
python manage.py migrate
```

## Testing Your Configuration

### Test WSGI File Directly

```bash
# Test if WSGI file can be imported
cd /home/emmanalhedad/student-server-django
python -c "import sys; sys.path.insert(0, '.'); from univ_services.wsgi import application; print('WSGI OK')"
```

### Test Django Settings

```bash
# Test if Django can load settings
cd /home/emmanalhedad/student-server-django
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univ_services.settings'); import django; django.setup(); print('Django OK')"
```

## Common Error Messages and Solutions

### Error: `ImportError: No module named 'django'`
**Solution**: Install Django in your virtualenv or system Python

### Error: `ImproperlyConfigured: The SECRET_KEY setting must not be empty`
**Solution**: Check your settings.py file exists and has SECRET_KEY defined

### Error: `OperationalError: no such table`
**Solution**: Run `python manage.py migrate`

### Error: `DisallowedHost`
**Solution**: Add your domain to ALLOWED_HOSTS in settings.py:
```python
ALLOWED_HOSTS = ['emmanalhedad.pythonanywhere.com', 'localhost']
```

## Final Checklist

- [ ] Project uploaded to correct directory
- [ ] All `__init__.py` files present
- [ ] WSGI file points to correct path
- [ ] Dependencies installed
- [ ] Static files collected
- [ ] Database migrated
- [ ] ALLOWED_HOSTS configured
- [ ] Web app reloaded in PythonAnywhere

## Getting Help

If issues persist:
1. Check PythonAnywhere error logs
2. Use the debug WSGI configuration above
3. Contact PythonAnywhere support with specific error messages
4. Check Django and Python versions compatibility

Remember to remove debug print statements from your WSGI file once everything is working!