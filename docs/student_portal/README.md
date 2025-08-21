# Student Portal API Documentation

## Overview

The Student Portal API provides endpoints for student services including dashboard data, service requests, document management, and support tickets.

**Base URL:** `/api/student/`

## Authentication

All endpoints require JWT authentication with student user privileges.

**Headers Required:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Endpoints

### 1. Student Dashboard

**Endpoint:** `GET /api/student/dashboard/`

**Description:** Get student dashboard overview with statistics and recent activities

**Authentication:** Bearer Token required (Student only)

**Request Body:** None

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Dashboard data retrieved successfully",
  "data": {
    "statistics": {
      "pending_requests": 3,
      "new_documents": 2,
      "open_tickets": 1,
      "completed_requests": 15
    },
    "recent_requests": [
      {
        "id": 1,
        "request_type": "transcript",
        "status": "pending",
        "created_at": "2024-12-01T10:30:00Z",
        "priority": "normal",
        "description": "Official transcript for job application"
      },
      {
        "id": 2,
        "request_type": "enrollment_certificate",
        "status": "approved",
        "created_at": "2024-11-28T14:15:00Z",
        "priority": "high",
        "description": "Enrollment certificate for scholarship"
      }
    ],
    "recent_documents": [
      {
        "id": 1,
        "document_type": "transcript",
        "title": "Official Transcript - Fall 2024",
        "issued_date": "2024-12-01T09:00:00Z",
        "download_url": "/api/student/documents/1/download/"
      }
    ],
    "notifications": [
      {
        "id": 1,
        "title": "Request Approved",
        "message": "Your transcript request has been approved",
        "type": "success",
        "created_at": "2024-12-01T09:00:00Z",
        "is_read": false
      }
    ]
  }
}
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/student/dashboard/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

---

### 2. Service Requests

#### 2.1 List Service Requests

**Endpoint:** `GET /api/student/requests/`

**Description:** Get paginated list of student's service requests

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `status` (optional): Filter by status (pending, in_review, approved, rejected, completed)
- `request_type` (optional): Filter by request type
- `search` (optional): Search in description

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 25,
    "next": "http://localhost:8000/api/student/requests/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "request_type": "transcript",
        "status": "pending",
        "priority": "normal",
        "description": "Official transcript for job application",
        "created_at": "2024-12-01T10:30:00Z",
        "updated_at": "2024-12-01T10:30:00Z",
        "due_date": "2024-12-15T23:59:59Z",
        "staff_notes": null,
        "documents": [
          {
            "id": 1,
            "name": "job_offer_letter.pdf",
            "file_size": 245760,
            "uploaded_at": "2024-12-01T10:30:00Z"
          }
        ]
      }
    ]
  }
}
```

#### 2.2 Create Service Request

**Endpoint:** `POST /api/student/requests/`

**Description:** Create a new service request

**Request Body (multipart/form-data):**
```
request_type: "transcript" | "enrollment_certificate" | "grade_report" | "letter_of_recommendation" | "course_completion" | "other"
priority: "low" | "normal" | "high" | "urgent"
description: "string"
due_date: "2024-12-15" (optional)
documents: [file1, file2] (optional)
```

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Service request created successfully",
  "data": {
    "id": 1,
    "request_type": "transcript",
    "status": "pending",
    "priority": "normal",
    "description": "Official transcript for job application",
    "created_at": "2024-12-01T10:30:00Z",
    "due_date": "2024-12-15T23:59:59Z"
  }
}
```

#### 2.3 Get Service Request Details

**Endpoint:** `GET /api/student/requests/{id}/`

**Description:** Get detailed information about a specific service request

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "request_type": "transcript",
    "status": "approved",
    "priority": "normal",
    "description": "Official transcript for job application",
    "created_at": "2024-12-01T10:30:00Z",
    "updated_at": "2024-12-02T14:20:00Z",
    "due_date": "2024-12-15T23:59:59Z",
    "staff_notes": "Request approved. Document will be ready in 2-3 business days.",
    "processed_by": {
      "id": 5,
      "name": "Jane Smith",
      "position": "Academic Registrar"
    },
    "documents": [
      {
        "id": 1,
        "name": "job_offer_letter.pdf",
        "file_size": 245760,
        "uploaded_at": "2024-12-01T10:30:00Z",
        "download_url": "/api/student/requests/1/documents/1/download/"
      }
    ],
    "status_history": [
      {
        "status": "pending",
        "timestamp": "2024-12-01T10:30:00Z",
        "notes": "Request submitted"
      },
      {
        "status": "in_review",
        "timestamp": "2024-12-02T09:15:00Z",
        "notes": "Under review by academic office"
      },
      {
        "status": "approved",
        "timestamp": "2024-12-02T14:20:00Z",
        "notes": "Request approved by Jane Smith"
      }
    ]
  }
}
```

#### 2.4 Cancel Service Request

**Endpoint:** `DELETE /api/student/requests/{id}/`

**Description:** Cancel a pending service request

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Service request cancelled successfully"
}
```

