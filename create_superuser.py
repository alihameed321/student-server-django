import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univ_services.settings')
django.setup()

from accounts.models import User

# Update existing admin user
try:
    user = User.objects.get(username='admin')
    user.university_id = 'ADMIN001'
    user.user_type = 'admin'
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f'Updated admin user: {user.username} ({user.university_id}) - {user.user_type}')
except User.DoesNotExist:
    # Create new superuser if doesn't exist
    user = User.objects.create_superuser(
        username='admin',
        email='admin@university.edu',
        password='admin123',
        university_id='ADMIN001',
        user_type='admin'
    )
    print(f'Created superuser: {user.username} ({user.university_id})')