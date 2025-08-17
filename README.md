# My University Services

A comprehensive web platform for university services built with Django, providing secure student portal and staff control panel functionality.

## 🚀 Features

### Student Portal (Phase 1)
- **Secure Authentication**: Login with username/student ID
- **Digital University ID**: QR code-enabled digital student ID
- **E-Services Center**: Submit and track various requests
- **Financial Center**: View fees, payment history, and manual payment verification
- **Document Inbox**: Access official documents and certificates
- **Notifications & Support**: Real-time notifications and support ticket system

### Staff Control Panel (Phase 2)
- **Main Dashboard**: Overview of system statistics and pending items
- **Academic Request Management**: Process and manage student requests
- **Financial Management**: Payment verification and invoice management
- **Student Affairs**: Student management and document handling
- **Announcements & Alerts**: System-wide communication tools

## 🛠 Technology Stack

- **Backend**: Django 4.2.7
- **Frontend**: Django Templates + Tailwind CSS + Alpine.js
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **File Storage**: Local storage with media handling
- **Authentication**: Django's built-in authentication system

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (for Celery)
- Node.js (for Tailwind CSS development, optional)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd univ_services
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### PostgreSQL Configuration
1. Create a PostgreSQL database:
```sql
CREATE DATABASE univ_services;
CREATE USER univ_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE univ_services TO univ_user;
```

2. Update database settings in `univ_services/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'univ_services',
        'USER': 'univ_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Collect Static Files
```bash
python manage.py collectstatic
```

### 8. Start Redis Server
```bash
# On Windows (if Redis is installed)
redis-server

# On macOS with Homebrew
brew services start redis

# On Ubuntu/Debian
sudo systemctl start redis-server
```

### 9. Start Celery Worker (Optional)
```bash
# In a separate terminal
celery -A univ_services worker --loglevel=info
```

### 10. Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## 📁 Project Structure

```
univ_services/
├── accounts/                 # User authentication and profiles
├── student_portal/          # Student-facing features
├── staff_panel/            # Staff control panel
├── financial/              # Financial management
├── notifications/          # Notifications and announcements
├── templates/              # HTML templates
│   ├── base/              # Base templates and navigation
│   ├── accounts/          # Authentication templates
│   ├── student_portal/    # Student portal templates
│   ├── staff_panel/       # Staff panel templates
│   ├── financial/         # Financial templates
│   └── notifications/     # Notification templates
├── static/                 # Static files
│   ├── css/              # Custom CSS
│   ├── js/               # Custom JavaScript
│   ├── images/           # Images
│   └── fonts/            # Fonts
├── media/                  # User uploaded files
├── univ_services/         # Main project settings
└── requirements.txt       # Python dependencies
```

## 🎨 Frontend Technologies

### Tailwind CSS
- Utility-first CSS framework
- Responsive design components
- Custom color schemes and animations
- CDN integration for development

### Alpine.js
- Lightweight JavaScript framework
- Reactive components for interactivity
- Form handling and validation
- AJAX requests and real-time updates

## 🔐 Security Features

- CSRF protection on all forms
- User authentication and authorization
- Role-based access control (Student/Staff)
- Secure file upload handling
- Password strength requirements
- Session management

## 📱 Responsive Design

- Mobile-first approach
- Responsive navigation
- Touch-friendly interfaces
- Optimized for tablets and smartphones

## 🚀 Deployment

### Environment Variables
Create a `.env` file for production:
```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up SSL/HTTPS
- [ ] Configure static file serving
- [ ] Set up database backups
- [ ] Configure email settings
- [ ] Set up monitoring and logging

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📊 Features Overview

### Student Features
- ✅ User authentication and profile management
- ✅ Digital ID with QR code
- ✅ Service request submission and tracking
- ✅ Financial dashboard and payment history
- ✅ Document management
- ✅ Support ticket system
- ✅ Real-time notifications

### Staff Features
- ✅ Dashboard with system statistics
- ✅ Request management and approval workflow
- ✅ Payment verification system
- ✅ Student management tools
- ✅ Announcement system
- ✅ Reporting and analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Version History

- **v1.0.0** - Initial release with student portal
- **v1.1.0** - Staff control panel (Phase 2)
- **v1.2.0** - Enhanced notifications and reporting

---

**Built with ❤️ using Django, Tailwind CSS, and Alpine.js**