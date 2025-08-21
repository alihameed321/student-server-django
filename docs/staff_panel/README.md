# Staff Panel API Documentation

## Overview

The Staff Panel API provides endpoints for administrative functions including dashboard management, request processing, student management, financial oversight, and system administration.

**Base URL:** `/api/staff/`

## Authentication

All endpoints require JWT authentication with staff user privileges.

**Headers Required:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Endpoints

### 1. Staff Dashboard

**Endpoint:** `GET /api/staff/dashboard/`

**Description:** Get comprehensive staff dashboard with statistics and recent activities

**Authentication:** Bearer Token required (Staff only)

**Request Body:** None

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Dashboard data retrieved successfully",
  "data": {
    "statistics": {
      "total_students": 1250,
      "new_students_today": 5,
      "active_students": 1180,
      "pending_requests": 23,
      "approved_requests_today": 8,
      "rejected_requests_today": 2,
      "total_fees_collected_today": "15750.00",
      "verified_payments_today": 12,
      "pending_payments": 45,
      "open_support_tickets": 18,
      "resolved_tickets_today": 6
    },
    "recent_activities": [
      {
        "id": 1,
        "activity_type": "request_approved",
        "description": "Approved transcript request for John Doe",
        "staff_member": {
          "id": 2,
          "name": "Jane Smith",
          "position": "Academic Registrar"
        },
        "target_user": {
          "id": 100,
          "name": "John Doe",
          "university_id": "STU2024001"
        },
        "timestamp": "2024-12-01T14:30:00Z",
        "ip_address": "192.168.1.100"
      }
    ],
    "pending_requests_summary": [
      {
        "request_type": "transcript",
        "count": 8,
        "urgent_count": 2
      },
      {
        "request_type": "enrollment_certificate",
        "count": 5,
        "urgent_count": 1
      }
    ],
    "financial_summary": {
      "total_outstanding_fees": "125000.00",
      "payments_pending_verification": 15,
      "overdue_payments": 8
    },
    "quick_actions": [
      {
        "id": 1,
        "title": "Review Pending Requests",
        "description": "Process student service requests",
        "url_pattern": "/staff/requests/pending/",
        "icon": "document-check",
        "count": 23
      },
      {
        "id": 2,
        "title": "Verify Payments",
        "description": "Verify pending payments",
        "url_pattern": "/staff/payments/pending/",
        "icon": "credit-card",
        "count": 15
      }
    ]
  }
}
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/staff/dashboard/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

---

### 2. Request Management

#### 2.1 List Service Requests

**Endpoint:** `GET /api/staff/requests/`

**Description:** Get paginated list of all service requests with filtering options

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `status` (optional): Filter by status (pending, in_review, approved, rejected, completed)
- `request_type` (optional): Filter by request type
- `priority` (optional): Filter by priority
- `student_id` (optional): Filter by student university ID
- `date_from` (optional): Filter requests from date (YYYY-MM-DD)
- `date_to` (optional): Filter requests to date (YYYY-MM-DD)
- `search` (optional): Search in description or student name

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 150,
    "next": "http://localhost:8000/api/staff/requests/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "student": {
          "id": 100,
          "name": "John Doe",
          "university_id": "STU2024001",
          "email": "john@university.edu",
          "phone_number": "+1234567890"
        },
        "request_type": "transcript",
        "status": "pending",
        "priority": "normal",
        "description": "Official transcript for job application",
        "created_at": "2024-12-01T10:30:00Z",
        "updated_at": "2024-12-01T10:30:00Z",
        "due_date": "2024-12-15T23:59:59Z",
        "days_pending": 2,
        "documents_count": 1
      }
    ]
  }
}
```

#### 2.2 Get Request Details

**Endpoint:** `GET /api/staff/requests/{id}/`

**Description:** Get detailed information about a specific service request

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "student": {
      "id": 100,
      "name": "John Doe",
      "university_id": "STU2024001",
      "email": "john@university.edu",
      "phone_number": "+1234567890",
      "major": "Computer Science",
      "academic_level": "undergraduate",
      "enrollment_year": 2024
    },
    "request_type": "transcript",
    "status": "pending",
    "priority": "normal",
    "description": "Official transcript for job application",
    "created_at": "2024-12-01T10:30:00Z",
    "updated_at": "2024-12-01T10:30:00Z",
    "due_date": "2024-12-15T23:59:59Z",
    "staff_notes": null,
    "processed_by": null,
    "documents": [
      {
        "id": 1,
        "name": "job_offer_letter.pdf",
        "file_size": 245760,
        "uploaded_at": "2024-12-01T10:30:00Z",
        "download_url": "/api/staff/requests/1/documents/1/download/"
      }
    ],
    "status_history": [
      {
        "status": "pending",
        "timestamp": "2024-12-01T10:30:00Z",
        "notes": "Request submitted by student",
        "changed_by": null
      }
    ]
  }
}
```

