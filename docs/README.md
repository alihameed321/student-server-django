# University Services API Documentation

This directory contains comprehensive API documentation for all university services endpoints.

## Documentation Structure

- `accounts/` - Authentication and user management APIs
- `student_portal/` - Student services and portal APIs
- `staff_panel/` - Staff administrative APIs
- `financial/` - Financial management and payment APIs
- `notifications/` - Notification system APIs

## API Base URL

**Development:** `http://localhost:8000/api/`
**Production:** `https://your-domain.com/api/`

## Authentication

All API endpoints (except login and registration) require JWT authentication.

### Headers Required:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token Management:
- Access tokens expire in 60 minutes
- Refresh tokens expire in 7 days
- Use `/api/auth/refresh/` to get new access tokens

## Response Format

All API responses follow this standard format:

```json
{
  "success": true|false,
  "message": "Response message",
  "data": {}, // Response data (optional)
  "errors": {} // Error details (optional)
}
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Getting Started

1. Obtain access token via `/api/auth/login/`
2. Include token in Authorization header for subsequent requests
3. Refer to individual app documentation for specific endpoints

## Documentation Updates

**Important:** This documentation must be updated whenever API endpoints are modified, added, or removed. Each app maintainer is responsible for keeping their respective documentation current.

## Support

For API support, contact the development team or create an issue in the project repository.