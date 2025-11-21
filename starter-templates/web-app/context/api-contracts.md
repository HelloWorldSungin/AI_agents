# {{PROJECT_NAME}} - API Contracts

## Overview

This document defines the API contracts for {{PROJECT_NAME}}. All endpoints follow RESTful conventions.

## Base URLs

| Environment | URL |
|-------------|-----|
| Development | `http://localhost:3000/api` |
| Staging | `https://staging-api.{{PROJECT_NAME}}.com` |
| Production | `https://api.{{PROJECT_NAME}}.com` |

## Authentication

### JWT Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

### Getting a Token

**POST /api/auth/login**

Request:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe"
    }
  }
}
```

## Standard Response Format

All API responses follow this structure:

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  }
}
```

## API Endpoints

### Authentication Endpoints

#### POST /api/auth/register
Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe"
    }
  }
}
```

#### POST /api/auth/login
Authenticate user and get token.

#### POST /api/auth/logout
Invalidate current token.

#### POST /api/auth/refresh
Refresh expired token.

---

### User Endpoints

#### GET /api/users/me
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2025-01-01T00:00:00Z"
  }
}
```

#### PUT /api/users/me
Update current user profile.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```

**Response:** `200 OK`

#### DELETE /api/users/me
Delete current user account.

---

### [Your Domain] Endpoints

**Add your domain-specific endpoints here. Examples:**

#### GET /api/items
List all items.

**Query Parameters:**
- `page` (number): Page number (default: 1)
- `limit` (number): Items per page (default: 20, max: 100)
- `sort` (string): Sort field (default: createdAt)
- `order` (string): Sort order - `asc` or `desc` (default: desc)
- `search` (string): Search query

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "Item Name",
        "description": "Item description",
        "createdAt": "2025-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

#### POST /api/items
Create a new item.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Item Name",
  "description": "Item description"
}
```

**Response:** `201 Created`

#### GET /api/items/:id
Get specific item by ID.

**Response:** `200 OK`

#### PUT /api/items/:id
Update specific item.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`

#### DELETE /api/items/:id
Delete specific item.

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Invalid or missing authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMIT` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Rate Limiting

- Anonymous requests: 100 requests per 15 minutes
- Authenticated requests: 1000 requests per 15 minutes

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640000000
```

## Versioning

API versioning uses URL path versioning:
- `/api/v1/...` - Current stable version
- `/api/v2/...` - Next version (when available)

Current version: `v1`

---

**Last Updated**: [Date]
**API Version**: v1
