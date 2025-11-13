# Testing Guide

Guide for running and writing tests for the Implementation Guides MCP server.

## Overview

The test suite covers:
- REST API endpoints
- MCP protocol handlers
- Notion synchronization
- Semantic search functionality
- Guide content retrieval

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Or with uv
uv pip install pytest pytest-cov pytest-mock
```

### Run All Tests

```bash
# From repository root
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=mcp --cov=scripts --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Specific Tests

```bash
# Single test file
pytest tests/test_guides_api.py

# Single test function
pytest tests/test_guides_api.py::test_list_divisions

# Tests matching pattern
pytest -k "search"

# Tests by marker
pytest -m "integration"
```

### Test Options

```bash
# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Disable output capture (see print statements)
pytest -s

# Run in parallel (requires pytest-xdist)
pytest -n auto
```

## Test Files

### test_guides_api.py

Tests REST API endpoints.

**Coverage**:
- `GET /` - Health check
- `GET /divisions` - List divisions
- `GET /divisions/{division}/guides` - List guides by division
- `GET /guides/{path}` - Get guide content
- `POST /search` - Semantic search
- `POST /recommendations` - Get recommendations

**Example**:
```python
def test_list_divisions(client):
    """Test listing all divisions."""
    response = client.get('/divisions')
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) == 4
    divisions = [d['name'] for d in data]
    assert 'se' in divisions
    assert 'exd' in divisions
```

**Run**:
```bash
pytest tests/test_guides_api.py -v
```

### test_guides_mcp.py

Tests MCP protocol handlers.

**Coverage**:
- Tool registration
- `list_guide_divisions` tool
- `list_guides_by_division` tool
- `get_guide_content` tool
- `search_guides` tool
- `get_guide_recommendations` tool

**Example**:
```python
def test_search_guides_tool(mcp_client):
    """Test search_guides MCP tool."""
    result = mcp_client.call_tool(
        "search_guides",
        {"query": "authentication", "top_k": 5}
    )
    assert "results" in result
    assert len(result["results"]) <= 5
```

**Run**:
```bash
pytest tests/test_guides_mcp.py -v
```

### test_notion_connection.py

Tests Notion API integration.

**Coverage**:
- Notion API authentication
- Database query
- Page retrieval
- Content conversion

**Example**:
```python
def test_notion_connection():
    """Test connection to Notion API."""
    from scripts.sync_notion import get_notion_client
    
    client = get_notion_client()
    user = client.users.me()
    assert user is not None
```

**Run**:
```bash
# Requires NOTION_API_KEY
export NOTION_API_KEY=your_key
pytest tests/test_notion_connection.py -v
```

### test_semantic_search.py

Tests semantic search functionality.

**Coverage**:
- Embedding generation
- Vector similarity search
- Division filtering
- Maturity filtering
- Foundational guide boosting

**Example**:
```python
def test_semantic_search():
    """Test semantic search."""
    from scripts.vector_search import search_guides
    
    results = search_guides("authentication", top_k=5)
    assert len(results) <= 5
    assert all('score' in r for r in results)
    assert all(r['score'] >= 0 and r['score'] <= 1 for r in results)
```

**Run**:
```bash
# Requires GCP authentication
gcloud auth application-default login
pytest tests/test_semantic_search.py -v
```

## Writing Tests

### Test Structure

```python
import pytest
from flask import Flask

# Fixtures
@pytest.fixture
def client():
    """Create test client."""
    from mcp.guides_mcp_http_server import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test function
def test_endpoint(client):
    """Test description."""
    # Arrange
    expected_status = 200
    
    # Act
    response = client.get('/endpoint')
    
    # Assert
    assert response.status_code == expected_status
```

### Common Fixtures

```python
# Client fixture
@pytest.fixture
def client():
    """Flask test client."""
    from mcp.guides_mcp_http_server import app
    with app.test_client() as client:
        yield client

# Auth token fixture
@pytest.fixture
def auth_token():
    """Get valid auth token."""
    import subprocess
    result = subprocess.run(
        ['gcloud', 'auth', 'print-identity-token'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

# Mock Firestore fixture
@pytest.fixture
def mock_firestore(monkeypatch):
    """Mock Firestore client."""
    class MockClient:
        def collection(self, name):
            return MockCollection()
    
    monkeypatch.setattr(
        'google.cloud.firestore.Client',
        MockClient
    )
```

### Testing API Endpoints