---

### 3. Documents

#### 3.1 List Documents

**Endpoint:** `GET /api/student/documents/`

**Description:** Get student's official documents

**Query Parameters:**
- `page` (optional): Page number
- `document_type` (optional): Filter by document type
- `search` (optional): Search in title

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "document_type": "transcript",
        "title": "Official Transcript - Fall 2024",
        "description": "Complete academic transcript",
        "issued_date": "2024-12-01T09:00:00Z",
        "expiry_date": null,
        "file_size": 512000,
        "download_url": "/api/student/documents/1/download/",
        "is_verified": true
      }
    ]
  }
}
```

#### 3.2 Download Document

**Endpoint:** `GET /api/student/documents/{id}/download/`

**Description:** Download a specific document

**Response:** File download (PDF/DOC/etc.)

---

### 4. Support Tickets

#### 4.1 List Support Tickets

**Endpoint:** `GET /api/student/tickets/`

**Description:** Get student's support tickets

**Query Parameters:**
- `page` (optional): Page number
- `status` (optional): Filter by status (open, in_progress, resolved, closed)
- `category` (optional): Filter by category

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 5,
    "results": [
      {
        "id": 1,
        "subject": "Unable to access online portal",
        "category": "technical",
        "priority": "medium",
        "status": "open",
        "description": "I'm getting an error when trying to log into the student portal",
        "created_at": "2024-12-01T11:00:00Z",
        "updated_at": "2024-12-01T11:00:00Z",
        "assigned_to": {
          "id": 3,
          "name": "Tech Support Team"
        },
        "response_count": 2
      }
    ]
  }
}
```

#### 4.2 Create Support Ticket

**Endpoint:** `POST /api/student/tickets/`

**Description:** Create a new support ticket

**Request Body:**
```json
{
  "subject": "Unable to access online portal",
  "category": "technical", // technical, academic, financial, general
  "priority": "medium", // low, medium, high, urgent
  "description": "I'm getting an error when trying to log into the student portal"
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Support ticket created successfully",
  "data": {
    "id": 1,
    "subject": "Unable to access online portal",
    "category": "technical",
    "priority": "medium",
    "status": "open",
    "created_at": "2024-12-01T11:00:00Z",
    "ticket_number": "TICK-2024-001"
  }
}
```

#### 4.3 Get Ticket Details

**Endpoint:** `GET /api/student/tickets/{id}/`

**Description:** Get detailed ticket information with responses

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "subject": "Unable to access online portal",
    "category": "technical",
    "priority": "medium",
    "status": "in_progress",
    "description": "I'm getting an error when trying to log into the student portal",
    "created_at": "2024-12-01T11:00:00Z",
    "updated_at": "2024-12-01T15:30:00Z",
    "ticket_number": "TICK-2024-001",
    "assigned_to": {
      "id": 3,
      "name": "John Tech",
      "position": "IT Support Specialist"
    },
    "responses": [
      {
        "id": 1,
        "message": "Thank you for contacting support. We're looking into this issue.",
        "created_at": "2024-12-01T12:00:00Z",
        "is_staff_response": true,
        "author": {
          "name": "John Tech",
          "position": "IT Support Specialist"
        }
      },
      {
        "id": 2,
        "message": "I've tried clearing my browser cache but the issue persists.",
        "created_at": "2024-12-01T15:30:00Z",
        "is_staff_response": false,
        "author": {
          "name": "Student User"
        }
      }
    ]
  }
}
```

#### 4.4 Add Ticket Response

**Endpoint:** `POST /api/student/tickets/{id}/responses/`

**Description:** Add a response to an existing ticket

**Request Body:**
```json
{
  "message": "I've tried the suggested solution but it didn't work."
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Response added successfully",
  "data": {
    "id": 3,
    "message": "I've tried the suggested solution but it didn't work.",
    "created_at": "2024-12-01T16:00:00Z"
  }
}
```

---

### 5. Notifications

#### 5.1 Get Notifications

**Endpoint:** `GET /api/student/notifications/`

**Description:** Get student notifications

**Query Parameters:**
- `page` (optional): Page number
- `is_read` (optional): Filter by read status (true/false)
- `type` (optional): Filter by notification type

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 15,
    "unread_count": 3,
    "results": [
      {
        "id": 1,
        "title": "Request Approved",
        "message": "Your transcript request has been approved and is being processed.",
        "type": "request_update",
        "priority": "normal",
        "is_read": false,
        "created_at": "2024-12-01T09:00:00Z",
        "related_object": {
          "type": "service_request",
          "id": 1,
          "url": "/api/student/requests/1/"
        }
      }
    ]
  }
}
```

