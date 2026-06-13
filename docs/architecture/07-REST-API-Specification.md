# MEMORIA AI - REST API Specification

## Version: 1.0
## Date: June 13, 2026
## Status: Final

---

## Executive Summary

This document provides the complete REST API specification for MEMORIA AI, including all endpoints, request/response schemas, authentication requirements, rate limits, and error handling. The API follows RESTful principles and uses OpenAPI 3.0 specification.

---

## API Overview

### Base URL
- **Development**: `https://api-dev.memoria.ai/v1`
- **Staging**: `https://api-staging.memoria.ai/v1`
- **Production**: `https://api.memoria.ai/v1`

### Authentication
All endpoints require authentication except for public endpoints. Use JWT Bearer tokens in the Authorization header.

```
Authorization: Bearer <access_token>
```

### Rate Limits
- **Free Tier**: 100 requests/minute
- **Pro Tier**: 1000 requests/minute
- **Team Tier**: 5000 requests/minute
- **Enterprise**: Custom limits

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1625097600
```

### Response Format
All responses follow this structure:

```json
{
  "data": {},
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100
  },
  "errors": []
}
```

### Error Response Format
```json
{
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "Invalid input",
      "details": {}
    }
  ]
}
```

---

## Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### POST /auth/login
Authenticate user and receive tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "refresh_token_here",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "John Doe"
    }
  }
}
```

### POST /auth/logout
Logout user and invalidate session.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
No content

### POST /auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

**Response (200):**
```json
{
  "data": {
    "access_token": "new_access_token",
    "refresh_token": "new_refresh_token",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### POST /auth/verify-email
Verify user email address.

**Request Body:**
```json
{
  "token": "verification_token"
}
```

**Response (200):**
```json
{
  "data": {
    "message": "Email verified successfully"
  }
}
```

### POST /auth/forgot-password
Initiate password reset.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "data": {
    "message": "Password reset email sent"
  }
}
```

### POST /auth/reset-password
Reset password with token.

**Request Body:**
```json
{
  "token": "reset_token",
  "new_password": "NewSecurePass123!"
}
```

**Response (200):**
```json
{
  "data": {
    "message": "Password reset successfully"
  }
}
```

### POST /auth/2fa/enable
Enable two-factor authentication.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "secret": "JBSWY3DPEHPK3PXP",
    "qr_code": "data:image/png;base64,..."
  }
}
```

### POST /auth/2fa/verify
Verify and enable 2FA.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "token": "123456"
}
```

**Response (200):**
```json
{
  "data": {
    "message": "2FA enabled successfully"
  }
}
```

### POST /auth/oauth/{provider}
OAuth login with third-party provider.

**Path Parameters:**
- `provider`: google, github, microsoft

**Request Body:**
```json
{
  "code": "oauth_code",
  "redirect_uri": "https://app.memoria.ai/auth/callback"
}
```

**Response (200):**
```json
{
  "data": {
    "access_token": "access_token",
    "refresh_token": "refresh_token",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "John Doe"
    }
  }
}
```

---

## User Management Endpoints

### GET /users/me
Get current user profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "avatar_url": "https://...",
    "role": "user",
    "is_verified": true,
    "two_factor_enabled": false,
    "preferences": {},
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### PUT /users/me
Update current user profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "full_name": "John Doe",
  "avatar_url": "https://..."
}
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "avatar_url": "https://..."
  }
}
```

### PUT /users/me/preferences
Update user preferences.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "theme": "dark",
  "language": "en",
  "notifications": {
    "email": true,
    "push": false
  }
}
```

**Response (200):**
```json
{
  "data": {
    "theme": "dark",
    "language": "en",
    "notifications": {
      "email": true,
      "push": false
    }
  }
}
```

