# Financial API Documentation

## Overview

The Financial API provides endpoints for managing student fees, payments, financial summaries, and payment history. It handles both student-facing financial operations and administrative financial management.

**Base URL:** `/api/financial/`

## Authentication

All endpoints require JWT authentication. Some endpoints are restricted to specific user types.

**Headers Required:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Endpoints

### 1. Financial Summary

**Endpoint:** `GET /api/financial/summary/`

**Description:** Get comprehensive financial summary for the authenticated student

**Authentication:** Bearer Token required (Student only)

**Request Body:** None

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Financial summary retrieved successfully",
  "data": {
    "student": {
      "id": 100,
      "name": "John Doe",
      "university_id": "STU2024001",
      "major": "Computer Science",
      "academic_level": "undergraduate"
    },
    "summary": {
      "total_fees": "5000.00",
      "total_paid": "2500.00",
      "outstanding_balance": "2500.00",
      "pending_payments": "500.00",
      "overdue_amount": "0.00",
      "next_due_date": "2024-12-31",
      "payment_plan_active": false
    },
    "current_semester": {
      "semester": "Fall 2024",
      "total_fees": "2500.00",
      "paid_amount": "1000.00",
      "remaining_balance": "1500.00",
      "due_date": "2024-12-31"
    },
    "fee_breakdown": [
      {
        "id": 1,
        "fee_type": {
          "id": 1,
          "name": "Tuition Fee",
          "description": "Semester tuition fee",
          "category": "academic"
        },
        "amount": "2000.00",
        "amount_paid": "800.00",
        "remaining_balance": "1200.00",
        "status": "partial",
        "due_date": "2024-12-31",
        "is_overdue": false,
        "created_at": "2024-08-15T00:00:00Z"
      },
      {
        "id": 2,
        "fee_type": {
          "id": 2,
          "name": "Library Fee",
          "description": "Annual library access fee",
          "category": "service"
        },
        "amount": "500.00",
        "amount_paid": "200.00",
        "remaining_balance": "300.00",
        "status": "partial",
        "due_date": "2024-12-31",
        "is_overdue": false,
        "created_at": "2024-08-15T00:00:00Z"
      }
    ],
    "recent_transactions": [
      {
        "id": 1,
        "transaction_type": "payment",
        "amount": "500.00",
        "description": "Partial tuition payment",
        "payment_method": "Bank Transfer",
        "transaction_date": "2024-11-15T10:30:00Z",
        "status": "verified",
        "receipt_number": "RCP-2024-001"
      },
      {
        "id": 2,
        "transaction_type": "fee",
        "amount": "2000.00",
        "description": "Fall 2024 Tuition Fee",
        "transaction_date": "2024-08-15T00:00:00Z",
        "status": "active"
      }
    ],
    "payment_methods": [
      {
        "id": 1,
        "name": "Bank Transfer",
        "type": "bank_transfer",
        "is_active": true,
        "processing_time": "1-2 business days",
        "instructions": "Transfer to account: 1234567890, Reference: STU2024001"
      },
      {
        "id": 2,
        "name": "Mobile Money",
        "type": "mobile_money",
        "is_active": true,
        "processing_time": "Instant",
        "instructions": "Send to: +1234567890, Reference: STU2024001"
      }
    ],
    "quick_actions": [
      {
        "id": 1,
        "title": "Pay Outstanding Fees",
        "description": "Pay your remaining balance",
        "amount": "2500.00",
        "url_pattern": "/financial/pay/",
        "icon": "credit-card"
      },
      {
        "id": 2,
        "title": "View Payment History",
        "description": "See all your transactions",
        "url_pattern": "/financial/history/",
        "icon": "history"
      }
    ]
  }
}
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/financial/summary/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

---

### 2. Fee Management

#### 2.1 List Student Fees

**Endpoint:** `GET /api/financial/fees/`

