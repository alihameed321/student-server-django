from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.files import File
from django.core.files.storage import default_storage
from django.conf import settings
import random
import os
import glob
import shutil

# Import all models
from accounts.models import User, StudentProfile, StaffProfile
from student_portal.models import ServiceRequest, RequestDocument, StudentDocument, SupportTicket, TicketResponse
from financial.models import FeeType, StudentFee, PaymentProvider, Payment
from notifications.models import Notification, Announcement, NotificationTemplate
from staff_panel.models import DashboardStats

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with sample data for development and testing'

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

    def create_notification_templates(self):
        """Create notification templates"""
        templates = [
            {
                'name': 'Request Approved',
                'template_type': 'request_approved',
                'subject_template': 'Your request has been approved',
                'message_template': 'Dear {student_name}, your request "{request_title}" has been approved.'
            },
            {
                'name': 'Payment Verified',
                'template_type': 'payment_verified',
                'subject_template': 'Payment verification successful',
                'message_template': 'Your payment of ${amount} has been verified successfully.'
            },
            {
                'name': 'Fee Due Reminder',
                'template_type': 'fee_due',
                'subject_template': 'Fee payment reminder',
                'message_template': 'This is a reminder that your {fee_type} of ${amount} is due on {due_date}.'
            },
        ]
        
        for template_data in templates:
            NotificationTemplate.objects.get_or_create(
                template_type=template_data['template_type'],
                defaults=template_data
            )
        
        self.stdout.write(f'Created {len(templates)} notification templates')

    def create_admin_user(self):
        """Create admin user"""
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@university.edu',
                password='admin123',
                university_id='ADMIN001',
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
                staff = User.objects.create_user(
                    username=username,
                    email=f'staff{i+1}@university.edu',
                    password='staff123',
                    university_id=f'STAFF{i+1:03d}',
                    user_type='staff',
                    first_name=f'Staff{i+1}',
                    last_name='Member',
                    department=random.choice(departments),
                    position=random.choice(positions)
                )
                
                # Create staff profile
                StaffProfile.objects.create(
                    user=staff,
                    employee_id=f'EMP{i+1:03d}',
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
                student = User.objects.create_user(
                    username=username,
                    email=f'student{i+1}@university.edu',
                    password='student123',
                    university_id=f'STU{i+1:05d}',
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
                
                # Create student profile
                StudentProfile.objects.create(
                    user=student,
                    student_id_number=f'SID{i+1:05d}',
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