### GET /users/me/workspaces
Get user workspaces.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Personal",
      "is_default": true
    }
  ]
}
```

### POST /users/me/api-keys
Create new API key.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Development Key",
  "scopes": ["read", "write"]
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "name": "Development Key",
    "key": "sk_mem_...",
    "scopes": ["read", "write"],
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /users/me/api-keys
List user API keys.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Development Key",
      "scopes": ["read", "write"],
      "is_active": true,
      "last_used_at": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### DELETE /users/me/api-keys/{id}
Delete API key.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
No content

---

## Notes Endpoints

### GET /notes
List notes with filtering and pagination.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `folder_id`: Filter by folder
- `tag`: Filter by tag
- `is_pinned`: Filter pinned notes
- `is_favorite`: Filter favorite notes
- `is_archived`: Filter archived notes
- `search`: Search query
- `sort`: Sort field (created_at, updated_at, title)
- `order`: Sort order (asc, desc)

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Note Title",
      "content": "Note content...",
      "note_type": "rich_text",
      "is_pinned": false,
      "is_favorite": false,
      "is_archived": false,
      "folder_id": "uuid",
      "folder_name": "My Folder",
      "tags": ["tag1", "tag2"],
      "ai_generated_title": false,
      "ai_generated_tags": false,
      "ai_summary": "AI summary...",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

### POST /notes
Create a new note.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Note Title",
  "content": "Note content...",
  "note_type": "rich_text",
  "folder_id": "uuid",
  "tags": ["tag1", "tag2"]
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "title": "Note Title",
    "content": "Note content...",
    "note_type": "rich_text",
    "is_pinned": false,
    "is_favorite": false,
    "is_archived": false,
    "folder_id": "uuid",
    "tags": ["tag1", "tag2"],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /notes/{id}
Get note by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "title": "Note Title",
    "content": "Note content...",
    "note_type": "rich_text",
    "is_pinned": false,
    "is_favorite": false,
    "is_archived": false,
    "folder_id": "uuid",
    "tags": ["tag1", "tag2"],
    "ai_generated_title": false,
    "ai_generated_tags": false,
    "ai_summary": "AI summary...",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### PUT /notes/{id}
Update note.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content...",
  "is_pinned": true,
  "is_favorite": true,
  "folder_id": "uuid",
  "tags": ["tag1", "tag2", "tag3"]
}
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "title": "Updated Title",
    "content": "Updated content...",
    "is_pinned": true,
    "is_favorite": true,
    "updated_at": "2024-01-01T01:00:00Z"
  }
}
```

### DELETE /notes/{id}
Delete note.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
No content

### GET /notes/{id}/versions
Get note version history.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "version_number": 1,
      "title": "Note Title",
      "content": "Note content...",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /notes/{id}/ai-generate-title
Generate AI title for note.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "title": "AI Generated Title",
    "ai_generated_title": true
  }
}
```

### POST /notes/{id}/ai-generate-tags
Generate AI tags for note.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "tags": ["tag1", "tag2", "tag3"],
    "ai_generated_tags": true
  }
}
```

### POST /notes/{id}/ai-generate-summary
Generate AI summary for note.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "summary": "AI generated summary of the note content..."
  }
}
```

### POST /notes/{id}/links
Create link between notes.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "target_note_id": "uuid",
  "link_type": "reference"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "source_note_id": "uuid",
    "target_note_id": "uuid",
    "link_type": "reference",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## Folders Endpoints

### GET /folders
List folders.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "My Folder",
      "parent_id": null,
      "icon": "folder",
      "color": "#3B82F6",
      "note_count": 10,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /folders
Create folder.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "New Folder",
  "parent_id": "uuid",
  "icon": "folder",
  "color": "#3B82F6"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "name": "New Folder",
    "parent_id": "uuid",
    "icon": "folder",
    "color": "#3B82F6",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### PUT /folders/{id}
Update folder.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Updated Folder",
  "icon": "folder",
  "color": "#10B981"
}
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "name": "Updated Folder",
    "icon": "folder",
    "color": "#10B981",
    "updated_at": "2024-01-01T01:00:00Z"
  }
}
```

### DELETE /folders/{id}
Delete folder.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
No content

---

## Tags Endpoints

### GET /tags
List tags.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "important",
      "color": "#EF4444",
      "note_count": 5,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /tags
Create tag.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "new-tag",
  "color": "#3B82F6"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "name": "new-tag",
    "color": "#3B82F6",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### PUT /tags/{id}