**Description:** Get paginated list of fees for the authenticated student

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `status` (optional): Filter by status (pending, partial, paid, overdue)
- `fee_type` (optional): Filter by fee type ID
- `semester` (optional): Filter by semester
- `academic_year` (optional): Filter by academic year
- `due_date_from` (optional): Filter fees due from date (YYYY-MM-DD)
- `due_date_to` (optional): Filter fees due to date (YYYY-MM-DD)

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
        "fee_type": {
          "id": 1,
          "name": "Tuition Fee",
          "description": "Semester tuition fee",
          "category": "academic"
        },
        "amount": "2000.00",
        "amount_paid": "800.00",
        "remaining_balance": "1200.00",
        "status": "partial",
        "due_date": "2024-12-31",
        "is_overdue": false,
        "days_until_due": 29,
        "semester": "Fall 2024",
        "academic_year": "2024-2025",
        "created_at": "2024-08-15T00:00:00Z",
        "last_payment_date": "2024-11-15T10:30:00Z",
        "payment_count": 2
      }
    ]
  }
}
```

#### 2.2 Get Fee Details

**Endpoint:** `GET /api/financial/fees/{id}/`

**Description:** Get detailed information about a specific fee

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "fee_type": {
      "id": 1,
      "name": "Tuition Fee",
      "description": "Semester tuition fee",
      "category": "academic",
      "is_mandatory": true
    },
    "amount": "2000.00",
    "amount_paid": "800.00",
    "remaining_balance": "1200.00",
    "status": "partial",
    "due_date": "2024-12-31",
    "is_overdue": false,
    "semester": "Fall 2024",
    "academic_year": "2024-2025",
    "created_at": "2024-08-15T00:00:00Z",
    "created_by": {
      "id": 2,
      "name": "Finance Office",
      "position": "Finance Administrator"
    },
    "payment_history": [
      {
        "id": 1,
        "amount": "500.00",
        "payment_date": "2024-11-15T10:30:00Z",
        "payment_method": "Bank Transfer",
        "transaction_reference": "TXN123456789",
        "status": "verified",
        "receipt_number": "RCP-2024-001",
        "verified_by": {
          "id": 3,
          "name": "Jane Smith",
          "position": "Finance Officer"
        }
      },
      {
        "id": 2,
        "amount": "300.00",
        "payment_date": "2024-10-15T14:20:00Z",
        "payment_method": "Mobile Money",
        "transaction_reference": "MM987654321",
        "status": "verified",
        "receipt_number": "RCP-2024-002"
      }
    ],
    "installment_plan": null,
    "late_fees": [],
    "notes": "Standard tuition fee for Fall 2024 semester"
  }
}
```

---

### 3. Payment Processing

#### 3.1 Initiate Payment

**Endpoint:** `POST /api/financial/payments/initiate/`

**Description:** Initiate a payment for one or more fees

**Request Body:**
```json
{
  "fees": [
    {
      "fee_id": 1,
      "amount": "1200.00" // Amount to pay for this fee
    },
    {
      "fee_id": 2,
      "amount": "300.00"
    }
  ],
  "payment_provider_id": 1,
  "total_amount": "1500.00",
  "payment_reference": "TXN789123456", // Optional, for bank transfers
  "sender_name": "John Doe",
  "sender_phone": "+1234567890",
  "payment_notes": "Payment for Fall 2024 fees"
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Payment initiated successfully",
  "data": {
    "payment_id": 1,
    "payment_reference": "PAY-2024-001",
    "total_amount": "1500.00",
    "fees_count": 2,
    "payment_provider": {
      "id": 1,
      "name": "Bank Transfer",
      "type": "bank_transfer",
      "processing_time": "1-2 business days"
    },
    "status": "pending",
    "created_at": "2024-12-02T10:00:00Z",
    "estimated_verification": "2024-12-04T10:00:00Z",
    "instructions": {
      "account_number": "1234567890",
      "account_name": "University Finance",
      "bank_name": "National Bank",
      "reference": "PAY-2024-001",
      "amount": "1500.00"
    },
    "next_steps": [
      "Complete the bank transfer using the provided details",
      "Keep your transaction receipt",
      "Payment will be verified within 1-2 business days",
      "You will receive a confirmation email once verified"
    ]
  }
}
```

#### 3.2 Check Payment Status

**Endpoint:** `GET /api/financial/payments/{payment_id}/status/`

