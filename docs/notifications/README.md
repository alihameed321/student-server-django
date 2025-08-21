# Notifications API Documentation

## Overview

The Notifications API provides endpoints for managing user notifications, announcements, and messaging within the university services system. It supports real-time notifications, email notifications, and notification preferences management.

**Base URL:** `/api/notifications/`

## Authentication

All endpoints require JWT authentication. Some endpoints have role-based access restrictions.

**Headers Required:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Endpoints

### 1. User Notifications

#### 1.1 Get User Notifications

**Endpoint:** `GET /api/notifications/`

**Description:** Get paginated list of notifications for the authenticated user

**Authentication:** Bearer Token required

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of notifications per page (default: 20, max: 100)
- `is_read` (optional): Filter by read status (true/false)
- `notification_type` (optional): Filter by type (system, academic, financial, support, announcement)
- `priority` (optional): Filter by priority (low, medium, high, urgent)
- `date_from` (optional): Filter from date (YYYY-MM-DD)
- `date_to` (optional): Filter to date (YYYY-MM-DD)
- `category` (optional): Filter by category
- `search` (optional): Search in title and message

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 45,
    "next": "http://localhost:8000/api/notifications/?page=2",
    "previous": null,
    "unread_count": 12,
    "results": [
      {
        "id": 1,
        "title": "Payment Verification Complete",
        "message": "Your payment of $500.00 has been verified and processed successfully.",
        "notification_type": "financial",
        "priority": "medium",
        "category": "payment_confirmation",
        "is_read": false,
        "is_archived": false,
        "created_at": "2024-12-02T10:30:00Z",
        "read_at": null,
        "expires_at": "2024-12-09T10:30:00Z",
        "sender": {
          "id": 2,
          "name": "Finance Office",
          "user_type": "staff",
          "position": "Finance Administrator"
        },
        "related_object": {
          "type": "payment",
          "id": 1,
          "reference": "PAY-2024-001"
        },
        "action_required": false,
        "action_url": "/financial/payments/1/",
        "action_text": "View Payment Details",
        "metadata": {
          "payment_amount": "500.00",
          "receipt_number": "RCP-2024-001"
        }
      },
      {
        "id": 2,
        "title": "Service Request Update",
        "message": "Your transcript request has been approved and is being processed.",
        "notification_type": "academic",
        "priority": "medium",
        "category": "request_update",
        "is_read": true,
        "is_archived": false,
        "created_at": "2024-12-01T14:20:00Z",
        "read_at": "2024-12-01T15:00:00Z",
        "expires_at": null,
        "sender": {
          "id": 3,
          "name": "Academic Office",
          "user_type": "staff",
          "position": "Registrar"
        },
        "related_object": {
          "type": "service_request",
          "id": 5,
          "reference": "REQ-2024-005"
        },
        "action_required": false,
        "action_url": "/student/requests/5/",
        "action_text": "View Request",
        "metadata": {
          "request_type": "transcript",
          "estimated_completion": "2024-12-05"
        }
      }
    ]
  }
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/notifications/?is_read=false&priority=high" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

#### 1.2 Get Notification Details

**Endpoint:** `GET /api/notifications/{id}/`