Update tag.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "updated-tag",
  "color": "#10B981"
}
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "name": "updated-tag",
    "color": "#10B981",
    "updated_at": "2024-01-01T01:00:00Z"
  }
}
```

### DELETE /tags/{id}
Delete tag.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
No content

---

## Documents Endpoints

### GET /documents
List documents.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `file_type`: Filter by file type
- `status`: Filter by status
- `search`: Search query

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Document Title",
      "file_name": "document.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "status": "ready",
      "thumbnail_url": "https://...",
      "extracted_text": "Extracted text...",
      "ocr_required": false,
      "indexed": true,
      "created_at": "2024-01-01T00:00:00Z",
      "processed_at": "2024-01-01T00:01:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 50
  }
}
```

### POST /documents/upload
Upload document.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <binary>
title: "Document Title"
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "title": "Document Title",
    "file_name": "document.pdf",
    "file_type": "pdf",
    "file_size": 1024000,
    "status": "processing",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /documents/{id}
Get document by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "title": "Document Title",
    "file_name": "document.pdf",
    "file_type": "pdf",
    "file_size": 1024000,
    "status": "ready",
    "thumbnail_url": "https://...",
    "extracted_text": "Extracted text...",
    "metadata": {},
    "ocr_required": false,
    "indexed": true,
    "created_at": "2024-01-01T00:00:00Z",
    "processed_at": "2024-01-01T00:01:00Z"
  }
}
```

### GET /documents/{id}/content
Get document content.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "content": "Extracted text content...",
    "chunks": [
      {
        "id": "uuid",
        "chunk_index": 0,
        "content": "Chunk content...",
        "start_page": 1,
        "end_page": 2
      }
    ]
  }
}
```

### DELETE /documents/{id}
Delete document.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
No content

### POST /documents/{id}/share
Share document.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "shared_with_user_id": "uuid",
  "permission": "view",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "document_id": "uuid",
    "shared_with_user_id": "uuid",
    "permission": "view",
    "expires_at": "2024-12-31T23:59:59Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /documents/{id}/shares
List document shares.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "shared_with_user_id": "uuid",
      "shared_with_user_email": "user@example.com",
      "permission": "view",
      "expires_at": "2024-12-31T23:59:59Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### DELETE /documents/{id}/shares/{share_id}
Revoke document share.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
No content

---

## Collections Endpoints

### GET /collections
List collections.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Research Papers",
      "description": "Collection of research papers",
      "icon": "book",
      "color": "#3B82F6",
      "item_count": 15,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /collections
Create collection.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "New Collection",
  "description": "Collection description",
  "icon": "folder",
  "color": "#3B82F6"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "name": "New Collection",
    "description": "Collection description",
    "icon": "folder",
    "color": "#3B82F6",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### PUT /collections/{id}
Update collection.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Updated Collection",
  "description": "Updated description"
}
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "name": "Updated Collection",
    "description": "Updated description",
    "updated_at": "2024-01-01T01:00:00Z"
  }
}
```

### DELETE /collections/{id}
Delete collection.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
No content

### POST /collections/{id}/items
Add item to collection.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "item_type": "note",
  "item_id": "uuid"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "collection_id": "uuid",
    "item_type": "note",
    "item_id": "uuid",
    "order_index": 0,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### DELETE /collections/{id}/items/{item_id}
Remove item from collection.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
No content

---

## Search Endpoints

### GET /search
Global search.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `q`: Search query
- `type`: Search type (all, notes, documents)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

**Response (200):**
```json
{
  "data": [
    {
      "type": "note",
      "id": "uuid",
      "title": "Note Title",
      "content": "Note content...",
      "score": 0.95,
      "highlight": "Matched <em>text</em>..."
    },
    {
      "type": "document",
      "id": "uuid",
      "title": "Document Title",
      "content": "Document content...",
      "score": 0.87,
      "highlight": "Matched <em>text</em>..."
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 50
  }
}
```

### POST /search/semantic
Semantic search using embeddings.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "query": "Search query",
  "filters": {
    "type": "notes",
    "folder_id": "uuid"
  },
  "limit": 20
}
```

**Response (200):**
```json
{
  "data": [
    {
      "type": "note",
      "id": "uuid",
      "title": "Note Title",
      "content": "Note content...",
      "score": 0.92
    }
  ]
}
```

### POST /search/hybrid
Hybrid search (keyword + semantic).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "query": "Search query",
  "filters": {},
  "limit": 20
}
```

**Response (200):**
```json
{
  "data": [
    {
      "type": "note",
      "id": "uuid",
      "title": "Note Title",
      "content": "Note content...",
      "score": 0.95
    }
  ]
}
```

### GET /search/suggestions
Get search suggestions.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `q`: Partial query

**Response (200):**
```json
{
  "data": [
    "suggestion 1",
    "suggestion 2",
    "suggestion 3"
  ]
}
```

### POST /search/save
Save search.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "My Saved Search",
  "query": "search query",
  "filters": {}
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "name": "My Saved Search",
    "query": "search query",
    "filters": {},
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## Learning Endpoints

### GET /learning/topics
List learning topics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Data Structures",
      "description": "Study of data structures",
      "parent_id": null,
      "difficulty_level": "intermediate",
      "color": "#3B82F6",
      "icon": "code",
      "total_minutes": 120,
      "session_count": 10,
      "mastery_level": 65.5,
      "last_studied_at": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /learning/topics
Create topic.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "New Topic",
  "description": "Topic description",
  "parent_id": "uuid",
  "difficulty_level": "beginner",
  "color": "#3B82F6",
  "icon": "book"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "name": "New Topic",
    "description": "Topic description",
    "parent_id": "uuid",
    "difficulty_level": "beginner",
    "color": "#3B82F6",
    "icon": "book",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### POST /learning/sessions
Create learning session.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "topic_id": "uuid",
  "note_id": "uuid",
  "document_id": "uuid",
  "duration_minutes": 30,
  "notes": "Session notes..."
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "topic_id": "uuid",
    "duration_minutes": 30,
    "notes": "Session notes...",
    "started_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T00:30:00Z"
  }
}
```