#### 2.3 Approve Request

**Endpoint:** `POST /api/staff/requests/{id}/approve/`

**Description:** Approve a service request

**Request Body:**
```json
{
  "staff_notes": "Request approved. Document will be ready in 2-3 business days.",
  "estimated_completion": "2024-12-05" // optional
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Request approved successfully",
  "data": {
    "id": 1,
    "status": "approved",
    "staff_notes": "Request approved. Document will be ready in 2-3 business days.",
    "processed_by": {
      "id": 2,
      "name": "Jane Smith",
      "position": "Academic Registrar"
    },
    "processed_at": "2024-12-02T14:20:00Z"
  }
}
```

#### 2.4 Reject Request

**Endpoint:** `POST /api/staff/requests/{id}/reject/`

**Description:** Reject a service request

**Request Body:**
```json
{
  "staff_notes": "Request rejected due to incomplete documentation. Please provide official ID copy.",
  "rejection_reason": "incomplete_documentation" // optional
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Request rejected successfully",
  "data": {
    "id": 1,
    "status": "rejected",
    "staff_notes": "Request rejected due to incomplete documentation.",
    "processed_by": {
      "id": 2,
      "name": "Jane Smith",
      "position": "Academic Registrar"
    },
    "processed_at": "2024-12-02T14:20:00Z"
  }
}
```

#### 2.5 Complete Request

**Endpoint:** `POST /api/staff/requests/{id}/complete/`

**Description:** Mark a request as completed and optionally upload the final document

**Request Body (multipart/form-data):**
```
staff_notes: "Document has been generated and sent to student"
final_document: [file] (optional)
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Request marked as completed",
  "data": {
    "id": 1,
    "status": "completed",
    "completed_at": "2024-12-05T10:00:00Z"
  }
}
```

---

### 3. Student Management

#### 3.1 List Students

**Endpoint:** `GET /api/staff/students/`

**Description:** Get paginated list of students with search and filter options

**Query Parameters:**
- `page` (optional): Page number
- `search` (optional): Search by name, university ID, or email
- `major` (optional): Filter by major
- `academic_level` (optional): Filter by academic level
- `enrollment_year` (optional): Filter by enrollment year
- `user_type` (optional): Filter by user type
- `is_active` (optional): Filter by active status

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 1250,
    "next": "http://localhost:8000/api/staff/students/?page=2",
    "previous": null,
    "results": [
      {
        "id": 100,
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@university.edu",
        "university_id": "STU2024001",
        "user_type": "student",
        "phone_number": "+1234567890",
        "major": "Computer Science",
        "academic_level": "undergraduate",
        "enrollment_year": 2024,
        "is_active": true,
        "date_joined": "2024-08-15T09:00:00Z",
        "last_login": "2024-12-01T08:30:00Z",
        "pending_requests": 2,
        "outstanding_fees": "2500.00"
      }
    ]
  }
}
```

#### 3.2 Get Student Details

**Endpoint:** `GET /api/staff/students/{id}/`

**Description:** Get comprehensive student information

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": 100,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@university.edu",
    "university_id": "STU2024001",
    "user_type": "student",
    "phone_number": "+1234567890",
    "date_of_birth": "2000-01-15",
    "major": "Computer Science",
    "academic_level": "undergraduate",
    "enrollment_year": 2024,
    "is_active": true,
    "date_joined": "2024-08-15T09:00:00Z",
    "last_login": "2024-12-01T08:30:00Z",
    "profile_picture": "/media/profiles/john_doe.jpg",
    "student_profile": {
      "student_id": "CS2024001",
      "gpa": "3.75",
      "credits_completed": 45,
      "graduation_date": "2028-05-15"
    },
    "statistics": {
      "total_requests": 8,
      "pending_requests": 2,
      "completed_requests": 6,
      "total_fees": "5000.00",
      "outstanding_fees": "2500.00",
      "support_tickets": 3
    },
    "recent_activity": [
      {
        "type": "service_request",
        "description": "Submitted transcript request",
        "timestamp": "2024-12-01T10:30:00Z"
      }
    ]
  }
}
```

