# API Documentation Auto-Update System

## Overview

This system automatically updates API documentation whenever API endpoints are modified, ensuring that documentation stays synchronized with the actual implementation.

## Components

### 1. Documentation Update Middleware

The middleware monitors API endpoint changes and triggers documentation updates.

**File:** `univ_services/middleware/doc_update_middleware.py`

### 2. Management Commands

Custom Django management commands for documentation generation and updates.

**Files:**
- `management/commands/generate_api_docs.py`
- `management/commands/update_api_docs.py`
- `management/commands/validate_api_docs.py`

### 3. Documentation Templates

Templates for generating consistent API documentation.

**Directory:** `docs/templates/`

### 4. Configuration

Settings and configuration for the documentation system.

**File:** `docs/config/doc_config.py`

## Installation and Setup

### 1. Add Middleware

Add the documentation update middleware to your Django settings:

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'univ_services.middleware.doc_update_middleware.DocumentationUpdateMiddleware',
]

# Documentation settings
DOCUMENTATION_SETTINGS = {
    'AUTO_UPDATE': True,
    'UPDATE_ON_CHANGE': True,
    'BACKUP_OLD_DOCS': True,
    'NOTIFICATION_EMAILS': ['admin@university.edu'],
    'APPS_TO_MONITOR': [
        'accounts.accounts_api',
        'student_portal.student_api', 
        'staff_panel.staff_api',
        'financial.financial_api',
        'notifications.notifications_api',
    ],
    'OUTPUT_DIRECTORY': 'docs/',
    'TEMPLATE_DIRECTORY': 'docs/templates/',
}
```

### 2. Create Required Directories

```bash
mkdir -p docs/templates
mkdir -p docs/backups
mkdir -p docs/logs
```

### 3. Run Initial Documentation Generation

```bash
python manage.py generate_api_docs
```

## Usage

### Automatic Updates

The system automatically detects changes to API endpoints and updates documentation when:

1. **View Functions Modified:** When API view functions are changed
2. **URL Patterns Updated:** When URL routing is modified
3. **Serializers Changed:** When API serializers are updated
4. **Model Changes:** When models used by APIs are modified

### Manual Updates

#### Generate Complete Documentation

```bash
# Generate documentation for all apps
python manage.py generate_api_docs

# Generate documentation for specific app
python manage.py generate_api_docs --app accounts

# Generate with custom template
python manage.py generate_api_docs --template custom_template.md
```

#### Update Existing Documentation

```bash
# Update all documentation
python manage.py update_api_docs

# Update specific app documentation
python manage.py update_api_docs --app financial

# Force update (ignore timestamps)
python manage.py update_api_docs --force
```

#### Validate Documentation

```bash
# Validate all documentation
python manage.py validate_api_docs

# Validate specific app
python manage.py validate_api_docs --app student_portal

# Check for missing documentation
python manage.py validate_api_docs --check-missing
```

## Documentation Templates

### Base Template Structure

```markdown
# {{app_name}} API Documentation

## Overview

{{app_description}}

**Base URL:** `{{base_url}}`

## Authentication

{{authentication_info}}

## Endpoints

{% for endpoint in endpoints %}
### {{endpoint.name}}

**Endpoint:** `{{endpoint.method}} {{endpoint.url}}`

**Description:** {{endpoint.description}}

**Authentication:** {{endpoint.auth_required}}

{% if endpoint.parameters %}
**Parameters:**
{% for param in endpoint.parameters %}
- `{{param.name}}` ({{param.type}}): {{param.description}}
{% endfor %}
{% endif %}

**Request Body:**
```json
{{endpoint.request_example}}
```

**Response (Success - {{endpoint.success_code}}):**
```json
{{endpoint.response_example}}
```

{% if endpoint.error_responses %}
**Error Responses:**
{% for error in endpoint.error_responses %}
**{{error.code}} - {{error.name}}:**
```json
{{error.example}}
```
{% endfor %}
{% endif %}

---

{% endfor %}

## Error Handling

{{error_handling_section}}

## Rate Limiting

{{rate_limiting_info}}

## Integration Examples

{{integration_examples}}

---

**Last Updated:** {{last_updated}}
**API Version:** {{api_version}}
**Auto-generated:** {{generation_timestamp}}
```

### Custom Templates

You can create custom templates for specific apps or use cases:

```markdown
<!-- docs/templates/financial_template.md -->
# Financial API Documentation

