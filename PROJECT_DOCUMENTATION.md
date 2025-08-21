# My University Services - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Database Models](#database-models)
6. [API Documentation](#api-documentation)
7. [Frontend Implementation](#frontend-implementation)
8. [Mobile App Architecture](#mobile-app-architecture)
9. [Installation & Setup](#installation--setup)
10. [Configuration](#configuration)
11. [Security Features](#security-features)
12. [Deployment Guide](#deployment-guide)
13. [Development Workflow](#development-workflow)
14. [Testing](#testing)
15. [Troubleshooting](#troubleshooting)

## Project Overview

**My University Services** is a comprehensive digital platform designed to streamline university operations and enhance student experience. The system consists of two main components:

- **Web Application**: Django-based platform with student portal and staff control panel
- **Mobile Application**: Flutter-based mobile app for students

### Key Features

#### Student Portal (Phase 1)
- **Secure Authentication**: JWT-based authentication with role-based access control
- **Digital Student ID**: QR code-enabled digital identification
- **E-Services**: Online service requests and document management
- **Financial Center**: Fee management, payment processing, and financial reporting
- **Document Inbox**: Secure document delivery and management
- **Notification System**: Real-time notifications and announcements
- **Support System**: Integrated ticketing system for student support

#### Staff Control Panel (Phase 2)
- **Request Management**: Workflow-based request processing
- **Financial Management**: Fee collection, payment verification, and reporting
- **Student Affairs**: Student data management and academic records
- **Announcement System**: University-wide communication management
- **Analytics Dashboard**: Real-time statistics and reporting
- **System Configuration**: Centralized system settings management

#### Mobile Application
- **Cross-platform**: Flutter-based app for iOS and Android
- **API Integration**: RESTful API integration with the Django backend
- **Offline Capabilities**: Local data caching and offline functionality
- **Push Notifications**: Real-time notification delivery

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter App   │    │   Web Frontend  │    │  Staff Panel    │
│   (Mobile)      │    │   (Students)    │    │   (Staff)       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴───────────┐
                    │     Django Backend      │
                    │   (REST API + Views)    │
                    └─────────────┬───────────┘
                                  │
                    ┌─────────────┴───────────┐
                    │     PostgreSQL DB       │
                    │   (Primary Database)    │
                    └─────────────────────────┘
                                  │
                    ┌─────────────┴───────────┐
                    │     Redis + Celery      │
                    │   (Task Queue/Cache)    │
                    └─────────────────────────┘
```

### Component Architecture

#### Backend Components
- **Django Core**: Main application framework
- **Django REST Framework**: API development
- **JWT Authentication**: Token-based authentication
- **Celery**: Asynchronous task processing
- **Redis**: Caching and message broker
- **PostgreSQL**: Primary database

#### Frontend Components
- **Django Templates**: Server-side rendering
- **Tailwind CSS**: Utility-first CSS framework
- **Alpine.js**: Lightweight JavaScript framework
- **Font Awesome**: Icon library

#### Mobile Components
- **Flutter**: Cross-platform mobile framework
- **Dart**: Programming language
- **HTTP Client**: API communication
- **Local Storage**: Data persistence

## Technology Stack

### Backend Technologies
- **Framework**: Django 5.2.5
- **API**: Django REST Framework 3.16.1
- **Authentication**: Django REST Framework SimpleJWT 5.5.1
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Task Queue**: Celery 5.5.3
- **Cache/Broker**: Redis
- **File Processing**: Pillow 11.3.0, openpyxl 3.1.5

### Frontend Technologies
- **CSS Framework**: Tailwind CSS (CDN)
- **JavaScript**: Alpine.js (CDN)
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Tajawal, IBM Plex Sans Arabic)
- **Template Engine**: Django Templates

### Mobile Technologies
- **Framework**: Flutter
- **Language**: Dart
- **State Management**: Provider/Bloc (to be implemented)
- **HTTP Client**: dio/http
- **Local Storage**: SharedPreferences/Hive

### Development Tools
- **Version Control**: Git
- **Package Management**: pip (Python), pub (Dart)
- **Environment Management**: virtualenv/conda
- **Code Quality**: flake8, black (Python), dartfmt (Dart)

## Project Structure

### Django Backend Structure

```
univ_services/
├── accounts/                    # User management and authentication
│   ├── accounts_api/           # API endpoints for authentication
│   ├── migrations/             # Database migrations
│   ├── management/             # Custom management commands
│   ├── models.py              # User models and profiles
│   ├── serializers.py         # API serializers
│   ├── views.py               # Web views
│   └── forms.py               # Django forms
├── student_portal/             # Student-specific functionality
│   ├── student_api/           # Student API endpoints
│   ├── migrations/            # Database migrations
│   ├── models.py              # Student-related models
│   ├── views.py               # Student portal views
│   └── forms.py               # Student forms
├── staff_panel/               # Staff management system
│   ├── staff_api/             # Staff API endpoints
│   ├── migrations/            # Database migrations
│   ├── models.py              # Staff and system models
│   ├── views.py               # Staff panel views
│   └── context_processors.py  # Template context processors
├── financial/                 # Financial management
│   ├── financial_api/         # Financial API endpoints
│   ├── migrations/            # Database migrations
│   ├── models.py              # Financial models
│   └── views.py               # Financial views
├── notifications/             # Notification system
│   ├── notifications_api/     # Notification API endpoints
│   ├── migrations/            # Database migrations
│   ├── models.py              # Notification models
│   └── views.py               # Notification views
├── templates/                 # Django templates
│   ├── base/                  # Base templates
│   ├── accounts/              # Authentication templates
│   ├── student_portal/        # Student portal templates
│   ├── staff_panel/           # Staff panel templates
│   ├── financial/             # Financial templates
│   └── notifications/         # Notification templates
├── static/                    # Static files
│   ├── css/                   # Custom CSS files
│   ├── js/                    # JavaScript files
│   ├── images/                # Image assets
│   └── fonts/                 # Font files
├── univ_services/             # Main Django project
│   ├── settings.py            # Django settings
│   ├── urls.py                # URL configuration
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
├── manage.py                  # Django management script
└── requirements.txt           # Python dependencies
```

### Flutter Mobile App Structure

```
studnet_mobile/
├── lib/
│   ├── core/                  # Core functionality
│   │   ├── constants/         # App constants
│   │   ├── network/           # Network layer
│   │   ├── utils/             # Utility functions
│   │   └── theme/             # App theming
│   ├── features/              # Feature modules
│   │   ├── auth/              # Authentication feature
│   │   ├── dashboard/         # Dashboard feature
│   │   ├── profile/           # Profile management
│   │   ├── services/          # Service requests
│   │   ├── financial/         # Financial features
│   │   └── notifications/     # Notifications
│   ├── shared/                # Shared components
│   │   ├── widgets/           # Reusable widgets
│   │   ├── models/            # Data models
│   │   └── services/          # Shared services
│   └── main.dart              # App entry point
├── android/                   # Android-specific files
├── ios/                       # iOS-specific files
├── web/                       # Web-specific files
├── pubspec.yaml               # Flutter dependencies
└── pubspec.lock               # Dependency lock file
```

## Database Models

### User Management (accounts/models.py)

#### CustomUser Model
```python
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Features:**
- Extends Django's AbstractUser
- Role-based user types (student, staff, admin)
- Profile management with picture upload
- Verification status tracking
- Timestamp tracking for audit purposes

#### StudentProfile Model
```python
class StudentProfile(models.Model):
    ACADEMIC_YEAR_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
        ('graduate', 'Graduate'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    major = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=10, choices=ACADEMIC_YEAR_CHOICES)
    department = models.CharField(max_length=100)
    enrollment_date = models.DateField()
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='active')
```

**Key Features:**
- One-to-one relationship with CustomUser
- Academic information management
- GPA tracking
- Student status management

#### StaffProfile Model
```python
class StaffProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    permissions = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
```

**Key Features:**
- Staff-specific information
- Department and position tracking
- JSON-based permissions system
- Active status management

### Student Portal (student_portal/models.py)

#### ServiceRequest Model
```python
class ServiceRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('transcript', 'Official Transcript'),
        ('enrollment_cert', 'Enrollment Certificate'),
        ('graduation_cert', 'Graduation Certificate'),
        ('grade_report', 'Grade Report'),
        ('letter_of_rec', 'Letter of Recommendation'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey('accounts.StaffProfile', on_delete=models.SET_NULL, null=True, blank=True)
    processing_notes = models.TextField(blank=True)
    attachments = models.JSONField(default=list)
```

**Key Features:**
- Comprehensive service request management
- Status tracking with workflow support
- Priority-based processing
- Staff assignment and processing notes
- File attachment support via JSON field
- Due date management

#### SupportTicket Model
```python
class SupportTicket(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical Issue'),
        ('academic', 'Academic Support'),
        ('financial', 'Financial Inquiry'),
        ('general', 'General Question'),
    ]
    
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey('accounts.StaffProfile', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
```

**Key Features:**
- Categorized support system
- Priority-based ticket management
- Staff assignment capabilities
- Resolution tracking
- Status workflow management

#### Document Model
```python
class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('transcript', 'Official Transcript'),
        ('certificate', 'Certificate'),
        ('letter', 'Official Letter'),
        ('report', 'Report'),
        ('other', 'Other'),
    ]
    
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file_path = models.FileField(upload_to='documents/')
    description = models.TextField(blank=True)
    is_official = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)
    is_downloaded = models.BooleanField(default=False)
```

**Key Features:**
- Secure document management
- Document type categorization
- Official document marking
- Download tracking
- Expiration date support
- File upload handling

### Financial Management (financial/models.py)

#### Fee Model
```python
class Fee(models.Model):
    FEE_TYPE_CHOICES = [
        ('tuition', 'Tuition Fee'),
        ('registration', 'Registration Fee'),
        ('library', 'Library Fee'),
        ('lab', 'Laboratory Fee'),
        ('graduation', 'Graduation Fee'),
        ('late_payment', 'Late Payment Fee'),
        ('other', 'Other Fee'),
    ]
    
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    academic_year = models.CharField(max_length=10)
    semester = models.CharField(max_length=20)
```

**Key Features:**
- Comprehensive fee management
- Multiple fee type support
- Payment status tracking
- Academic period association
- Due date management

#### Payment Model
```python
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('online', 'Online Payment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE)
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    verified_by = models.ForeignKey('accounts.StaffProfile', on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    receipt_file = models.FileField(upload_to='receipts/', null=True, blank=True)
    notes = models.TextField(blank=True)
```

**Key Features:**
- Multiple payment method support
- Transaction tracking with unique IDs
- Staff verification workflow
- Receipt file management
- Payment status management

#### FinancialReport Model
```python
class FinancialReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('student_statement', 'Student Financial Statement'),
        ('payment_history', 'Payment History'),
        ('outstanding_fees', 'Outstanding Fees Report'),
        ('revenue_report', 'Revenue Report'),
    ]
    
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE, null=True, blank=True)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    generated_by = models.ForeignKey('accounts.StaffProfile', on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.FileField(upload_to='reports/')
    parameters = models.JSONField(default=dict)
```

**Key Features:**
- Multiple report types
- Student-specific and system-wide reports
- Staff generation tracking
- Parameterized report generation
- File-based report storage

### Notification System (notifications/models.py)

#### Notification Model
```python
class Notification(models.Model):
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('announcement', 'Announcement'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='info')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    action_url = models.URLField(blank=True)
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
```

**Key Features:**
- Multi-type notification system
- Priority-based notifications
- Read status tracking
- Expiration date support
- Action URL for interactive notifications
- Utility methods for status management

#### Announcement Model
```python
class Announcement(models.Model):
    AUDIENCE_CHOICES = [
        ('all', 'All Users'),
        ('students', 'All Students'),
        ('staff', 'All Staff'),
        ('specific_major', 'Specific Major'),
        ('specific_year', 'Specific Academic Year'),
        ('specific_department', 'Specific Department'),
    ]
    
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    target_major = models.CharField(max_length=100, blank=True)
    target_year = models.CharField(max_length=10, blank=True)
    target_department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')
    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('accounts.StaffProfile', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def is_published(self):
        return self.is_active and self.publish_date <= timezone.now()
    
    def is_expired(self):
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False
    
    def get_target_users(self):
        # Implementation for getting target users based on audience
        pass
    
    def send_notifications(self):
        # Implementation for sending notifications to target users
        pass
```

**Key Features:**
- Targeted announcement system
- Multiple audience types
- Urgency levels
- Publication scheduling
- View count tracking
- Automatic notification generation

#### NotificationTemplate Model
```python
class NotificationTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(max_length=15, choices=Notification.TYPE_CHOICES)
    subject_template = models.CharField(max_length=200)
    message_template = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def render(self, context):
        # Template rendering implementation
        pass
```

**Key Features:**
- Reusable notification templates
- Template-based message generation
- Context-aware rendering
- Centralized template management

#### NotificationPreference Model
```python
class NotificationPreference(models.Model):
    DIGEST_FREQUENCY_CHOICES = [
        ('immediate', 'Immediate'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
    ]
    
    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE)
    email_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)
    announcement_notifications = models.BooleanField(default=True)
    request_update_notifications = models.BooleanField(default=True)
    payment_notifications = models.BooleanField(default=True)
    fee_reminder_notifications = models.BooleanField(default=True)
    digest_frequency = models.CharField(max_length=15, choices=DIGEST_FREQUENCY_CHOICES, default='immediate')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Features:**
- User-specific notification preferences
- Multiple notification channels
- Category-based preferences
- Digest frequency options
- Default preference management

### Staff Panel (staff_panel/models.py)

#### DashboardStats Model
```python
class DashboardStats(models.Model):
    date = models.DateField(unique=True)
    total_students = models.PositiveIntegerField(default=0)
    new_students_today = models.PositiveIntegerField(default=0)
    total_requests = models.PositiveIntegerField(default=0)
    pending_requests = models.PositiveIntegerField(default=0)
    completed_requests = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_support_tickets = models.PositiveIntegerField(default=0)
    open_support_tickets = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_stats(self):
        # Implementation for calculating daily statistics
        pass
```

**Key Features:**
- Daily statistics tracking
- Comprehensive metrics collection
- Automatic calculation methods
- Financial and operational metrics
- Historical data preservation

#### StaffActivity Model
```python
class StaffActivity(models.Model):
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('request_approved', 'Request Approved'),
        ('request_rejected', 'Request Rejected'),
        ('payment_verified', 'Payment Verified'),
        ('document_generated', 'Document Generated'),
        ('announcement_created', 'Announcement Created'),
        ('user_created', 'User Created'),
        ('system_config_changed', 'System Configuration Changed'),
    ]
    
    staff = models.ForeignKey('accounts.StaffProfile', on_delete=models.CASCADE)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    target_model = models.CharField(max_length=50, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Key Features:**
- Comprehensive audit logging
- Action categorization
- Target object tracking
- IP and user agent logging
- Detailed activity descriptions

#### WorkflowTemplate Model
```python
class WorkflowTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    workflow_type = models.CharField(max_length=50)
    steps = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('accounts.StaffProfile', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Features:**
- Workflow template management
- JSON-based step definitions
- Template versioning support
- Creator tracking
- Active status management

#### QuickAction Model
```python
class QuickAction(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    action_type = models.CharField(max_length=50)
    url_pattern = models.CharField(max_length=200)
    icon = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    required_permissions = models.JSONField(default=list)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Key Features:**
- Dashboard quick actions
- Permission-based access control
- Customizable action types
- Icon and ordering support
- URL pattern matching

#### SystemConfiguration Model
```python
class SystemConfiguration(models.Model):
    CONFIG_TYPE_CHOICES = [
        ('general', 'General Settings'),
        ('academic', 'Academic Settings'),
        ('financial', 'Financial Settings'),
        ('notification', 'Notification Settings'),
        ('security', 'Security Settings'),
    ]
    
    config_type = models.CharField(max_length=20, choices=CONFIG_TYPE_CHOICES)
    key = models.CharField(max_length=100)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['config_type', 'key']
    
    @classmethod
    def get_value(cls, config_type, key, default=None):
        # Implementation for getting configuration values
        pass
    
    @classmethod
    def set_value(cls, config_type, key, value, description=''):
        # Implementation for setting configuration values
        pass
```

**Key Features:**
- Centralized configuration management
- Type-based configuration grouping
- Key-value storage system
- Default value support
- Configuration description support

## API Documentation

### Authentication Endpoints

#### POST /api/accounts/login/
**Description**: Authenticate user and return JWT tokens

**Request Body**:
```json
{
    "username": "string",
    "password": "string"
}
```

**Response (200)**:
```json
{
    "access_token": "string",
    "refresh_token": "string",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "user_type": "string",
        "first_name": "string",
        "last_name": "string",
        "profile_picture": "string",
        "is_verified": "boolean"
    }
 }
 ```

### Celery Configuration

#### celery.py
```python
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_services.settings.development')

app = Celery('university_services')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'send-daily-notifications': {
        'task': 'notifications.tasks.send_daily_notifications',
        'schedule': 60.0 * 60.0 * 24,  # Daily
    },
    'cleanup-expired-tokens': {
        'task': 'accounts.tasks.cleanup_expired_tokens',
        'schedule': 60.0 * 60.0 * 6,  # Every 6 hours
    },
    'generate-financial-reports': {
        'task': 'financial.tasks.generate_daily_reports',
        'schedule': 60.0 * 60.0 * 24,  # Daily at midnight
    },
}

app.conf.timezone = 'UTC'
```

## Security Features

### Authentication & Authorization

#### JWT Token Security
- **Access Token Lifetime**: 15 minutes (configurable)
- **Refresh Token Lifetime**: 7 days (configurable)
- **Token Rotation**: Automatic refresh token rotation
- **Token Blacklisting**: Blacklist tokens after rotation
- **Secure Headers**: Authorization header with Bearer token

#### Password Security
```python
# Custom password validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'accounts.validators.CustomPasswordValidator',
    },
]
```

#### Custom Password Validator
```python
# accounts/validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.findall(r'[A-Z]', password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        if not re.findall(r'[a-z]', password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter."),
                code='password_no_lower',
            )
        if not re.findall(r'\d', password):
            raise ValidationError(
                _("Password must contain at least one digit."),
                code='password_no_digit',
            )
        if not re.findall(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Password must contain at least one special character."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character."
        )
```

### CSRF Protection

#### CSRF Settings
```python
# CSRF Protection
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]
```

#### CSRF Token in Templates
```html
<!-- In forms -->
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>

<!-- In AJAX requests -->
<script>
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Use in fetch requests
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify(data)
});
</script>
```

### File Upload Security

#### File Validation
```python
# utils/file_validators.py
import os
import magic
from django.core.exceptions import ValidationError
from django.conf import settings

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')

def validate_file_size(value):
    filesize = value.size
    if filesize > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise ValidationError("File too large. Size should not exceed 10 MB.")

def validate_file_type(value):
    file_mime = magic.from_buffer(value.read(1024), mime=True)
    value.seek(0)  # Reset file pointer
    
    allowed_mimes = {
        'application/pdf': ['.pdf'],
        'application/msword': ['.doc'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
    }
    
    if file_mime not in allowed_mimes:
        raise ValidationError('Invalid file type.')
    
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed_mimes[file_mime]:
        raise ValidationError('File extension does not match file type.')
```

#### Secure File Storage
```python
# models.py
import uuid
import os
from django.db import models
from django.contrib.auth import get_user_model
from .validators import validate_file_extension, validate_file_size, validate_file_type

User = get_user_model()

def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    return f'user_{instance.user.id}/{filename}'

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to=user_directory_path,
        validators=[
            validate_file_extension,
            validate_file_size,
            validate_file_type,
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def delete(self, *args, **kwargs):
        # Delete file from storage when model is deleted
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)
```

### Rate Limiting

#### Django Rate Limiting
```python
# Install django-ratelimit
# pip install django-ratelimit

from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def api_login(request):
    # Login logic here
    pass

@ratelimit(key='user', rate='100/h', method='GET', block=True)
def api_user_profile(request):
    # Profile logic here
    pass

# Custom rate limit exceeded handler
def ratelimited(request, exception):
    return JsonResponse({
        'error': 'Rate limit exceeded. Please try again later.',
        'detail': 'Too many requests'
    }, status=429)
```

### SQL Injection Prevention

#### Safe Database Queries
```python
# Good - Using Django ORM (automatically escaped)
users = User.objects.filter(username=username)

# Good - Using parameterized queries
from django.db import connection

def get_user_by_id(user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM accounts_customuser WHERE id = %s", [user_id])
        return cursor.fetchone()

# Bad - Never do this (vulnerable to SQL injection)
# cursor.execute(f"SELECT * FROM accounts_customuser WHERE id = {user_id}")
```

### XSS Prevention

#### Template Auto-escaping
```html
<!-- Django templates auto-escape by default -->
<p>{{ user.username }}</p>  <!-- Safe -->

<!-- To disable escaping (use with caution) -->
<p>{{ content|safe }}</p>

<!-- For user-generated content, use additional filters -->
<p>{{ user_content|escape|linebreaks }}</p>
```

#### Content Security Policy
```python
# settings.py
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",  # Only for development
    "https://cdn.tailwindcss.com",
    "https://unpkg.com",
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://fonts.googleapis.com",
    "https://cdn.tailwindcss.com",
)
CSP_FONT_SRC = (
    "'self'",
    "https://fonts.gstatic.com",
)
CSP_IMG_SRC = ("'self'", "data:", "https:")
```

## Deployment

### Production Settings

#### settings/production.py
```python
from .base import *
import dj_database_url

# Security Settings
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')

# Database
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

# Static Files (AWS S3 or similar)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Static files settings
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Media files settings
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/university_services.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'university_services': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = config('SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)
ADMINS = [('Admin', config('ADMIN_EMAIL'))]
```

### Docker Production Setup

#### docker-compose.prod.yml
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    depends_on:
      - web
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    restart: unless-stopped

  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: gunicorn university_services.wsgi:application --bind 0.0.0.0:8000 --workers 3
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    expose:
      - 8000
    env_file:
      - .env.prod
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A university_services worker --loglevel=info
    volumes:
      - media_volume:/app/media
    env_file:
      - .env.prod
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A university_services beat --loglevel=info
    env_file:
      - .env.prod
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

#### Dockerfile.prod
```dockerfile
# Multi-stage build
FROM python:3.9-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.9-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        netcat \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput --settings=university_services.settings.production

EXPOSE 8000

CMD ["gunicorn", "university_services.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    upstream web {
        server web:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        client_max_body_size 10M;

        location / {
            proxy_pass http://web;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
        }

        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /var/www/media/;
            expires 1y;
            add_header Cache-Control "public";
        }

        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:;" always;
    }
}
```

### Deployment Checklist

#### Pre-deployment
- [ ] Update `ALLOWED_HOSTS` in production settings
- [ ] Set `DEBUG = False`
- [ ] Configure secure database connection
- [ ] Set up SSL certificates
- [ ] Configure static file storage (S3, CDN)
- [ ] Set up email backend
- [ ] Configure logging
- [ ] Set up monitoring (Sentry, New Relic)
- [ ] Run security checks: `python manage.py check --deploy`
- [ ] Update dependencies: `pip list --outdated`
- [ ] Run tests: `python manage.py test`

#### Deployment Steps
1. **Backup Database**
   ```bash
   pg_dump university_services > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Deploy Code**
   ```bash
   git pull origin main
   pip install -r requirements.txt
   python manage.py collectstatic --noinput
   python manage.py migrate
   ```

3. **Restart Services**
   ```bash
   sudo systemctl restart gunicorn
   sudo systemctl restart celery
   sudo systemctl restart nginx
   ```

4. **Verify Deployment**
   - Check application logs
   - Test critical functionality
   - Monitor error rates
   - Verify SSL certificate

## Development Workflow

### Git Workflow

#### Branch Strategy
```
main (production)
├── develop (integration)
│   ├── feature/user-authentication
│   ├── feature/student-dashboard
│   ├── feature/payment-system
│   └── hotfix/security-patch
└── release/v1.0.0
```

#### Commit Message Convention
```
type(scope): description

Types:
- feat: new feature
- fix: bug fix
- docs: documentation
- style: formatting
- refactor: code restructuring
- test: adding tests
- chore: maintenance

Examples:
feat(auth): add JWT token refresh functionality
fix(student): resolve dashboard loading issue
docs(api): update authentication endpoints
```

### Code Quality

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
        args: [--profile=black]
```

#### Code Style Configuration

**pyproject.toml**
```toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
(
  /(
      \.eggs
    | \.git
    | \.hg
    | \.mypy_cache
    | \.tox
    | \.venv
    | _build
    | buck-out
    | build
    | dist
    | migrations
  )/
)
'''

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88
skip_glob = ["*/migrations/*"]
```

## Testing

### Backend Testing (Django)

#### Test Structure
```
tests/
├── __init__.py
├── test_models.py
├── test_views.py
├── test_api.py
├── test_forms.py
├── test_utils.py
└── fixtures/
    ├── users.json
    └── sample_data.json
```

#### Model Tests
```python
# tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from accounts.models import StudentProfile

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'student'
        }
    
    def test_create_user(self):
        user = User.objects.create_user(
            password='testpass123',
            **self.user_data
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
    
    def test_user_str_representation(self):
        user = User.objects.create_user(
            password='testpass123',
            **self.user_data
        )
        self.assertEqual(str(user), 'testuser')
    
    def test_student_profile_creation(self):
        user = User.objects.create_user(
            password='testpass123',
            **self.user_data
        )
        profile = StudentProfile.objects.create(
            user=user,
            student_id='STU001',
            major='Computer Science',
            academic_year='2023-2024',
            department='Engineering'
        )
        self.assertEqual(profile.student_id, 'STU001')
        self.assertEqual(profile.user, user)
```

#### API Tests
```python
# tests/test_api.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AuthenticationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='student'
        )
        self.login_url = reverse('accounts_api:login')
        self.profile_url = reverse('accounts_api:profile')
    
    def test_user_login_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_profile_authenticated(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_user_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

#### Test Coverage
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Frontend Testing (Flutter)

#### Unit Tests
```dart
// test/unit/auth_service_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:university_services/features/auth/data/services/auth_service.dart';
import 'package:university_services/features/auth/data/models/user_model.dart';

class MockApiClient extends Mock implements ApiClient {}
class MockStorageService extends Mock implements StorageService {}

void main() {
  group('AuthService', () {
    late AuthService authService;
    late MockApiClient mockApiClient;
    late MockStorageService mockStorageService;

    setUp(() {
      mockApiClient = MockApiClient();
      mockStorageService = MockStorageService();
      authService = AuthService();
    });

    test('login should return LoginResponse on success', () async {
      // Arrange
      final mockResponse = {
        'access_token': 'mock_access_token',
        'refresh_token': 'mock_refresh_token',
        'user': {
          'id': 1,
          'username': 'testuser',
          'email': 'test@example.com',
          'user_type': 'student',
          'first_name': 'Test',
          'last_name': 'User',
          'is_verified': true,
          'created_at': '2023-01-01T00:00:00Z',
        }
      };

      when(mockApiClient.post(
        '/accounts/login/',
        data: anyNamed('data'),
      )).thenAnswer((_) async => Response(
        data: mockResponse,
        statusCode: 200,
        requestOptions: RequestOptions(path: '/accounts/login/'),
      ));

      // Act
      final result = await authService.login('testuser', 'password123');

      // Assert
      expect(result.accessToken, 'mock_access_token');
      expect(result.refreshToken, 'mock_refresh_token');
      expect(result.user.username, 'testuser');
    });

    test('login should throw exception on invalid credentials', () async {
      // Arrange
      when(mockApiClient.post(
        '/accounts/login/',
        data: anyNamed('data'),
      )).thenThrow(DioException(
        requestOptions: RequestOptions(path: '/accounts/login/'),
        response: Response(
          statusCode: 401,
          data: {'detail': 'Invalid credentials'},
          requestOptions: RequestOptions(path: '/accounts/login/'),
        ),
      ));

      // Act & Assert
      expect(
        () => authService.login('testuser', 'wrongpassword'),
        throwsA(isA<NetworkException>()),
      );
    });
  });
}
```

#### Widget Tests
```dart
// test/widget/login_page_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:university_services/features/auth/presentation/pages/login_page.dart';
import 'package:university_services/features/auth/presentation/providers/auth_provider.dart';

void main() {
  group('LoginPage Widget Tests', () {
    late AuthProvider mockAuthProvider;

    setUp(() {
      mockAuthProvider = MockAuthProvider();
    });

    testWidgets('should display login form', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<AuthProvider>(
            create: (_) => mockAuthProvider,
            child: const LoginPage(),
          ),
        ),
      );

      expect(find.text('University Services'), findsOneWidget);
      expect(find.text('Sign in to your account'), findsOneWidget);
      expect(find.byType(TextFormField), findsNWidgets(2));
      expect(find.text('Sign In'), findsOneWidget);
    });

    testWidgets('should validate empty fields', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<AuthProvider>(
            create: (_) => mockAuthProvider,
            child: const LoginPage(),
          ),
        ),
      );

      // Tap login button without entering credentials
      await tester.tap(find.text('Sign In'));
      await tester.pump();

      expect(find.text('Please enter your username'), findsOneWidget);
      expect(find.text('Please enter your password'), findsOneWidget);
    });

    testWidgets('should call login on valid form submission', (WidgetTester tester) async {
      when(mockAuthProvider.login(any, any)).thenAnswer((_) async {});

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<AuthProvider>(
            create: (_) => mockAuthProvider,
            child: const LoginPage(),
          ),
        ),
      );

      // Enter valid credentials
      await tester.enterText(find.byType(TextFormField).first, 'testuser');
      await tester.enterText(find.byType(TextFormField).last, 'password123');
      
      // Tap login button
      await tester.tap(find.text('Sign In'));
      await tester.pump();

      verify(mockAuthProvider.login('testuser', 'password123')).called(1);
    });
  });
}
```

### Integration Tests

#### End-to-End Testing
```dart
// integration_test/app_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:university_services/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('App Integration Tests', () {
    testWidgets('complete login flow', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Verify login page is displayed
      expect(find.text('University Services'), findsOneWidget);
      expect(find.text('Sign in to your account'), findsOneWidget);

      // Enter credentials
      await tester.enterText(
        find.byKey(const Key('username_field')),
        'testuser',
      );
      await tester.enterText(
        find.byKey(const Key('password_field')),
        'password123',
      );

      // Tap login button
      await tester.tap(find.byKey(const Key('login_button')));
      await tester.pumpAndSettle();

      // Verify navigation to dashboard
      expect(find.text('Dashboard'), findsOneWidget);
      expect(find.text('Welcome back'), findsOneWidget);
    });

    testWidgets('navigation between screens', (WidgetTester tester) async {
      // Login first
      await _performLogin(tester);

      // Navigate to profile
      await tester.tap(find.byIcon(Icons.person));
      await tester.pumpAndSettle();
      expect(find.text('Profile'), findsOneWidget);

      // Navigate to services
      await tester.tap(find.byIcon(Icons.list));
      await tester.pumpAndSettle();
      expect(find.text('Services'), findsOneWidget);

      // Navigate back to dashboard
      await tester.tap(find.byIcon(Icons.home));
      await tester.pumpAndSettle();
      expect(find.text('Dashboard'), findsOneWidget);
    });
  });
}