#### 3.3 Create Student

**Endpoint:** `POST /api/staff/students/`

**Description:** Create a new student account

**Request Body:**
```json
{
  "username": "jane_smith",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@university.edu",
  "university_id": "STU2024002",
  "phone_number": "+1234567891",
  "date_of_birth": "1999-05-20",
  "major": "Mathematics",
  "academic_level": "undergraduate",
  "enrollment_year": 2024,
  "password": "temporaryPassword123",
  "student_profile": {
    "student_id": "MATH2024001",
    "expected_graduation": "2028-05-15"
  }
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Student created successfully",
  "data": {
    "id": 101,
    "username": "jane_smith",
    "university_id": "STU2024002",
    "email": "jane@university.edu",
    "temporary_password": "temporaryPassword123"
  }
}
```

#### 3.4 Update Student

**Endpoint:** `PUT /api/staff/students/{id}/`

**Description:** Update student information

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith-Johnson",
  "email": "jane.johnson@university.edu",
  "phone_number": "+1234567892",
  "major": "Applied Mathematics",
  "is_active": true
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Student updated successfully",
  "data": {
    "id": 101,
    "first_name": "Jane",
    "last_name": "Smith-Johnson",
    "email": "jane.johnson@university.edu",
    "updated_at": "2024-12-02T15:00:00Z"
  }
}
```

#### 3.5 Deactivate Student

**Endpoint:** `POST /api/staff/students/{id}/deactivate/`

**Description:** Deactivate a student account

**Request Body:**
```json
{
  "reason": "Graduated",
  "notes": "Student completed degree program"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Student account deactivated successfully"
}
```

---

### 4. Financial Management

#### 4.1 Payment Verification

**Endpoint:** `GET /api/staff/payments/pending/`

**Description:** Get payments pending verification

**Query Parameters:**
- `page` (optional): Page number
- `payment_provider` (optional): Filter by payment provider
- `amount_min` (optional): Minimum amount filter
- `amount_max` (optional): Maximum amount filter
- `date_from` (optional): Filter from date
- `date_to` (optional): Filter to date

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 25,
    "results": [
      {
        "id": 1,
        "student": {
          "id": 100,
          "name": "John Doe",
          "university_id": "STU2024001"
        },
        "fee": {
          "id": 1,
          "fee_type": "Tuition Fee",
          "amount": "2500.00"
        },
        "amount": "2500.00",
        "payment_provider": {
          "id": 1,
          "name": "Bank Transfer",
          "type": "bank_transfer"
        },
        "transaction_reference": "TXN123456789",
        "payment_date": "2024-12-01T14:30:00Z",
        "status": "pending",
        "sender_name": "John Doe",
        "sender_phone": "+1234567890",
        "transfer_notes": "Tuition payment for Fall 2024",
        "days_pending": 1
      }
    ]
  }
}
```

#### 4.2 Verify Payment

**Endpoint:** `POST /api/staff/payments/{id}/verify/`

**Description:** Verify a pending payment