**Description:** Get detailed information about a specific notification

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Payment Verification Complete",
    "message": "Your payment of $500.00 has been verified and processed successfully. Receipt number: RCP-2024-001. You can download your receipt from the financial portal.",
    "notification_type": "financial",
    "priority": "medium",
    "category": "payment_confirmation",
    "is_read": false,
    "is_archived": false,
    "created_at": "2024-12-02T10:30:00Z",
    "read_at": null,
    "expires_at": "2024-12-09T10:30:00Z",
    "sender": {
      "id": 2,
      "name": "Finance Office",
      "user_type": "staff",
      "position": "Finance Administrator",
      "email": "finance@university.edu",
      "phone": "+1234567890"
    },
    "recipient": {
      "id": 100,
      "name": "John Doe",
      "university_id": "STU2024001",
      "email": "john@university.edu"
    },
    "related_object": {
      "type": "payment",
      "id": 1,
      "reference": "PAY-2024-001",
      "url": "/api/financial/payments/1/"
    },
    "action_required": false,
    "action_url": "/financial/payments/1/",
    "action_text": "View Payment Details",
    "metadata": {
      "payment_amount": "500.00",
      "receipt_number": "RCP-2024-001",
      "payment_method": "Bank Transfer",
      "verification_date": "2024-12-02T10:00:00Z"
    },
    "delivery_status": {
      "in_app": {
        "delivered": true,
        "delivered_at": "2024-12-02T10:30:00Z"
      },
      "email": {
        "sent": true,
        "sent_at": "2024-12-02T10:31:00Z",
        "delivered": true,
        "delivered_at": "2024-12-02T10:32:00Z",
        "opened": false
      },
      "sms": {
        "sent": false,
        "reason": "SMS notifications disabled for this category"
      }
    },
    "tags": ["payment", "verification", "financial"],
    "attachments": [
      {
        "id": 1,
        "name": "receipt_RCP-2024-001.pdf",
        "file_type": "application/pdf",
        "file_size": 245760,
        "download_url": "/api/notifications/1/attachments/1/download/"
      }
    ]
  }
}
```

#### 1.3 Mark Notification as Read

**Endpoint:** `POST /api/notifications/{id}/mark-read/`

**Description:** Mark a specific notification as read

**Request Body:** None

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Notification marked as read",
  "data": {
    "id": 1,
    "is_read": true,
    "read_at": "2024-12-02T16:30:00Z"
  }
}
```

#### 1.4 Mark Notification as Unread

**Endpoint:** `POST /api/notifications/{id}/mark-unread/`

**Description:** Mark a specific notification as unread

**Request Body:** None

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Notification marked as unread",
  "data": {
    "id": 1,
    "is_read": false,
    "read_at": null
  }
}
```

#### 1.5 Mark All Notifications as Read

**Endpoint:** `POST /api/notifications/mark-all-read/`

**Description:** Mark all unread notifications as read for the authenticated user

**Request Body (Optional):**
```json
{
  "notification_type": "financial", // Optional: only mark specific type as read
  "category": "payment_confirmation", // Optional: only mark specific category as read
  "before_date": "2024-12-01T00:00:00Z" // Optional: only mark notifications before this date
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "All notifications marked as read",
  "data": {
    "marked_count": 12,
    "remaining_unread": 0
  }
}
```

#### 1.6 Archive Notification

**Endpoint:** `POST /api/notifications/{id}/archive/`

**Description:** Archive a notification (hide from main list)

**Request Body:** None

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Notification archived",
  "data": {
    "id": 1,
    "is_archived": true,
    "archived_at": "2024-12-02T16:45:00Z"
  }
}
```

#### 1.7 Delete Notification

**Endpoint:** `DELETE /api/notifications/{id}/`

**Description:** Delete a notification permanently

**Response (Success - 204):** No content

---

### 2. Notification Statistics

#### 2.1 Get Notification Summary

**Endpoint:** `GET /api/notifications/summary/`