## Payment Processing

{{payment_endpoints}}

## Fee Management

{{fee_endpoints}}

## Financial Reports

{{report_endpoints}}
```

## Configuration Options

### Documentation Settings

```python
# docs/config/doc_config.py

DOCUMENTATION_CONFIG = {
    # Auto-update settings
    'AUTO_UPDATE': {
        'ENABLED': True,
        'DELAY_SECONDS': 5,  # Delay before updating after change
        'BATCH_UPDATES': True,  # Batch multiple changes
        'MAX_BATCH_SIZE': 10,
    },
    
    # Monitoring settings
    'MONITORING': {
        'WATCH_FILES': [
            'views.py',
            'serializers.py', 
            'urls.py',
            'models.py',
        ],
        'IGNORE_PATTERNS': [
            '*.pyc',
            '__pycache__',
            '.git',
        ],
    },
    
    # Generation settings
    'GENERATION': {
        'INCLUDE_EXAMPLES': True,
        'INCLUDE_ERROR_CODES': True,
        'INCLUDE_RATE_LIMITS': True,
        'INCLUDE_AUTHENTICATION': True,
        'GENERATE_POSTMAN_COLLECTION': True,
        'GENERATE_OPENAPI_SPEC': True,
    },
    
    # Backup settings
    'BACKUP': {
        'ENABLED': True,
        'MAX_BACKUPS': 10,
        'BACKUP_DIRECTORY': 'docs/backups/',
        'COMPRESS_BACKUPS': True,
    },
    
    # Notification settings
    'NOTIFICATIONS': {
        'EMAIL_ON_UPDATE': True,
        'SLACK_WEBHOOK': None,
        'DISCORD_WEBHOOK': None,
    },
}
```

### App-Specific Configuration

```python
# In each app's apps.py
from django.apps import AppConfig

class AccountsApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts.accounts_api'
    
    # Documentation configuration
    doc_config = {
        'title': 'Accounts API',
        'description': 'User authentication and profile management',
        'version': '1.0.0',
        'base_url': '/api/accounts/',
        'authentication': 'JWT Bearer Token',
        'rate_limits': {
            'login': '5 per minute',
            'profile': '30 per minute',
        },
        'custom_template': 'accounts_template.md',
        'include_in_global_docs': True,
    }
```

## Monitoring and Logging

### Log Files

The system creates detailed logs of all documentation updates:

```
docs/logs/
├── doc_updates.log          # General update log
├── errors.log              # Error log
├── performance.log         # Performance metrics
└── changes.log            # Detailed change log
```

### Log Format

```
2024-12-03 10:30:00 [INFO] Documentation update triggered for accounts.accounts_api
2024-12-03 10:30:01 [INFO] Detected changes in views.py: api_login function modified
2024-12-03 10:30:02 [INFO] Backing up existing documentation to docs/backups/accounts_20241203_103002.md
2024-12-03 10:30:03 [INFO] Generating new documentation using template accounts_template.md
2024-12-03 10:30:04 [INFO] Documentation updated successfully: docs/accounts/README.md
2024-12-03 10:30:05 [INFO] Notification sent to admin@university.edu
```

## API Endpoint Detection

### Automatic Detection

The system automatically detects API endpoints by:

1. **URL Pattern Analysis:** Scanning URL patterns for API routes
2. **View Function Inspection:** Analyzing view functions and classes
3. **Decorator Detection:** Finding DRF decorators and viewsets
4. **Serializer Analysis:** Examining serializer classes for data structures

### Manual Endpoint Registration

You can manually register endpoints for documentation:

```python
# In your views.py
from univ_services.docs.decorators import document_api