**Description:** Check the status of a payment

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "payment_id": 1,
    "payment_reference": "PAY-2024-001",
    "status": "verified",
    "total_amount": "1500.00",
    "payment_date": "2024-12-02T10:00:00Z",
    "verified_date": "2024-12-03T14:30:00Z",
    "verified_by": {
      "id": 3,
      "name": "Jane Smith",
      "position": "Finance Officer"
    },
    "receipt_number": "RCP-2024-003",
    "receipt_url": "/api/financial/receipts/RCP-2024-003/download/",
    "fees_paid": [
      {
        "fee_id": 1,
        "amount_paid": "1200.00",
        "remaining_balance": "0.00",
        "status": "paid"
      },
      {
        "fee_id": 2,
        "amount_paid": "300.00",
        "remaining_balance": "0.00",
        "status": "paid"
      }
    ]
  }
}
```

#### 3.3 Cancel Payment

**Endpoint:** `POST /api/financial/payments/{payment_id}/cancel/`

**Description:** Cancel a pending payment

**Request Body:**
```json
{
  "reason": "Changed payment method",
  "notes": "Will use mobile money instead"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Payment cancelled successfully",
  "data": {
    "payment_id": 1,
    "status": "cancelled",
    "cancelled_at": "2024-12-02T15:00:00Z",
    "refund_amount": "0.00"
  }
}
```

---

### 4. Payment History

#### 4.1 Get Payment History

**Endpoint:** `GET /api/financial/payments/history/`

**Description:** Get paginated payment history for the authenticated student

**Query Parameters:**
- `page` (optional): Page number
- `status` (optional): Filter by status (pending, verified, rejected, cancelled)
- `payment_method` (optional): Filter by payment method
- `date_from` (optional): Filter from date (YYYY-MM-DD)
- `date_to` (optional): Filter to date (YYYY-MM-DD)
- `amount_min` (optional): Minimum amount filter
- `amount_max` (optional): Maximum amount filter

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "count": 25,
    "next": "http://localhost:8000/api/financial/payments/history/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "payment_reference": "PAY-2024-001",
        "amount": "1500.00",
        "payment_date": "2024-12-02T10:00:00Z",
        "payment_provider": {
          "id": 1,
          "name": "Bank Transfer",
          "type": "bank_transfer"
        },
        "status": "verified",
        "transaction_reference": "TXN789123456",
        "receipt_number": "RCP-2024-003",
        "receipt_url": "/api/financial/receipts/RCP-2024-003/download/",
        "verified_date": "2024-12-03T14:30:00Z",
        "fees_count": 2,
        "description": "Payment for Fall 2024 fees"
      }
    ],
    "summary": {
      "total_payments": 25,
      "total_amount_paid": "12500.00",
      "verified_payments": 23,
      "pending_payments": 2,
      "average_payment_amount": "500.00"
    }
  }
}
```

#### 4.2 Get Payment Details

**Endpoint:** `GET /api/financial/payments/{payment_id}/`

**Description:** Get detailed information about a specific payment

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "payment_reference": "PAY-2024-001",
    "amount": "1500.00",
    "payment_date": "2024-12-02T10:00:00Z",
    "payment_provider": {
      "id": 1,
      "name": "Bank Transfer",
      "type": "bank_transfer",
      "account_details": {
        "account_number": "1234567890",
        "account_name": "University Finance",
        "bank_name": "National Bank"
      }
    },
    "status": "verified",
    "transaction_reference": "TXN789123456",
    "sender_name": "John Doe",
    "sender_phone": "+1234567890",
    "payment_notes": "Payment for Fall 2024 fees",
    "receipt_number": "RCP-2024-003",
    "receipt_url": "/api/financial/receipts/RCP-2024-003/download/",
    "verified_date": "2024-12-03T14:30:00Z",
    "verified_by": {
      "id": 3,
      "name": "Jane Smith",
      "position": "Finance Officer"
    },
    "verification_notes": "Payment verified against bank records",
    "fees_paid": [
      {
        "fee_id": 1,
        "fee_type": "Tuition Fee",
        "amount_paid": "1200.00",
        "previous_balance": "1200.00",
        "remaining_balance": "0.00"
      },
      {
        "fee_id": 2,
        "fee_type": "Library Fee",
        "amount_paid": "300.00",
        "previous_balance": "300.00",
        "remaining_balance": "0.00"
      }
    ],
    "status_history": [
      {
        "status": "pending",
        "timestamp": "2024-12-02T10:00:00Z",
        "notes": "Payment initiated by student"
      },
      {
        "status": "verified",
        "timestamp": "2024-12-03T14:30:00Z",
        "notes": "Payment verified against bank records",
        "changed_by": {
          "id": 3,
          "name": "Jane Smith"
        }
      }
    ]
  }
}
```

---

### 5. Receipts and Documents

#### 5.1 Download Receipt

**Endpoint:** `GET /api/financial/receipts/{receipt_number}/download/`

**Description:** Download a payment receipt as PDF

**Response (Success - 200):**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="receipt_RCP-2024-003.pdf"

[PDF Binary Data]
```