**Description:** Get notification statistics and summary for the authenticated user

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "total_notifications": 45,
    "unread_count": 12,
    "read_count": 33,
    "archived_count": 8,
    "urgent_count": 2,
    "action_required_count": 3,
    "expiring_soon_count": 1,
    "by_type": {
      "system": {
        "total": 5,
        "unread": 1
      },
      "academic": {
        "total": 15,
        "unread": 4
      },
      "financial": {
        "total": 12,
        "unread": 3
      },
      "support": {
        "total": 8,
        "unread": 2
      },
      "announcement": {
        "total": 5,
        "unread": 2
      }
    },
    "by_priority": {
      "low": {
        "total": 20,
        "unread": 5
      },
      "medium": {
        "total": 18,
        "unread": 5
      },
      "high": {
        "total": 5,
        "unread": 2
      },
      "urgent": {
        "total": 2,
        "unread": 0
      }
    },
    "recent_activity": {
      "last_7_days": 15,
      "last_30_days": 35,
      "average_daily": 2.3
    },
    "delivery_preferences": {
      "in_app_enabled": true,
      "email_enabled": true,
      "sms_enabled": false,
      "digest_frequency": "daily"
    }
  }
}
```

---

### 3. Notification Preferences

#### 3.1 Get Notification Preferences

**Endpoint:** `GET /api/notifications/preferences/`

**Description:** Get notification preferences for the authenticated user

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "user_id": 100,
    "global_settings": {
      "in_app_notifications": true,
      "email_notifications": true,
      "sms_notifications": false,
      "push_notifications": true,
      "digest_frequency": "daily", // none, daily, weekly
      "quiet_hours": {
        "enabled": true,
        "start_time": "22:00",
        "end_time": "07:00",
        "timezone": "UTC"
      }
    },
    "category_preferences": {
      "system": {
        "in_app": true,
        "email": true,
        "sms": false,
        "push": true,
        "priority_threshold": "medium" // Only notify for medium+ priority
      },
      "academic": {
        "in_app": true,
        "email": true,
        "sms": false,
        "push": true,
        "priority_threshold": "low"
      },
      "financial": {
        "in_app": true,
        "email": true,
        "sms": true,
        "push": true,
        "priority_threshold": "low"
      },
      "support": {
        "in_app": true,
        "email": true,
        "sms": false,
        "push": true,
        "priority_threshold": "medium"
      },
      "announcement": {
        "in_app": true,
        "email": false,
        "sms": false,
        "push": false,
        "priority_threshold": "high"
      }
    },
    "specific_preferences": {
      "payment_confirmations": true,
      "request_updates": true,
      "grade_notifications": true,
      "deadline_reminders": true,
      "system_maintenance": false,
      "promotional_content": false
    },
    "contact_information": {
      "email": "john@university.edu",
      "phone": "+1234567890",
      "email_verified": true,
      "phone_verified": false
    },
    "last_updated": "2024-11-15T10:00:00Z"
  }
}
```

#### 3.2 Update Notification Preferences

**Endpoint:** `PUT /api/notifications/preferences/`

**Description:** Update notification preferences for the authenticated user

**Request Body:**
```json
{
  "global_settings": {
    "in_app_notifications": true,
    "email_notifications": true,
    "sms_notifications": true,
    "push_notifications": true,
    "digest_frequency": "weekly",
    "quiet_hours": {
      "enabled": true,
      "start_time": "23:00",
      "end_time": "06:00",
      "timezone": "UTC"
    }
  },
  "category_preferences": {
    "financial": {
      "in_app": true,
      "email": true,
      "sms": true,
      "push": true,
      "priority_threshold": "low"
    }
  },
  "specific_preferences": {
    "payment_confirmations": true,
    "deadline_reminders": true,
    "promotional_content": false
  }
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Notification preferences updated successfully",
  "data": {
    "updated_settings": 8,
    "updated_at": "2024-12-02T16:00:00Z",
    "changes_summary": [
      "Enabled SMS notifications for financial category",
      "Changed digest frequency to weekly",
      "Updated quiet hours schedule"
    ]
  }
}
```

#### 3.3 Reset Preferences to Default

**Endpoint:** `POST /api/notifications/preferences/reset/`

**Description:** Reset notification preferences to system defaults

**Request Body (Optional):**
```json
{
  "categories": ["financial", "academic"], // Optional: reset only specific categories
  "confirm": true // Required confirmation
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Notification preferences reset to defaults",
  "data": {
    "reset_categories": ["financial", "academic"],
    "reset_at": "2024-12-02T16:15:00Z"
  }
}
```

---

### 4. Announcements

#### 4.1 Get Public Announcements

**Endpoint:** `GET /api/notifications/announcements/`

**Description:** Get public announcements visible to the authenticated user

