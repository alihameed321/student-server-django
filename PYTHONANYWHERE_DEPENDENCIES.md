# PythonAnywhere Dependencies Installation Guide

## Current Error: Missing Dependencies

You're encountering: `ModuleNotFoundError: No module named 'rest_framework_simplejwt'`

This error occurs because the required Python packages haven't been installed on your PythonAnywhere account.

## Solution: Install All Dependencies

### Step 1: Open a PythonAnywhere Console

1. Log into your PythonAnywhere account
2. Go to the **Consoles** tab
3. Start a **Bash console**

### Step 2: Navigate to Your Project Directory

```bash
cd /home/emmanalhedad/student-server-django
```

### Step 3: Check if Virtual Environment Exists

```bash
# Check if you have a virtual environment
ls -la
# Look for directories like 'venv', 'env', or '.venv'
```

### Step 4A: If Using Virtual Environment (Recommended)

If you have a virtual environment:

```bash
# Activate your virtual environment
# Replace 'venv' with your actual virtualenv name
source venv/bin/activate

# You should see (venv) at the beginning of your prompt
```

### Step 4B: If No Virtual Environment (Create One)

```bash
# Create a new virtual environment
python3.13 -m venv venv

# Activate it
source venv/bin/activate
```

### Step 5: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### Step 6: Verify Installation

```bash
# Check if djangorestframework-simplejwt is installed
pip show djangorestframework-simplejwt

# List all installed packages
pip list
```

## Alternative: Manual Installation

If the requirements.txt installation fails, install packages individually:

```bash
# Core Django packages
pip install Django==5.2.4
pip install djangorestframework==3.14.0
pip install djangorestframework-simplejwt==5.3.0
pip install django-cors-headers==4.7.0

# Database
pip install psycopg2-binary==2.9.10

# Other dependencies
pip install pillow==11.3.0
pip install qrcode==8.2
pip install reportlab==4.4.3
pip install python-decouple==3.8
pip install Faker==37.5.3
pip install arabic-reshaper==3.0.0
pip install python-bidi==0.6.6
pip install django-extensions==4.1
```

## Update Web App Configuration

### Step 7: Configure Virtual Environment in Web Tab

1. Go to the **Web** tab in PythonAnywhere
2. In the **Virtualenv** section, enter:
   ```
   /home/emmanalhedad/student-server-django/venv
   ```
3. Click **Reload** button

### Step 8: Test Your Installation

```bash
# Test Django import
cd /home/emmanalhedad/student-server-django
python -c "import django; print('Django version:', django.get_version())"

# Test JWT import
python -c "import rest_framework_simplejwt; print('JWT installed successfully')"

# Test your Django settings
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univ_services.settings'); import django; django.setup(); print('Django setup successful')"
```

## Common Issues and Solutions

### Issue 1: Permission Denied
```bash
# If you get permission errors, try:
pip install --user -r requirements.txt
```

### Issue 2: Package Conflicts
```bash
# Clear pip cache and reinstall
pip cache purge
pip install --force-reinstall -r requirements.txt
```

### Issue 3: Python Version Mismatch
```bash
# Check Python version
python --version

# If using Python 3.13, ensure compatibility
pip install --upgrade setuptools wheel
```

### Issue 4: psycopg2 Installation Error
```bash
# If psycopg2-binary fails, try:
pip install psycopg2-binary --no-cache-dir

# Or use alternative:
pip install psycopg2cffi
```

## Verification Checklist

After installation, verify these packages are available:

- [ ] Django (5.2.4)
- [ ] djangorestframework (3.14.0)
- [ ] djangorestframework-simplejwt (5.3.0)
- [ ] django-cors-headers (4.7.0)
- [ ] psycopg2-binary (2.9.10)
- [ ] pillow (11.3.0)
- [ ] All other requirements from requirements.txt

## Final Steps

1. **Reload your web app** in the Web tab
2. **Check error logs** for any remaining issues
3. **Test your application** by visiting your domain

## Troubleshooting Commands

```bash
# Check which packages are installed
pip list | grep -E "django|rest_framework"

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Test WSGI file directly
python /var/www/emmanalhedad_pythonanywhere_com_wsgi.py
```

## Environment Variables (Optional)

If using python-decouple, create a `.env` file:

```bash
# Create .env file in project root
cd /home/emmanalhedad/student-server-django
touch .env

# Add your environment variables
echo "DEBUG=False" >> .env
echo "SECRET_KEY=your-secret-key-here" >> .env
```

## Next Steps After Installation

1. Run database migrations:
   ```bash
   python manage.py migrate
   ```

2. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

3. Create superuser (if needed):
   ```bash
   python manage.py createsuperuser
   ```

4. Test the application in your browser

Remember to reload your web app after making any changes!