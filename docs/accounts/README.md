# Accounts API Documentation

## Overview

The Accounts API handles user authentication, profile management, and user-related operations for the university services system.

**Base URL:** `/api/auth/`

## Endpoints

### 1. User Login

**Endpoint:** `POST /api/auth/login/`

**Description:** Authenticate user and obtain JWT tokens

**Authentication:** None required

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@university.edu",
    "first_name": "John",
    "last_name": "Doe",
    "university_id": "STU2024001",
    "user_type": "student",
    "phone_number": "+1234567890",
    "date_of_birth": "2000-01-15",
    "major": "Computer Science",
    "academic_level": "undergraduate",
    "enrollment_year": 2024,
    "department": null,
    "position": null,
    "is_student": true,
    "is_staff_member": false,
    "student_profile": {
      "student_id": "CS2024001",
      "gpa": "3.75",
      "credits_completed": 45,
      "graduation_date": "2028-05-15"
    },
    "staff_profile": null
  }
}
```

**Response (Error - 401):**
```json
{
  "success": false,
  "message": "Invalid credentials",
  "errors": {
    "non_field_errors": ["Invalid username or password"]
  }
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

---

### 2. User Logout

**Endpoint:** `POST /api/auth/logout/`

**Description:** Logout user and blacklist refresh token

**Authentication:** Bearer Token required

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "message": "Logout failed"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

---

### 3. Get User Profile

**Endpoint:** `GET /api/auth/profile/`

**Description:** Retrieve current authenticated user's profile information

**Authentication:** Bearer Token required

**Request Body:** None

**Response (Success - 200):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@university.edu",
    "first_name": "John",
    "last_name": "Doe",
    "university_id": "STU2024001",
    "user_type": "student",
    "phone_number": "+1234567890",
    "date_of_birth": "2000-01-15",
    "major": "Computer Science",
    "academic_level": "undergraduate",
    "enrollment_year": 2024,
    "department": null,
    "position": null,
    "is_student": true,
    "is_staff_member": false,
    "student_profile": {
      "student_id": "CS2024001",
      "gpa": "3.75",
      "credits_completed": 45,
      "graduation_date": "2028-05-15"
    },
    "staff_profile": null
  }
}
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

---

### 4. Refresh Token

**Endpoint:** `POST /api/auth/refresh/`

**Description:** Obtain new access token using refresh token

**Authentication:** None required

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (Error - 401):**
```json
{
  "success": false,
  "message": "Invalid refresh token"
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "message": "Refresh token required"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

## User Types

### Student User Response
```json
{
  "user_type": "student",
  "is_student": true,
  "is_staff_member": false,
  "major": "Computer Science",
  "academic_level": "undergraduate", // undergraduate, graduate, phd
  "enrollment_year": 2024,
  "student_profile": {
    "student_id": "CS2024001",
    "gpa": "3.75",
    "credits_completed": 45,
    "graduation_date": "2028-05-15"
  }
}
```

### Staff User Response
```json
{
  "user_type": "staff",
  "is_student": false,
  "is_staff_member": true,
  "department": "Computer Science",
  "position": "Professor",
  "staff_profile": {
    "employee_id": "EMP2024001",
    "hire_date": "2020-08-15",
    "office_location": "Building A, Room 301",
    "office_hours": "Mon-Fri 2:00-4:00 PM"
  }
}
```

## Error Handling

### Common Error Responses

**Invalid Token (401):**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

**Missing Token (401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Validation Errors (400):**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "username": ["This field is required."],
    "password": ["This field is required."]
  }
}
```

## Security Notes

1. **Token Storage:** Store tokens securely on the client side
2. **Token Expiry:** Access tokens expire in 60 minutes, refresh tokens in 7 days
3. **HTTPS:** Always use HTTPS in production
4. **Rate Limiting:** Login attempts may be rate-limited
5. **Password Policy:** Passwords must meet university security requirements

## Integration Examples

### JavaScript/Fetch
```javascript
// Login
const login = async (username, password) => {
  const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  
  const data = await response.json();
  
  if (data.success) {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data.user;
  } else {
    throw new Error(data.message);
  }
};

// Authenticated Request
const getProfile = async () => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('/api/auth/profile/', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  return response.json();
};
```

### Flutter/Dart
```dart
// Login
Future<Map<String, dynamic>> login(String username, String password) async {
  final response = await http.post(
    Uri.parse('${ApiConstants.baseUrl}/auth/login/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'username': username,
      'password': password,
    }),
  );
  
  final data = jsonDecode(response.body);
  
  if (data['success']) {
    await storage.write(key: 'access_token', value: data['access_token']);
    await storage.write(key: 'refresh_token', value: data['refresh_token']);
  }
  
  return data;
}
```

## Changelog

### Version 1.0.0 (Current)
- Initial API implementation
- JWT authentication
- User profile management
- Token refresh mechanism

---

**Last Updated:** December 2024
**API Version:** 1.0.0
**Maintainer:** Development Team