Future<void> _performLogin(WidgetTester tester) async {
  await tester.enterText(
    find.byKey(const Key('username_field')),
    'testuser',
  );
  await tester.enterText(
    find.byKey(const Key('password_field')),
    'password123',
  );
  await tester.tap(find.byKey(const Key('login_button')));
  await tester.pumpAndSettle();
}
```

## Troubleshooting

### Common Issues

#### Database Connection Issues

**Problem**: `django.db.utils.OperationalError: could not connect to server`

**Solutions**:
1. Check PostgreSQL service status:
   ```bash
   # Windows
   net start postgresql-x64-13
   
   # Linux/macOS
   sudo systemctl start postgresql
   ```

2. Verify database credentials in `.env`:
   ```env
   DB_NAME=university_services
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. Test database connection:
   ```bash
   psql -h localhost -U your_username -d university_services
   ```

#### Migration Issues

**Problem**: `django.db.migrations.exceptions.InconsistentMigrationHistory`

**Solutions**:
1. Reset migrations (development only):
   ```bash
   # Delete migration files (keep __init__.py)
   find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
   find . -path "*/migrations/*.pyc" -delete
   
   # Create new migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Fake migrations (if database is already in sync):
   ```bash
   python manage.py migrate --fake-initial
   ```

#### Static Files Not Loading

**Problem**: CSS/JS files not loading in production

**Solutions**:
1. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

2. Check static files configuration:
   ```python
   # settings.py
   STATIC_URL = '/static/'
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   STATICFILES_DIRS = [BASE_DIR / 'static']
   ```

3. Configure web server (Nginx example):
   ```nginx
   location /static/ {
       alias /path/to/staticfiles/;
   }
   ```

#### Celery Worker Not Starting

**Problem**: `kombu.exceptions.OperationalError: [Errno 111] Connection refused`

**Solutions**:
1. Start Redis server:
   ```bash
   # Windows (if using Redis for Windows)
   redis-server
   
   # Linux/macOS
   sudo systemctl start redis
   ```

2. Check Redis connection:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

3. Verify Celery configuration:
   ```python
   # settings.py
   CELERY_BROKER_URL = 'redis://localhost:6379/0'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
   ```

#### JWT Token Issues

**Problem**: `Token is invalid or expired`

**Solutions**:
1. Check token expiration settings:
   ```python
   # settings.py
   SIMPLE_JWT = {
       'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
       'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
       'ROTATE_REFRESH_TOKENS': True,
   }
   ```

2. Implement token refresh in frontend:
   ```javascript
   // Auto-refresh token before expiration
   const refreshToken = async () => {
       const refreshToken = localStorage.getItem('refresh_token');
       const response = await fetch('/api/accounts/refresh-token/', {
           method: 'POST',
           headers: {'Content-Type': 'application/json'},
           body: JSON.stringify({refresh_token: refreshToken})
       });
       const data = await response.json();
       localStorage.setItem('access_token', data.access_token);
   };
   ```

#### File Upload Issues

**Problem**: `Request Entity Too Large` or file upload fails

**Solutions**:
1. Check Django settings:
   ```python
   # settings.py
   FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
   DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE
   ```

2. Configure web server limits:
   ```nginx
   # nginx.conf
   client_max_body_size 10M;
   ```

3. Check file permissions:
   ```bash
   # Ensure media directory is writable
   chmod 755 media/
   chown -R www-data:www-data media/
   ```

### Performance Issues

#### Slow Database Queries

**Solutions**:
1. Enable query logging:
   ```python
   # settings.py
   LOGGING = {
       'loggers': {
           'django.db.backends': {
               'level': 'DEBUG',
               'handlers': ['console'],
           }
       }
   }
   ```

2. Use Django Debug Toolbar:
   ```bash
   pip install django-debug-toolbar
   ```

3. Add database indexes:
   ```python
   class Meta:
       indexes = [
           models.Index(fields=['user', 'created_at']),
           models.Index(fields=['status']),
       ]
   ```

4. Use select_related and prefetch_related:
   ```python
   # Optimize queries
   users = User.objects.select_related('student_profile').all()
   requests = ServiceRequest.objects.prefetch_related('documents').all()
   ```

#### Memory Issues

**Solutions**:
1. Monitor memory usage:
   ```bash
   # Install memory profiler
   pip install memory-profiler
   
   # Profile memory usage
   @profile
   def my_function():
       # Your code here
       pass
   ```

2. Use pagination for large datasets:
   ```python
   # views.py
   from django.core.paginator import Paginator
   
   def list_view(request):
       objects = MyModel.objects.all()
       paginator = Paginator(objects, 25)  # 25 items per page
       page = request.GET.get('page')
       objects = paginator.get_page(page)
       return render(request, 'list.html', {'objects': objects})
   ```

3. Implement caching:
   ```python
   # Install Redis cache
   pip install django-redis
   
   # settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }
   
   # Use caching in views
   from django.core.cache import cache
   
   def expensive_view(request):
       result = cache.get('expensive_data')
       if result is None:
           result = expensive_computation()
           cache.set('expensive_data', result, 300)  # Cache for 5 minutes
       return JsonResponse(result)
   ```

### Debugging Tips

#### Django Debugging

1. **Use Django Debug Toolbar**:
   ```python
   # settings.py (development only)
   if DEBUG:
       INSTALLED_APPS += ['debug_toolbar']
       MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
       INTERNAL_IPS = ['127.0.0.1']
   ```

2. **Use pdb for debugging**:
   ```python
   import pdb; pdb.set_trace()  # Set breakpoint
   ```

3. **Log debugging information**:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   def my_view(request):
       logger.debug(f'Processing request: {request.method} {request.path}')
       logger.info(f'User: {request.user}')
       # Your code here
   ```

