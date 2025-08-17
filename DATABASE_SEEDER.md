# Database Seeder

This document explains how to use the database seeder to populate your development database with sample data.

## Overview

The database seeder creates realistic sample data for all models in the university services system, including:

- **Users**: Admin, staff, and student accounts
- **Fee Types**: Various university fees (tuition, registration, library, etc.)
- **Student Fees**: Fee assignments for students with different statuses
- **Service Requests**: Student requests for certificates, transcripts, etc.
- **Support Tickets**: Help desk tickets with responses
- **Payments**: Payment records for student fees
- **Notifications**: System notifications for users
- **Announcements**: University announcements
- **Dashboard Statistics**: Historical data for admin dashboard

## Usage

### Basic Command

```bash
python manage.py seed_db
```

This creates:
- 50 students (default)
- 10 staff members (default)
- 1 admin user
- Related data for all models

### Command Options

#### Custom Numbers

```bash
# Create 100 students and 20 staff members
python manage.py seed_db --students 100 --staff 20
```

#### Clear Existing Data

```bash
# Clear all existing data before seeding
python manage.py seed_db --clear
```

#### Combined Options

```bash
# Clear data and create custom amounts
python manage.py seed_db --clear --students 25 --staff 5
```

### Help

```bash
python manage.py seed_db --help
```

## Default Accounts Created

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@university.edu`
- **University ID**: `ADMIN001`

### Staff Accounts
- **Username Pattern**: `staff001`, `staff002`, etc.
- **Password**: `staff123` (for all staff)
- **Email Pattern**: `staff1@university.edu`, `staff2@university.edu`, etc.
- **University ID Pattern**: `STAFF001`, `STAFF002`, etc.

### Student Accounts
- **Username Pattern**: `student001`, `student002`, etc.
- **Password**: `student123` (for all students)
- **Email Pattern**: `student1@university.edu`, `student2@university.edu`, etc.
- **University ID Pattern**: `STU00001`, `STU00002`, etc.

## Sample Data Details

### Fee Types
1. Tuition Fee
2. Registration Fee
3. Library Fee
4. Lab Fee
5. Graduation Fee
6. Late Payment Fee

### Payment Providers
1. Bank Transfer
2. Credit Card
3. Mobile Money

### Service Request Types
- Enrollment Certificate
- Schedule Modification
- Semester Postponement
- Transcript
- Graduation Certificate
- Other

### Support Ticket Categories
- Login Issues
- Payment Problems
- Course Registration
- Grade Inquiry
- Technical Support
- Account Access

## Data Relationships

The seeder creates realistic relationships between models:

- Each student gets 2-4 random fees
- Students create 1-3 service requests
- Students may create 0-2 support tickets
- Fees with 'paid' or 'partial' status get corresponding payments
- All users receive 2-5 notifications
- Dashboard statistics are created for the last 7 days

## Development Tips

### Quick Reset

```bash
# Quickly reset and repopulate with fresh data
python manage.py seed_db --clear --students 20 --staff 5
```

### Testing Different Scenarios

```bash
# Small dataset for quick testing
python manage.py seed_db --clear --students 5 --staff 2

# Large dataset for performance testing
python manage.py seed_db --clear --students 500 --staff 50
```

### Incremental Seeding

```bash
# Add more data without clearing existing
python manage.py seed_db --students 25 --staff 5
```

## Security Notes

- **Never use this seeder in production**
- All seeded accounts use simple passwords for development only
- The seeder is designed for development and testing environments
- Always use strong, unique passwords in production

## Troubleshooting

### Permission Errors
Ensure your database user has CREATE, INSERT, UPDATE, and DELETE permissions.

### Memory Issues
For very large datasets (1000+ users), consider running the seeder in smaller batches.

### Existing Data Conflicts
Use the `--clear` flag to remove existing data before seeding if you encounter unique constraint errors.