**Query Parameters:**
- `page` (optional): Page number
- `announcement_type` (optional): Filter by type (general, academic, maintenance, event)
- `priority` (optional): Filter by priority
- `is_active` (optional): Filter by active status
- `target_audience` (optional): Filter by target audience

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 8,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "title": "System Maintenance Scheduled",
        "content": "The student portal will be unavailable for maintenance on December 5th from 2:00 AM to 4:00 AM. Please plan accordingly.",
        "announcement_type": "maintenance",
        "priority": "high",
        "target_audience": "all",
        "is_published": true,
        "is_active": true,
        "publish_date": "2024-12-03T08:00:00Z",
        "expiry_date": "2024-12-06T23:59:59Z",
        "created_by": {
          "id": 2,
          "name": "IT Administration",
          "position": "System Administrator"
        },
        "views_count": 850,
        "is_pinned": true,
        "tags": ["maintenance", "portal", "downtime"],
        "attachments": [],
        "created_at": "2024-12-02T16:00:00Z",
        "updated_at": "2024-12-02T16:00:00Z"
      },
      {
        "id": 2,
        "title": "New Academic Calendar Released",
        "content": "The academic calendar for Spring 2025 semester has been published. Key dates include registration opening on January 15th and classes starting on February 1st.",
        "announcement_type": "academic",
        "priority": "medium",
        "target_audience": "students",
        "is_published": true,
        "is_active": true,
        "publish_date": "2024-12-01T09:00:00Z",
        "expiry_date": "2025-01-31T23:59:59Z",
        "created_by": {
          "id": 3,
          "name": "Academic Office",
          "position": "Registrar"
        },
        "views_count": 1200,
        "is_pinned": false,
        "tags": ["academic", "calendar", "spring2025"],
        "attachments": [
          {
            "id": 1,
            "name": "spring_2025_calendar.pdf",
            "file_type": "application/pdf",
            "file_size": 512000,
            "download_url": "/api/notifications/announcements/2/attachments/1/download/"
          }
        ],
        "created_at": "2024-12-01T09:00:00Z",
        "updated_at": "2024-12-01T09:00:00Z"
      }
    ]
  }
}
```

#### 4.2 Get Announcement Details

**Endpoint:** `GET /api/notifications/announcements/{id}/`

**Description:** Get detailed information about a specific announcement

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "System Maintenance Scheduled",
    "content": "The student portal will be unavailable for maintenance on December 5th from 2:00 AM to 4:00 AM. During this time, you will not be able to access online services including course registration, grade viewing, and payment processing.\n\nWe apologize for any inconvenience and recommend completing any urgent tasks before the maintenance window.\n\nFor emergency assistance during maintenance, please contact the IT helpdesk at +1234567890.",
    "announcement_type": "maintenance",
    "priority": "high",
    "target_audience": "all",
    "target_criteria": {},
    "is_published": true,
    "is_active": true,
    "publish_date": "2024-12-03T08:00:00Z",
    "expiry_date": "2024-12-06T23:59:59Z",
    "created_by": {
      "id": 2,
      "name": "IT Administration",
      "position": "System Administrator",
      "email": "it@university.edu",
      "phone": "+1234567890"
    },
    "views_count": 850,
    "unique_views_count": 720,
    "is_pinned": true,
    "pin_until": "2024-12-06T23:59:59Z",
    "tags": ["maintenance", "portal", "downtime"],
    "attachments": [],
    "related_links": [
      {
        "title": "IT Status Page",
        "url": "https://status.university.edu",
        "description": "Check real-time system status"
      }
    ],
    "notification_sent": true,
    "notification_sent_at": "2024-12-03T08:05:00Z",
    "notification_recipients_count": 1250,
    "email_sent": true,
    "email_sent_at": "2024-12-03T08:10:00Z",
    "email_recipients_count": 1180,
    "created_at": "2024-12-02T16:00:00Z",
    "updated_at": "2024-12-02T16:00:00Z",
    "user_interaction": {
      "has_viewed": true,
      "viewed_at": "2024-12-03T09:15:00Z",
      "is_bookmarked": false
    }
  }
}
```

