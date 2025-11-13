# API Reference

The Implementation Guides MCP server provides both REST API endpoints and MCP protocol handlers.

**Base URL**: `https://mcp-server-375955300575.us-central1.run.app`

## Authentication

All API endpoints require authentication via Google Cloud Identity token.

### Get Authentication Token

```bash
# Using gcloud CLI
TOKEN=$(gcloud auth print-identity-token)

# Use in requests
curl -H "Authorization: Bearer $TOKEN" <endpoint>
```

### For MCP Tools

MCP tools can use either:
- **Google OAuth**: Automatic via `gcloud` CLI
- **API Key**: Set `IMPLEMENTATION_GUIDES_API_KEY` environment variable

## REST API Endpoints

### 1. List Guide Divisions

Get all available divisions with guide counts.

**Endpoint**: `GET /divisions`

**Request**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/divisions
```

**Response**:
```json
[
  {
    "name": "se",
    "guide_count": 70
  },
  {
    "name": "exd", 
    "guide_count": 25
  },
  {
    "name": "pm",
    "guide_count": 20
  },
  {
    "name": "qa",
    "guide_count": 15
  }
]
```

---

### 2. List Guides by Division

Get all guides in a specific division.

**Endpoint**: `GET /divisions/{division}/guides`

**Parameters**:
- `division` (path): Division name (`se`, `exd`, `pm`, `qa`)

**Request**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/divisions/se/guides
```

**Response**:
```json
[
  {
    "title": "Authentication Module - Introduction 1",
    "path": "se/authentication-module---introduction-1/index.md",
    "maturity": "introduction-1",
    "division": "se"
  },
  {
    "title": "OAuth Integration - Growth 1",
    "path": "se/oauth-integration---growth-1/index.md",
    "maturity": "growth-1",
    "division": "se"
  }
]
```

---

### 3. Get Guide Content

Retrieve full content of a specific guide.

**Endpoint**: `GET /guides/{path}`

**Parameters**:
- `path` (path): Full guide path (e.g., `se/authentication-module---introduction-1/index.md`)

**Request**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/guides/se/authentication-module---introduction-1/index.md
```

**Response**:
```json
{
  "title": "Authentication Module - Introduction 1",
  "division": "se",
  "maturity": "introduction-1",
  "content": "# Authentication Module\n\n## Functional Requirements\n...",
  "metadata": {
    "created_at": "2024-10-15T10:30:00",
    "updated_at": "2024-11-01T14:20:00",
    "source_url": "https://notion.so/..."
  },
  "requirements": {
    "functional": [
      "User must be able to log in with email and password",
      "System must support OAuth 2.0 authentication"
    ],
    "security": [
      "Passwords must be hashed using bcrypt",
      "Implement rate limiting on login attempts"
    ]
  }
}
```

---

### 4. Search Guides (Semantic Search)

Search for guides using AI-powered semantic search.

**Endpoint**: `POST /search`

**Request Body**:
```json
{
  "query": "user authentication OAuth setup",
  "top_k": 5,
  "division": "se",  // optional: filter by division
  "maturity_level": "introduction-1"  // optional: filter by maturity
}
```

**Request**:
```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "user authentication OAuth",
    "top_k": 5
  }' \
  https://mcp-server-375955300575.us-central1.run.app/search
```

**Response**:
```json
{
  "query": "user authentication OAuth",
  "results": [
    {
      "title": "Authentication Module - OAuth Integration",
      "path": "se/oauth-integration---growth-1/index.md",
      "division": "se",
      "maturity": "growth-1",
      "score": 0.92,
      "excerpt": "This guide covers OAuth 2.0 implementation for user authentication..."
    },
    {
      "title": "SSO Integration - Introduction 2",
      "path": "se/sso-integration---introduction-2/index.md",
      "division": "se", 
      "maturity": "introduction-2",
      "score": 0.87,
      "excerpt": "Setting up Single Sign-On with OAuth providers..."
    }
  ],
  "total": 2
}
```

---

### 5. Get Guide Recommendations

Get personalized guide recommendations based on topics and context.

**Endpoint**: `POST /recommendations`

**Request Body**:
```json
{
  "topics": ["authentication", "security", "OAuth"],
  "division": "se",  // optional
  "maturity_level": "introduction-1",  // optional
  "top_k": 5  // optional, default 5
}
```

**Request**:
```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topics": ["authentication", "security"],
    "division": "se",
    "maturity_level": "introduction-1"
  }' \
  https://mcp-server-375955300575.us-central1.run.app/recommendations