#### 5.2 Get Receipt Details

**Endpoint:** `GET /api/financial/receipts/{receipt_number}/`

**Description:** Get receipt information without downloading

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "receipt_number": "RCP-2024-003",
    "payment_reference": "PAY-2024-001",
    "student": {
      "id": 100,
      "name": "John Doe",
      "university_id": "STU2024001"
    },
    "amount": "1500.00",
    "payment_date": "2024-12-02T10:00:00Z",
    "payment_method": "Bank Transfer",
    "transaction_reference": "TXN789123456",
    "issued_date": "2024-12-03T14:30:00Z",
    "issued_by": {
      "id": 3,
      "name": "Jane Smith",
      "position": "Finance Officer"
    },
    "fees_paid": [
      {
        "fee_type": "Tuition Fee",
        "amount": "1200.00",
        "semester": "Fall 2024"
      },
      {
        "fee_type": "Library Fee",
        "amount": "300.00",
        "semester": "Fall 2024"
      }
    ],
    "download_url": "/api/financial/receipts/RCP-2024-003/download/",
    "file_size": 245760,
    "expires_at": null
  }
}
```

#### 5.3 Generate Financial Statement

**Endpoint:** `POST /api/financial/statements/generate/`

**Description:** Generate a comprehensive financial statement

**Request Body:**
```json
{
  "period_type": "semester", // semester, academic_year, custom
  "semester": "Fall 2024", // Required if period_type is semester
  "academic_year": "2024-2025", // Required if period_type is academic_year
  "date_from": "2024-08-01", // Required if period_type is custom
  "date_to": "2024-12-31", // Required if period_type is custom
  "include_pending": true,
  "format": "pdf" // pdf, excel
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Financial statement generated successfully",
  "data": {
    "statement_id": "STMT-2024-001",
    "download_url": "/api/financial/statements/STMT-2024-001/download/",
    "expires_at": "2024-12-09T16:00:00Z",
    "file_size": 512000,
    "period": {
      "type": "semester",
      "semester": "Fall 2024",
      "date_from": "2024-08-15",
      "date_to": "2024-12-31"
    },
    "summary": {
      "total_fees": "2500.00",
      "total_paid": "1500.00",
      "outstanding_balance": "1000.00",
      "payment_count": 3
    }
  }
}
```

---

### 6. Payment Methods and Providers

#### 6.1 Get Available Payment Methods

**Endpoint:** `GET /api/financial/payment-methods/`

**Description:** Get list of available payment methods

**Response (Success - 200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Bank Transfer",
      "type": "bank_transfer",
      "is_active": true,
      "processing_time": "1-2 business days",
      "minimum_amount": "10.00",
      "maximum_amount": "50000.00",
      "fees": "0.00",
      "instructions": "Transfer to the provided account details with your payment reference",
      "account_details": {
        "account_number": "1234567890",
        "account_name": "University Finance",
        "bank_name": "National Bank",
        "swift_code": "NATBANK123"
      },
      "supported_currencies": ["USD"],
      "verification_required": true
    },
    {
      "id": 2,
      "name": "Mobile Money",
      "type": "mobile_money",
      "is_active": true,
      "processing_time": "Instant",
      "minimum_amount": "5.00",
      "maximum_amount": "10000.00",
      "fees": "2.5%",
      "instructions": "Send money to the provided number with your payment reference",
      "account_details": {
        "phone_number": "+1234567890",
        "account_name": "University Finance",
        "provider": "MobilePay"
      },
      "supported_currencies": ["USD"],
      "verification_required": false
    }
  ]
}
```

#### 6.2 Get Payment Method Details

**Endpoint:** `GET /api/financial/payment-methods/{id}/`