### GET /learning/progress
Get learning progress.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "total_topics": 20,
    "active_topics": 15,
    "total_minutes": 5000,
    "total_sessions": 100,
    "average_mastery": 65.5,
    "streak_days": 7,
    "topics": [
      {
        "topic_id": "uuid",
        "topic_name": "Data Structures",
        "mastery_level": 65.5,
        "total_minutes": 120,
        "session_count": 10
      }
    ]
  }
}
```

### POST /learning/revision-plan
Generate revision plan.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "topics": ["uuid1", "uuid2"],
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "daily_hours": 2
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "name": "Revision Plan",
    "topics": ["uuid1", "uuid2"],
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "daily_hours": 2,
    "schedule": [
      {
        "date": "2024-01-01",
        "topics": ["uuid1"],
        "hours": 2
      }
    ],
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /learning/flashcards
List flashcards.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `topic_id`: Filter by topic
- `deck_name`: Filter by deck
- `due_only`: Only due cards (boolean)

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "topic_id": "uuid",
      "front": "Question",
      "back": "Answer",
      "deck_name": "DSA",
      "next_review_date": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /learning/flashcards
Create flashcard.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "topic_id": "uuid",
  "front": "Question",
  "back": "Answer",
  "deck_name": "DSA"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "topic_id": "uuid",
    "front": "Question",
    "back": "Answer",
    "deck_name": "DSA",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### POST /learning/flashcards/{id}/review
Review flashcard.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "quality": 4
}
```

**Response (200):**
```json
{
  "data": {
    "next_review_date": "2024-01-02T00:00:00Z",
    "ease_factor": 2.6,
    "interval_days": 3
  }
}
```

### POST /learning/quizzes
Create quiz.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "topic_id": "uuid",
  "title": "DSA Quiz",
  "question_count": 10
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "topic_id": "uuid",
    "title": "DSA Quiz",
    "question_count": 10,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### POST /learning/quizzes/{id}/attempt
Attempt quiz.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "answers": [
    {
      "question_id": "uuid",
      "answer": 0
    }
  ]
}
```

**Response (200):**
```json
{
  "data": {
    "attempt_id": "uuid",
    "score": 8,
    "total_questions": 10,
    "percentage": 80,
    "correct_answers": [1, 2, 3],
    "completed_at": "2024-01-01T00:10:00Z"
  }
}
```

---

## Career Endpoints

### GET /career/resumes
List resumes.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Software Engineer Resume",
      "file_path": "https://...",
      "ats_score": 85.5,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /career/resumes
Upload resume.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <binary>
title: "My Resume"
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "title": "My Resume",
    "file_path": "https://...",
    "status": "processing",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### POST /career/resumes/{id}/analyze
Analyze resume with AI.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "ats_score": 85.5,
    "strengths": ["Strong technical skills", "Good experience"],
    "weaknesses": ["Missing keywords", "Poor formatting"],
    "suggestions": ["Add more keywords", "Improve formatting"],
    "parsed_data": {
      "skills": ["Python", "JavaScript"],
      "experience": [...],
      "education": [...]
    }
  }
}
```