```python
def test_list_divisions(client):
    """Test GET /divisions."""
    response = client.get('/divisions')
    
    # Check status
    assert response.status_code == 200
    
    # Check response type
    assert response.content_type == 'application/json'
    
    # Check data structure
    data = response.json
    assert isinstance(data, list)
    assert all('name' in d for d in data)
    assert all('guide_count' in d for d in data)
```

### Testing MCP Tools

```python
def test_mcp_tool(mcp_server):
    """Test MCP tool invocation."""
    result = mcp_server.call_tool(
        "tool_name",
        {"param": "value"}
    )
    
    # Check result structure
    assert isinstance(result, dict)
    assert "key" in result
    
    # Check result values
    assert result["key"] == expected_value
```

### Testing Search Functionality

```python
def test_search():
    """Test semantic search."""
    from scripts.vector_search import search_guides
    
    # Basic search
    results = search_guides("query", top_k=5)
    assert len(results) <= 5
    
    # Check scores
    scores = [r['score'] for r in results]
    assert all(s >= 0 and s <= 1 for s in scores)
    assert scores == sorted(scores, reverse=True)  # Descending
    
    # With filters
    results = search_guides(
        "query",
        division="se",
        maturity_level="introduction-1",
        top_k=10
    )
    assert all(r['division'] == 'se' for r in results)
    assert all(r['maturity'] == 'introduction-1' for r in results)
```

### Testing Error Handling

```python
def test_error_handling(client):
    """Test error responses."""
    # Test 404
    response = client.get('/guides/nonexistent/path')
    assert response.status_code == 404
    assert 'error' in response.json
    
    # Test 400
    response = client.post('/search', json={})
    assert response.status_code == 400
    
    # Test 401
    response = client.get('/divisions')  # without auth
    assert response.status_code == 401
```

### Mocking External Services

```python
def test_with_mock_firestore(monkeypatch):
    """Test with mocked Firestore."""
    class MockCollection:
        def stream(self):
            return [
                MockDoc('doc1', {'title': 'Test Guide 1'}),
                MockDoc('doc2', {'title': 'Test Guide 2'})
            ]
    
    class MockDB:
        def collection(self, name):
            return MockCollection()
    
    monkeypatch.setattr(
        'google.cloud.firestore.Client',
        lambda **kwargs: MockDB()
    )
    
    # Test code that uses Firestore
    from mcp.guides_mcp_http_server import do_list_guide_divisions
    divisions = do_list_guide_divisions()
    assert len(divisions) > 0
```

## Test Markers

Use markers to categorize tests:

```python
# Mark as integration test
@pytest.mark.integration
def test_firestore_connection():
    """Test real Firestore connection."""
    pass

# Mark as slow test
@pytest.mark.slow
def test_full_sync():
    """Test full Notion sync."""
    pass

# Mark as requiring API key
@pytest.mark.requires_notion
def test_notion_api():
    """Test Notion API."""
    pass
```

Run specific markers:
```bash
# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run tests requiring Notion
pytest -m requires_notion
```

## Coverage Goals

Target coverage by module:

- **mcp/**: 80%+ coverage
- **scripts/**: 70%+ coverage
- **Overall**: 75%+ coverage

Check coverage:
```bash
pytest --cov=mcp --cov=scripts --cov-report=term-missing
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Scheduled daily builds

### GitHub Actions

See `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest --cov=mcp --cov=scripts
      - run: codecov  # Upload coverage
```

## Best Practices

1. **Test naming**: Use descriptive names starting with `test_`
2. **One assertion**: Test one thing per test function
3. **Arrange-Act-Assert**: Clear test structure
4. **Use fixtures**: Share common setup code
5. **Mock external services**: Don't rely on external APIs in tests
6. **Test edge cases**: Include error cases and boundaries
7. **Keep tests fast**: Mock slow operations
8. **Document tests**: Add docstrings explaining what's tested
9. **Run before commit**: Ensure tests pass locally
10. **Update tests**: Keep tests in sync with code changes

## Debugging Tests

### Run Single Test with Debugging

```bash
# With pdb
pytest tests/test_file.py::test_function --pdb

# With print statements
pytest tests/test_file.py::test_function -s

# With full traceback
pytest tests/test_file.py::test_function --tb=long
```

### VS Code Debugging

Add to `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "tests/",
        "-v"
      ],
      "console": "integratedTerminal"
    }
  ]
}
```

## Related Documentation

- [Local Development Guide](local-development.md)
- [API Reference](api-reference.md)
- [Scripts Documentation](scripts.md)
- [Troubleshooting](troubleshooting.md)

---

**Last Updated**: November 13, 2025
