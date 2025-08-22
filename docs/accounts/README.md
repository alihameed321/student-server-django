# Accounts API Documentation

## Overview

The Accounts API handles user authentication, profile management, and user-related operations for the university services system. This API supports both web and mobile applications, with enhanced profile data structure for comprehensive student information display.

**Base URL:** `/api/auth/`

## Recent Updates

### Version 2.1.0 - Student Details Enhancement
- **Enhanced User Profile Endpoint**: The `/api/auth/profile/` endpoint now returns comprehensive user data including profile pictures, emergency contacts, and extended academic information
- **Mobile App Integration**: Added full support for the mobile app's Student Details page with detailed profile sections
- **Improved Data Structure**: Updated response format to include all necessary fields for complete student profile display
- **Authentication Context**: Enhanced BLoC integration for seamless state management in Flutter mobile app
- **Profile Picture Support**: Added profile picture URL handling for user avatars
- **Emergency Contact Information**: Extended student profiles to include emergency contact details

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

**Description:** Get current authenticated user's comprehensive profile information including personal details, academic information, and extended profile data. This endpoint is used by the mobile app's Student Details page to display complete user information.

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
    "profile_picture": "/media/profiles/john_doe.jpg",
    "major": "Computer Science",
    "academic_level": "undergraduate",
    "enrollment_year": 2024,
    "department": null,
    "position": null,
    "is_student": true,
    "is_staff_member": false,
    "student_profile": {
      "student_id_number": "CS2024001",
      "gpa": "3.75",
      "total_credits": 45,
      "graduation_date": "2028-05-15",
      "emergency_contact_name": "Jane Doe",
      "emergency_contact_phone": "+1234567891"
    },
    "staff_profile": null
  }
}
```

**Profile Data Structure:**

**Personal Information:**
- `first_name`, `last_name`: User's full name
- `university_id`: Unique university identifier
- `email`: Primary email address
- `phone_number`: Contact phone number
- `date_of_birth`: Date of birth (YYYY-MM-DD format)
- `profile_picture`: URL to profile image (if uploaded)
- `user_type`: Account type ("student" or "staff")

**Academic Information (Students):**
- `major`: Field of study/program
- `academic_level`: Academic level (undergraduate, graduate, etc.)
- `enrollment_year`: Year of enrollment
- `student_profile.gpa`: Current GPA
- `student_profile.total_credits`: Total credits completed
- `student_profile.graduation_date`: Expected graduation date

**Account Status:**
- `is_student`: Boolean indicating student status
- `is_staff_member`: Boolean indicating staff status

**Emergency Contact (Students):**
- `student_profile.emergency_contact_name`: Emergency contact person
- `student_profile.emergency_contact_phone`: Emergency contact number

**Mobile App Integration:**
This endpoint is specifically designed to support the mobile app's Student Details page, which displays:
- Profile picture and basic information
- Personal information section
- Academic information section
- Account information section
- Emergency contact details

**Usage Notes:**
- All profile fields are optional except core identification fields
- Profile pictures are served as full URLs when available
- Student-specific fields are only populated for student accounts
- Staff-specific fields are only populated for staff accounts

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

## Mobile App Integration

### Student Details Page

The mobile application includes a comprehensive Student Details page that displays complete student profile information. This page is accessible through the profile section and provides a detailed view of all student data.

**Features:**
- **Profile Section**: Displays profile picture, name, and university ID
- **Personal Information**: Shows contact details, enrollment information, and account status
- **Academic Information**: Displays major, academic level, university ID, and student status
- **Account Information**: Shows account status and verification details

**API Integration:**
The Student Details page uses the `/api/auth/profile/` endpoint to fetch comprehensive user data. The mobile app processes the following data structure:

```dart
// Flutter/Dart model structure
class User {
  final int id;
  final String email;
  final String firstName;
  final String lastName;
  final String? studentId;        // maps to university_id
  final String? phone;            // maps to phone_number
  final bool isActive;
  final bool isStaff;             // maps to is_staff_member
  final DateTime? dateJoined;
  final String? major;
  final String? academicLevel;    // maps to academic_level
  final String? department;
  final String? profilePicture;   // maps to profile_picture
  final String? userType;         // maps to user_type
}
```

**Navigation:**
The Student Details page is accessed via navigation from the profile header:
```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => BlocProvider.value(
      value: context.read<AuthBloc>(),
      child: const StudentDetailsPage(),
    ),
  ),
);
```

**Authentication Context:**
The page uses `BlocBuilder<AuthBloc, AuthState>` to access authenticated user data and automatically updates when the authentication state changes.

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
const loginResponse = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'password123'
  })
});

const loginData = await loginResponse.json();
if (loginData.success) {
  localStorage.setItem('access_token', loginData.access_token);
  localStorage.setItem('refresh_token', loginData.refresh_token);
  // User profile data is included in login response
  console.log('User profile:', loginData.user);
}

// Get Updated Profile
const profileResponse = await fetch('/api/auth/profile/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json',
  }
});

const profileData = await profileResponse.json();
console.log('Updated user profile:', profileData.user);
```

### Flutter/Dart Mobile App

```dart
// Login with comprehensive user data
final response = await http.post(
  Uri.parse('$baseUrl/api/auth/login/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'username': 'john_doe',
    'password': 'password123',
  }),
);

if (response.statusCode == 200) {
  final data = jsonDecode(response.body);
  final accessToken = data['access_token'];
  final refreshToken = data['refresh_token'];
  
  // Parse comprehensive user data
  final user = UserModel.fromJson(data['user']);
  
  // Store tokens and user data
  await _secureStorage.write(key: 'access_token', value: accessToken);
  await _secureStorage.write(key: 'refresh_token', value: refreshToken);
}

// Get Profile for Student Details Page
final profileResponse = await http.get(
  Uri.parse('$baseUrl/api/auth/profile/'),
  headers: {
    'Authorization': 'Bearer $accessToken',
    'Content-Type': 'application/json',
  },
);

if (profileResponse.statusCode == 200) {
  final profileData = jsonDecode(profileResponse.body);
  final user = UserModel.fromJson(profileData['user']);
  
  // Use in Student Details Page
  return StudentDetailsPage(user: user);
}

// BLoC Integration for Student Details
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  AuthBloc() : super(AuthInitial()) {
    on<AuthCheckRequested>((event, emit) async {
      final token = await _secureStorage.read(key: 'access_token');
      if (token != null) {
        final user = await _getUserProfile(token);
        emit(AuthAuthenticated(user: user));
      } else {
        emit(AuthUnauthenticated());
      }
    });
  }
}

// Student Details Page Usage
class StudentDetailsPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AuthBloc, AuthState>(
      builder: (context, state) {
        if (state is AuthAuthenticated) {
          final user = state.user;
          return Scaffold(
            appBar: AppBar(title: Text('Student Details')),
            body: Column(
              children: [
                // Profile Section
                _buildProfileSection(user),
                // Personal Information
                _buildPersonalInfo(user),
                // Academic Information
                _buildAcademicInfo(user),
              ],
            ),
          );
        }
        return CircularProgressIndicator();
      },
    );
  }
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