### GET /career/skills
List skills.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Python",
      "category": "Programming",
      "proficiency_level": "advanced",
      "years_of_experience": 5,
      "last_used_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /career/skills
Add skill.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Python",
  "category": "Programming",
  "proficiency_level": "advanced",
  "years_of_experience": 5
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "name": "Python",
    "category": "Programming",
    "proficiency_level": "advanced",
    "years_of_experience": 5,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /career/skill-gaps
Get skill gaps analysis.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `target_role`: Target role for analysis

**Response (200):**
```json
{
  "data": {
    "target_role": "Senior Software Engineer",
    "current_skills": ["Python", "JavaScript"],
    "required_skills": ["Python", "JavaScript", "System Design", "Leadership"],
    "missing_skills": [
      {
        "name": "System Design",
        "importance": "high",
        "resources": ["link1", "link2"]
      },
      {
        "name": "Leadership",
        "importance": "medium",
        "resources": ["link1"]
      }
    ]
  }
}
```

### POST /career/roadmap
Generate career roadmap.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "target_role": "Senior Software Engineer",
  "current_role": "Software Engineer"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "target_role": "Senior Software Engineer",
    "current_role": "Software Engineer",
    "estimated_months": 12,
    "milestones": [
      {
        "title": "Learn System Design",
        "timeline": "Months 1-3",
        "skills": ["System Design", "Distributed Systems"]
      }
    ],
    "skills_to_acquire": ["System Design", "Leadership"],
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /career/jobs
List job applications.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: Filter by status
- `company`: Filter by company

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "company_name": "Google",
      "job_title": "Software Engineer",
      "status": "interview",
      "applied_at": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /career/jobs
Add job application.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "company_name": "Google",
  "job_title": "Software Engineer",
  "job_description": "Job description...",
  "application_url": "https://...",
  "status": "applied"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "company_name": "Google",
    "job_title": "Software Engineer",
    "status": "applied",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### POST /career/interviews
Add interview preparation.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "job_application_id": "uuid",
  "company_name": "Google",
  "interview_type": "technical",
  "interview_date": "2024-01-15T10:00:00Z"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "job_application_id": "uuid",
    "company_name": "Google",
    "interview_type": "technical",
    "interview_date": "2024-01-15T10:00:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### POST /career/interviews/{id}/mock
Generate mock interview.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "questions": [
      {
        "question": "Tell me about yourself",
        "type": "behavioral",
        "suggested_answer": "..."
      },
      {
        "question": "Design a URL shortener",
        "type": "technical",
        "suggested_answer": "..."
      }
    ]
  }
}
```

---

## Projects Endpoints

### GET /projects
List projects.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: Filter by status
- `search`: Search query

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Personal Website",
      "description": "Build personal website",
      "status": "active",
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "github_url": "https://github.com/...",
      "milestone_count": 5,
      "task_count": 20,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /projects
Create project.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "New Project",
  "description": "Project description",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "github_url": "https://github.com/..."
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "name": "New Project",
    "description": "Project description",
    "status": "active",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "github_url": "https://github.com/...",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /projects/{id}
Get project details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "name": "Project Name",
    "description": "Project description",
    "status": "active",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "github_url": "https://github.com/...",
    "repository_name": "username/repo",
    "milestones": [...],
    "tasks": [...],
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### PUT /projects/{id}
Update project.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Updated Project",
  "status": "completed"
}
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "name": "Updated Project",
    "status": "completed",
    "updated_at": "2024-01-01T01:00:00Z"
  }
}
```

### POST /projects/{id}/milestones
Create milestone.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Milestone 1",
  "description": "Complete first phase",
  "due_date": "2024-01-15",
  "order_index": 0
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "project_id": "uuid",
    "name": "Milestone 1",
    "description": "Complete first phase",
    "due_date": "2024-01-15",
    "status": "pending",
    "order_index": 0,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### POST /projects/{id}/tasks