#### 4.3 Mark Announcement as Viewed

**Endpoint:** `POST /api/notifications/announcements/{id}/view/`

**Description:** Mark an announcement as viewed (for analytics)

**Request Body:** None

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Announcement marked as viewed",
  "data": {
    "announcement_id": 1,
    "viewed_at": "2024-12-03T09:15:00Z",
    "total_views": 851
  }
}
```

---

### 5. Real-time Notifications (WebSocket)

#### 5.1 WebSocket Connection

**Endpoint:** `ws://localhost:8000/ws/notifications/`

**Description:** Establish WebSocket connection for real-time notifications

**Authentication:** Include JWT token in connection headers or as query parameter

**Connection Example:**
```javascript
const token = localStorage.getItem('access_token');
const socket = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${token}`);

socket.onopen = function(event) {
    console.log('WebSocket connected');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    handleNotification(data);
};

socket.onclose = function(event) {
    console.log('WebSocket disconnected');
};
```

#### 5.2 Real-time Message Format

**New Notification:**
```json
{
  "type": "new_notification",
  "data": {
    "id": 15,
    "title": "Payment Received",
    "message": "Your payment has been received and is being processed.",
    "notification_type": "financial",
    "priority": "medium",
    "created_at": "2024-12-03T10:30:00Z",
    "action_required": false,
    "action_url": "/financial/payments/15/"
  }
}
```

**Notification Update:**
```json
{
  "type": "notification_update",
  "data": {
    "id": 10,
    "status": "read",
    "updated_at": "2024-12-03T10:35:00Z"
  }
}
```

**Unread Count Update:**
```json
{
  "type": "unread_count_update",
  "data": {
    "unread_count": 8,
    "by_type": {
      "system": 1,
      "academic": 3,
      "financial": 2,
      "support": 1,
      "announcement": 1
    }
  }
}
```

**System Announcement:**
```json
{
  "type": "system_announcement",
  "data": {
    "id": 5,
    "title": "Emergency Maintenance",
    "message": "Unexpected maintenance required. System will be down for 30 minutes.",
    "priority": "urgent",
    "announcement_type": "maintenance",
    "created_at": "2024-12-03T11:00:00Z"
  }
}
```

---

### 6. Notification Templates (Staff Only)

#### 6.1 Get Notification Templates

**Endpoint:** `GET /api/notifications/templates/`

**Description:** Get list of notification templates (Staff only)

**Authentication:** Bearer Token required (Staff only)

**Response (Success - 200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Payment Confirmation",
      "template_key": "payment_confirmed",
      "category": "financial",
      "title_template": "Payment Verification Complete",
      "message_template": "Your payment of ${amount} has been verified and processed successfully. Receipt number: ${receipt_number}.",
      "notification_type": "financial",
      "priority": "medium",
      "variables": [
        {
          "name": "amount",
          "type": "decimal",
          "required": true,
          "description": "Payment amount"
        },
        {
          "name": "receipt_number",
          "type": "string",
          "required": true,
          "description": "Receipt reference number"
        }
      ],
      "is_active": true,
      "created_at": "2024-11-01T00:00:00Z",
      "updated_at": "2024-11-15T10:00:00Z"
    }
  ]
}
```

#### 6.2 Send Custom Notification

**Endpoint:** `POST /api/notifications/send/`

**Description:** Send a custom notification to specific users (Staff only)

**Authentication:** Bearer Token required (Staff only)

