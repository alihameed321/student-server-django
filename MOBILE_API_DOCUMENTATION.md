# Student Document Management Mobile API Documentation

This document provides comprehensive information about the mobile API endpoints for student document management, designed to mirror the web interface functionality.

## Base URL
```
/api/student/
```

## Authentication
All endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. Document Listing API
**Endpoint:** `GET /api/student/documents/`

**Description:** Enhanced document listing with advanced filtering and sorting options

**Query Parameters:**
- `document_type` (string): Filter by document type
- `is_official` (boolean): Filter by official status (true/false)
- `search` (string): Search in title and document type
- `date_from` (string): Filter documents from date (YYYY-MM-DD format)
- `date_to` (string): Filter documents to date (YYYY-MM-DD format)
- `sort_by` (string): Sort field (issued_date, title, document_type, download_count)
- `sort_order` (string): Sort order (asc/desc)
- `page` (integer): Page number for pagination
- `page_size` (integer): Number of items per page

**Response Example:**
```json
{
  "success": true,
  "count": 25,
  "next": "http://localhost:8000/api/student/documents/?page=2",
  "previous": null,
  "results": {
    "data": [
      {
        "id": 1,
        "title": "Academic Transcript",
        "document_type": "transcript",
        "document_type_display": "Academic Transcript",
        "issued_date": "2024-01-15T10:30:00Z",
        "issued_date_formatted": "Jan 15, 2024",
        "is_official": true,
        "download_count": 5,
        "file_size": 2048576,
        "file_size_formatted": "2.0 MB",
        "file_extension": ".pdf",
        "download_url": "/api/student/documents/1/download/",
        "preview_url": "/api/student/documents/1/",
        "is_downloadable": true,
        "status_badge": "Official"
      }
    ],
    "applied_filters": {
      "document_type": null,
      "is_official": null,
      "search": null,
      "date_from": null,
      "date_to": null,
      "sort_by": "issued_date",
      "sort_order": "desc"
    }
  }
}
```

### 2. Document Detail/Preview API
**Endpoint:** `GET /api/student/documents/<document_id>/`

**Description:** Get document metadata and preview information without downloading

