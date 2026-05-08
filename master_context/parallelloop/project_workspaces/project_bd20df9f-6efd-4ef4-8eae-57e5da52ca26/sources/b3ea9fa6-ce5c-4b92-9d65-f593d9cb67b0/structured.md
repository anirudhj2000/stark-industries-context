# WA Sample ones — 2026-05-08 13:26 jpg

**Source**: WA Sample ones — 2026-05-08 13:26 jpg
**Format**: IMAGE (JPG)
**Word Count**: 156
**Processed**: 2026-05-08T13:27:00Z

---

## Extracted Content

This image is a screenshot of an API testing interface (likely Swagger or similar documentation tool) showing the **User Token Refresh Endpoint**.

### Curl Command

```bash
curl -X 'POST' \
  'https://awsdevsourcingapi.scimplify.com/api/v1/users/refresh-token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "refresh_token": "eyJhbGci..."
}'
```

### Request URL

```
https://awsdevsourcingapi.scimplify.com/api/v1/users/refresh-token
```

### Server Response

**Code**: 200

**Response Body**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "created_at": "2025-05-29T05:07:41.590000",
    "updated_at": "2026-05-07T15:21:08.623000",
    "email": "kartikey.g@scimplify.com",
    "username": "kartikey",
    "full_name": "Kartikey Gautam",
    "phone": "7411114084",
    "department": null,
    "role": "TEAM",
    "id": 2,
    "is_active": true,
    "is_superuser": false
  }
}
```

### Key Details

- **API Endpoint**: Scimplify AWS Dev Sourcing API
- **Authentication**: Bearer token (JWT-based)
- **Token Expiry**: 86400 seconds (24 hours)
- **User Profile**: Kartikey Gautam (kartikey.g@scimplify.com)
- **User Role**: TEAM member

---

## Enrichment Legend

### Vocabulary (0 terms normalized)

_No vocabulary terms matched._

### Entities (0 found)

_No known entities detected._