```

**Response**:
```json
{
  "recommendations": [
    {
      "title": "Authentication Module - Introduction 1",
      "path": "se/authentication-module---introduction-1/index.md",
      "division": "se",
      "maturity": "introduction-1",
      "relevance_score": 0.95,
      "reason": "Core authentication implementation guide for introduction-level projects"
    },
    {
      "title": "Security Best Practices - Foundational",
      "path": "se/security-best-practices---foundational/index.md",
      "division": "se",
      "maturity": "foundational",
      "relevance_score": 0.88,
      "reason": "Foundational security concepts (always recommended)"
    }
  ]
}
```

---

## MCP Protocol Endpoints

The server also exposes MCP protocol handlers at `/mcp` endpoint.

**Endpoint**: `POST /mcp`

**Request Body** (MCP protocol):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_guides",
    "arguments": {
      "query": "authentication",
      "top_k": 5
    }
  }
}
```

## Error Responses

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing or invalid authentication)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (guide or division not found)
- `500` - Internal Server Error

### Error Response Format

```json
{
  "error": {
    "code": "GUIDE_NOT_FOUND",
    "message": "Guide not found: se/nonexistent-guide/index.md",
    "details": "The requested guide does not exist in the repository"
  }
}
```

### Common Error Codes

- `INVALID_DIVISION` - Division must be one of: se, exd, pm, qa
- `GUIDE_NOT_FOUND` - The specified guide path does not exist
- `SEARCH_FAILED` - Semantic search service unavailable
- `INVALID_MATURITY_LEVEL` - Maturity level not recognized
- `AUTHENTICATION_REQUIRED` - Missing Authorization header
- `INVALID_TOKEN` - Authentication token is invalid or expired
- `RATE_LIMIT_EXCEEDED` - Too many requests (429)

## Rate Limiting

- **Anonymous requests**: Not allowed
- **Authenticated requests**: 1000 requests/hour per user
- **Burst limit**: 100 requests/minute

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1699876543
```

## Examples

### Python

```python
import requests
import subprocess

def get_token():
    result = subprocess.run(
        ['gcloud', 'auth', 'print-identity-token'],
        capture_output=True, 
        text=True
    )
    return result.stdout.strip()

# Search for guides
token = get_token()
response = requests.post(
    'https://mcp-server-375955300575.us-central1.run.app/search',
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    json={
        'query': 'authentication OAuth',
        'top_k': 3
    }
)

guides = response.json()
for guide in guides['results']:
    print(f"{guide['title']} (score: {guide['score']:.2f})")
```

### JavaScript/TypeScript

```typescript
import { execSync } from 'child_process';

function getToken(): string {
  return execSync('gcloud auth print-identity-token')
    .toString()
    .trim();
}

async function searchGuides(query: string, topK: number = 5) {
  const token = getToken();
  
  const response = await fetch(
    'https://mcp-server-375955300575.us-central1.run.app/search',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query, top_k: topK })
    }
  );
  
  return await response.json();
}

// Usage
const results = await searchGuides('authentication OAuth', 3);
console.log(results);
```

### cURL

```bash
# Set token
export TOKEN=$(gcloud auth print-identity-token)

# List divisions
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/divisions

# Search guides
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "top_k": 3}' \
  https://mcp-server-375955300575.us-central1.run.app/search | jq

# Get guide content
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-server-375955300575.us-central1.run.app/guides/se/authentication-module---introduction-1/index.md | jq
```

## Best Practices

1. **Cache authentication tokens**: Tokens are valid for 1 hour
2. **Use semantic search**: More effective than exact string matching
3. **Filter by division**: Narrow results to relevant domain
4. **Respect rate limits**: Implement exponential backoff
5. **Handle errors gracefully**: Check HTTP status codes
6. **Use foundational guides**: They're boosted in search results
7. **Batch requests**: Combine multiple operations when possible

## Support

For issues or questions:
- **GitHub Issues**: [ys-requirements-list/issues](https://github.com/yousourcephinc/ys-requirements-list/issues)
- **Documentation**: [docs/](../docs/)
- **Troubleshooting**: [troubleshooting.md](troubleshooting.md)

---

**Last Updated**: November 13, 2025