**Request Body:**
```json
{
  "recipients": {
    "type": "specific", // specific, all, filter
    "user_ids": [100, 101, 102], // Required if type is 'specific'
    "filter_criteria": { // Required if type is 'filter'
      "user_type": "student",
      "major": "Computer Science",
      "academic_level": "undergraduate"
    }
  },
  "notification": {
    "title": "Important Academic Update",
    "message": "Please review the updated academic policies in your student portal.",
    "notification_type": "academic",
    "priority": "high",
    "category": "policy_update",
    "action_required": true,
    "action_url": "/academic/policies/",
    "action_text": "Review Policies",
    "expires_at": "2024-12-31T23:59:59Z"
  },
  "delivery_options": {
    "in_app": true,
    "email": true,
    "sms": false,
    "push": true,
    "respect_user_preferences": true
  },
  "schedule": {
    "send_immediately": true,
    "scheduled_time": null // Use if send_immediately is false
  },
  "metadata": {
    "campaign_id": "POLICY-UPDATE-2024",
    "department": "Academic Affairs"
  }
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Notification sent successfully",
  "data": {
    "notification_batch_id": "BATCH-2024-001",
    "recipients_count": 350,
    "delivery_summary": {
      "in_app": 350,
      "email": 320,
      "sms": 0,
      "push": 280
    },
    "estimated_delivery_time": "2024-12-03T11:05:00Z",
    "tracking_url": "/api/notifications/batches/BATCH-2024-001/status/"
  }
}
```

---

### 7. Notification Analytics (Staff Only)

#### 7.1 Get Notification Analytics

**Endpoint:** `GET /api/notifications/analytics/`

**Description:** Get comprehensive notification analytics (Staff only)

**Authentication:** Bearer Token required (Staff only)