@document_api(
    title="User Login",
    description="Authenticate user and return JWT tokens",
    request_example={
        "username": "john_doe",
        "password": "secure_password"
    },
    response_example={
        "success": True,
        "data": {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    },
    error_responses=[
        {
            "code": 401,
            "description": "Invalid credentials",
            "example": {"success": False, "message": "Invalid username or password"}
        }
    ]
)
@api_view(['POST'])
def api_login(request):
    # Your login logic here
    pass
```

## Integration with CI/CD

### GitHub Actions

```yaml
# .github/workflows/update-docs.yml
name: Update API Documentation

on:
  push:
    paths:
      - '**/views.py'
      - '**/serializers.py'
      - '**/urls.py'
      - '**/models.py'
  pull_request:
    paths:
      - '**/views.py'
      - '**/serializers.py'
      - '**/urls.py'
      - '**/models.py'

jobs:
  update-docs:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Update API Documentation
      run: |
        python manage.py update_api_docs --force
    
    - name: Validate Documentation
      run: |
        python manage.py validate_api_docs
    
    - name: Commit updated documentation
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add docs/
        git diff --staged --quiet || git commit -m "Auto-update API documentation"
        git push
```

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Update documentation before commit
python manage.py update_api_docs

# Add updated docs to commit
git add docs/

exit 0
```

## Troubleshooting

### Common Issues

#### Documentation Not Updating

1. Check if middleware is properly installed
2. Verify `AUTO_UPDATE` is enabled in settings
3. Check log files for errors
4. Ensure proper file permissions

#### Template Errors

1. Validate template syntax
2. Check template variables are available
3. Verify template file paths

#### Performance Issues

1. Adjust `DELAY_SECONDS` in configuration
2. Enable `BATCH_UPDATES`
3. Limit monitored file types
4. Use specific app monitoring instead of global

### Debug Commands

```bash
# Check system status
python manage.py validate_api_docs --verbose

# Test template rendering
python manage.py generate_api_docs --dry-run --app accounts

# Check file monitoring
python manage.py check_doc_monitoring

# View recent changes
python manage.py show_doc_changes --days 7
```

## Best Practices

### 1. Documentation Standards

- Use consistent naming conventions
- Include comprehensive examples
- Document all error responses
- Provide integration examples
- Keep descriptions clear and concise

### 2. Template Management

- Use version control for templates
- Test templates before deployment
- Keep templates modular and reusable
- Document template variables

### 3. Monitoring

- Regularly check log files
- Monitor system performance
- Set up alerts for failures
- Review generated documentation

### 4. Maintenance

- Clean up old backups regularly
- Update templates as needed
- Review and update configuration
- Test the system after Django updates

## API Reference

### Management Commands

#### generate_api_docs

```bash
python manage.py generate_api_docs [options]

Options:
  --app APP_NAME          Generate docs for specific app
  --template TEMPLATE     Use custom template
  --output OUTPUT_DIR     Specify output directory
  --format FORMAT         Output format (markdown, html, json)
  --include-examples      Include request/response examples
  --dry-run              Show what would be generated without writing files
```

#### update_api_docs

```bash
python manage.py update_api_docs [options]

Options:
  --app APP_NAME          Update docs for specific app
  --force                Force update regardless of timestamps
  --backup               Create backup before update
  --notify               Send notifications after update
```

#### validate_api_docs

```bash
python manage.py validate_api_docs [options]

Options:
  --app APP_NAME          Validate docs for specific app
  --check-missing        Check for missing documentation
  --check-outdated       Check for outdated documentation
  --verbose              Show detailed validation results
```

### Python API

```python
from univ_services.docs.generator import DocumentationGenerator
from univ_services.docs.updater import DocumentationUpdater

# Generate documentation programmatically
generator = DocumentationGenerator()
docs = generator.generate_for_app('accounts.accounts_api')

# Update documentation
updater = DocumentationUpdater()
updater.update_app_docs('financial.financial_api')

# Check if documentation needs update
needs_update = updater.check_if_update_needed('student_portal.student_api')
```

## Future Enhancements

### Planned Features

1. **Interactive Documentation:** Generate interactive API documentation with try-it-out functionality
2. **API Versioning Support:** Handle multiple API versions in documentation
3. **Multi-language Support:** Generate documentation in multiple languages
4. **Advanced Analytics:** Track documentation usage and API endpoint popularity
5. **Integration Testing:** Automatically test documented examples
6. **Visual Documentation:** Generate API flow diagrams and visual guides

### Roadmap

- **v1.1:** Interactive documentation generation
- **v1.2:** API versioning support
- **v1.3:** Multi-language documentation
- **v2.0:** Complete rewrite with plugin architecture

---

**Last Updated:** December 2024
**System Version:** 1.0.0
**Maintainer:** Documentation Systems Team