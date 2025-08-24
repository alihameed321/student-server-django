# Financial API Documentation

This document provides comprehensive documentation for the refactored Financial API, designed for seamless integration with the student mobile application.

## Base URL
```
/api/financial/
```

## Authentication
All endpoints require authentication using Django's session authentication or token authentication.

## Common Response Format

### Success Response
```json
{
    "success": true,
    "data": {...},
    "message": "Optional success message"
}
```

### Error Response
```json
{
    "error": "Error type",
    "detail": "Detailed error message",
    "validation_errors": [...] // Optional, for validation errors
}
```

## Endpoints

### 1. Financial Summary
**GET** `/summary/`

Returns comprehensive financial overview for the authenticated student.

**Response:**
```json
{
    "success": true,
    "summary": {
        "total_fees": "1500.00",
        "pending_payments": "800.00",
        "paid_this_semester": "700.00",
        "overdue_count": 2,
        "overdue_amount": "300.00"
    },
    "payment_statistics": {
        "total_transactions": 15,
        "verified_payments": 12,
        "pending_payments": 3
    },
    "recent_transactions": [...],
    "fee_breakdown": [...]
}
```

### 2. Student Fees

#### List Fees
**GET** `/fees/`

**Query Parameters:**
- `status`: Filter by status (pending, partial, paid, overdue)
- `fee_type`: Filter by fee type ID
- `outstanding`: Filter outstanding fees (true/false)
- `semester`: Filter by semester
- `search`: Search in fee type name or description
- `page`: Page number for pagination
- `page_size`: Number of items per page (max 100)

**Response:**
```json
{
    "count": 25,
    "next": "http://example.com/api/financial/fees/?page=2",
    "previous": null,
    "results": [...],
    "summary": {
        "total_fees": "2500.00",
        "total_outstanding": "800.00",
        "overdue_count": 3
    },
    "filters": {
        "available_statuses": ["pending", "partial", "paid", "overdue"],
        "available_fee_types": [...]
    }
}
```

#### Fee Detail
**GET** `/fees/{id}/`

**Response:**
```json
{
    "id": 1,
    "fee_type": {
        "id": 1,
        "name": "Tuition Fee",
        "description": "Semester tuition fee"
    },
    "amount": "1000.00",
    "amount_paid": "200.00",
    "remaining_balance": "800.00",
    "due_date": "2024-03-15",
    "status": "partial",
    "is_overdue": false,
    "description": "Spring 2024 tuition fee",
    "created_at": "2024-01-15T10:00:00Z"
}
```

#### Outstanding Fees
**GET** `/fees/outstanding/`

**Response:**
```json
{
    "success": true,
    "outstanding_fees": [...],
    "summary": {
        "total_outstanding": "1200.00",
        "total_count": 5,
        "overdue_count": 2,
        "overdue_amount": "300.00",
        "pending_count": 3,
        "partial_count": 2
    }
}
```

### 3. Payment Providers
**GET** `/payment-providers/`

**Response:**
```json
[
    {
        "id": 1,
        "name": "Bank Transfer",
        "description": "Direct bank transfer",
        "instructions": "Transfer to university account",
        "is_active": true,
        "logo": "/media/providers/bank.png",
        "university_account_name": "University Account",
        "university_account_number": "1234567890",
        "university_phone": "+1234567890",
        "additional_info": "Include student ID in reference"
    }
]
```

### 4. Payments

#### List Payments
**GET** `/payments/`

**Query Parameters:**
- `status`: Filter by payment status
- `payment_provider`: Filter by provider ID
- `start_date`: Filter payments from date (YYYY-MM-DD)
- `end_date`: Filter payments to date (YYYY-MM-DD)
- `page`: Page number
- `page_size`: Items per page

**Response:**
```json
{
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "fee": {...},
            "payment_provider": {...},
            "amount": "500.00",
            "transaction_reference": "TXN123456",
            "payment_date": "2024-02-15T14:30:00Z",
            "status": "verified",
            "status_display": "Verified",
            "verified_at": "2024-02-16T09:00:00Z",
            "can_view_receipt": true
        }
    ]
}
```

#### Payment Detail
**GET** `/payments/{id}/`

#### Create Payment
**POST** `/payments/create/`

**Request Body:**
```json
{
    "fees": [
        {
            "id": "1",
            "amount": "500.00"
        },
        {
            "id": "2",
            "amount": "300.00"
        }
    ],
    "payment_provider_id": 1,
    "total_amount": "800.00",
    "transaction_reference": "TXN123456",
    "sender_name": "John Doe",
    "sender_phone": "+1234567890",
    "transfer_notes": "Payment for spring semester"
}
```