**Description:** Get detailed information about a specific payment method

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Bank Transfer",
    "type": "bank_transfer",
    "is_active": true,
    "processing_time": "1-2 business days",
    "minimum_amount": "10.00",
    "maximum_amount": "50000.00",
    "fees": "0.00",
    "instructions": "Transfer to the provided account details with your payment reference",
    "detailed_instructions": [
      "Log into your online banking or visit your bank branch",
      "Select 'Transfer Money' or 'Send Money'",
      "Enter the provided account details",
      "Use your payment reference as the transfer description",
      "Complete the transfer and keep your receipt",
      "Payment will be verified within 1-2 business days"
    ],
    "account_details": {
      "account_number": "1234567890",
      "account_name": "University Finance",
      "bank_name": "National Bank",
      "swift_code": "NATBANK123",
      "routing_number": "123456789"
    },
    "supported_currencies": ["USD"],
    "verification_required": true,
    "average_processing_time_hours": 36,
    "success_rate": "99.5%",
    "customer_support": {
      "phone": "+1234567890",
      "email": "finance@university.edu",
      "hours": "Monday-Friday 8:00 AM - 5:00 PM"
    }
  }
}
```

---

### 7. Financial Analytics (Student)

#### 7.1 Get Payment Analytics

**Endpoint:** `GET /api/financial/analytics/payments/`

**Description:** Get payment analytics for the authenticated student

**Query Parameters:**
- `period` (optional): month, semester, year (default: semester)
- `academic_year` (optional): Filter by academic year

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "period": "semester",
    "academic_year": "2024-2025",
    "semester": "Fall 2024",
    "summary": {
      "total_fees_assigned": "2500.00",
      "total_payments_made": "1500.00",
      "outstanding_balance": "1000.00",
      "payment_completion_rate": 60.0,
      "average_payment_amount": "500.00",
      "payment_frequency_days": 30
    },
    "payment_timeline": [
      {
        "month": "2024-08",
        "fees_assigned": "2500.00",
        "payments_made": "0.00",
        "balance": "2500.00"
      },
      {
        "month": "2024-09",
        "fees_assigned": "0.00",
        "payments_made": "500.00",
        "balance": "2000.00"
      },
      {
        "month": "2024-10",
        "fees_assigned": "0.00",
        "payments_made": "300.00",
        "balance": "1700.00"
      },
      {
        "month": "2024-11",
        "fees_assigned": "0.00",
        "payments_made": "700.00",
        "balance": "1000.00"
      }
    ],
    "payment_methods_usage": [
      {
        "method": "Bank Transfer",
        "count": 2,
        "total_amount": "1200.00",
        "percentage": 80.0
      },
      {
        "method": "Mobile Money",
        "count": 1,
        "total_amount": "300.00",
        "percentage": 20.0
      }
    ],
    "fee_categories": [
      {
        "category": "academic",
        "total_amount": "2000.00",
        "paid_amount": "1200.00",
        "percentage_paid": 60.0
      },
      {
        "category": "service",
        "total_amount": "500.00",
        "paid_amount": "300.00",
        "percentage_paid": 60.0
      }
    ]
  }
}
```

---

### 8. Installment Plans

#### 8.1 Get Available Installment Plans

**Endpoint:** `GET /api/financial/installment-plans/available/`

**Description:** Get available installment plans for outstanding fees

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "eligible_amount": "1000.00",
    "minimum_plan_amount": "500.00",
    "available_plans": [
      {
        "id": 1,
        "name": "3-Month Plan",
        "duration_months": 3,
        "installments": 3,
        "interest_rate": "0.00",
        "setup_fee": "25.00",
        "monthly_amount": "341.67",
        "total_amount": "1025.00",
        "first_payment_date": "2024-12-15",
        "final_payment_date": "2025-02-15"
      },
      {
        "id": 2,
        "name": "6-Month Plan",
        "duration_months": 6,
        "installments": 6,
        "interest_rate": "2.00",
        "setup_fee": "50.00",
        "monthly_amount": "175.00",
        "total_amount": "1050.00",
        "first_payment_date": "2024-12-15",
        "final_payment_date": "2025-05-15"
      }
    ],
    "terms_and_conditions": [
      "All installments must be paid on time",
      "Late payment fees apply for overdue installments",
      "Plan can be cancelled with 30 days notice",
      "Early payment is allowed without penalties"
    ]
  }
}
```

#### 8.2 Create Installment Plan

**Endpoint:** `POST /api/financial/installment-plans/`

**Description:** Create a new installment plan

**Request Body:**
```json
{
  "plan_id": 1,
  "fees": [1, 2], // Fee IDs to include in the plan
  "total_amount": "1000.00",
  "first_payment_date": "2024-12-15",
  "agree_to_terms": true
}
```

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Installment plan created successfully",
  "data": {
    "plan_id": 1,
    "plan_reference": "INST-2024-001",
    "total_amount": "1025.00",
    "installments": 3,
    "monthly_amount": "341.67",
    "setup_fee": "25.00",
    "first_payment_date": "2024-12-15",
    "final_payment_date": "2025-02-15",
    "status": "active",
    "installment_schedule": [
      {
        "installment_number": 1,
        "amount": "341.67",
        "due_date": "2024-12-15",
        "status": "pending"
      },
      {
        "installment_number": 2,
        "amount": "341.67",
        "due_date": "2025-01-15",
        "status": "pending"
      },
      {
        "installment_number": 3,
        "amount": "341.66",
        "due_date": "2025-02-15",
        "status": "pending"
      }
    ]
  }
}
```

