from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo
from django.core.files import File
from django.core.files.storage import default_storage
from django.conf import settings
from django.db import models
from faker import Faker
import random
import os
import glob
import shutil

# Import all models
from accounts.models import User, StudentProfile, StaffProfile
from student_portal.models import ServiceRequest, RequestDocument, StudentDocument, SupportTicket, TicketResponse
from financial.models import FeeType, StudentFee, PaymentProvider, Payment, PaymentReceipt, FinancialReport
from notifications.models import Notification, Announcement, NotificationTemplate, NotificationPreference
from staff_panel.models import DashboardStats, StaffActivity, WorkflowTemplate, QuickAction, SystemConfiguration

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with sample data for development and testing'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--students',
            type=int,
            default=50,
            help='Number of students to create (default: 50)',
        )
        parser.add_argument(
            '--staff',
            type=int,
            default=10,
            help='Number of staff members to create (default: 10)',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        # Create basic data
        self.create_fee_types()
        self.create_payment_providers()
        self.create_notification_templates()
        
        # Create users
        self.create_admin_user()
        staff_users = self.create_staff_users(options['staff'])
        student_users = self.create_student_users(options['students'])
        
        # Create related data
        self.create_student_fees(student_users)
        self.create_service_requests(student_users, staff_users)
        self.create_support_tickets(student_users, staff_users)
        self.create_payments(student_users)
        self.create_notifications(student_users + staff_users)
        self.create_announcements(staff_users)
        self.create_dashboard_stats()
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))

    def clear_data(self):
        """Clear existing data from all models"""
        models_to_clear = [
            Payment, StudentFee, ServiceRequest, SupportTicket, TicketResponse,
            StudentDocument, Notification, Announcement, DashboardStats,
            StudentProfile, StaffProfile, User
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'Cleared {count} {model.__name__} records')

    def create_fee_types(self):
        """Create basic fee types"""
        fee_types = [
            {'name': 'Tuition Fee', 'description': 'Semester tuition fee'},
            {'name': 'Registration Fee', 'description': 'Course registration fee'},
            {'name': 'Library Fee', 'description': 'Library access and services fee'},
            {'name': 'Lab Fee', 'description': 'Laboratory usage fee'},
            {'name': 'Graduation Fee', 'description': 'Graduation ceremony and certificate fee'},
            {'name': 'Late Payment Fee', 'description': 'Fee for late payment of dues'},
        ]
        
        for fee_data in fee_types:
            FeeType.objects.get_or_create(
                name=fee_data['name'],
                defaults={'description': fee_data['description']}
            )
        
        self.stdout.write(f'Created {len(fee_types)} fee types')

    def create_payment_providers(self):
        """Create payment providers"""
        providers = [
            {
                'name': 'Jaib',
                'description': 'Jaib mobile payment',
                'instructions': 'Transfer money to the university Jaib account and submit your payment details below',
                'university_account_name': 'University of Excellence',
                'university_account_number': '967-123-456-789',
                'university_phone': '+967-1-234-567',
                'additional_info': 'Jaib Business Account - University Official Payment Gateway',
                'logo_filename': 'jaib_logo.webp'
            },
            {
                'name': 'OneCash',
                'description': 'OneCash digital wallet',
                'instructions': 'Send money to the university OneCash account',
                'university_account_name': 'University of Excellence',
                'university_account_number': '967-987-654-321',
                'university_phone': '+967-1-234-568',
                'additional_info': 'OneCash Business Wallet - Secure Digital Payments',
                'logo_filename': 'oneCash_logo.webp'
            },
            {
                'name': 'Cash',
                'description': 'Cash mobile payment',
                'instructions': 'Transfer funds using Cash mobile payment service',
                'university_account_name': 'University of Excellence',
                'university_account_number': '967-555-123-456',
                'university_phone': '+967-1-234-569',
                'additional_info': 'Cash Business Account - Mobile Payment Solution',
                'logo_filename': 'cash_logo.webp'
            },
            {
                'name': 'Kuraimi',
                'description': 'Kuraimi banking service',
                'instructions': 'Use Kuraimi banking to transfer funds to the university account',
                'university_account_name': 'University of Excellence',
                'university_account_number': '967-777-888-999',
                'university_phone': '+967-1-234-570',
                'additional_info': 'Kuraimi Bank - Branch: Main Campus, Account Type: Business',
                'logo_filename': 'kuraimi_logo.webp'
            },
        ]

        # Base path for provider logos in static files
        static_provider_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'provider')
        
        for provider_data in providers:
            provider, created = PaymentProvider.objects.get_or_create(
                name=provider_data['name'],
                defaults={
                    'description': provider_data['description'],
                    'instructions': provider_data['instructions'],
                    'university_account_name': provider_data['university_account_name'],
                    'university_account_number': provider_data['university_account_number'],
                    'university_phone': provider_data['university_phone'],
                    'additional_info': provider_data['additional_info']
                }
            )
            
            # Handle logo file upload
            if created or not provider.logo:
                logo_filename = provider_data['logo_filename']
                static_logo_path = os.path.join(static_provider_path, logo_filename)
                
                if os.path.exists(static_logo_path):
                    try:
                        with open(static_logo_path, 'rb') as f:
                            provider.logo.save(logo_filename, File(f), save=True)
                        self.stdout.write(f'  - Assigned logo {logo_filename} to {provider.name}')
                    except Exception as e:
                        self.stdout.write(f'  - Error assigning logo to {provider.name}: {e}')
                else:
                    self.stdout.write(f'  - Logo file not found: {static_logo_path}')
        
        self.stdout.write(f'Created {len(providers)} payment providers')



    def create_admin_user(self):
        """Create admin user"""
        if not User.objects.filter(username='admin').exists():
            # Check if university_id already exists and generate unique one if needed
            university_id = 'ADMIN001'
            counter = 1
            while User.objects.filter(university_id=university_id).exists():
                counter += 1
                university_id = f'ADMIN{counter:03d}'
            
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@university.edu',
                password='admin123',
                university_id=university_id,
                user_type='admin',
                first_name='System',
                last_name='Administrator'
            )
            self.stdout.write('Created admin user (username: admin, password: admin123)')
        else:
            self.stdout.write('Admin user already exists')

    def create_staff_users(self, count):
        """Create staff users"""
        staff_users = []
        departments = ['Admissions', 'Finance', 'IT Support', 'Academic Affairs', 'Student Services']
        positions = ['Manager', 'Officer', 'Assistant', 'Coordinator', 'Specialist']
        
        for i in range(count):
            username = f'staff{i+1:03d}'
            if not User.objects.filter(username=username).exists():
                # Generate unique university_id
                university_id = f'STAFF{i+1:03d}'
                counter = i + 1
                while User.objects.filter(university_id=university_id).exists():
                    counter += 1
                    university_id = f'STAFF{counter:03d}'
                
                staff = User.objects.create_user(
                    username=username,
                    email=f'staff{i+1}@university.edu',
                    password='staff123',
                    university_id=university_id,
                    user_type='staff',
                    first_name=f'Staff{i+1}',
                    last_name='Member',
                    department=random.choice(departments),
                    position=random.choice(positions)
                )
                
                # Create staff profile only for staff users
                if staff.user_type == 'staff':
                    StaffProfile.objects.create(
                        user=staff,
                        employee_id=f'EMP{counter:03d}',
                        hire_date=timezone.now().date() - timedelta(days=random.randint(30, 1000)),
                        salary=Decimal(str(random.randint(3000, 8000)))
                    )
                
                staff_users.append(staff)
        
        self.stdout.write(f'Created {len(staff_users)} staff users')
        return staff_users

    def create_student_users(self, count):
        """Create student users"""
        student_users = []
        majors = ['Computer Science', 'Business Administration', 'Engineering', 'Medicine', 'Law', 'Arts']
        levels = ['Freshman', 'Sophomore', 'Junior', 'Senior', 'Graduate']
        
        # Get available profile photos
        photos_dir = os.path.join('static', 'images', 'persons')
        available_photos = []
        if os.path.exists(photos_dir):
            # Create list of photo filenames (per1.jpg, per2.jpg, etc.)
            for i in range(1, 62):  # Based on the available photos per1.jpg to per61.jpg
                photo_file = f'per{i}.jpg'
                photo_full_path = os.path.join(photos_dir, photo_file)
                if os.path.exists(photo_full_path):
                    available_photos.append((photo_file, photo_full_path))
        
        for i in range(count):
            username = f'student{i+1:03d}'
            if not User.objects.filter(username=username).exists():
                # Generate unique university_id
                university_id = f'STU{i+1:05d}'
                counter = i + 1
                while User.objects.filter(university_id=university_id).exists():
                    counter += 1
                    university_id = f'STU{counter:05d}'
                
                student = User.objects.create_user(
                    username=username,
                    email=f'student{i+1}@university.edu',
                    password='student123',
                    university_id=university_id,
                    user_type='student',
                    first_name=f'Student{i+1}',
                    last_name='User',
                    major=random.choice(majors),
                    academic_level=random.choice(levels),
                    enrollment_year=random.randint(2020, 2024),
                    date_of_birth=datetime(1995, 1, 1).date() + timedelta(days=random.randint(0, 3650))
                )
                
                # Assign random profile photo
                if available_photos:
                    photo_file, photo_path = random.choice(available_photos)
                    try:
                        with open(photo_path, 'rb') as f:
                            student.profile_picture.save(
                                photo_file,
                                File(f),
                                save=True
                            )
                    except Exception as e:
                        print(f'Error assigning photo to {username}: {e}')
                
                # Create student profile only for student users
                if student.user_type == 'student':
                    StudentProfile.objects.create(
                        user=student,
                        student_id_number=f'SID{counter:05d}',
                        gpa=Decimal(str(round(random.uniform(2.0, 4.0), 2))),
                        total_credits=random.randint(30, 120),
                        emergency_contact_name=f'Parent{i+1}',
                        emergency_contact_phone=f'+1234567{i+1:03d}'
                    )
                
                student_users.append(student)
        
        self.stdout.write(f'Created {len(student_users)} student users')
        return student_users

    def create_student_fees(self, student_users):
        """Create fees for students"""
        fee_types = list(FeeType.objects.all())
        fees_created = 0
        
        for student in student_users:
            # Create 2-4 fees per student
            num_fees = random.randint(2, 4)
            selected_fee_types = random.sample(fee_types, min(num_fees, len(fee_types)))
            
            for fee_type in selected_fee_types:
                amount = Decimal(str(random.randint(100, 2000)))
                due_date = timezone.now().date() + timedelta(days=random.randint(-30, 90))
                
                StudentFee.objects.create(
                    student=student,
                    fee_type=fee_type,
                    amount=amount,
                    due_date=due_date,
                    status=random.choice(['pending', 'paid', 'overdue', 'partial']),
                    description=f'{fee_type.name} for {student.academic_level} student'
                )
                fees_created += 1
        
        self.stdout.write(f'Created {fees_created} student fees')

    def create_service_requests(self, student_users, staff_users):
        """Create service requests"""
        request_types = [
            'enrollment_certificate', 'schedule_modification', 'semester_postponement',
            'transcript', 'graduation_certificate', 'other'
        ]
        statuses = ['pending', 'in_review', 'approved', 'rejected', 'completed']
        
        requests_created = 0
        
        for student in student_users:
            # Create 1-3 requests per student
            num_requests = random.randint(1, 3)
            
            for _ in range(num_requests):
                request_type = random.choice(request_types)
                status = random.choice(statuses)
                
                service_request = ServiceRequest.objects.create(
                    student=student,
                    request_type=request_type,
                    title=f'{request_type.replace("_", " ").title()} Request',
                    description=f'Request for {request_type.replace("_", " ")} by {student.get_full_name()}',
                    status=status,
                    priority=random.choice(['low', 'medium', 'high']),
                    processed_by=random.choice(staff_users) if status != 'pending' else None,
                    created_at=timezone.now() - timedelta(days=random.randint(0, 30))
                )
                
                if status == 'rejected':
                    service_request.rejection_reason = 'Missing required documentation'
                    service_request.save()
                
                requests_created += 1
        
        self.stdout.write(f'Created {requests_created} service requests')
        
        # Create request documents for some service requests
        self.create_request_documents()
        
        # Create student documents
        self.create_student_documents(student_users)

    def create_support_tickets(self, student_users, staff_users):
        """Create support tickets"""
        priorities = ['low', 'medium', 'high', 'urgent']
        statuses = ['open', 'in_progress', 'resolved', 'closed']
        subjects = [
            'Login Issues', 'Payment Problems', 'Course Registration',
            'Grade Inquiry', 'Technical Support', 'Account Access'
        ]
        
        tickets_created = 0
        
        for student in student_users:
            # Create 0-2 tickets per student
            num_tickets = random.randint(0, 2)
            
            for _ in range(num_tickets):
                subject = random.choice(subjects)
                status = random.choice(statuses)
                
                ticket = SupportTicket.objects.create(
                    student=student,
                    subject=subject,
                    description=f'Student needs help with {subject.lower()}',
                    priority=random.choice(priorities),
                    status=status,
                    assigned_to=random.choice(staff_users) if status != 'open' else None,
                    created_at=timezone.now() - timedelta(days=random.randint(0, 15))
                )
                
                # Add some responses
                if status in ['in_progress', 'resolved', 'closed']:
                    TicketResponse.objects.create(
                        ticket=ticket,
                        responder=ticket.assigned_to,
                        message='Thank you for contacting support. We are looking into your issue.',
                        created_at=ticket.created_at + timedelta(hours=random.randint(1, 24))
                    )
                
                tickets_created += 1
        
        self.stdout.write(f'Created {tickets_created} support tickets')

    def create_payments(self, student_users):
        """Create payments for student fees"""
        payment_providers = list(PaymentProvider.objects.all())
        payments_created = 0
        
        # Get fees that should have payments
        fees_with_payments = StudentFee.objects.filter(
            status__in=['paid', 'partial']
        )
        
        for fee in fees_with_payments:
            # Create 1-2 payments per fee
            num_payments = 1 if fee.status == 'paid' else random.randint(1, 2)
            
            total_paid = Decimal('0')
            for i in range(num_payments):
                if fee.status == 'paid' and i == 0:
                    amount = fee.amount
                else:
                    amount = Decimal(str(random.randint(50, int(fee.amount))))
                
                total_paid += amount
                if total_paid > fee.amount:
                    amount = fee.amount - (total_paid - amount)
                    if amount <= 0:
                        break
                
                Payment.objects.create(
                    student=fee.student,
                    fee=fee,
                    payment_provider=random.choice(payment_providers),
                    amount=amount,
                    transaction_reference=f'TXN{random.randint(100000, 999999)}',
                    payment_date=timezone.now() - timedelta(days=random.randint(0, 30)),
                    status=random.choice(['pending', 'verified', 'rejected']),
                    created_at=timezone.now() - timedelta(days=random.randint(0, 30))
                )
                payments_created += 1
        
        self.stdout.write(f'Created {payments_created} payments')
        
        # Create payment receipts for verified payments
        self.create_payment_receipts()

    def create_notifications(self, all_users):
        """Create notifications for users"""
        notification_types = ['info', 'warning', 'success', 'error', 'announcement']
        priorities = ['low', 'medium', 'high', 'urgent']
        
        notifications_created = 0
        
        for user in all_users:
            # Create 2-5 notifications per user
            num_notifications = random.randint(2, 5)
            
            for _ in range(num_notifications):
                notification_type = random.choice(notification_types)
                
                Notification.objects.create(
                    recipient=user,
                    title=f'{notification_type.title()} Notification',
                    message=f'This is a {notification_type} notification for {user.get_full_name()}',
                    notification_type=notification_type,
                    priority=random.choice(priorities),
                    is_read=random.choice([True, False]),
                    created_at=timezone.now() - timedelta(days=random.randint(0, 7))
                )
                notifications_created += 1
        
        self.stdout.write(f'Created {notifications_created} notifications')

    def create_announcements(self, staff_users):
        """Create announcements"""
        announcements = [
            {
                'title': 'New Academic Year Registration',
                'content': 'Registration for the new academic year is now open. Please complete your registration by the deadline.',
                'target_audience': 'students'
            },
            {
                'title': 'System Maintenance Notice',
                'content': 'The university portal will undergo maintenance this weekend. Services may be temporarily unavailable.',
                'target_audience': 'all'
            },
            {
                'title': 'Fee Payment Deadline',
                'content': 'Reminder: All outstanding fees must be paid by the end of this month to avoid late charges.',
                'target_audience': 'students'
            },
            {
                'title': 'Staff Meeting',
                'content': 'Monthly staff meeting scheduled for next Friday at 2 PM in the conference room.',
                'target_audience': 'staff'
            },
        ]
        
        for announcement_data in announcements:
            Announcement.objects.create(
                title=announcement_data['title'],
                content=announcement_data['content'],
                target_audience=announcement_data['target_audience'],
                created_by=random.choice(staff_users),
                publish_date=timezone.now() - timedelta(days=random.randint(0, 10)),
                is_urgent=random.choice([True, False])
            )
        
        self.stdout.write(f'Created {len(announcements)} announcements')

    def create_dashboard_stats(self):
        """Create dashboard statistics"""
        # Create stats for the last 7 days
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            
            DashboardStats.objects.get_or_create(
                date=date,
                defaults={
                    'total_students': User.objects.filter(user_type='student').count(),
                    'new_students_today': random.randint(0, 5),
                    'active_students': random.randint(80, 95),
                    'total_requests': ServiceRequest.objects.count(),
                    'pending_requests': ServiceRequest.objects.filter(status='pending').count(),
                    'approved_requests_today': random.randint(2, 10),
                    'rejected_requests_today': random.randint(0, 3),
                    'total_fees_collected_today': Decimal(str(random.randint(5000, 15000))),
                    'pending_payments': Payment.objects.filter(status='pending').count(),
                    'verified_payments_today': random.randint(5, 20),
                    'open_support_tickets': SupportTicket.objects.filter(status='open').count(),
                    'resolved_tickets_today': random.randint(1, 8)
                }
            )
        
        self.stdout.write('Created dashboard statistics for the last 7 days')
        
        # Create system configurations
        self.create_system_configurations()
        
        # Create financial reports
        self.create_financial_reports()
        
        # Create notification preferences
        self.create_notification_preferences()
        
        # Create staff activities
        self.create_staff_activities()
        
        # Create workflow templates
        self.create_workflow_templates()
        
        # Create quick actions
        self.create_quick_actions()

    def create_request_documents(self):
        """Create documents attached to service requests"""
        service_requests = ServiceRequest.objects.all()
        documents_created = 0
        
        # Document types that might be attached to requests
        document_types = [
            ('id_copy', 'ID Copy'),
            ('transcript', 'Academic Transcript'),
            ('certificate', 'Certificate'),
            ('application_form', 'Application Form'),
            ('supporting_document', 'Supporting Document')
        ]
        
        for request in service_requests:
            # 30% chance of having documents attached
            if random.random() < 0.3:
                num_docs = random.randint(1, 3)
                selected_types = random.sample(document_types, min(num_docs, len(document_types)))
                
                for doc_type, doc_name in selected_types:
                    # Create a simple text file as document
                    file_content = f"Sample {doc_name} for {request.student.get_full_name()}\nRequest: {request.title}\nGenerated on: {timezone.now()}"
                    file_name = f"{doc_type}_{request.id}_{random.randint(1000, 9999)}.txt"
                    
                    try:
                        # Create the document record
                        RequestDocument.objects.create(
                            request=request,
                            document_name=doc_name,
                            uploaded_at=request.created_at + timedelta(minutes=random.randint(5, 60))
                        )
                        documents_created += 1
                    except Exception as e:
                        self.stdout.write(f'Error creating document: {e}')
        
        self.stdout.write(f'Created {documents_created} request documents')

    def create_student_documents(self, student_users):
        """Create academic documents for students"""
        documents_created = 0
        staff_users = User.objects.filter(user_type='staff')
        
        # Document types for students
        document_types = [
            ('transcript', 'Official Transcript'),
            ('enrollment_certificate', 'Enrollment Certificate'),
            ('graduation_certificate', 'Graduation Certificate'),
            ('student_id', 'Student ID Card'),
            ('academic_record', 'Academic Record'),
            ('degree_certificate', 'Degree Certificate')
        ]
        
        for student in student_users:
            # Each student gets 2-4 documents
            num_docs = random.randint(2, 4)
            selected_types = random.sample(document_types, min(num_docs, len(document_types)))
            
            for doc_type, doc_name in selected_types:
                # Skip graduation/degree certificates for current students
                if doc_type in ['graduation_certificate', 'degree_certificate'] and student.academic_level != 'graduate':
                    continue
                    
                file_name = f"{doc_type}_{student.university_id}_{random.randint(1000, 9999)}.pdf"
                file_content = f"Official {doc_name} for {student.get_full_name()}\nStudent ID: {student.university_id}\nIssued: {timezone.now().date()}"
                
                try:
                    StudentDocument.objects.create(
                        student=student,
                        document_type=doc_type,
                        title=doc_name,
                        issued_date=timezone.now().date() - timedelta(days=random.randint(30, 365)),
                        issued_by=random.choice(staff_users) if staff_users.exists() else None,
                        is_official=random.choice([True, False])
                    )
                    documents_created += 1
                except Exception as e:
                    self.stdout.write(f'Error creating student document: {e}')
        
        self.stdout.write(f'Created {documents_created} student documents')

    def create_system_configurations(self):
        """Create system-wide configuration settings"""
        configurations = [
            {
                'key': 'university_name',
                'value': 'Sample University',
                'description': 'Official name of the university',
                'category': 'general'
            },
            {
                'key': 'academic_year',
                'value': '2024-2025',
                'description': 'Current academic year',
                'category': 'academic'
            },
            {
                'key': 'semester',
                'value': 'Fall 2024',
                'description': 'Current semester',
                'category': 'academic'
            },
            {
                'key': 'registration_deadline',
                'value': '2024-08-15',
                'description': 'Last date for course registration',
                'category': 'academic'
            },
            {
                'key': 'fee_payment_deadline',
                'value': '2024-09-30',
                'description': 'Deadline for fee payments',
                'category': 'financial'
            },
            {
                'key': 'late_fee_amount',
                'value': '50.00',
                'description': 'Late fee amount for overdue payments',
                'category': 'financial'
            },
            {
                'key': 'max_service_requests_per_student',
                'value': '5',
                'description': 'Maximum number of active service requests per student',
                'category': 'services'
            },
            {
                'key': 'support_ticket_auto_close_days',
                'value': '30',
                'description': 'Days after which resolved tickets are auto-closed',
                'category': 'support'
            },
            {
                'key': 'notification_retention_days',
                'value': '90',
                'description': 'Days to retain read notifications',
                'category': 'notifications'
            },
            {
                'key': 'system_maintenance_mode',
                'value': 'false',
                'description': 'Enable/disable system maintenance mode',
                'category': 'system'
            },
            {
                'key': 'contact_email',
                'value': 'support@university.edu',
                'description': 'Main contact email for support',
                'category': 'contact'
            },
            {
                'key': 'contact_phone',
                'value': '+1-555-0123',
                'description': 'Main contact phone number',
                'category': 'contact'
            }
        ]
        
        configs_created = 0
        for config_data in configurations:
            config, created = SystemConfiguration.objects.get_or_create(
                key=config_data['key'],
                defaults={
                    'value': config_data['value'],
                    'description': config_data['description'],
                    'category': config_data['category'],
                    'is_active': True
                }
            )
            if created:
                configs_created += 1
        
        self.stdout.write(f'Created {configs_created} system configurations')

    def create_payment_receipts(self):
        """Create receipts for verified payments"""
        verified_payments = Payment.objects.filter(status='verified')
        receipts_created = 0
        
        for payment in verified_payments:
            try:
                # Generate receipt number
                receipt_number = f'RCP{payment.id:06d}{random.randint(100, 999)}'
                
                PaymentReceipt.objects.create(
                    payment=payment,
                    receipt_number=receipt_number,
                    generated_by=payment.verified_by
                )
                receipts_created += 1
            except Exception as e:
                self.stdout.write(f'Error creating receipt for payment {payment.id}: {e}')
        
        self.stdout.write(f'Created {receipts_created} payment receipts')

    def create_financial_reports(self):
        """Create periodic financial reports"""
        reports_created = 0
        
        # Create monthly reports for the last 6 months
        for i in range(6):
            report_date = timezone.now().date().replace(day=1) - timedelta(days=30*i)
            month_start_date = report_date.replace(day=1)
            if report_date.month == 12:
                month_end_date = report_date.replace(year=report_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end_date = report_date.replace(month=report_date.month + 1, day=1) - timedelta(days=1)
            
            # Convert to timezone-aware datetimes
            month_start = timezone.make_aware(datetime.combine(month_start_date, datetime.min.time()))
            month_end = timezone.make_aware(datetime.combine(month_end_date, datetime.max.time()))
            
            # Calculate totals for the month
            monthly_payments = Payment.objects.filter(
                payment_date__range=[month_start, month_end],
                status='verified'
            )
            
            total_collected = sum(payment.amount for payment in monthly_payments)
            total_fees = StudentFee.objects.filter(
                created_at__date__range=[month_start, month_end]
            ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
            
            outstanding_fees = StudentFee.objects.filter(
                status__in=['pending', 'overdue', 'partial'],
                created_at__date__lte=month_end
            ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
            
            try:
                FinancialReport.objects.create(
                    report_type='monthly',
                    start_date=month_start_date,
                    end_date=month_end_date,
                    total_fees_issued=total_fees,
                    total_payments_received=total_collected,
                    total_pending_verification=outstanding_fees,
                    report_data={
                        'summary': f'Monthly financial report for {month_start.strftime("%B %Y")}',
                        'number_of_transactions': monthly_payments.count(),
                        'payment_methods': {
                            'online': random.randint(50, 80),
                            'bank_transfer': random.randint(10, 30),
                            'cash': random.randint(5, 15)
                        },
                        'fee_types': {
                            'tuition': float(total_collected * Decimal('0.7')),
                            'library': float(total_collected * Decimal('0.1')),
                            'lab': float(total_collected * Decimal('0.1')),
                            'other': float(total_collected * Decimal('0.1'))
                        }
                    }
                )
                reports_created += 1
            except Exception as e:
                self.stdout.write(f'Error creating financial report for {month_start}: {e}')
        
        # Create one annual report
        try:
            year_start = timezone.now().date().replace(month=1, day=1)
            year_end = timezone.now().date().replace(month=12, day=31)
            
            # Convert to timezone-aware datetimes for payment filtering
            year_start_dt = timezone.make_aware(datetime.combine(year_start, datetime.min.time()))
            year_end_dt = timezone.make_aware(datetime.combine(year_end, datetime.max.time()))
            
            yearly_payments = Payment.objects.filter(
                payment_date__range=[year_start_dt, year_end_dt],
                status='verified'
            )
            
            total_yearly_collected = sum(payment.amount for payment in yearly_payments)
            total_yearly_fees = StudentFee.objects.filter(
                created_at__date__range=[year_start, year_end]
            ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
            
            FinancialReport.objects.create(
                report_type='yearly',
                start_date=year_start,
                end_date=year_end,
                total_fees_issued=total_yearly_fees,
                total_payments_received=total_yearly_collected,
                total_pending_verification=total_yearly_fees - total_yearly_collected,
                report_data={
                    'summary': f'Annual financial report for {year_start.year}',
                    'number_of_transactions': yearly_payments.count(),
                    'quarterly_breakdown': {
                        'Q1': float(total_yearly_collected * Decimal('0.25')),
                        'Q2': float(total_yearly_collected * Decimal('0.30')),
                        'Q3': float(total_yearly_collected * Decimal('0.20')),
                        'Q4': float(total_yearly_collected * Decimal('0.25'))
                    },
                    'growth_rate': random.uniform(5.0, 15.0)
                }
            )
            reports_created += 1
        except Exception as e:
            self.stdout.write(f'Error creating annual financial report: {e}')
        
        self.stdout.write(f'Created {reports_created} financial reports')

    def create_notification_templates(self):
        """Create reusable notification templates"""
        templates = [
            {
                'name': 'payment_reminder',
                'subject': 'Payment Reminder - {fee_type}',
                'body': 'Dear {student_name},\n\nThis is a reminder that your {fee_type} payment of ${amount} is due on {due_date}.\n\nPlease make your payment to avoid late fees.\n\nBest regards,\nFinance Office',
                'notification_type': 'payment',
                'is_active': True
            },
            {
                'name': 'service_request_approved',
                'subject': 'Service Request Approved - {request_title}',
                'body': 'Dear {student_name},\n\nYour service request "{request_title}" has been approved.\n\nRequest ID: {request_id}\nProcessed by: {staff_name}\n\nYou can track the progress in your student portal.\n\nBest regards,\nStudent Services',
                'notification_type': 'service',
                'is_active': True
            },
            {
                'name': 'service_request_rejected',
                'subject': 'Service Request Update - {request_title}',
                'body': 'Dear {student_name},\n\nWe regret to inform you that your service request "{request_title}" has been rejected.\n\nReason: {rejection_reason}\n\nPlease contact our office for more information or to resubmit with corrections.\n\nBest regards,\nStudent Services',
                'notification_type': 'service',
                'is_active': True
            },
            {
                'name': 'support_ticket_response',
                'subject': 'Support Ticket Update - {ticket_subject}',
                'body': 'Dear {student_name},\n\nThere has been an update to your support ticket "{ticket_subject}".\n\nTicket ID: {ticket_id}\nStatus: {ticket_status}\n\nPlease check your student portal for the latest response.\n\nBest regards,\nSupport Team',
                'notification_type': 'support',
                'is_active': True
            },
            {
                'name': 'enrollment_confirmation',
                'subject': 'Enrollment Confirmation - {semester}',
                'body': 'Dear {student_name},\n\nYour enrollment for {semester} has been confirmed.\n\nStudent ID: {student_id}\nProgram: {program}\nCredits: {credits}\n\nWelcome to the new semester!\n\nBest regards,\nRegistrar Office',
                'notification_type': 'academic',
                'is_active': True
            },
            {
                'name': 'document_ready',
                'subject': 'Document Ready for Collection - {document_type}',
                'body': 'Dear {student_name},\n\nYour requested document "{document_type}" is ready for collection.\n\nDocument ID: {document_id}\nCollection Location: Student Services Office\nOffice Hours: Monday-Friday, 9:00 AM - 5:00 PM\n\nPlease bring your student ID for verification.\n\nBest regards,\nStudent Services',
                'notification_type': 'document',
                'is_active': True
            },
            {
                'name': 'fee_payment_received',
                'subject': 'Payment Confirmation - {fee_type}',
                'body': 'Dear {student_name},\n\nWe have received your payment for {fee_type}.\n\nAmount: ${amount}\nTransaction ID: {transaction_id}\nPayment Date: {payment_date}\n\nThank you for your payment.\n\nBest regards,\nFinance Office',
                'notification_type': 'payment',
                'is_active': True
            },
            {
                'name': 'system_maintenance',
                'subject': 'System Maintenance Notice',
                'body': 'Dear Students,\n\nThe student portal will undergo scheduled maintenance on {maintenance_date} from {start_time} to {end_time}.\n\nDuring this time, the system will be unavailable. Please plan accordingly.\n\nWe apologize for any inconvenience.\n\nBest regards,\nIT Department',
                'notification_type': 'system',
                'is_active': True
            }
        ]
        
        templates_created = 0
        for template_data in templates:
            # Map the template_data to correct field names
            template_type_mapping = {
                'payment': 'fee_due',
                'service': 'request_approved',
                'support': 'general',
                'academic': 'general',
                'document': 'document_ready',
                'system': 'general'
            }
            
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'template_type': template_type_mapping.get(template_data['notification_type'], 'general'),
                    'subject_template': template_data['subject'],
                    'message_template': template_data['body'],
                    'is_active': template_data['is_active']
                }
            )
            if created:
                templates_created += 1
        
        self.stdout.write(f'Created {templates_created} notification templates')

    def create_notification_preferences(self):
        """Create notification preferences for users"""
        users = User.objects.all()
        preferences_created = 0
        
        for user in users:
            # Create one notification preference per user with randomized settings
            preference, created = NotificationPreference.objects.get_or_create(
                user=user,
                defaults={
                    # Email notifications
                    'email_announcements': self.fake.boolean(chance_of_getting_true=90),
                    'email_request_updates': self.fake.boolean(chance_of_getting_true=85),
                    'email_payment_updates': self.fake.boolean(chance_of_getting_true=95),
                    'email_fee_reminders': self.fake.boolean(chance_of_getting_true=90),
                    
                    # In-app notifications
                    'app_announcements': self.fake.boolean(chance_of_getting_true=95),
                    'app_request_updates': self.fake.boolean(chance_of_getting_true=90),
                    'app_payment_updates': self.fake.boolean(chance_of_getting_true=95),
                    'app_fee_reminders': self.fake.boolean(chance_of_getting_true=85),
                    
                    # Notification frequency
                    'digest_frequency': self.fake.random_element(elements=('immediate', 'daily', 'weekly'))
                }
            )
            if created:
                preferences_created += 1
        
        self.stdout.write(f'Created {preferences_created} notification preferences')

    def create_staff_activities(self):
        """Create staff activity logs"""
        staff_users = User.objects.filter(is_staff=True)
        activities_created = 0
        
        activity_types = [
            'login', 'logout', 'service_request_processed', 'ticket_assigned', 'ticket_resolved',
            'payment_verified', 'document_generated', 'user_created', 'user_updated',
            'system_config_changed', 'report_generated', 'announcement_created'
        ]
        
        descriptions = {
            'login': 'Staff member logged into the system',
            'logout': 'Staff member logged out of the system',
            'service_request_processed': 'Processed service request #{request_id}',
            'ticket_assigned': 'Assigned support ticket #{ticket_id} to staff member',
            'ticket_resolved': 'Resolved support ticket #{ticket_id}',
            'payment_verified': 'Verified payment #{payment_id} for student',
            'document_generated': 'Generated {document_type} document for student',
            'user_created': 'Created new user account: {username}',
            'user_updated': 'Updated user profile for: {username}',
            'system_config_changed': 'Modified system configuration: {config_key}',
            'report_generated': 'Generated {report_type} report',
            'announcement_created': 'Created new announcement: {title}'
        }
        
        # Create activities for the last 30 days
        for staff_user in staff_users:
            # Each staff member has 5-15 activities
            num_activities = self.fake.random_int(min=5, max=15)
            
            for _ in range(num_activities):
                activity_type = self.fake.random_element(elements=activity_types)
                description = descriptions[activity_type]
                
                # Add some context to descriptions
                if 'request_id' in description:
                    description = description.format(request_id=self.fake.random_int(min=1, max=100))
                elif 'ticket_id' in description:
                    description = description.format(ticket_id=self.fake.random_int(min=1, max=50))
                elif 'payment_id' in description:
                    description = description.format(payment_id=self.fake.random_int(min=1, max=200))
                elif 'document_type' in description:
                    doc_type = self.fake.random_element(elements=['Transcript', 'Certificate', 'ID Card'])
                    description = description.format(document_type=doc_type)
                elif 'username' in description:
                    description = description.format(username=self.fake.user_name())
                elif 'config_key' in description:
                    config_key = self.fake.random_element(elements=['academic_year', 'fee_deadline', 'contact_email'])
                    description = description.format(config_key=config_key)
                elif 'report_type' in description:
                    report_type = self.fake.random_element(elements=['Financial', 'Academic', 'Student'])
                    description = description.format(report_type=report_type)
                elif 'title' in description:
                    description = description.format(title=self.fake.sentence(nb_words=4))
                
                activity = StaffActivity.objects.create(
                    staff_member=staff_user,
                    activity_type=activity_type,
                    description=description,
                    ip_address=self.fake.ipv4(),
                    user_agent=self.fake.user_agent(),
                    timestamp=self.fake.date_time_between(start_date='-30d', end_date='now', tzinfo=ZoneInfo('UTC'))
                )
                activities_created += 1
        
        self.stdout.write(f'Created {activities_created} staff activities')

    def create_workflow_templates(self):
        """Create workflow templates for common processes"""
        templates = [
            {
                'name': 'Student Registration Process',
                'description': 'Complete workflow for new student registration and enrollment',
                'workflow_type': 'student_onboarding',
                'steps': [
                    {'step_number': 1, 'title': 'Document Verification', 'description': 'Verify submitted academic documents', 'estimated_duration': 60, 'required': True},
                    {'step_number': 2, 'title': 'Fee Assessment', 'description': 'Calculate and assign appropriate fees', 'estimated_duration': 30, 'required': True},
                    {'step_number': 3, 'title': 'Course Selection', 'description': 'Student selects courses for enrollment', 'estimated_duration': 45, 'required': True},
                    {'step_number': 4, 'title': 'Payment Processing', 'description': 'Process initial registration fees', 'estimated_duration': 15, 'required': True},
                    {'step_number': 5, 'title': 'ID Card Generation', 'description': 'Generate and print student ID card', 'estimated_duration': 20, 'required': False}
                ],
                'is_active': True
            },
            {
                'name': 'Service Request Processing',
                'description': 'Standard workflow for processing student service requests',
                'workflow_type': 'request_processing',
                'steps': [
                    {'step_number': 1, 'title': 'Initial Review', 'description': 'Review request for completeness', 'estimated_duration': 15, 'required': True},
                    {'step_number': 2, 'title': 'Document Collection', 'description': 'Collect required supporting documents', 'estimated_duration': 30, 'required': True},
                    {'step_number': 3, 'title': 'Verification', 'description': 'Verify student eligibility and requirements', 'estimated_duration': 45, 'required': True},
                    {'step_number': 4, 'title': 'Processing', 'description': 'Process the actual service request', 'estimated_duration': 120, 'required': True},
                    {'step_number': 5, 'title': 'Quality Check', 'description': 'Final quality assurance check', 'estimated_duration': 20, 'required': True},
                    {'step_number': 6, 'title': 'Notification', 'description': 'Notify student of completion', 'estimated_duration': 5, 'required': True}
                ],
                'is_active': True
            },
            {
                'name': 'Support Ticket Resolution',
                'description': 'Process for resolving student support tickets',
                'workflow_type': 'request_processing',
                'steps': [
                    {'step_number': 1, 'title': 'Ticket Assignment', 'description': 'Assign ticket to appropriate staff member', 'estimated_duration': 10, 'required': True},
                    {'step_number': 2, 'title': 'Initial Response', 'description': 'Provide initial response to student', 'estimated_duration': 30, 'required': True},
                    {'step_number': 3, 'title': 'Investigation', 'description': 'Investigate the reported issue', 'estimated_duration': 90, 'required': True},
                    {'step_number': 4, 'title': 'Resolution', 'description': 'Implement solution or provide answer', 'estimated_duration': 60, 'required': True},
                    {'step_number': 5, 'title': 'Follow-up', 'description': 'Follow up with student for satisfaction', 'estimated_duration': 15, 'required': False}
                ],
                'is_active': True
            },
            {
                'name': 'Payment Verification Process',
                'description': 'Workflow for verifying and processing student payments',
                'workflow_type': 'payment_verification',
                'steps': [
                    {'step_number': 1, 'title': 'Payment Receipt', 'description': 'Receive and log payment information', 'estimated_duration': 10, 'required': True},
                    {'step_number': 2, 'title': 'Bank Verification', 'description': 'Verify payment with bank/payment provider', 'estimated_duration': 30, 'required': True},
                    {'step_number': 3, 'title': 'Amount Validation', 'description': 'Validate payment amount against fees', 'estimated_duration': 15, 'required': True},
                    {'step_number': 4, 'title': 'Account Update', 'description': 'Update student account with payment', 'estimated_duration': 10, 'required': True},
                    {'step_number': 5, 'title': 'Receipt Generation', 'description': 'Generate official payment receipt', 'estimated_duration': 5, 'required': True}
                ],
                'is_active': True
            },
            {
                'name': 'Document Request Processing',
                'description': 'Process for handling official document requests',
                'workflow_type': 'document_generation',
                'steps': [
                    {'step_number': 1, 'title': 'Eligibility Check', 'description': 'Verify student eligibility for document', 'estimated_duration': 20, 'required': True},
                    {'step_number': 2, 'title': 'Fee Verification', 'description': 'Check if required fees are paid', 'estimated_duration': 15, 'required': True},
                    {'step_number': 3, 'title': 'Document Generation', 'description': 'Generate the requested document', 'estimated_duration': 45, 'required': True},
                    {'step_number': 4, 'title': 'Authorization', 'description': 'Get necessary approvals and signatures', 'estimated_duration': 60, 'required': True},
                    {'step_number': 5, 'title': 'Delivery Preparation', 'description': 'Prepare document for collection/delivery', 'estimated_duration': 10, 'required': True}
                ],
                'is_active': True
            }
        ]
        
        templates_created = 0
        # Get a staff user to be the creator
        staff_user = User.objects.filter(is_staff=True).first()
        if not staff_user:
            self.stdout.write('No staff users found. Skipping workflow templates.')
            return
            
        for template_data in templates:
            template, created = WorkflowTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'workflow_type': template_data['workflow_type'],
                    'steps': template_data['steps'],
                    'is_active': template_data['is_active'],
                    'created_by': staff_user
                }
            )
            if created:
                templates_created += 1
        
        self.stdout.write(f'Created {templates_created} workflow templates')

    def create_quick_actions(self):
        """Create quick action shortcuts for staff panel"""
        actions = [
            {
                'name': 'Create New Student',
                'description': 'Quickly create a new student account',
                'icon_class': 'user-plus',
                'action_type': 'create',
                'target_model': 'User',
                'url_pattern': '/admin/accounts/user/add/',
                'permissions': ['accounts.add_user'],
                'category': 'student_management',
                'is_active': True,
                'order': 1
            },
            {
                'name': 'Process Service Request',
                'description': 'Process pending service requests',
                'icon_class': 'clipboard-check',
                'action_type': 'process',
                'target_model': 'ServiceRequest',
                'url_pattern': '/staff/service-requests/pending/',
                'permissions': ['student_portal.change_servicerequest'],
                'category': 'service_management',
                'is_active': True,
                'order': 2
            },
            {
                'name': 'Verify Payments',
                'description': 'Verify pending payments',
                'icon_class': 'credit-card',
                'action_type': 'verify',
                'target_model': 'Payment',
                'url_pattern': '/staff/payments/pending/',
                'permissions': ['financial.change_payment'],
                'category': 'financial_management',
                'is_active': True,
                'order': 3
            },
            {
                'name': 'Generate Report',
                'description': 'Generate financial or academic reports',
                'icon_class': 'chart-bar',
                'action_type': 'generate',
                'target_model': 'FinancialReport',
                'url_pattern': '/staff/reports/generate/',
                'permissions': ['financial.add_financialreport'],
                'category': 'reporting',
                'is_active': True,
                'order': 4
            },
            {
                'name': 'Assign Support Ticket',
                'description': 'Assign unassigned support tickets',
                'icon_class': 'ticket-alt',
                'action_type': 'assign',
                'target_model': 'SupportTicket',
                'url_pattern': '/staff/tickets/unassigned/',
                'permissions': ['student_portal.change_supportticket'],
                'category': 'support_management',
                'is_active': True,
                'order': 5
            },
            {
                'name': 'Create Announcement',
                'description': 'Create new system announcement',
                'icon_class': 'bullhorn',
                'action_type': 'create',
                'target_model': 'Announcement',
                'url_pattern': '/staff/announcements/create/',
                'permissions': ['notifications.add_announcement'],
                'category': 'communication',
                'is_active': True,
                'order': 6
            },
            {
                'name': 'Generate Student ID',
                'description': 'Generate student ID cards',
                'icon_class': 'id-card',
                'action_type': 'generate',
                'target_model': 'StudentDocument',
                'url_pattern': '/staff/documents/generate-id/',
                'permissions': ['student_portal.add_studentdocument'],
                'category': 'document_management',
                'is_active': True,
                'order': 7
            },
            {
                'name': 'Update Fee Structure',
                'description': 'Update fee types and amounts',
                'icon_class': 'dollar-sign',
                'action_type': 'update',
                'target_model': 'FeeType',
                'url_pattern': '/staff/fees/structure/',
                'permissions': ['financial.change_feetype'],
                'category': 'financial_management',
                'is_active': True,
                'order': 8
            },
            {
                'name': 'View Dashboard Stats',
                'description': 'View comprehensive dashboard statistics',
                'icon_class': 'tachometer-alt',
                'action_type': 'view',
                'target_model': 'DashboardStats',
                'url_pattern': '/staff/dashboard/stats/',
                'permissions': ['staff_panel.view_dashboardstats'],
                'category': 'analytics',
                'is_active': True,
                'order': 9
            },
            {
                'name': 'System Configuration',
                'description': 'Manage system-wide configurations',
                'icon_class': 'cogs',
                'action_type': 'configure',
                'target_model': 'SystemConfiguration',
                'url_pattern': '/staff/system/config/',
                'permissions': ['staff_panel.change_systemconfiguration'],
                'category': 'system_management',
                'is_active': True,
                'order': 10
            }
        ]
        
        actions_created = 0
        for action_data in actions:
            action, created = QuickAction.objects.get_or_create(
                name=action_data['name'],
                defaults={
                    'description': action_data['description'],
                    'icon_class': action_data['icon_class'],
                    'action_type': action_data['action_type'],
                    'url_pattern': action_data['url_pattern'],
                    'required_permissions': action_data['permissions'],
                    'is_active': action_data['is_active'],
                    'order': action_data['order']
                }
            )
            if created:
                actions_created += 1
        
        self.stdout.write(f'Created {actions_created} quick actions')