Create project task.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "milestone_id": "uuid",
  "title": "Task title",
  "description": "Task description",
  "priority": "high",
  "due_date": "2024-01-10",
  "estimated_hours": 4
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "project_id": "uuid",
    "milestone_id": "uuid",
    "title": "Task title",
    "description": "Task description",
    "status": "todo",
    "priority": "high",
    "due_date": "2024-01-10",
    "estimated_hours": 4,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### POST /projects/{id}/analyze
AI project analysis.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "completion_percentage": 65,
    "risks": [
      {
        "title": "Timeline risk",
        "probability": "high",
        "impact": "medium",
        "mitigation": "Add more resources"
      }
    ],
    "suggestions": [
      "Consider breaking down large tasks",
      "Add buffer time for critical path"
    ]
  }
}
```

---

## Tasks Endpoints

### GET /tasks
List tasks.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: Filter by status
- `priority`: Filter by priority
- `due_date`: Filter by due date
- `project_id`: Filter by project

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Task title",
      "description": "Task description",
      "status": "todo",
      "priority": "high",
      "due_date": "2024-01-10T10:00:00Z",
      "is_recurring": false,
      "project_id": "uuid",
      "project_name": "Project Name",
      "tags": ["urgent"],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /tasks
Create task.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "New Task",
  "description": "Task description",
  "priority": "medium",
  "due_date": "2024-01-10T10:00:00Z",
  "project_id": "uuid",
  "tags": ["work"]
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "title": "New Task",
    "description": "Task description",
    "status": "todo",
    "priority": "medium",
    "due_date": "2024-01-10T10:00:00Z",
    "project_id": "uuid",
    "tags": ["work"],
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### PUT /tasks/{id}
Update task.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "status": "in_progress",
  "priority": "high"
}
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "status": "in_progress",
    "priority": "high",
    "updated_at": "2024-01-01T01:00:00Z"
  }
}
```

### POST /tasks/{id}/complete
Complete task.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "status": "completed",
    "completed_at": "2024-01-01T01:00:00Z"
  }
}
```

### DELETE /tasks/{id}
Delete task.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
No content

---

## Calendar Endpoints

### GET /calendar/events
List events.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `start_date`: Start date filter
- `end_date`: End date filter
- `calendar_id`: Filter by calendar

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "calendar_id": "uuid",
      "calendar_name": "Personal",
      "title": "Meeting",
      "description": "Team meeting",
      "location": "Conference Room",
      "start_time": "2024-01-10T10:00:00Z",
      "end_time": "2024-01-10T11:00:00Z",
      "is_all_day": false,
      "status": "confirmed",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /calendar/events
Create event.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "calendar_id": "uuid",
  "title": "Meeting",
  "description": "Team meeting",
  "location": "Conference Room",
  "start_time": "2024-01-10T10:00:00Z",
  "end_time": "2024-01-10T11:00:00Z",
  "is_all_day": false,
  "reminder_minutes_before": 15
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "calendar_id": "uuid",
    "title": "Meeting",
    "description": "Team meeting",
    "location": "Conference Room",
    "start_time": "2024-01-10T10:00:00Z",
    "end_time": "2024-01-10T11:00:00Z",
    "is_all_day": false,
    "reminder_minutes_before": 15,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### PUT /calendar/events/{id}
Update event.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Updated Meeting",
  "start_time": "2024-01-10T11:00:00Z",
  "end_time": "2024-01-10T12:00:00Z"
}
```

**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "title": "Updated Meeting",
    "start_time": "2024-01-10T11:00:00Z",
    "end_time": "2024-01-10T12:00:00Z",
    "updated_at": "2024-01-01T01:00:00Z"
  }
}
```

### DELETE /calendar/events/{id}
Delete event.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
No content

### GET /calendar/calendars
List calendars.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Personal",
      "description": "Personal calendar",
      "color": "#3B82F6",
      "provider": "local",
      "is_default": true,
      "is_synced": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /calendar/calendars
Create calendar.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Work Calendar",
  "description": "Work events",
  "color": "#EF4444",
  "provider": "google"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "name": "Work Calendar",
    "description": "Work events",
    "color": "#EF4444",
    "provider": "google",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## Agents Endpoints

### GET /agents
List agents.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Study Agent",
      "agent_type": "study",
      "description": "Helps with studying",
      "is_active": true,
      "execution_count": 50,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /agents
Create agent.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "My Agent",
  "agent_type": "study",
  "description": "Agent description",
  "configuration": {
    "model": "gpt-4",
    "temperature": 0.7,
    "tools": ["search", "calculator"]
  }
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "name": "My Agent",
    "agent_type": "study",
    "description": "Agent description",
    "configuration": {
      "model": "gpt-4",
      "temperature": 0.7,
      "tools": ["search", "calculator"]
    },
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### POST /agents/{id}/execute
Execute agent.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "input": {
    "query": "Help me study DSA"
  }
}
```