**Success Response:**
```json
{
    "success": true,
    "message": "Payment submitted successfully. Awaiting verification.",
    "payment_count": 2,
    "total_amount": "800.00",
    "payment_provider": "Bank Transfer",
    "transaction_reference": "TXN123456",
    "payments": [...],
    "created_at": "2024-02-15T14:30:00Z"
}
```

**Error Response:**
```json
{
    "error": "Invalid payment amounts",
    "validation_errors": [
        {
            "fee_id": 1,
            "fee_name": "Tuition Fee",
            "error": "Payment amount 600.00 exceeds remaining balance 500.00"
        }
    ]
}
```

#### Payment Statistics
**GET** `/payments/statistics/`

**Response:**
```json
{
    "success": true,
    "summary": {
        "total_payments": "5000.00",
        "total_transactions": 25,
        "recent_payments_count": 3,
        "recent_payments_amount": "800.00"
    },
    "payment_counts": {
        "pending": 2,
        "verified": 20,
        "rejected": 1
    },
    "payment_amounts": {
        "pending": "400.00",
        "verified": "4500.00",
        "rejected": "100.00"
    },
    "current_year": {
        "total_amount": "3000.00",
        "transaction_count": 15,
        "year": 2024
    },
    "monthly_summary": [
        {
            "month": "2024-01",
            "total": "1000.00",
            "count": 5
        }
    ],
    "provider_usage": [
        {
            "provider": "Bank Transfer",
            "count": 15,
            "total_amount": "3000.00"
        }
    ]
}
```

### 5. Receipts

#### View Receipt
**GET** `/receipts/{payment_id}/view/`

Returns PDF receipt for inline viewing.

**Response:** PDF file with headers:
- `Content-Type: application/pdf`
- `Content-Disposition: inline; filename="receipt_{payment_id}.pdf"`
- `X-Payment-ID: {payment_id}`
- `X-Payment-Amount: {amount}`

#### Download Receipt
**GET** `/receipts/{payment_id}/download/`

Returns PDF receipt for download.

**Response:** PDF file with headers:
- `Content-Type: application/pdf`
- `Content-Disposition: attachment; filename="receipt_{payment_id}_{date}.pdf"`
- `X-Payment-ID: {payment_id}`
- `X-Payment-Amount: {amount}`
- `X-Payment-Date: {iso_date}`

## Error Codes

- `400 Bad Request`: Invalid request data or validation errors
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Mobile App Integration Notes

### 1. Pagination
- All list endpoints support pagination
- Use `page` and `page_size` parameters
- Response includes `count`, `next`, and `previous` fields

### 2. Filtering and Search
- Most list endpoints support filtering
- Use query parameters for filtering
- Search functionality available where applicable

### 3. Data Formatting
- All monetary amounts are returned as strings to preserve precision
- Dates are in ISO 8601 format
- Boolean fields are properly typed

### 4. Error Handling
- Consistent error response format
- Detailed validation errors for form submissions
- Appropriate HTTP status codes

### 5. Performance Optimizations
- Database queries are optimized with select_related and prefetch_related
- Pagination limits large result sets
- Computed fields are annotated at database level where possible

### 6. Security
- All endpoints require authentication
- Users can only access their own data
- Database transactions ensure data consistency
- Input validation prevents malicious data

## Example Mobile App Usage

### 1. Get Financial Overview
```dart
final response = await apiService.getFinancialSummary();
if (response['success']) {
    final summary = response['summary'];
    // Update UI with financial data
}
```

### 2. Load Outstanding Fees
```dart
final fees = await apiService.getOutstandingFees();
if (fees['success']) {
    final outstandingFees = fees['outstanding_fees'];
    final summary = fees['summary'];
    // Display fees and summary
}
```

### 3. Submit Payment
```dart
final paymentData = {
    'fees': selectedFees,
    'payment_provider_id': providerId,
    'total_amount': totalAmount.toString(),
    'transaction_reference': reference,
};

final result = await apiService.createPayment(paymentData);
if (result['success']) {
    // Payment submitted successfully
    showSuccessMessage(result['message']);
} else {
    // Handle validation errors
    showErrorMessage(result['error']);
}
```

This refactored API provides a robust, mobile-friendly interface for financial operations with comprehensive error handling, optimized queries, and consistent response formats.