#### 5.2 Mark Notification as Read

**Endpoint:** `PATCH /api/student/notifications/{id}/read/`

**Description:** Mark a notification as read

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

#### 5.3 Mark All Notifications as Read

**Endpoint:** `POST /api/student/notifications/mark-all-read/`

**Description:** Mark all notifications as read

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "All notifications marked as read"
}
```

## Data Models

### Service Request Types
```json
{
  "transcript": "Official Transcript",
  "enrollment_certificate": "Enrollment Certificate",
  "grade_report": "Grade Report",
  "letter_of_recommendation": "Letter of Recommendation",
  "course_completion": "Course Completion Certificate",
  "other": "Other Request"
}
```

### Request Status
```json
{
  "pending": "Pending Review",
  "in_review": "Under Review",
  "approved": "Approved",
  "rejected": "Rejected",
  "completed": "Completed"
}
```

### Priority Levels
```json
{
  "low": "Low Priority",
  "normal": "Normal Priority",
  "high": "High Priority",
  "urgent": "Urgent"
}
```

### Support Ticket Categories
```json
{
  "technical": "Technical Support",
  "academic": "Academic Issues",
  "financial": "Financial Matters",
  "general": "General Inquiry"
}
```

## Error Handling

### Common Error Responses

**Access Denied (403):**
```json
{
  "success": false,
  "message": "Access denied. Students only.",
  "error_code": "STUDENT_ACCESS_REQUIRED"
}
```

**Resource Not Found (404):**
```json
{
  "success": false,
  "message": "Service request not found",
  "error_code": "RESOURCE_NOT_FOUND"
}
```

**Validation Error (400):**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "request_type": ["This field is required."],
    "description": ["This field cannot be blank."]
  }
}
```

## Integration Examples

### Flutter/Dart Example
```dart
class StudentApiService {
  static const String baseUrl = 'http://localhost:8000/api/student';
  
  Future<Map<String, dynamic>> getDashboard() async {
    final token = await storage.read(key: 'access_token');
    
    final response = await http.get(
      Uri.parse('$baseUrl/dashboard/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );
    
    return jsonDecode(response.body);
  }
  
  Future<Map<String, dynamic>> createServiceRequest({
    required String requestType,
    required String description,
    String priority = 'normal',
    List<File>? documents,
  }) async {
    final token = await storage.read(key: 'access_token');
    
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/requests/'),
    );
    
    request.headers['Authorization'] = 'Bearer $token';
    request.fields['request_type'] = requestType;
    request.fields['description'] = description;
    request.fields['priority'] = priority;
    
    if (documents != null) {
      for (var doc in documents) {
        request.files.add(
          await http.MultipartFile.fromPath('documents', doc.path),
        );
      }
    }
    
    final response = await request.send();
    final responseBody = await response.stream.bytesToString();
    
    return jsonDecode(responseBody);
  }
}
```

## Rate Limiting

- **Dashboard:** 60 requests per minute
- **Service Requests:** 30 requests per minute
- **Support Tickets:** 20 requests per minute
- **File Downloads:** 100 requests per minute

## File Upload Limits

- **Maximum file size:** 10MB per file
- **Maximum files per request:** 5 files
- **Supported formats:** PDF, DOC, DOCX, JPG, PNG

## Changelog

### Version 1.0.0 (Current)
- Initial API implementation
- Dashboard endpoint
- Service request management
- Document management
- Support ticket system
- Notification system

---

**Last Updated:** December 2024
**API Version:** 1.0.0
**Maintainer:** Student Services Team