#### Flutter Debugging

1. **Use Flutter Inspector**:
   ```bash
   flutter run
   # Press 'i' to open Flutter Inspector
   ```

2. **Debug prints**:
   ```dart
   import 'dart:developer' as developer;
   
   void debugFunction() {
     developer.log('Debug message', name: 'MyApp');
     print('Simple debug print');
   }
   ```

3. **Use debugger**:
   ```dart
   import 'dart:developer';
   
   void someFunction() {
     debugger(); // Set breakpoint
     // Your code here
   }
   ```

---

## Conclusion

This comprehensive documentation covers all aspects of the University Services system, from architecture and setup to deployment and troubleshooting. The system provides a robust, scalable solution for managing university services with modern web and mobile interfaces.

### Key Strengths
- **Modular Architecture**: Clean separation of concerns with Django apps
- **Modern Frontend**: Tailwind CSS and Alpine.js for responsive UI
- **Mobile Ready**: Flutter app with comprehensive API integration
- **Security First**: JWT authentication, CSRF protection, and secure file handling
- **Scalable**: Celery for background tasks, Redis for caching
- **Developer Friendly**: Comprehensive testing, documentation, and debugging tools

### Next Steps
- Implement additional features based on university requirements
- Set up monitoring and alerting systems
- Optimize performance based on usage patterns
- Expand mobile app functionality
- Add internationalization support