**Request Body:**
```json
{
  "verification_notes": "Payment verified against bank records",
  "verified_amount": "2500.00" // optional, if different from original
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Payment verified successfully",
  "data": {
    "id": 1,
    "status": "verified",
    "verified_by": {
      "id": 2,
      "name": "Jane Smith",
      "position": "Finance Officer"
    },
    "verified_at": "2024-12-02T10:00:00Z",
    "receipt_generated": true,
    "receipt_number": "RCP-2024-001"
  }
}
```

#### 4.3 Reject Payment

**Endpoint:** `POST /api/staff/payments/{id}/reject/`

**Description:** Reject a payment

**Request Body:**
```json
{
  "verification_notes": "Transaction reference not found in bank records",
  "rejection_reason": "invalid_reference"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Payment rejected successfully",
  "data": {
    "id": 1,
    "status": "rejected",
    "verified_by": {
      "id": 2,
      "name": "Jane Smith"
    },
    "verified_at": "2024-12-02T10:00:00Z"
  }
}
```

#### 4.4 Fee Management

**Endpoint:** `GET /api/staff/fees/`

**Description:** Get list of student fees

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 500,
    "results": [
      {
        "id": 1,
        "student": {
          "id": 100,
          "name": "John Doe",
          "university_id": "STU2024001"
        },
        "fee_type": {
          "id": 1,
          "name": "Tuition Fee",
          "description": "Semester tuition fee"
        },
        "amount": "2500.00",
        "amount_paid": "0.00",
        "remaining_balance": "2500.00",
        "status": "pending",
        "due_date": "2024-12-31",
        "is_overdue": false,
        "created_at": "2024-11-01T00:00:00Z"
      }
    ]
  }
}
```

#### 4.5 Create Fee

**Endpoint:** `POST /api/staff/fees/`

**Description:** Create a new fee for student(s)

**Request Body:**
```json
{
  "fee_type_id": 1,
  "amount": "2500.00",
  "due_date": "2024-12-31",
  "description": "Spring 2025 tuition fee",
  "students": [100, 101, 102], // Student IDs
  "apply_to_all_students": false, // If true, ignores students array
  "filter_criteria": { // Optional, used with apply_to_all_students
    "major": "Computer Science",
    "academic_level": "undergraduate"
  }
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Fees created successfully",
  "data": {
    "fees_created": 3,
    "total_amount": "7500.00",
    "fee_ids": [1, 2, 3]
  }
}
```

---

### 5. Support Ticket Management

#### 5.1 List Support Tickets

**Endpoint:** `GET /api/staff/tickets/`

**Description:** Get list of support tickets with filtering

**Query Parameters:**
- `status` (optional): Filter by status
- `category` (optional): Filter by category
- `priority` (optional): Filter by priority
- `assigned_to` (optional): Filter by assigned staff member
- `unassigned` (optional): Show only unassigned tickets

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 50,
    "results": [
      {
        "id": 1,
        "ticket_number": "TICK-2024-001",
        "subject": "Unable to access online portal",
        "category": "technical",
        "priority": "medium",
        "status": "open",
        "student": {
          "id": 100,
          "name": "John Doe",
          "university_id": "STU2024001"
        },
        "assigned_to": {
          "id": 3,
          "name": "Tech Support Team"
        },
        "created_at": "2024-12-01T11:00:00Z",
        "updated_at": "2024-12-01T15:30:00Z",
        "response_count": 2,
        "days_open": 1
      }
    ]
  }
}
```

#### 5.2 Assign Ticket

**Endpoint:** `POST /api/staff/tickets/{id}/assign/`

**Description:** Assign a ticket to a staff member

**Request Body:**
```json
{
  "assigned_to": 3, // Staff member ID
  "notes": "Assigning to technical support team"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Ticket assigned successfully",
  "data": {
    "assigned_to": {
      "id": 3,
      "name": "John Tech",
      "position": "IT Support Specialist"
    },
    "status": "in_progress"
  }
}
```

#### 5.3 Add Ticket Response

**Endpoint:** `POST /api/staff/tickets/{id}/responses/`

**Description:** Add a staff response to a ticket