#### 8.3 Get Installment Plan Details

**Endpoint:** `GET /api/financial/installment-plans/{plan_id}/`

**Description:** Get details of an active installment plan

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "plan_reference": "INST-2024-001",
    "student": {
      "id": 100,
      "name": "John Doe",
      "university_id": "STU2024001"
    },
    "total_amount": "1025.00",
    "amount_paid": "341.67",
    "remaining_balance": "683.33",
    "installments_total": 3,
    "installments_paid": 1,
    "installments_remaining": 2,
    "monthly_amount": "341.67",
    "setup_fee": "25.00",
    "interest_rate": "0.00",
    "status": "active",
    "created_date": "2024-12-01T10:00:00Z",
    "first_payment_date": "2024-12-15",
    "final_payment_date": "2025-02-15",
    "next_payment_date": "2025-01-15",
    "next_payment_amount": "341.67",
    "fees_included": [
      {
        "fee_id": 1,
        "fee_type": "Tuition Fee",
        "amount": "800.00"
      },
      {
        "fee_id": 2,
        "fee_type": "Library Fee",
        "amount": "200.00"
      }
    ],
    "installment_schedule": [
      {
        "installment_number": 1,
        "amount": "341.67",
        "due_date": "2024-12-15",
        "status": "paid",
        "paid_date": "2024-12-14T16:30:00Z",
        "payment_reference": "PAY-2024-005"
      },
      {
        "installment_number": 2,
        "amount": "341.67",
        "due_date": "2025-01-15",
        "status": "pending",
        "days_until_due": 44
      },
      {
        "installment_number": 3,
        "amount": "341.66",
        "due_date": "2025-02-15",
        "status": "pending",
        "days_until_due": 75
      }
    ],
    "payment_history": [
      {
        "installment_number": 1,
        "amount": "341.67",
        "payment_date": "2024-12-14T16:30:00Z",
        "payment_method": "Bank Transfer",
        "payment_reference": "PAY-2024-005",
        "receipt_number": "RCP-2024-005"
      }
    ]
  }
}
```

---

## Error Handling

### Common Error Responses

**Insufficient Balance (422):**
```json
{
  "success": false,
  "message": "Payment amount exceeds outstanding balance",
  "error_code": "INSUFFICIENT_BALANCE",
  "details": {
    "requested_amount": "2000.00",
    "available_balance": "1500.00",
    "fee_id": 1
  }
}
```

**Payment Method Unavailable (422):**
```json
{
  "success": false,
  "message": "Selected payment method is currently unavailable",
  "error_code": "PAYMENT_METHOD_UNAVAILABLE",
  "details": {
    "payment_method_id": 3,
    "reason": "maintenance",
    "estimated_availability": "2024-12-03T08:00:00Z"
  }
}
```

**Invalid Payment Amount (400):**
```json
{
  "success": false,
  "message": "Payment amount is below minimum threshold",
  "error_code": "INVALID_AMOUNT",
  "details": {
    "minimum_amount": "10.00",
    "provided_amount": "5.00"
  }
}
```

**Fee Not Found (404):**
```json
{
  "success": false,
  "message": "Fee not found or not accessible",
  "error_code": "FEE_NOT_FOUND"
}
```

**Payment Already Processed (409):**
```json
{
  "success": false,
  "message": "Payment has already been processed",
  "error_code": "PAYMENT_ALREADY_PROCESSED",
  "details": {
    "payment_id": 1,
    "current_status": "verified",
    "processed_date": "2024-12-03T14:30:00Z"
  }
}
```

## Data Models

### Fee Model
```json
{
  "id": "integer",
  "student_id": "integer",
  "fee_type": {
    "id": "integer",
    "name": "string",
    "description": "string",
    "category": "string"
  },
  "amount": "decimal(10,2)",
  "amount_paid": "decimal(10,2)",
  "remaining_balance": "decimal(10,2)",
  "status": "enum[pending, partial, paid, overdue]",
  "due_date": "datetime",
  "semester": "string",
  "academic_year": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Payment Model
```json
{
  "id": "integer",
  "student_id": "integer",
  "payment_reference": "string",
  "amount": "decimal(10,2)",
  "payment_provider": {
    "id": "integer",
    "name": "string",
    "type": "string"
  },
  "status": "enum[pending, verified, rejected, cancelled]",
  "transaction_reference": "string",
  "payment_date": "datetime",
  "verified_date": "datetime",
  "receipt_number": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Rate Limiting

- **Financial Summary:** 20 requests per minute
- **Payment Operations:** 10 requests per minute
- **Payment History:** 30 requests per minute
- **Receipt Downloads:** 50 requests per minute
- **Analytics:** 15 requests per minute

## Security Notes

1. **Payment Verification:** All payments require manual verification by finance staff
2. **Transaction References:** Must be unique and verifiable
3. **Amount Validation:** Payment amounts are validated against outstanding balances
4. **Receipt Security:** Receipts contain security watermarks and verification codes
5. **Audit Trail:** All financial transactions are logged with full audit trails

## Integration Examples

### Flutter/Dart Example
```dart
class FinancialApiService {
  static const String baseUrl = 'http://localhost:8000/api/financial';
  
  Future<Map<String, dynamic>> getFinancialSummary() async {
    final token = await storage.read(key: 'access_token');
    
    final response = await http.get(
      Uri.parse('$baseUrl/summary/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load financial summary');
    }
  }
  
  Future<Map<String, dynamic>> initiatePayment({
    required List<Map<String, dynamic>> fees,
    required int paymentProviderId,
    required String totalAmount,
    String? paymentReference,
    required String senderName,
    required String senderPhone,
    String? paymentNotes,
  }) async {
    final token = await storage.read(key: 'access_token');
    
    final response = await http.post(
      Uri.parse('$baseUrl/payments/initiate/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'fees': fees,
        'payment_provider_id': paymentProviderId,
        'total_amount': totalAmount,
        'payment_reference': paymentReference,
        'sender_name': senderName,
        'sender_phone': senderPhone,
        'payment_notes': paymentNotes,
      }),
    );
    
    return jsonDecode(response.body);
  }
  
  Future<Uint8List> downloadReceipt(String receiptNumber) async {
    final token = await storage.read(key: 'access_token');
    
    final response = await http.get(
      Uri.parse('$baseUrl/receipts/$receiptNumber/download/'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );
    
    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else {
      throw Exception('Failed to download receipt');
    }
  }
}
```

### JavaScript/Fetch Example
```javascript
class FinancialAPI {
  constructor(baseURL = 'http://localhost:8000/api/financial') {
    this.baseURL = baseURL;
  }
  
  async getFinancialSummary() {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${this.baseURL}/summary/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch financial summary');
    }
    
    return await response.json();
  }
  
  async initiatePayment(paymentData) {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${this.baseURL}/payments/initiate/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(paymentData),
    });
    
    return await response.json();
  }
  
  async downloadReceipt(receiptNumber) {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${this.baseURL}/receipts/${receiptNumber}/download/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to download receipt');
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `receipt_${receiptNumber}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
}
```

## Changelog

### Version 1.0.0 (Current)
- Initial API implementation
- Financial summary and analytics
- Fee management system
- Payment processing and verification
- Receipt generation and download
- Payment history and tracking
- Installment plan support
- Multiple payment method integration

---

**Last Updated:** December 2024
**API Version:** 1.0.0
**Maintainer:** Financial Systems Team