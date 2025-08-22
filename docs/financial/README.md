# Financial API Documentation

## Overview

The Financial API provides comprehensive endpoints for managing student fees, payments, financial summaries, and payment history. This API mirrors all web functionality for the mobile application, enabling students to manage their financial obligations seamlessly.

**Base URL:** `/financial/api/`

## Authentication

All endpoints require JWT authentication with student permissions.

**Headers Required:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Core Features

- **Financial Dashboard**: Complete financial overview with summaries and statistics
- **Fee Management**: View, filter, and manage student fees
- **Payment Processing**: Submit payments for multiple fees with various providers
- **Payment History**: Track all payment transactions with detailed filtering
- **Receipt Management**: View and download payment receipts as PDF
- **Real-time Status**: Check payment verification status and updates

## API Endpoints

### 1. Financial Summary

**Endpoint:** `GET /financial/api/summary/`

**Description:** Get comprehensive financial summary including totals, recent transactions, and fee breakdown

**Authentication:** Bearer Token required (Student only)

**Request Body:** None

**Response (Success - 200):**
```json
{
  "total_fees": "5000.00",
  "pending_payments": "2500.00",
  "paid_this_semester": "1500.00",
  "overdue_count": 2,
  "recent_transactions": [
    {
      "id": 1,
      "student": 100,
      "student_name": "John Doe",
      "student_id": "STU2024001",
      "fee": {
        "id": 1,
        "student": 100,
        "student_name": "John Doe",
        "student_id": "STU2024001",
        "fee_type": {
          "id": 1,
          "name": "Tuition Fee",
          "description": "Semester tuition fee",
          "is_active": true,
          "created_at": "2024-08-15T00:00:00Z"
        },
        "amount": "2000.00",
        "due_date": "2024-12-31",
        "status": "partially_paid",
        "description": "Fall 2024 tuition fee",
        "created_at": "2024-08-15T00:00:00Z",
        "amount_paid": "800.00",
        "remaining_balance": "1200.00",
        "is_overdue": false
      },
      "payment_provider": {
        "id": 1,
        "name": "Bank Transfer",
        "description": "Direct bank transfer",
        "instructions": "Transfer to university account",
        "is_active": true,
        "logo": null,
        "university_account_name": "University Finance",
        "university_account_number": "1234567890",
        "university_phone": "+1234567890",
        "additional_info": "Include student ID in reference"
      },
      "amount": "500.00",
      "transaction_reference": "TXN123456789",
      "payment_date": "2024-11-15",
      "status": "verified",
      "status_display": "Verified",
      "sender_name": "John Doe",
      "sender_phone": "+1234567890",
      "transfer_notes": "Partial tuition payment",
      "verification_notes": "Payment verified against bank records",
      "verified_by": 3,
      "verified_by_name": "Jane Smith",
      "verified_at": "2024-11-16T10:30:00Z",
      "created_at": "2024-11-15T14:20:00Z",
      "can_view_receipt": true
    }
  ],
  "fee_breakdown": [
    {
      "id": 1,
      "student": 100,
      "student_name": "John Doe",
      "student_id": "STU2024001",
      "fee_type": {
        "id": 1,
        "name": "Tuition Fee",
        "description": "Semester tuition fee",
        "is_active": true,
        "created_at": "2024-08-15T00:00:00Z"
      },
      "amount": "2000.00",
      "due_date": "2024-12-31",
      "status": "partially_paid",
      "description": "Fall 2024 tuition fee",
      "created_at": "2024-08-15T00:00:00Z",
      "amount_paid": "800.00",
      "remaining_balance": "1200.00",
      "is_overdue": false
    },
    {
      "id": 2,
      "student": 100,
      "student_name": "John Doe",
      "student_id": "STU2024001",
      "fee_type": {
        "id": 2,
        "name": "Library Fee",
        "description": "Annual library access fee",
        "is_active": true,
        "created_at": "2024-08-15T00:00:00Z"
      },
      "amount": "500.00",
      "due_date": "2024-12-31",
      "status": "partially_paid",
      "description": "Annual library access",
      "created_at": "2024-08-15T00:00:00Z",
      "amount_paid": "200.00",
      "remaining_balance": "300.00",
      "is_overdue": false
    }
  ]
}
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
}
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/financial/api/summary/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

---

### 2. Student Fees Management

#### 2.1 List Student Fees

**Endpoint:** `GET /financial/api/fees/`

**Description:** Get paginated list of all fees for the authenticated student with filtering options

**Query Parameters:**
- `status` (optional): Filter by status (unpaid, partially_paid, paid)
- `fee_type` (optional): Filter by fee type ID
- `overdue` (optional): Filter overdue fees (true/false)
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page

**Response (Success - 200):**
```json
{
  "count": 8,
  "next": "http://localhost:8000/financial/api/fees/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "student": 100,
      "student_name": "John Doe",
      "student_id": "STU2024001",
      "fee_type": {
        "id": 1,
        "name": "Tuition Fee",
        "description": "Semester tuition fee",
        "is_active": true,
        "created_at": "2024-08-15T00:00:00Z"
      },
      "amount": "2000.00",
      "due_date": "2024-12-31",
      "status": "partially_paid",
      "description": "Fall 2024 tuition fee",
      "created_at": "2024-08-15T00:00:00Z",
      "amount_paid": "800.00",
      "remaining_balance": "1200.00",
      "is_overdue": false
    }
  ]
}
```

#### 2.2 Get Fee Details

**Endpoint:** `GET /financial/api/fees/{id}/`

**Description:** Get detailed information about a specific fee

**Response (Success - 200):**
```json
{
  "id": 1,
  "student": 100,
  "student_name": "John Doe",
  "student_id": "STU2024001",
  "fee_type": {
    "id": 1,
    "name": "Tuition Fee",
    "description": "Semester tuition fee",
    "is_active": true,
    "created_at": "2024-08-15T00:00:00Z"
  },
  "amount": "2000.00",
  "due_date": "2024-12-31",
  "status": "partially_paid",
  "description": "Fall 2024 tuition fee",
  "created_at": "2024-08-15T00:00:00Z",
  "amount_paid": "800.00",
  "remaining_balance": "1200.00",
  "is_overdue": false
}
```

#### 2.3 Get Outstanding Fees

**Endpoint:** `GET /financial/api/fees/outstanding/`

**Description:** Get all outstanding fees that require payment

**Response (Success - 200):**
```json
[
  {
    "id": 1,
    "student": 100,
    "student_name": "John Doe",
    "student_id": "STU2024001",
    "fee_type": {
      "id": 1,
      "name": "Tuition Fee",
      "description": "Semester tuition fee",
      "is_active": true,
      "created_at": "2024-08-15T00:00:00Z"
    },
    "amount": "2000.00",
    "due_date": "2024-12-31",
    "status": "partially_paid",
    "description": "Fall 2024 tuition fee",
    "created_at": "2024-08-15T00:00:00Z",
    "amount_paid": "800.00",
    "remaining_balance": "1200.00",
    "is_overdue": false
  }
]
```

---

### 3. Payment Providers

#### 3.1 List Payment Providers

**Endpoint:** `GET /financial/api/payment-providers/`

**Description:** Get list of active payment providers

**Response (Success - 200):**
```json
[
  {
    "id": 1,
    "name": "Stripe",
    "description": "Credit/Debit Card payments via Stripe",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "name": "PayPal",
    "description": "PayPal payments",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### 4. Payment Management

#### 4.1 List Payments

**Endpoint:** `GET /financial/api/payments/`

**Description:** Get paginated list of payments for the authenticated student

**Query Parameters:**
- `status` (optional): Filter by status (pending, completed, failed, cancelled)
- `date_from` (optional): Filter payments from date (YYYY-MM-DD)
- `date_to` (optional): Filter payments to date (YYYY-MM-DD)
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page

**Response (Success - 200):**
```json
{
  "count": 15,
  "next": "http://localhost:8000/financial/api/payments/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "student": 100,
      "student_name": "John Doe",
      "student_id": "STU2024001",
      "fees": [
        {
          "id": 1,
          "fee_type": {
            "id": 1,
            "name": "Tuition Fee",
            "description": "Semester tuition fee",
            "is_active": true,
            "created_at": "2024-08-15T00:00:00Z"
          },
          "amount": "2000.00",
          "due_date": "2024-12-31",
          "status": "partially_paid",
          "description": "Fall 2024 tuition fee",
          "created_at": "2024-08-15T00:00:00Z",
          "amount_paid": "800.00",
          "remaining_balance": "1200.00",
          "is_overdue": false
        }
      ],
      "amount": "500.00",
      "payment_provider": {
        "id": 1,
        "name": "Stripe",
        "description": "Credit/Debit Card payments via Stripe",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z"
      },
      "status": "completed",
      "transaction_id": "txn_1234567890",
      "payment_date": "2024-11-15T10:30:00Z",
      "created_at": "2024-11-15T10:25:00Z",
      "notes": "Partial payment for tuition fee"
    }
  ]
}
```

#### 4.2 Get Payment Details

**Endpoint:** `GET /financial/api/payments/{id}/`

**Description:** Get detailed information about a specific payment

**Response (Success - 200):**
```json
{
  "id": 1,
  "student": 100,
  "student_name": "John Doe",
  "student_id": "STU2024001",
  "fees": [
    {
      "id": 1,
      "fee_type": {
        "id": 1,
        "name": "Tuition Fee",
        "description": "Semester tuition fee",
        "is_active": true,
        "created_at": "2024-08-15T00:00:00Z"
      },
      "amount": "2000.00",
      "due_date": "2024-12-31",
      "status": "partially_paid",
      "description": "Fall 2024 tuition fee",
      "created_at": "2024-08-15T00:00:00Z",
      "amount_paid": "800.00",
      "remaining_balance": "1200.00",
      "is_overdue": false
    }
  ],
  "amount": "500.00",
  "payment_provider": {
    "id": 1,
    "name": "Stripe",
    "description": "Credit/Debit Card payments via Stripe",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "status": "completed",
  "transaction_id": "txn_1234567890",
  "payment_date": "2024-11-15T10:30:00Z",
  "created_at": "2024-11-15T10:25:00Z",
  "notes": "Partial payment for tuition fee"
}
```

#### 4.3 Create Payment

**Endpoint:** `POST /financial/api/payments/create/`

**Description:** Create a new payment for selected fees

**Request Body:**
```json
{
  "fees": [1, 2],
  "amounts": ["500.00", "300.00"],
  "payment_provider": 1,
  "notes": "Partial payment for tuition and library fees"
}
```

**Response (Success - 201):**
```json
{
  "id": 15,
  "student": 100,
  "student_name": "John Doe",
  "student_id": "STU2024001",
  "fees": [
    {
      "id": 1,
      "fee_type": {
        "id": 1,
        "name": "Tuition Fee",
        "description": "Semester tuition fee",
        "is_active": true,
        "created_at": "2024-08-15T00:00:00Z"
      },
      "amount": "2000.00",
      "due_date": "2024-12-31",
      "status": "partially_paid",
      "description": "Fall 2024 tuition fee",
      "created_at": "2024-08-15T00:00:00Z",
      "amount_paid": "1300.00",
      "remaining_balance": "700.00",
      "is_overdue": false
    },
    {
      "id": 2,
      "fee_type": {
        "id": 2,
        "name": "Library Fee",
        "description": "Library access fee",
        "is_active": true,
        "created_at": "2024-08-15T00:00:00Z"
      },
      "amount": "300.00",
      "due_date": "2024-12-31",
      "status": "paid",
      "description": "Fall 2024 library fee",
      "created_at": "2024-08-15T00:00:00Z",
      "amount_paid": "300.00",
      "remaining_balance": "0.00",
      "is_overdue": false
    }
  ],
  "amount": "800.00",
  "payment_provider": {
    "id": 1,
    "name": "Stripe",
    "description": "Credit/Debit Card payments via Stripe",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "status": "pending",
  "transaction_id": null,
  "payment_date": null,
  "created_at": "2024-12-02T10:30:00Z",
  "notes": "Partial payment for tuition and library fees"
}
```

#### 4.4 Get Payment Statistics

**Endpoint:** `GET /financial/api/payments/statistics/`

**Description:** Get payment statistics for the authenticated student

**Response (Success - 200):**
```json
{
  "total_payments": "5500.00",
  "payment_count": 8,
  "status_breakdown": {
    "completed": 6,
    "pending": 1,
    "failed": 1,
    "cancelled": 0
  },
  "monthly_summary": [
    {
      "month": "2024-09",
      "total_amount": "2000.00",
      "payment_count": 3
    },
    {
      "month": "2024-10",
      "total_amount": "1500.00",
      "payment_count": 2
    },
    {
      "month": "2024-11",
      "total_amount": "2000.00",
      "payment_count": 3
    }
  ]
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

### 5. Receipt Management

#### 5.1 View Receipt

**Endpoint:** `GET /financial/api/receipts/{payment_id}/view/`

**Description:** Generate and view a payment receipt as PDF in browser

**Response (Success - 200):**
- **Content-Type:** `application/pdf`
- Binary PDF content displayed in browser

#### 5.2 Download Receipt

**Endpoint:** `GET /financial/api/receipts/{payment_id}/download/`

**Description:** Download a payment receipt as PDF file

**Response (Success - 200):**
- **Content-Type:** `application/pdf`
- **Content-Disposition:** `attachment; filename="receipt-{payment_id}.pdf"`
- Binary PDF content

**Response (Error - 404):**
```json
{
  "detail": "Payment not found or you don't have permission to access it"
}
```

---

## Error Handling

All API endpoints follow consistent error response formats:

### Authentication Errors (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Permission Errors (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Validation Errors (400)
```json
{
  "field_name": [
    "This field is required."
  ],
  "non_field_errors": [
    "Invalid payment amount."
  ]
}
```

### Not Found Errors (404)
```json
{
  "detail": "Not found."
}
```

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- **General endpoints**: 100 requests per minute
- **Payment creation**: 10 requests per minute
- **Receipt generation**: 20 requests per minute

---

## Integration Examples

### Mobile App Integration

```dart
// Flutter/Dart example
class FinancialService {
  static const String baseUrl = 'http://localhost:8000/financial/api';
  
  Future<Map<String, dynamic>> getFinancialSummary() async {
    final response = await http.get(
      Uri.parse('$baseUrl/summary/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );
    return json.decode(response.body);
  }
  
  Future<Map<String, dynamic>> createPayment(List<int> feeIds, List<String> amounts, int providerId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/payments/create/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'fees': feeIds,
        'amounts': amounts,
        'payment_provider': providerId,
      }),
    );
    return json.decode(response.body);
  }
}
```

---

## Changelog

### Version 2.0.0 (Current)
- Complete API restructure for mobile app support
- Added comprehensive financial summary endpoint
- Implemented payment statistics and analytics
- Enhanced receipt management with PDF generation
- Added proper error handling and validation
- Improved authentication and permissions

### Version 1.0.0
- Initial web-based financial system
- Basic fee and payment management
- Staff panel integration