**Response Example:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Academic Transcript",
    "document_type_display": "Academic Transcript",
    "issued_date_formatted": "Jan 15, 2024",
    "file_size_formatted": "2.0 MB",
    "is_downloadable": true,
    "download_count": 5
  }
}
```

### 3. Document Download API
**Endpoint:** `GET /api/student/documents/<document_id>/download/`

**Description:** Download document file and increment download counter

**Response:** File stream with appropriate headers

### 4. Document Types API
**Endpoint:** `GET /api/student/document-types/`

**Description:** Get available document categories for filtering

**Response Example:**
```json
{
  "success": true,
  "data": {
    "document_types": [
      {"value": "transcript", "label": "Academic Transcript"},
      {"value": "certificate", "label": "Certificate"},
      {"value": "diploma", "label": "Diploma"}
    ],
    "total_types": 3
  }
}
```

### 5. Document Statistics API
**Endpoint:** `GET /api/student/documents/statistics/`

**Description:** Get document statistics for dashboard integration

**Response Example:**
```json
{
  "success": true,
  "data": {
    "total_documents": 15,
    "official_documents": 12,
    "total_downloads": 45,
    "recent_documents": [
      {
        "id": 1,
        "title": "Academic Transcript",
        "issued_date_formatted": "Jan 15, 2024"
      }
    ],
    "documents_by_type": [
      {"type": "Academic Transcript", "count": 5},
      {"type": "Certificate", "count": 7}
    ],
    "most_downloaded": [
      {
        "id": 1,
        "title": "Academic Transcript",
        "download_count": 15
      }
    ]
  }
}
```

### 6. Document Status Tracking API
**Endpoint:** `GET /api/student/documents/status/`

**Description:** Get document processing status and availability information

**Response Example:**
```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "id": 1,
        "title": "Academic Transcript",
        "document_type": "Academic Transcript",
        "issued_date": "2024-01-15T10:30:00Z",
        "is_official": true,
        "download_count": 5,
        "status": {
          "is_available": true,
          "is_downloadable": true,
          "file_exists": true,
          "processing_status": "completed",
          "status_message": "Document is ready for download"
        },
        "file_info": {
          "has_file": true,
          "file_size": 2048576,
          "file_extension": ".pdf"
        }
      }
    ],
    "summary": {
      "total_documents": 15,
      "available_documents": 14,
      "processing_documents": 1,
      "availability_rate": 93.33
    }
  }
}
```

### 7. Advanced Document Search API
**Endpoint:** `GET /api/student/documents/search/`

**Description:** Advanced search with multiple criteria

**Query Parameters:**
- `q` (string): Search query (minimum 2 characters)
- `document_type` (string): Filter by document type
- `is_official` (boolean): Filter by official status
- `date_from` (string): Date range start (YYYY-MM-DD)
- `date_to` (string): Date range end (YYYY-MM-DD)
- `min_downloads` (integer): Minimum download count
- `max_downloads` (integer): Maximum download count
- `sort_by` (string): Sort field
- `sort_order` (string): Sort order (asc/desc)

**Response Example:**
```json
{
  "success": true,
  "count": 5,
  "next": null,
  "previous": null,
  "results": {
    "data": [...],
    "search_params": {
      "query": "transcript",
      "document_type": null,
      "is_official": "true",
      "date_from": "2024-01-01",
      "date_to": "2024-12-31",
      "sort_by": "issued_date",
      "sort_order": "desc"
    },
    "total_matches": 5
  }
}
```

### 8. Document Sharing API
**Endpoint:** `GET/POST /api/student/documents/sharing/`

**Description:** Manage document sharing and access control

#### GET - List Sharing Capabilities
**Query Parameters:**
- `document_id` (optional): Get sharing info for specific document

**Response Example:**
```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "document_id": 1,
        "title": "Academic Transcript",
        "document_type": "Academic Transcript",
        "is_official": true,
        "issued_date": "2024-01-15T10:30:00Z",
        "sharing_capabilities": {
          "can_share": true,
          "can_generate_link": true,
          "supports_access_control": true,
          "reason": "Document ready for sharing"
        }
      }
    ],
    "total_shareable": 12
  }
}
```

#### POST - Create Sharing Link
**Request Body:**
```json
{
  "document_id": 1,
  "action": "create_link",
  "expiry_hours": 24,
  "allow_download": true,
  "max_downloads": 5,
  "requires_auth": false
}
```

**Response Example:**
```json
{
  "success": true,
  "message": "Sharing link created successfully",
  "data": {
    "document_id": 1,
    "sharing_token": "abc123def456",
    "sharing_url": "/api/student/documents/1/shared/abc123def456/",
    "created_at": "2024-01-15T10:30:00Z",
    "expires_at": "2024-01-16T10:30:00Z",
    "access_settings": {
      "download_enabled": true,
      "view_enabled": true,
      "max_downloads": 5,
      "requires_auth": false
    }
  }
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "Invalid request parameters",
    "details": {
      "field": "document_type",
      "issue": "Invalid document type provided"
    }
  }
}
```

## Common HTTP Status Codes
- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Mobile App Integration Tips

1. **Pagination**: Use pagination for document lists to improve performance
2. **Caching**: Cache document types and statistics data
3. **Error Handling**: Implement proper error handling for network issues
4. **File Downloads**: Handle large file downloads with progress indicators
5. **Search**: Implement debounced search to avoid excessive API calls
6. **Offline Support**: Cache document metadata for offline viewing

## Security Considerations

1. **Authentication**: Always include JWT tokens in requests
2. **HTTPS**: Use HTTPS in production
3. **File Access**: Document files are protected and require authentication
4. **Rate Limiting**: API may have rate limiting in place
5. **Sharing Links**: Sharing tokens are time-limited and can be revoked

This API provides comprehensive functionality that mirrors the web interface, making it easy to build a feature-rich mobile application for student document management.