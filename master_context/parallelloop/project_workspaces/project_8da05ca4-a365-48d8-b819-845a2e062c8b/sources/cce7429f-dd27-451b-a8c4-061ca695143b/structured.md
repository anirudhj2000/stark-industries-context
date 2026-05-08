# WA Anirudh Joshi — 2026-05-08 13:26 jpg

**Source**: WA Anirudh Joshi — 2026-05-08 13:26 jpg
**Format**: IMAGE (jpg)
**Word Count**: 142
**Processed**: 2026-05-08T13:26:20+00:00

---

## Extracted Content

This image shows an API documentation interface (likely Swagger UI) displaying a token refresh endpoint request and response.

### cURL Command

```bash
curl -X 'POST' \
  'https://awsdevsourcingapi.scimplify.com/api/v1/users/refresh-token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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

### Key Information

- **API Endpoint**: Scimplify User Authentication Service
- **Operation**: Token refresh (POST)
- **User**: Kartikey Gautam (kartikey.g@scimplify.com)
- **Token Expiry**: 86400 seconds (24 hours)
- **User Role**: TEAM

---

## Enrichment Legend

### Vocabulary (0 terms normalized)

*No vocabulary terms found*

### Entities (0 found)

*No matching entities found*
