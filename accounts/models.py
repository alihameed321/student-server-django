from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
import qrcode
from io import BytesIO
from django.core.files import File


class User(AbstractUser):
    """Custom User model for university students and staff"""
    
    USER_TYPES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    
    university_id = models.CharField(max_length=20, unique=True, default='MY-UNIV-001')
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    
    # Student specific fields
    major = models.CharField(max_length=100, blank=True)
    academic_level = models.CharField(max_length=50, blank=True)
    enrollment_year = models.IntegerField(null=True, blank=True)
    
    # Staff specific fields
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.university_id} - {self.get_full_name()}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Temporarily disabled QR code generation to avoid recursion error
        # self.generate_qr_code()
    
    def generate_qr_code(self):
        """Generate QR code for the user's digital ID"""
        qr_data = f"University ID: {self.university_id}\nName: {self.get_full_name()}\nType: {self.user_type}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_{self.university_id}.png'
        filebuffer = File(buffer, name=filename)
        self.qr_code.save(filename, filebuffer)
        buffer.close()
    
    @property
    def is_student(self):
        return self.user_type == 'student'
    
    @property
    def is_staff_member(self):
        return self.user_type in ['staff', 'admin']


class StudentProfile(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id_number = models.CharField(max_length=20, unique=True)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    total_credits = models.IntegerField(default=0)
    graduation_date = models.DateField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"Student Profile - {self.user.get_full_name()}"


class StaffProfile(models.Model):
    """Extended profile for staff members"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    permissions = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Staff Profile - {self.user.get_full_name()}"