**Query Parameters:**
- `period` (optional): day, week, month, year (default: month)
- `date_from` (optional): Custom date range start
- `date_to` (optional): Custom date range end
- `notification_type` (optional): Filter by type
- `department` (optional): Filter by sending department

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
    "summary": {
      "total_notifications_sent": 15000,
      "unique_recipients": 1250,
      "average_per_user": 12.0,
      "delivery_rate": 98.5,
      "read_rate": 75.2,
      "action_rate": 35.8
    },
    "by_type": {
      "system": {
        "sent": 2000,
        "delivered": 1970,
        "read": 1500,
        "read_rate": 76.1
      },
      "academic": {
        "sent": 5000,
        "delivered": 4925,
        "read": 3800,
        "read_rate": 77.2
      },
      "financial": {
        "sent": 4000,
        "delivered": 3960,
        "read": 3200,
        "read_rate": 80.8
      },
      "support": {
        "sent": 2500,
        "delivered": 2475,
        "read": 1800,
        "read_rate": 72.7
      },
      "announcement": {
        "sent": 1500,
        "delivered": 1485,
        "read": 900,
        "read_rate": 60.6
      }
    },
    "by_priority": {
      "low": {
        "sent": 8000,
        "read_rate": 65.5
      },
      "medium": {
        "sent": 5000,
        "read_rate": 78.2
      },
      "high": {
        "sent": 1800,
        "read_rate": 89.4
      },
      "urgent": {
        "sent": 200,
        "read_rate": 95.5
      }
    },
    "delivery_channels": {
      "in_app": {
        "sent": 15000,
        "delivered": 14775,
        "delivery_rate": 98.5
      },
      "email": {
        "sent": 12000,
        "delivered": 11640,
        "opened": 8200,
        "delivery_rate": 97.0,
        "open_rate": 70.4
      },
      "sms": {
        "sent": 3000,
        "delivered": 2940,
        "delivery_rate": 98.0
      },
      "push": {
        "sent": 10000,
        "delivered": 9500,
        "delivery_rate": 95.0
      }
    },
    "timeline": [
      {
        "date": "2024-11-01",
        "sent": 500,
        "delivered": 492,
        "read": 380
      },
      {
        "date": "2024-11-02",
        "sent": 520,
        "delivered": 512,
        "read": 395
      }
    ],
    "top_templates": [
      {
        "template_key": "payment_confirmed",
        "name": "Payment Confirmation",
        "usage_count": 2500,
        "read_rate": 85.2
      },
      {
        "template_key": "request_update",
        "name": "Request Status Update",
        "usage_count": 2000,
        "read_rate": 78.5
      }
    ],
    "user_engagement": {
      "most_active_users": [
        {
          "user_id": 100,
          "name": "John Doe",
          "notifications_received": 45,
          "read_rate": 92.0
        }
      ],
      "least_engaged_users": [
        {
          "user_id": 200,
          "name": "Jane Smith",
          "notifications_received": 30,
          "read_rate": 25.0
        }
      ]
    }
  }
}
```

---

## Error Handling

### Common Error Responses

**Notification Not Found (404):**
```json
{
  "success": false,
  "message": "Notification not found or not accessible",
  "error_code": "NOTIFICATION_NOT_FOUND"
}
```

**Invalid Notification Type (400):**
```json
{
  "success": false,
  "message": "Invalid notification type specified",
  "error_code": "INVALID_NOTIFICATION_TYPE",
  "details": {
    "valid_types": ["system", "academic", "financial", "support", "announcement"]
  }
}
```

**Preference Update Failed (422):**
```json
{
  "success": false,
  "message": "Failed to update notification preferences",
  "error_code": "PREFERENCE_UPDATE_FAILED",
  "errors": {
    "quiet_hours.start_time": ["Invalid time format. Use HH:MM format."]
  }
}
```

**Rate Limit Exceeded (429):**
```json
{
  "success": false,
  "message": "Rate limit exceeded. Too many requests.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "retry_after": 60,
    "limit": 100,
    "window": "1 hour"
  }
}
```

**WebSocket Authentication Failed (401):**
```json
{
  "type": "error",
  "data": {
    "error_code": "WEBSOCKET_AUTH_FAILED",
    "message": "Invalid or expired token"
  }
}
```

## Data Models

### Notification Model
```json
{
  "id": "integer",
  "recipient_id": "integer",
  "sender_id": "integer",
  "title": "string(200)",
  "message": "text",
  "notification_type": "enum[system, academic, financial, support, announcement]",
  "priority": "enum[low, medium, high, urgent]",
  "category": "string(50)",
  "is_read": "boolean",
  "is_archived": "boolean",
  "action_required": "boolean",
  "action_url": "string(500)",
  "action_text": "string(100)",
  "expires_at": "datetime",
  "metadata": "json",
  "created_at": "datetime",
  "read_at": "datetime",
  "archived_at": "datetime"
}
```

### Notification Preferences Model
```json
{
  "user_id": "integer",
  "in_app_notifications": "boolean",
  "email_notifications": "boolean",
  "sms_notifications": "boolean",
  "push_notifications": "boolean",
  "digest_frequency": "enum[none, daily, weekly]",
  "quiet_hours_enabled": "boolean",
  "quiet_hours_start": "time",
  "quiet_hours_end": "time",
  "category_preferences": "json",
  "specific_preferences": "json",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Rate Limiting

- **Get Notifications:** 60 requests per minute
- **Mark as Read/Unread:** 100 requests per minute
- **Preferences:** 20 requests per minute
- **WebSocket Connections:** 5 connections per user
- **Staff Endpoints:** 30 requests per minute

## Security Notes

1. **User Isolation:** Users can only access their own notifications
2. **Staff Permissions:** Template and analytics endpoints require staff privileges
3. **WebSocket Security:** Real-time connections require valid JWT tokens
4. **Data Sanitization:** All notification content is sanitized before storage
5. **Audit Logging:** All notification activities are logged for security

## Integration Examples

### Flutter/Dart Example
```dart
class NotificationsApiService {
  static const String baseUrl = 'http://localhost:8000/api/notifications';
  
  Future<Map<String, dynamic>> getNotifications({
    int page = 1,
    bool? isRead,
    String? notificationType,
    String? priority,
  }) async {
    final token = await storage.read(key: 'access_token');
    
    var queryParams = {'page': page.toString()};
    if (isRead != null) queryParams['is_read'] = isRead.toString();
    if (notificationType != null) queryParams['notification_type'] = notificationType;
    if (priority != null) queryParams['priority'] = priority;
    
    final uri = Uri.parse('$baseUrl/').replace(queryParameters: queryParams);
    
    final response = await http.get(
      uri,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );
    
    return jsonDecode(response.body);
  }
  
  Future<Map<String, dynamic>> markAsRead(int notificationId) async {
    final token = await storage.read(key: 'access_token');
    
    final response = await http.post(
      Uri.parse('$baseUrl/$notificationId/mark-read/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );
    
    return jsonDecode(response.body);
  }
  
  Future<Map<String, dynamic>> updatePreferences(Map<String, dynamic> preferences) async {
    final token = await storage.read(key: 'access_token');
    
    final response = await http.put(
      Uri.parse('$baseUrl/preferences/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(preferences),
    );
    
    return jsonDecode(response.body);
  }
}

// WebSocket connection for real-time notifications
class NotificationWebSocket {
  late WebSocketChannel channel;
  
  void connect(String token) {
    channel = WebSocketChannel.connect(
      Uri.parse('ws://localhost:8000/ws/notifications/?token=$token'),
    );
    
    channel.stream.listen(
      (data) {
        final notification = jsonDecode(data);
        handleNotification(notification);
      },
      onError: (error) {
        print('WebSocket error: $error');
      },
      onDone: () {
        print('WebSocket connection closed');
      },
    );
  }
  
  void handleNotification(Map<String, dynamic> notification) {
    switch (notification['type']) {
      case 'new_notification':
        showNotificationToUser(notification['data']);
        break;
      case 'unread_count_update':
        updateUnreadCount(notification['data']['unread_count']);
        break;
      case 'system_announcement':
        showSystemAnnouncement(notification['data']);
        break;
    }
  }
  
  void disconnect() {
    channel.sink.close();
  }
}
```

### JavaScript/Fetch Example
```javascript
class NotificationsAPI {
  constructor(baseURL = 'http://localhost:8000/api/notifications') {
    this.baseURL = baseURL;
    this.websocket = null;
  }
  
  async getNotifications(options = {}) {
    const token = localStorage.getItem('access_token');
    const params = new URLSearchParams();
    
    Object.entries(options).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });
    
    const response = await fetch(`${this.baseURL}/?${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return await response.json();
  }
  
  async markAsRead(notificationId) {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${this.baseURL}/${notificationId}/mark-read/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return await response.json();
  }
  
  async markAllAsRead(filters = {}) {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${this.baseURL}/mark-all-read/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(filters),
    });
    
    return await response.json();
  }
  
  connectWebSocket() {
    const token = localStorage.getItem('access_token');
    this.websocket = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${token}`);
    
    this.websocket.onopen = (event) => {
      console.log('Notifications WebSocket connected');
    };
    
    this.websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleWebSocketMessage(data);
    };
    
    this.websocket.onclose = (event) => {
      console.log('Notifications WebSocket disconnected');
      // Implement reconnection logic
      setTimeout(() => this.connectWebSocket(), 5000);
    };
    
    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  handleWebSocketMessage(data) {
    switch (data.type) {
      case 'new_notification':
        this.showNotification(data.data);
        this.updateUnreadCount();
        break;
      case 'unread_count_update':
        this.updateUnreadBadge(data.data.unread_count);
        break;
      case 'system_announcement':
        this.showSystemAnnouncement(data.data);
        break;
    }
  }
  
  showNotification(notification) {
    // Show browser notification
    if (Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/static/icons/notification.png',
        tag: `notification-${notification.id}`,
      });
    }
    
    // Update UI
    this.addNotificationToUI(notification);
  }
  
  disconnectWebSocket() {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }
}
```

## Changelog

### Version 1.0.0 (Current)
- Initial API implementation
- User notification management
- Real-time WebSocket notifications
- Notification preferences system
- Public announcements
- Staff notification tools
- Analytics and reporting
- Multi-channel delivery (in-app, email, SMS, push)

---

**Last Updated:** December 2024
**API Version:** 1.0.0
**Maintainer:** Notifications Systems Team