**Request Body:**
```json
{
  "message": "Thank you for contacting support. We're looking into this issue and will get back to you shortly.",
  "is_internal": false, // true for internal staff notes
  "status_update": "in_progress" // optional status change
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Response added successfully",
  "data": {
    "id": 3,
    "message": "Thank you for contacting support...",
    "created_at": "2024-12-02T09:00:00Z",
    "is_internal": false
  }
}
```

#### 5.4 Close Ticket

**Endpoint:** `POST /api/staff/tickets/{id}/close/`

**Description:** Close a support ticket

**Request Body:**
```json
{
  "resolution_notes": "Issue resolved. Student can now access the portal.",
  "resolution_type": "resolved" // resolved, duplicate, invalid
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Ticket closed successfully",
  "data": {
    "status": "closed",
    "closed_at": "2024-12-02T16:00:00Z",
    "resolution_time_hours": 29
  }
}
```

---

### 6. Announcements

#### 6.1 Create Announcement

**Endpoint:** `POST /api/staff/announcements/`

**Description:** Create a new announcement

**Request Body:**
```json
{
  "title": "System Maintenance Scheduled",
  "content": "The student portal will be unavailable for maintenance on December 5th from 2:00 AM to 4:00 AM.",
  "announcement_type": "maintenance",
  "priority": "high",
  "target_audience": "all", // all, students, staff, specific_major, specific_year
  "target_criteria": {}, // Used when target_audience is specific
  "publish_date": "2024-12-03T08:00:00Z",
  "expiry_date": "2024-12-06T23:59:59Z",
  "send_notifications": true,
  "send_email": true
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Announcement created successfully",
  "data": {
    "id": 1,
    "title": "System Maintenance Scheduled",
    "slug": "system-maintenance-scheduled",
    "is_published": true,
    "target_users_count": 1250,
    "notifications_sent": 1250
  }
}
```

#### 6.2 List Announcements

**Endpoint:** `GET /api/staff/announcements/`

**Description:** Get list of announcements

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 15,
    "results": [
      {
        "id": 1,
        "title": "System Maintenance Scheduled",
        "announcement_type": "maintenance",
        "priority": "high",
        "target_audience": "all",
        "is_published": true,
        "publish_date": "2024-12-03T08:00:00Z",
        "expiry_date": "2024-12-06T23:59:59Z",
        "created_by": {
          "id": 2,
          "name": "Jane Smith"
        },
        "views_count": 850,
        "created_at": "2024-12-02T16:00:00Z"
      }
    ]
  }
}
```

---

### 7. Reports and Analytics

#### 7.1 Generate Report

**Endpoint:** `POST /api/staff/reports/generate/`

**Description:** Generate various system reports

**Request Body:**
```json
{
  "report_type": "financial_summary", // financial_summary, student_activity, request_analytics
  "date_from": "2024-11-01",
  "date_to": "2024-11-30",
  "filters": {
    "department": "Computer Science",
    "include_charts": true
  },
  "format": "pdf" // pdf, excel, json
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Report generated successfully",
  "data": {
    "report_id": "RPT-2024-001",
    "download_url": "/api/staff/reports/RPT-2024-001/download/",
    "expires_at": "2024-12-09T16:00:00Z",
    "file_size": 2048576
  }
}
```

#### 7.2 System Statistics

**Endpoint:** `GET /api/staff/statistics/`

**Description:** Get comprehensive system statistics

**Query Parameters:**
- `period` (optional): time, week, month, year (default: month)
- `date_from` (optional): Custom date range start
- `date_to` (optional): Custom date range end

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "period": "month",
    "date_range": {
      "from": "2024-11-01",
      "to": "2024-11-30"
    },
    "students": {
      "total": 1250,
      "new_registrations": 45,
      "active_users": 1180,
      "by_major": {
        "Computer Science": 350,
        "Mathematics": 200,
        "Engineering": 300
      }
    },
    "requests": {
      "total": 450,
      "pending": 23,
      "approved": 380,
      "rejected": 47,
      "by_type": {
        "transcript": 180,
        "enrollment_certificate": 120,
        "grade_report": 90
      },
      "average_processing_time_hours": 48
    },
    "financial": {
      "total_fees_issued": "125000.00",
      "total_payments_received": "98000.00",
      "pending_verification": "15000.00",
      "outstanding_balance": "27000.00"
    },
    "support": {
      "total_tickets": 85,
      "resolved": 70,
      "open": 15,
      "average_resolution_time_hours": 24,
      "by_category": {
        "technical": 35,
        "academic": 25,
        "financial": 15,
        "general": 10
      }
    }
  }
}
```