For questions or contributions, please refer to the project repository and follow the established development workflow.

### Login Page (login_page.dart)

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../widgets/login_form.dart';
import '../../dashboard/presentation/pages/dashboard_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({Key? key}) : super(key: key);
  
  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true;
  
  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
  
  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    
    setState(() {
      _isLoading = true;
    });
    
    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      await authProvider.login(
        _usernameController.text.trim(),
        _passwordController.text,
      );
      
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const DashboardPage()),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Login failed: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 60),
              
              // Logo and Title
              Column(
                children: [
                  Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      color: Theme.of(context).primaryColor,
                      borderRadius: BorderRadius.circular(60),
                    ),
                    child: const Icon(
                      Icons.school,
                      size: 60,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'University Services',
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).primaryColor,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Sign in to your account',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 48),
              
              // Login Form
              Form(
                key: _formKey,
                child: Column(
                  children: [
                    // Username Field
                    TextFormField(
                      controller: _usernameController,
                      decoration: InputDecoration(
                        labelText: 'Username or Student ID',
                        prefixIcon: const Icon(Icons.person),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: Colors.grey[50],
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your username';
                        }
                        return null;
                      },
                      textInputAction: TextInputAction.next,
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // Password Field
                    TextFormField(
                      controller: _passwordController,
                      obscureText: _obscurePassword,
                      decoration: InputDecoration(
                        labelText: 'Password',
                        prefixIcon: const Icon(Icons.lock),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePassword ? Icons.visibility : Icons.visibility_off,
                          ),
                          onPressed: () {
                            setState(() {
                              _obscurePassword = !_obscurePassword;
                            });
                          },
                        ),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: Colors.grey[50],
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your password';
                        }
                        return null;
                      },
                      textInputAction: TextInputAction.done,
                      onFieldSubmitted: (_) => _handleLogin(),
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // Login Button
                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton(
                        onPressed: _isLoading ? null : _handleLogin,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Theme.of(context).primaryColor,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          elevation: 2,
                        ),
                        child: _isLoading
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                ),
                              )
                            : const Text(
                                'Sign In',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 24),
              
              // Forgot Password
              TextButton(
                onPressed: () {
                  // Navigate to forgot password page
                },
                child: Text(
                  'Forgot Password?',
                  style: TextStyle(
                    color: Theme.of(context).primaryColor,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              
              const SizedBox(height: 48),
              
              // Footer
              Text(
                'Need help? Contact IT Support',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### State Management with Provider

#### Auth Provider (auth_provider.dart)

```dart
import 'package:flutter/foundation.dart';
import '../../../shared/services/storage_service.dart';
import '../data/services/auth_service.dart';
import '../data/models/user_model.dart';
import '../data/models/login_response.dart';

class AuthProvider with ChangeNotifier {
  final AuthService _authService = AuthService();
  final StorageService _storageService = StorageService();
  
  UserModel? _user;
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _error;
  
  // Getters
  UserModel? get user => _user;
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  // Initialize auth state
  Future<void> initialize() async {
    _setLoading(true);
    
    try {
      final isLoggedIn = await _authService.isLoggedIn();
      if (isLoggedIn) {
        _user = await _authService.getCurrentUser();
        _isAuthenticated = true;
      }
    } catch (e) {
      _setError('Failed to initialize authentication');
    } finally {
      _setLoading(false);
    }
  }
  
  // Login
  Future<void> login(String username, String password) async {
    _setLoading(true);
    _clearError();
    
    try {
      final loginResponse = await _authService.login(username, password);
      _user = loginResponse.user;
      _isAuthenticated = true;
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
      throw e;
    } finally {
      _setLoading(false);
    }
  }
  
  // Logout
  Future<void> logout() async {
    _setLoading(true);
    
    try {
      await _authService.logout();
      _user = null;
      _isAuthenticated = false;
      notifyListeners();
    } catch (e) {
      _setError('Failed to logout');
    } finally {
      _setLoading(false);
    }
  }
  
  // Refresh user data
  Future<void> refreshUser() async {
    if (!_isAuthenticated) return;
    
    try {
      _user = await _authService.getCurrentUser();
      notifyListeners();
    } catch (e) {
      _setError('Failed to refresh user data');
    }
  }
  
  // Private methods
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
  
  void _setError(String error) {
    _error = error;
    notifyListeners();
  }
  
  void _clearError() {
    _error = null;
    notifyListeners();
  }
}
```

## Installation and Setup

### Prerequisites

#### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher (for frontend build tools)
- **PostgreSQL**: 12.x or higher (recommended) or SQLite for development
- **Redis**: 6.x or higher (for Celery task queue)
- **Git**: Latest version

#### Development Tools
- **Code Editor**: VS Code, PyCharm, or similar
- **Database Client**: pgAdmin, DBeaver, or similar
- **API Testing**: Postman, Insomnia, or similar

### Backend Setup (Django)

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/university-services.git
cd university-services
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Environment Configuration
Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/university_services
# For SQLite (development only)
# DATABASE_URL=sqlite:///db.sqlite3

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# File Upload Settings
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=pdf,doc,docx,jpg,jpeg,png

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=15  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# Celery Settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security Settings
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Static Files
STATIC_URL=/static/
MEDIA_URL=/media/
STATIC_ROOT=staticfiles/
MEDIA_ROOT=media/
```

#### 5. Database Setup

**For PostgreSQL:**
```bash
# Create database
psql -U postgres
CREATE DATABASE university_services;
CREATE USER db_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE university_services TO db_user;
\q
```

**Run Migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Create Superuser
```bash
python manage.py createsuperuser
```

#### 7. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

#### 8. Load Sample Data (Optional)
```bash
python manage.py loaddata fixtures/sample_data.json
```

#### 9. Start Development Server
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A university_services worker --loglevel=info

# Terminal 3: Celery beat (for scheduled tasks)
celery -A university_services beat --loglevel=info
```

### Mobile App Setup (Flutter)

#### 1. Install Flutter
Follow the official Flutter installation guide: https://flutter.dev/docs/get-started/install

#### 2. Clone Mobile App Repository
```bash
git clone https://github.com/your-username/university-services-mobile.git
cd university-services-mobile
```

#### 3. Install Dependencies
```bash
flutter pub get
```

#### 4. Configure API Endpoints
Update `lib/core/constants/api_constants.dart`:

```dart
class ApiConstants {
  // Update these URLs to match your backend
  static const String baseUrl = 'http://your-backend-url:8000';
  static const String apiBaseUrl = '$baseUrl/api/v1';
  
  // ... rest of the configuration
}
```

#### 5. Run the App
```bash
# Check connected devices
flutter devices

# Run on specific device
flutter run -d <device-id>

# Run in debug mode
flutter run --debug

# Run in release mode
flutter run --release
```

### Docker Setup (Optional)

#### Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: university_services
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/university_services
      - REDIS_URL=redis://redis:6379/0

  celery:
    build: .
    command: celery -A university_services worker --loglevel=info
    volumes:
      - .:/code
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/university_services
      - REDIS_URL=redis://redis:6379/0

  celery-beat:
    build: .
    command: celery -A university_services beat --loglevel=info
    volumes:
      - .:/code
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/university_services
      - REDIS_URL=redis://redis:6379/0

volumes:
  postgres_data:
```

Create `Dockerfile`:

```dockerfile
FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### Run with Docker
```bash
# Build and start services
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Stop services
docker-compose down
```

## Configuration

### Django Settings

#### settings/base.py
```python
import os
from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'crispy_forms',
    'crispy_tailwind',
    'celery',
]

LOCAL_APPS = [
    'accounts',
    'student_portal',
    'staff_panel',
    'financial',
    'notifications',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'university_services.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'university_services.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=15, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS Settings
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='').split(',')

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@university.edu')

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = config('MAX_UPLOAD_SIZE', default=10485760, cast=int)  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE
ALLOWED_FILE_TYPES = config('ALLOWED_FILE_TYPES', default='pdf,doc,docx,jpg,jpeg,png').split(',')

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'university_services': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

**Error Responses**:
- 400: Invalid credentials
- 401: Account not verified
- 429: Too many login attempts

#### POST /api/accounts/logout/
**Description**: Logout user and blacklist refresh token

**Headers**: `Authorization: Bearer <access_token>`

**Request Body**:
```json
{
    "refresh_token": "string"
}
```

**Response (200)**:
```json
{
    "message": "Successfully logged out"
}
```

#### GET /api/accounts/profile/
**Description**: Get current user profile

**Headers**: `Authorization: Bearer <access_token>`

**Response (200)**:
```json
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "user_type": "string",
    "first_name": "string",
    "last_name": "string",
    "phone_number": "string",
    "date_of_birth": "date",
    "profile_picture": "string",
    "is_verified": "boolean",
    "created_at": "datetime",
    "student_profile": {
        "student_id": "string",
        "major": "string",
        "academic_year": "string",
        "department": "string",
        "gpa": "decimal",
        "status": "string"
    }
}
```

#### POST /api/accounts/refresh-token/
**Description**: Refresh access token using refresh token

**Request Body**:
```json
{
    "refresh_token": "string"
}
```

**Response (200)**:
```json
{
    "access_token": "string"
}
```

### Student Portal Endpoints

#### GET /api/student/dashboard/
**Description**: Get student dashboard data

**Headers**: `Authorization: Bearer <access_token>`

**Response (200)**:
```json
{
    "stats": {
        "pending_requests": "integer",
        "outstanding_fees": "decimal",
        "new_documents": "integer",
        "unread_notifications": "integer"
    },
    "recent_requests": [
        {
            "id": "integer",
            "request_type": "string",
            "title": "string",
            "status": "string",
            "created_at": "datetime",
            "due_date": "datetime"
        }
    ],
    "upcoming_fees": [
        {
            "id": "integer",
            "fee_type": "string",
            "amount": "decimal",
            "due_date": "date",
            "description": "string"
        }
    ]
}
```

#### POST /api/student/requests/
**Description**: Create a new service request

**Headers**: `Authorization: Bearer <access_token>`

**Request Body**:
```json
{
    "request_type": "string",
    "title": "string",
    "description": "string",
    "priority": "string",
    "attachments": ["file_urls"]
}
```

**Response (201)**:
```json
{
    "id": "integer",
    "request_type": "string",
    "title": "string",
    "description": "string",
    "status": "pending",
    "priority": "string",
    "created_at": "datetime",
    "due_date": "datetime"
}
```

#### GET /api/student/requests/
**Description**: Get student's service requests

**Headers**: `Authorization: Bearer <access_token>`

**Query Parameters**:
- `status`: Filter by status
- `request_type`: Filter by request type
- `page`: Page number
- `limit`: Items per page

**Response (200)**:
```json
{
    "count": "integer",
    "next": "string",
    "previous": "string",
    "results": [
        {
            "id": "integer",
            "request_type": "string",
            "title": "string",
            "description": "string",
            "status": "string",
            "priority": "string",
            "created_at": "datetime",
            "updated_at": "datetime",
            "due_date": "datetime",
            "processing_notes": "string",
            "attachments": ["file_urls"]
        }
    ]
}
```

#### GET /api/student/documents/
**Description**: Get student's documents

**Headers**: `Authorization: Bearer <access_token>`

**Response (200)**:
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "title": "string",
            "document_type": "string",
            "description": "string",
            "is_official": "boolean",
            "created_at": "datetime",
            "expires_at": "datetime",
            "download_count": "integer",
            "is_downloaded": "boolean",
            "download_url": "string"
        }
    ]
}
```

#### GET /api/student/fees/
**Description**: Get student's fees

**Headers**: `Authorization: Bearer <access_token>`

**Query Parameters**:
- `is_paid`: Filter by payment status
- `fee_type`: Filter by fee type
- `academic_year`: Filter by academic year

**Response (200)**:
```json
{
    "count": "integer",
    "total_outstanding": "decimal",
    "results": [
        {
            "id": "integer",
            "fee_type": "string",
            "amount": "decimal",
            "description": "string",
            "due_date": "date",
            "is_paid": "boolean",
            "academic_year": "string",
            "semester": "string",
            "created_at": "datetime"
        }
    ]
}
```

#### POST /api/student/payments/
**Description**: Submit a payment

**Headers**: `Authorization: Bearer <access_token>`

**Request Body**:
```json
{
    "fee_id": "integer",
    "amount": "decimal",
    "payment_method": "string",
    "transaction_id": "string",
    "receipt_file": "file",
    "notes": "string"
}
```

**Response (201)**:
```json
{
    "id": "integer",
    "fee_id": "integer",
    "amount": "decimal",
    "payment_method": "string",
    "transaction_id": "string",
    "status": "pending",
    "payment_date": "datetime",
    "receipt_file": "string"
}
```

### Notification Endpoints

#### GET /api/notifications/
**Description**: Get user notifications

**Headers**: `Authorization: Bearer <access_token>`

**Query Parameters**:
- `is_read`: Filter by read status
- `notification_type`: Filter by type
- `priority`: Filter by priority
- `page`: Page number
- `limit`: Items per page

**Response (200)**:
```json
{
    "count": "integer",
    "unread_count": "integer",
    "results": [
        {
            "id": "integer",
            "title": "string",
            "message": "string",
            "notification_type": "string",
            "priority": "string",
            "is_read": "boolean",
            "created_at": "datetime",
            "read_at": "datetime",
            "expires_at": "datetime",
            "action_url": "string"
        }
    ]
}
```

#### POST /api/notifications/{id}/mark-read/
**Description**: Mark notification as read

**Headers**: `Authorization: Bearer <access_token>`

**Response (200)**:
```json
{
    "message": "Notification marked as read"
}
```

#### GET /api/announcements/
**Description**: Get active announcements

**Response (200)**:
```json
{
    "count": "integer",
    "results": [
        {
            "id": "integer",
            "title": "string",
            "content": "string",
            "urgency": "string",
            "publish_date": "datetime",
            "expiry_date": "datetime",
            "view_count": "integer"
        }
    ]
}
```

### Error Response Format

All API endpoints follow a consistent error response format:

```json
{
    "error": {
        "code": "string",
        "message": "string",
        "details": "object"
    }
}
```

**Common Error Codes**:
- `AUTHENTICATION_FAILED`: Invalid or expired token
- `PERMISSION_DENIED`: Insufficient permissions
- `VALIDATION_ERROR`: Request data validation failed
- `NOT_FOUND`: Resource not found
- `RATE_LIMITED`: Too many requests
- `SERVER_ERROR`: Internal server error

### API Rate Limiting

- **Authentication endpoints**: 5 requests per minute
- **General endpoints**: 100 requests per minute
- **File upload endpoints**: 10 requests per minute

### API Versioning

The API uses URL versioning:
- Current version: `v1`
- Base URL: `/api/v1/`
- Deprecated versions are supported for 6 months

## Frontend Implementation

### Template Structure

The frontend uses Django's template system with a hierarchical structure:

```
templates/
├── base/
│   ├── base.html              # Main base template
│   ├── navbar.html            # Navigation components
│   └── footer.html            # Footer component
├── accounts/
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   └── profile.html           # Profile management
├── student_portal/
│   ├── dashboard.html         # Student dashboard
│   ├── requests.html          # Service requests
│   ├── documents.html         # Document management
│   ├── fees.html              # Fee management
│   └── support.html           # Support tickets
├── staff_panel/
│   ├── dashboard.html         # Staff dashboard
│   ├── requests.html          # Request management
│   ├── students.html          # Student management
│   └── reports.html           # Reporting interface
└── notifications/
    ├── list.html              # Notification list
    └── announcements.html     # Announcements
```

### Base Template (base.html)

```html
<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My University Services{% endblock %}</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        'arabic': ['Tajawal', 'sans-serif'],
                        'sans': ['IBM Plex Sans Arabic', 'sans-serif'],
                    }
                }
            }
        }
    </script>
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@200;300;400;500;700;800;900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@100;200;300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Alpine.js -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{% static 'css/custom.css' %}">
    <link rel="stylesheet" href="{% static 'css/forms.css' %}">
    
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-gray-50 font-sans">
    <!-- Navigation -->
    {% if user.is_authenticated %}
        {% if user.user_type == 'student' %}
            {% include 'base/student_navbar.html' %}
        {% elif user.user_type == 'staff' %}
            {% include 'base/staff_navbar.html' %}
        {% endif %}
    {% endif %}
    
    <!-- Flash Messages -->
    {% if messages %}
        <div class="fixed top-4 right-4 z-50 space-y-2" x-data="{ show: true }" x-show="show">
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} max-w-sm" x-transition>
                    <div class="flex items-center justify-between">
                        <span>{{ message }}</span>
                        <button @click="show = false" class="ml-2">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            {% endfor %}
        </div>
    {% endif %}
    
    <!-- Main Content -->
    <main class="{% if user.is_authenticated %}pt-16{% endif %}">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    {% if user.is_authenticated %}
        {% include 'base/footer.html' %}
    {% endif %}
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Tailwind CSS Integration

The project uses Tailwind CSS via CDN with custom configuration:

#### Custom Configuration
```javascript
tailwind.config = {
    theme: {
        extend: {
            fontFamily: {
                'arabic': ['Tajawal', 'sans-serif'],
                'sans': ['IBM Plex Sans Arabic', 'sans-serif'],
            },
            colors: {
                'primary': {
                    50: '#eff6ff',
                    500: '#3b82f6',
                    600: '#2563eb',
                    700: '#1d4ed8',
                },
                'secondary': {
                    50: '#f8fafc',
                    500: '#64748b',
                    600: '#475569',
                }
            }
        }
    }
}
```

#### Custom CSS Classes (custom.css)
```css
/* Font Definitions */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@200;300;400;500;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@100;200;300;400;500;600;700&display=swap');

/* Base Styles */
body {
    font-family: 'IBM Plex Sans Arabic', sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Tajawal', sans-serif;
}

/* Arabic Text Support */
.arabic-text {
    direction: rtl;
    text-align: right;
    font-family: 'Tajawal', sans-serif;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    @apply bg-gray-100;
}

::-webkit-scrollbar-thumb {
    @apply bg-gray-400 rounded-full;
}

::-webkit-scrollbar-thumb:hover {
    @apply bg-gray-500;
}

/* Card Hover Effects */
.card-hover {
    @apply transition-all duration-300 hover:shadow-lg hover:-translate-y-1;
}

/* Button Animations */
.btn-animate {
    @apply transition-all duration-200 hover:scale-105 active:scale-95;
}

/* Status Badges */
.status-pending {
    @apply bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-medium;
}

.status-approved {
    @apply bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium;
}

.status-rejected {
    @apply bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium;
}

.status-completed {
    @apply bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium;
}

/* Priority Indicators */
.priority-low {
    @apply text-green-600;
}

.priority-medium {
    @apply text-yellow-600;
}

.priority-high {
    @apply text-red-600;
}

.priority-urgent {
    @apply text-red-800 font-bold;
}

/* Loading Spinner */
.spinner {
    @apply animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600;
}

/* QR Code Container */
.qr-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    @apply p-6 rounded-lg shadow-lg;
}

/* Digital ID Card */
.digital-id-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    @apply p-6 rounded-xl shadow-xl text-white;
}

/* Dashboard Stats Cards */
.stats-card {
    @apply bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-300;
}

.stats-card-gradient-1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-card-gradient-2 {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-card-gradient-3 {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-card-gradient-4 {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

/* Form Styles */
.form-input {
    @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200;
}

.form-input:focus {
    @apply outline-none shadow-md;
}

/* File Upload Area */
.file-upload-area {
    @apply border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors duration-200;
}

.file-upload-area.dragover {
    @apply border-blue-500 bg-blue-50;
}
```

### Alpine.js Integration

Alpine.js is used for interactive components:

#### Dashboard Statistics Component
```html
<div x-data="dashboardStats()" x-init="loadStats()">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <template x-for="stat in stats" :key="stat.id">
            <div class="stats-card" :class="stat.gradient">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white text-sm font-medium" x-text="stat.label"></p>
                        <p class="text-white text-2xl font-bold" x-text="stat.value"></p>
                    </div>
                    <div class="text-white text-3xl">
                        <i :class="stat.icon"></i>
                    </div>
                </div>
            </div>
        </template>
    </div>
</div>

<script>
function dashboardStats() {
    return {
        stats: [],
        loading: false,
        
        async loadStats() {
            this.loading = true;
            try {
                const response = await fetch('/api/student/dashboard/');
                const data = await response.json();
                this.stats = [
                    {
                        id: 1,
                        label: 'Pending Requests',
                        value: data.stats.pending_requests,
                        icon: 'fas fa-clock',
                        gradient: 'stats-card-gradient-1'
                    },
                    {
                        id: 2,
                        label: 'Outstanding Fees',
                        value: `$${data.stats.outstanding_fees}`,
                        icon: 'fas fa-dollar-sign',
                        gradient: 'stats-card-gradient-2'
                    },
                    {
                        id: 3,
                        label: 'New Documents',
                        value: data.stats.new_documents,
                        icon: 'fas fa-file-alt',
                        gradient: 'stats-card-gradient-3'
                    },
                    {
                        id: 4,
                        label: 'Unread Notifications',
                        value: data.stats.unread_notifications,
                        icon: 'fas fa-bell',
                        gradient: 'stats-card-gradient-4'
                    }
                ];
            } catch (error) {
                console.error('Error loading stats:', error);
            } finally {
                this.loading = false;
            }
        }
    }
}
</script>
```

#### Notification Component
```html
<div x-data="notificationManager()" x-init="loadNotifications()">
    <!-- Notification Bell -->
    <div class="relative">
        <button @click="toggleDropdown()" class="relative p-2 text-gray-600 hover:text-gray-900">
            <i class="fas fa-bell text-xl"></i>
            <span x-show="unreadCount > 0" 
                  x-text="unreadCount" 
                  class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            </span>
        </button>
        
        <!-- Dropdown -->
        <div x-show="showDropdown" 
             x-transition
             @click.away="showDropdown = false"
             class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border z-50">
            
            <div class="p-4 border-b">
                <h3 class="font-semibold text-gray-900">Notifications</h3>
                <p class="text-sm text-gray-600" x-text="`${unreadCount} unread`"></p>
            </div>
            
            <div class="max-h-96 overflow-y-auto">
                <template x-for="notification in notifications" :key="notification.id">
                    <div class="p-4 border-b hover:bg-gray-50 cursor-pointer" 
                         :class="{ 'bg-blue-50': !notification.is_read }"
                         @click="markAsRead(notification.id)">
                        <div class="flex items-start space-x-3">
                            <div class="flex-shrink-0">
                                <i :class="getNotificationIcon(notification.notification_type)" 
                                   class="text-lg"></i>
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="text-sm font-medium text-gray-900" x-text="notification.title"></p>
                                <p class="text-sm text-gray-600" x-text="notification.message"></p>
                                <p class="text-xs text-gray-400" x-text="formatDate(notification.created_at)"></p>
                            </div>
                            <div x-show="!notification.is_read" class="flex-shrink-0">
                                <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                            </div>
                        </div>
                    </div>
                </template>
            </div>
            
            <div class="p-4 border-t">
                <button @click="markAllAsRead()" class="text-sm text-blue-600 hover:text-blue-800">
                    Mark all as read
                </button>
            </div>
        </div>
    </div>
</div>

<script>
function notificationManager() {
    return {
        notifications: [],
        unreadCount: 0,
        showDropdown: false,
        
        async loadNotifications() {
            try {
                const response = await fetch('/api/notifications/');
                const data = await response.json();
                this.notifications = data.results;
                this.unreadCount = data.unread_count;
            } catch (error) {
                console.error('Error loading notifications:', error);
            }
        },
        
        toggleDropdown() {
            this.showDropdown = !this.showDropdown;
        },
        
        async markAsRead(notificationId) {
            try {
                await fetch(`/api/notifications/${notificationId}/mark-read/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                const notification = this.notifications.find(n => n.id === notificationId);
                if (notification && !notification.is_read) {
                    notification.is_read = true;
                    this.unreadCount--;
                }
            } catch (error) {
                console.error('Error marking notification as read:', error);
            }
        },
        
        async markAllAsRead() {
            try {
                const unreadNotifications = this.notifications.filter(n => !n.is_read);
                
                for (const notification of unreadNotifications) {
                    await this.markAsRead(notification.id);
                }
                
                this.showDropdown = false;
            } catch (error) {
                console.error('Error marking all notifications as read:', error);
            }
        },
        
        getNotificationIcon(type) {
            const icons = {
                'info': 'fas fa-info-circle text-blue-500',
                'warning': 'fas fa-exclamation-triangle text-yellow-500',
                'success': 'fas fa-check-circle text-green-500',
                'error': 'fas fa-times-circle text-red-500',
                'announcement': 'fas fa-bullhorn text-purple-500'
            };
            return icons[type] || 'fas fa-bell text-gray-500';
        },
        
        formatDate(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diffInHours = (now - date) / (1000 * 60 * 60);
            
            if (diffInHours < 1) {
                return 'Just now';
            } else if (diffInHours < 24) {
                return `${Math.floor(diffInHours)}h ago`;
            } else {
                return date.toLocaleDateString();
            }
        }
    }
}
</script>
```

#### File Upload Component
```html
<div x-data="fileUpload()" class="file-upload-area" 
     @dragover.prevent="dragover = true"
     @dragleave.prevent="dragover = false"
     @drop.prevent="handleDrop($event)"
     :class="{ 'dragover': dragover }">
    
    <input type="file" 
           x-ref="fileInput" 
           @change="handleFileSelect($event)"
           multiple
           accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
           class="hidden">
    
    <div class="text-center">
        <i class="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-4"></i>
        <p class="text-lg font-medium text-gray-700 mb-2">Drop files here or click to browse</p>
        <p class="text-sm text-gray-500 mb-4">Supported formats: PDF, DOC, DOCX, JPG, PNG (Max 10MB each)</p>
        <button @click="$refs.fileInput.click()" 
                class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
            Choose Files
        </button>
    </div>
    
    <!-- File List -->
    <div x-show="files.length > 0" class="mt-6">
        <h4 class="font-medium text-gray-700 mb-3">Selected Files:</h4>
        <div class="space-y-2">
            <template x-for="(file, index) in files" :key="index">
                <div class="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                    <div class="flex items-center space-x-3">
                        <i class="fas fa-file text-gray-400"></i>
                        <div>
                            <p class="text-sm font-medium text-gray-700" x-text="file.name"></p>
                            <p class="text-xs text-gray-500" x-text="formatFileSize(file.size)"></p>
                        </div>
                    </div>
                    <button @click="removeFile(index)" 
                            class="text-red-500 hover:text-red-700">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </template>
        </div>
    </div>
</div>

<script>
function fileUpload() {
    return {
        files: [],
        dragover: false,
        maxFileSize: 10 * 1024 * 1024, // 10MB
        allowedTypes: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg', 'image/png'],
        
        handleDrop(event) {
            this.dragover = false;
            const droppedFiles = Array.from(event.dataTransfer.files);
            this.addFiles(droppedFiles);
        },
        
        handleFileSelect(event) {
            const selectedFiles = Array.from(event.target.files);
            this.addFiles(selectedFiles);
        },
        
        addFiles(newFiles) {
            for (const file of newFiles) {
                if (this.validateFile(file)) {
                    this.files.push(file);
                }
            }
        },
        
        validateFile(file) {
            if (file.size > this.maxFileSize) {
                alert(`File "${file.name}" is too large. Maximum size is 10MB.`);
                return false;
            }
            
            if (!this.allowedTypes.includes(file.type)) {
                alert(`File "${file.name}" has an unsupported format.`);
                return false;
            }
            
            return true;
        },
        
        removeFile(index) {
            this.files.splice(index, 1);
        },
        
        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
    }
}
</script>
```

### Responsive Design

The frontend is fully responsive using Tailwind's responsive utilities:

#### Breakpoint System
- `sm`: 640px and up
- `md`: 768px and up  
- `lg`: 1024px and up
- `xl`: 1280px and up
- `2xl`: 1536px and up

#### Responsive Grid Examples
```html
<!-- Dashboard Stats Grid -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Stats cards -->
</div>

<!-- Content Layout -->
<div class="flex flex-col lg:flex-row gap-6">
    <div class="lg:w-2/3">
        <!-- Main content -->
    </div>
    <div class="lg:w-1/3">
        <!-- Sidebar -->
    </div>
</div>

<!-- Navigation -->
<nav class="hidden md:flex space-x-6">
    <!-- Desktop navigation -->
</nav>
<div class="md:hidden">
    <!-- Mobile navigation -->
</div>
```

## Mobile App Architecture

### Flutter Project Structure

The Flutter mobile app follows a feature-based architecture:

```
lib/
├── core/
│   ├── constants/
│   │   ├── api_constants.dart      # API endpoints and configuration
│   │   ├── app_constants.dart      # App-wide constants
│   │   └── storage_constants.dart  # Local storage keys
│   ├── network/
│   │   ├── api_client.dart         # HTTP client configuration
│   │   ├── api_interceptor.dart    # Request/response interceptors
│   │   └── network_exceptions.dart # Network error handling
│   ├── utils/
│   │   ├── date_utils.dart         # Date formatting utilities
│   │   ├── validation_utils.dart   # Form validation
│   │   └── file_utils.dart         # File handling utilities
│   └── theme/
│       ├── app_theme.dart          # App theme configuration
│       ├── colors.dart             # Color palette
│       └── text_styles.dart        # Typography styles
├── features/
│   ├── auth/
│   │   ├── data/
│   │   │   ├── models/
│   │   │   │   ├── user_model.dart
│   │   │   │   └── login_response.dart
│   │   │   ├── repositories/
│   │   │   │   └── auth_repository.dart
│   │   │   └── services/
│   │   │       └── auth_service.dart
│   │   ├── presentation/
│   │   │   ├── pages/
│   │   │   │   ├── login_page.dart
│   │   │   │   └── register_page.dart
│   │   │   ├── widgets/
│   │   │   │   ├── login_form.dart
│   │   │   │   └── social_login_buttons.dart
│   │   │   └── providers/
│   │   │       └── auth_provider.dart
│   │   └── domain/
│   │       ├── entities/
│   │       │   └── user.dart
│   │       └── usecases/
│   │           ├── login_usecase.dart
│   │           └── logout_usecase.dart
│   ├── dashboard/
│   │   ├── data/
│   │   ├── presentation/
│   │   └── domain/
│   ├── profile/
│   ├── services/
│   ├── financial/
│   └── notifications/
├── shared/
│   ├── widgets/
│   │   ├── custom_button.dart
│   │   ├── custom_text_field.dart
│   │   ├── loading_widget.dart
│   │   └── error_widget.dart
│   ├── models/
│   │   ├── api_response.dart
│   │   └── base_model.dart
│   └── services/
│       ├── storage_service.dart
│       ├── notification_service.dart
│       └── file_service.dart
└── main.dart
```

### API Constants (api_constants.dart)

```dart
class ApiConstants {
  // Base URLs
  static const String baseUrl = 'http://10.0.2.2:8000'; // Android emulator
  static const String baseUrlIOS = 'http://localhost:8000'; // iOS simulator
  static const String apiVersion = 'v1';
  static const String apiBaseUrl = '$baseUrl/api/$apiVersion';
  
  // Authentication Endpoints
  static const String login = '$apiBaseUrl/accounts/login/';
  static const String logout = '$apiBaseUrl/accounts/logout/';
  static const String profile = '$apiBaseUrl/accounts/profile/';
  static const String refreshToken = '$apiBaseUrl/accounts/refresh-token/';
  
  // Student Endpoints
  static const String studentDashboard = '$apiBaseUrl/student/dashboard/';
  static const String serviceRequests = '$apiBaseUrl/student/requests/';
  static const String documents = '$apiBaseUrl/student/documents/';
  static const String fees = '$apiBaseUrl/student/fees/';
  static const String payments = '$apiBaseUrl/student/payments/';
  
  // Notification Endpoints
  static const String notifications = '$apiBaseUrl/notifications/';
  static const String announcements = '$apiBaseUrl/announcements/';
  
  // File Upload
  static const String fileUpload = '$apiBaseUrl/files/upload/';
  
  // Request Headers
  static const Map<String, String> defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  // Request Timeouts
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 30);
  
  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;
  
  // File Upload Limits
  static const int maxFileSize = 10 * 1024 * 1024; // 10MB
  static const List<String> allowedFileTypes = [
    'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'
  ];
}
```

### API Client (api_client.dart)

```dart
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../constants/api_constants.dart';
import '../utils/storage_service.dart';
import 'api_interceptor.dart';
import 'network_exceptions.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  ApiClient._internal();
  
  late Dio _dio;
  
  Dio get dio => _dio;
  
  void initialize() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.apiBaseUrl,
      connectTimeout: ApiConstants.connectTimeout,
      receiveTimeout: ApiConstants.receiveTimeout,
      sendTimeout: ApiConstants.sendTimeout,
      headers: ApiConstants.defaultHeaders,
    ));
    
    // Add interceptors
    _dio.interceptors.add(ApiInterceptor());
    
    if (kDebugMode) {
      _dio.interceptors.add(LogInterceptor(
        requestBody: true,
        responseBody: true,
        requestHeader: true,
        responseHeader: false,
      ));
    }
  }
  
  // GET request
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.get(
        path,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } on DioException catch (e) {
      throw NetworkExceptions.fromDioException(e);
    }
  }
  
  // POST request
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } on DioException catch (e) {
      throw NetworkExceptions.fromDioException(e);
    }
  }
  
  // PUT request
  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } on DioException catch (e) {
      throw NetworkExceptions.fromDioException(e);
    }
  }
  
  // DELETE request
  Future<Response> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.delete(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response;
    } on DioException catch (e) {
      throw NetworkExceptions.fromDioException(e);
    }
  }
  
  // File upload
  Future<Response> uploadFile(
    String path,
    String filePath, {
    Map<String, dynamic>? data,
    ProgressCallback? onSendProgress,
  }) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath),
        ...?data,
      });
      
      final response = await _dio.post(
        path,
        data: formData,
        onSendProgress: onSendProgress,
      );
      return response;
    } on DioException catch (e) {
      throw NetworkExceptions.fromDioException(e);
    }
  }
}
```

### Authentication Service (auth_service.dart)

```dart
import 'dart:convert';
import '../../../core/network/api_client.dart';
import '../../../core/constants/api_constants.dart';
import '../../../shared/services/storage_service.dart';
import '../models/user_model.dart';
import '../models/login_response.dart';

class AuthService {
  final ApiClient _apiClient = ApiClient();
  final StorageService _storageService = StorageService();
  
  // Login
  Future<LoginResponse> login(String username, String password) async {
    final response = await _apiClient.post(
      '/accounts/login/',
      data: {
        'username': username,
        'password': password,
      },
    );
    
    final loginResponse = LoginResponse.fromJson(response.data);
    
    // Store tokens
    await _storageService.setString('access_token', loginResponse.accessToken);
    await _storageService.setString('refresh_token', loginResponse.refreshToken);
    await _storageService.setString('user_data', jsonEncode(loginResponse.user.toJson()));
    
    return loginResponse;
  }
  
  // Logout
  Future<void> logout() async {
    final refreshToken = await _storageService.getString('refresh_token');
    
    if (refreshToken != null) {
      try {
        await _apiClient.post(
          '/accounts/logout/',
          data: {'refresh_token': refreshToken},
        );
      } catch (e) {
        // Continue with local logout even if server logout fails
      }
    }
    
    // Clear local storage
    await _storageService.remove('access_token');
    await _storageService.remove('refresh_token');
    await _storageService.remove('user_data');
  }
  
  // Get current user
  Future<UserModel?> getCurrentUser() async {
    final userData = await _storageService.getString('user_data');
    if (userData != null) {
      return UserModel.fromJson(jsonDecode(userData));
    }
    return null;
  }
  
  // Check if user is logged in
  Future<bool> isLoggedIn() async {
    final accessToken = await _storageService.getString('access_token');
    return accessToken != null;
  }
  
  // Refresh token
  Future<String?> refreshAccessToken() async {
    final refreshToken = await _storageService.getString('refresh_token');
    
    if (refreshToken == null) {
      return null;
    }
    
    try {
      final response = await _apiClient.post(
        '/accounts/refresh-token/',
        data: {'refresh_token': refreshToken},
      );
      
      final newAccessToken = response.data['access_token'];
      await _storageService.setString('access_token', newAccessToken);
      
      return newAccessToken;
    } catch (e) {
      // Refresh token is invalid, logout user
      await logout();
      return null;
    }
  }
  
  // Get access token
  Future<String?> getAccessToken() async {
    return await _storageService.getString('access_token');
  }
}
```

### User Model (user_model.dart)

```dart
class UserModel {
  final int id;
  final String username;
  final String email;
  final String userType;
  final String firstName;
  final String lastName;
  final String? phoneNumber;
  final DateTime? dateOfBirth;
  final String? profilePicture;
  final bool isVerified;
  final DateTime createdAt;
  final StudentProfile? studentProfile;
  final StaffProfile? staffProfile;
  
  UserModel({
    required this.id,
    required this.username,
    required this.email,
    required this.userType,
    required this.firstName,
    required this.lastName,
    this.phoneNumber,
    this.dateOfBirth,
    this.profilePicture,
    required this.isVerified,
    required this.createdAt,
    this.studentProfile,
    this.staffProfile,
  });
  
  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      username: json['username'],
      email: json['email'],
      userType: json['user_type'],
      firstName: json['first_name'],
      lastName: json['last_name'],
      phoneNumber: json['phone_number'],
      dateOfBirth: json['date_of_birth'] != null 
          ? DateTime.parse(json['date_of_birth']) 
          : null,
      profilePicture: json['profile_picture'],
      isVerified: json['is_verified'],
      createdAt: DateTime.parse(json['created_at']),
      studentProfile: json['student_profile'] != null 
          ? StudentProfile.fromJson(json['student_profile']) 
          : null,
      staffProfile: json['staff_profile'] != null 
          ? StaffProfile.fromJson(json['staff_profile']) 
          : null,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'user_type': userType,
      'first_name': firstName,
      'last_name': lastName,
      'phone_number': phoneNumber,
      'date_of_birth': dateOfBirth?.toIso8601String(),
      'profile_picture': profilePicture,
      'is_verified': isVerified,
      'created_at': createdAt.toIso8601String(),
      'student_profile': studentProfile?.toJson(),
      'staff_profile': staffProfile?.toJson(),
    };
  }
  
  String get fullName => '$firstName $lastName';
  
  String get displayName => fullName.isNotEmpty ? fullName : username;
}

class StudentProfile {
  final String studentId;
  final String major;
  final String academicYear;
  final String department;
  final double? gpa;
  final String status;
  final DateTime enrollmentDate;
  
  StudentProfile({
    required this.studentId,
    required this.major,
    required this.academicYear,
    required this.department,
    this.gpa,
    required this.status,
    required this.enrollmentDate,
  });
  
  factory StudentProfile.fromJson(Map<String, dynamic> json) {
    return StudentProfile(
      studentId: json['student_id'],
      major: json['major'],
      academicYear: json['academic_year'],
      department: json['department'],
      gpa: json['gpa']?.toDouble(),
      status: json['status'],
      enrollmentDate: DateTime.parse(json['enrollment_date']),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'student_id': studentId,
      'major': major,
      'academic_year': academicYear,
      'department': department,
      'gpa': gpa,
      'status': status,
      'enrollment_date': enrollmentDate.toIso8601String(),
    };
  }
}

class StaffProfile {
  final String employeeId;
  final String department;
  final String position;
  final DateTime hireDate;
  final Map<String, dynamic> permissions;
  final bool isActive;
  
  StaffProfile({
    required this.employeeId,
    required this.department,
    required this.position,
    required this.hireDate,
    required this.permissions,
    required this.isActive,
  });
  
  factory StaffProfile.fromJson(Map<String, dynamic> json) {
    return StaffProfile(
      employeeId: json['employee_id'],
      department: json['department'],
      position: json['position'],
      hireDate: DateTime.parse(json['hire_date']),
      permissions: json['permissions'] ?? {},
      isActive: json['is_active'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'employee_id': employeeId,
      'department': department,
      'position': position,
      'hire_date': hireDate.toIso8601String(),
      'permissions': permissions,
      'is_active': isActive,
    };
  }
}
```