**Response (200):**
```json
{
  "data": {
    "execution_id": "uuid",
    "agent_id": "uuid",
    "status": "completed",
    "output": {
      "response": "Here's a study plan for DSA...",
      "steps": [...]
    },
    "duration_seconds": 5,
    "completed_at": "2024-01-01T00:00:05Z"
  }
}
```

### GET /agents/{id}/executions
List agent executions.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "agent_id": "uuid",
      "status": "completed",
      "duration_seconds": 5,
      "started_at": "2024-01-01T00:00:00Z",
      "completed_at": "2024-01-01T00:00:05Z"
    }
  ]
}
```

---

## Analytics Endpoints

### GET /analytics/overview
Get analytics overview.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `period`: Time period (7d, 30d, 90d, 1y)

**Response (200):**
```json
{
  "data": {
    "period": "30d",
    "notes_created": 50,
    "documents_uploaded": 10,
    "learning_minutes": 500,
    "tasks_completed": 30,
    "search_queries": 100,
    "ai_interactions": 75,
    "knowledge_growth": 15.5,
    "activity_trend": [
      {
        "date": "2024-01-01",
        "activity": 10
      }
    ]
  }
}
```

### GET /analytics/knowledge-growth
Get knowledge growth metrics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `period`: Time period
- `topic_id`: Filter by topic

**Response (200):**
```json
{
  "data": [
    {
      "date": "2024-01-01",
      "topic_id": "uuid",
      "topic_name": "Data Structures",
      "metric_name": "mastery_level",
      "metric_value": 65.5
    }
  ]
}
```

### GET /analytics/learning-progress
Get learning progress metrics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "total_topics": 20,
    "active_topics": 15,
    "completed_topics": 5,
    "total_hours": 100,
    "average_session_duration": 30,
    "streak_days": 7,
    "topic_progress": [
      {
        "topic_name": "Data Structures",
        "progress": 65,
        "hours_spent": 20
      }
    ]
  }
}
```

---

## AI Endpoints

### POST /ai/chat
Chat with AI.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello, how can you help me?"
    }
  ],
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response (200):**
```json
{
  "data": {
    "message": {
      "role": "assistant",
      "content": "I can help you with..."
    },
    "model": "gpt-4",
    "tokens_used": 150,
    "cost": 0.003
  }
}
```

### POST /ai/completions
Get text completion.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "prompt": "Complete this text...",
  "model": "gpt-4",
  "max_tokens": 500
}
```

**Response (200):**
```json
{
  "data": {
    "completion": "Completed text...",
    "model": "gpt-4",
    "tokens_used": 100
  }
}
```

### POST /ai/embeddings
Generate embeddings.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "text": "Text to embed",
  "model": "text-embedding-3-small"
}
```

**Response (200):**
```json
{
  "data": {
    "embedding": [0.1, 0.2, 0.3, ...],
    "model": "text-embedding-3-small",
    "dimensions": 1536
  }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid input data |
| `UNAUTHORIZED` | Missing or invalid authentication |
| `FORBIDDEN` | Insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `CONFLICT` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Internal server error |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable |
| `AI_ERROR` | AI service error |
| `STORAGE_ERROR` | Storage service error |

---

## Webhooks

### POST /webhooks
Create webhook.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "url": "https://example.com/webhook",
  "events": ["note.created", "document.uploaded"],
  "secret": "webhook_secret"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "url": "https://example.com/webhook",
    "events": ["note.created", "document.uploaded"],
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

**Document Status:** Approved
**Next Review:** Q4 2026
**Owner:** API Team