---

### 8. System Configuration

#### 8.1 Get Configuration

**Endpoint:** `GET /api/staff/config/`

**Description:** Get system configuration settings

**Query Parameters:**
- `category` (optional): Filter by category (general, academic, financial, notification, security)

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "general": {
      "university_name": "University of Excellence",
      "academic_year": "2024-2025",
      "semester": "Fall 2024",
      "timezone": "UTC"
    },
    "academic": {
      "max_request_processing_days": 7,
      "auto_approve_simple_requests": false,
      "require_documents_for_transcript": true
    },
    "financial": {
      "payment_verification_required": true,
      "auto_generate_receipts": true,
      "late_payment_penalty_rate": "0.05"
    },
    "notification": {
      "email_notifications_enabled": true,
      "sms_notifications_enabled": false,
      "digest_frequency_default": "daily"
    }
  }
}
```

#### 8.2 Update Configuration

**Endpoint:** `PUT /api/staff/config/`

**Description:** Update system configuration

**Request Body:**
```json
{
  "category": "academic",
  "settings": {
    "max_request_processing_days": 5,
    "auto_approve_simple_requests": true
  }
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "data": {
    "updated_settings": 2,
    "updated_at": "2024-12-02T16:30:00Z"
  }
}
```

## Error Handling

### Common Error Responses

**Access Denied (403):**
```json
{
  "success": false,
  "message": "Access denied. Staff privileges required.",
  "error_code": "STAFF_ACCESS_REQUIRED"
}
```

**Resource Not Found (404):**
```json
{
  "success": false,
  "message": "Student not found",
  "error_code": "RESOURCE_NOT_FOUND"
}
```

**Validation Error (400):**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "amount": ["This field is required."],
    "due_date": ["Date cannot be in the past."]
  }
}
```

**Business Logic Error (422):**
```json
{
  "success": false,
  "message": "Cannot approve request in current status",
  "error_code": "INVALID_STATUS_TRANSITION",
  "details": {
    "current_status": "completed",
    "attempted_action": "approve"
  }
}
```

## Activity Logging

All staff actions are automatically logged with the following information:
- Staff member details
- Action performed
- Target resource/user
- Timestamp
- IP address
- User agent
- Additional metadata

## Rate Limiting

- **Dashboard:** 30 requests per minute
- **Request Management:** 60 requests per minute
- **Student Management:** 30 requests per minute
- **Financial Operations:** 20 requests per minute
- **Reports:** 10 requests per minute

## Permissions

Different staff roles have different permissions:

- **Academic Staff:** Request management, student information
- **Finance Staff:** Payment verification, fee management
- **IT Support:** Ticket management, system configuration
- **Administrators:** Full access to all endpoints

## Integration Examples

### Flutter/Dart Example
```dart
class StaffApiService {
  static const String baseUrl = 'http://localhost:8000/api/staff';
  
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
  
  Future<Map<String, dynamic>> approveRequest(int requestId, String notes) async {
    final token = await storage.read(key: 'access_token');
    
    final response = await http.post(
      Uri.parse('$baseUrl/requests/$requestId/approve/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'staff_notes': notes,
      }),
    );
    
    return jsonDecode(response.body);
  }
}
```

## Changelog

### Version 1.0.0 (Current)
- Initial API implementation
- Dashboard and statistics
- Request management system
- Student management
- Financial operations
- Support ticket management
- Announcement system
- Reporting and analytics
- System configuration

---

**Last Updated:** December 2024
**API Version:** 1.0.0
**Maintainer:** Administrative Systems Team