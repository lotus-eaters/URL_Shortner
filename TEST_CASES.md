# URL Shortener - Test Cases Documentation

## Overview
This document outlines comprehensive test cases for the URL Shortener FastAPI application. Tests are organized by feature/module with detailed scenarios, expected outcomes, and implementation examples.

---

## Table of Contents
1. [User Management Tests](#user-management-tests)
2. [Authentication Tests](#authentication-tests)
3. [URL Shortening Tests](#url-shortening-tests)
4. [URL Redirect Tests](#url-redirect-tests)
5. [URL Statistics Tests](#url-statistics-tests)
6. [Authorization & Security Tests](#authorization--security-tests)
7. [Error Handling Tests](#error-handling-tests)
8. [Performance & Edge Case Tests](#performance--edge-case-tests)
9. [Integration Tests](#integration-tests)

---

## User Management Tests

### Test 1.1: Valid User Registration
**Description:** User successfully registers with valid credentials
**Pre-condition:** User doesn't exist in database
**Steps:**
1. POST `/api/auth/register`
2. Provide: `email`, `username`, `password` (min 8 chars)
3. Verify response

**Expected Result:**
```json
Status: 201 Created
{
  "id": "507f1f77bcf86cd799439011",
  "email": "test@example.com",
  "username": "testuser",
  "created_at": "2024-01-15T10:30:00"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_register_user_success(client, db):
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "securepass123"
    }
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"
    assert "id" in response.json()
```

---

### Test 1.2: Duplicate Email Registration
**Description:** Registration fails when email already exists
**Pre-condition:** User exists with email "test@example.com"
**Steps:**
1. POST `/api/auth/register`
2. Use existing email
3. Expect error response

**Expected Result:**
```json
Status: 400 Bad Request
{
  "detail": "Email already registered"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_register_duplicate_email(client, db, sample_user):
    user_data = {
        "email": sample_user["email"],
        "username": "anotheruser",
        "password": "securepass123"
    }
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]
```

---

### Test 1.3: Invalid Email Format
**Description:** Registration fails with invalid email
**Steps:**
1. POST `/api/auth/register`
2. Provide: `email`: "notanemail"
3. Expect validation error

**Expected Result:**
```json
Status: 422 Unprocessable Entity
{
  "detail": [{"type": "value_error.email"}]
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_register_invalid_email(client):
    user_data = {
        "email": "invalid-email",
        "username": "testuser",
        "password": "securepass123"
    }
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 422
```

---

### Test 1.4: Password Too Short
**Description:** Registration fails when password < 8 characters
**Steps:**
1. POST `/api/auth/register`
2. Provide: `password`: "short"
3. Expect validation error

**Expected Result:**
```json
Status: 400 Bad Request
{
  "detail": "Password must be at least 8 characters"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_register_short_password(client):
    user_data = {
        "email": "user@example.com",
        "username": "testuser",
        "password": "short"
    }
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400
    assert "8 characters" in response.json()["detail"]
```

---

### Test 1.5: Missing Required Fields
**Description:** Registration fails when required fields are missing
**Steps:**
1. POST `/api/auth/register`
2. Omit `username` field
3. Expect validation error

**Expected Result:**
```json
Status: 422 Unprocessable Entity
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_register_missing_fields(client):
    user_data = {
        "email": "user@example.com",
        # Missing username
        "password": "securepass123"
    }
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 422
```

---

## Authentication Tests

### Test 2.1: Valid Login
**Description:** User successfully logs in with correct credentials
**Pre-condition:** User exists in database
**Steps:**
1. POST `/api/auth/login`
2. Provide: `email`, `password`
3. Verify JWT token returned

**Expected Result:**
```json
Status: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "test@example.com",
    "username": "testuser",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_login_success(client, sample_user):
    login_data = {
        "email": sample_user["email"],
        "password": "demo_password"
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
```

---

### Test 2.2: Invalid Password
**Description:** Login fails with incorrect password
**Steps:**
1. POST `/api/auth/login`
2. Provide: correct email, wrong password
3. Expect error

**Expected Result:**
```json
Status: 401 Unauthorized
{
  "detail": "Invalid email or password"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_login_invalid_password(client, sample_user):
    login_data = {
        "email": sample_user["email"],
        "password": "wrongpassword"
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]
```

---

### Test 2.3: Non-existent User Login
**Description:** Login fails for non-existent user
**Steps:**
1. POST `/api/auth/login`
2. Use non-existent email
3. Expect error

**Expected Result:**
```json
Status: 401 Unauthorized
{
  "detail": "Invalid email or password"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    login_data = {
        "email": "nonexistent@example.com",
        "password": "anypassword"
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
```

---

### Test 2.4: Inactive User Cannot Login
**Description:** Login fails for deactivated users
**Pre-condition:** User marked as inactive
**Steps:**
1. POST `/api/auth/login`
2. Use inactive user credentials
3. Expect error

**Expected Result:**
```json
Status: 401 Unauthorized
{
  "detail": "User account is inactive"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_login_inactive_user(client, db, sample_user):
    # Deactivate user
    await db["users"].update_one(
        {"_id": ObjectId(sample_user["_id"])},
        {"$set": {"is_active": False}}
    )
    
    login_data = {
        "email": sample_user["email"],
        "password": "demo_password"
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert "inactive" in response.json()["detail"]
```

---

### Test 2.5: JWT Token Validation
**Description:** Valid token grants access to protected endpoints
**Steps:**
1. Login to get token
2. Use token in Authorization header
3. Access protected endpoint

**Expected Result:**
```json
Status: 200 OK
(endpoint-specific response)
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_jwt_token_valid(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.get("/api/auth/profile", headers=headers)
    assert response.status_code == 200
```

---

### Test 2.6: Invalid JWT Token
**Description:** Invalid token rejected for protected endpoints
**Steps:**
1. Use invalid/malformed token
2. Try to access protected endpoint
3. Expect 401 error

**Expected Result:**
```json
Status: 401 Unauthorized
{
  "detail": "Invalid authentication credentials"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_jwt_token_invalid(client):
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = await client.get("/api/auth/profile", headers=headers)
    assert response.status_code == 401
```

---

### Test 2.7: Missing Authorization Header
**Description:** Missing token denied access to protected endpoints
**Steps:**
1. Omit Authorization header
2. Try to access protected endpoint
3. Expect 403 error

**Expected Result:**
```json
Status: 403 Forbidden
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_missing_auth_header(client):
    response = await client.get("/api/auth/profile")
    assert response.status_code == 403
```

---

## URL Shortening Tests

### Test 3.1: Valid URL Shortening
**Description:** Successfully shorten a valid URL
**Pre-condition:** User authenticated
**Steps:**
1. POST `/api/urls/shorten`
2. Provide: `original_url`: "https://www.example.com/very/long/path"
3. Verify short code generated

**Expected Result:**
```json
Status: 201 Created
{
  "short_code": "abc123",
  "original_url": "https://www.example.com/very/long/path",
  "created_at": "2024-01-15T10:30:00",
  "url_id": "507f1f77bcf86cd799439012"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_shorten_url_success(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    url_data = {
        "original_url": "https://www.geeksforgeeks.org/system-design/"
    }
    response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
    assert response.status_code == 201
    assert "short_code" in response.json()
    assert response.json()["original_url"] == url_data["original_url"]
```

---

### Test 3.2: Invalid URL Format
**Description:** Shortening fails with invalid URL
**Steps:**
1. POST `/api/urls/shorten`
2. Provide: `original_url`: "not a valid url"
3. Expect error

**Expected Result:**
```json
Status: 400 Bad Request
{
  "detail": "Invalid URL format"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_shorten_invalid_url(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    url_data = {
        "original_url": "not a valid url"
    }
    response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
    assert response.status_code == 400
    assert "Invalid URL" in response.json()["detail"]
```

---

### Test 3.3: Custom Short Code
**Description:** User can provide custom short code
**Steps:**
1. POST `/api/urls/shorten`
2. Provide: `original_url`, `custom_alias`: "mycode"
3. Verify custom code used

**Expected Result:**
```json
Status: 201 Created
{
  "short_code": "mycode",
  ...
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_shorten_with_custom_alias(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    url_data = {
        "original_url": "https://www.example.com",
        "custom_alias": "mycustom"
    }
    response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
    assert response.status_code == 201
    assert response.json()["short_code"] == "mycustom"
```

---

### Test 3.4: Duplicate Short Code
**Description:** Cannot use already-taken short code
**Pre-condition:** Short code "abc123" already exists
**Steps:**
1. POST `/api/urls/shorten`
2. Provide: `custom_alias`: "abc123"
3. Expect error or retry with new code

**Expected Result:**
```json
Status: 400 Bad Request
{
  "detail": "Short code already exists"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_duplicate_short_code(client, auth_token, db, sample_url):
    headers = {"Authorization": f"Bearer {auth_token}"}
    url_data = {
        "original_url": "https://another.com",
        "custom_alias": sample_url["short_code"]
    }
    response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
    assert response.status_code == 400
```

---

### Test 3.5: URL with Expiration
**Description:** Shorten URL with custom expiration date
**Steps:**
1. POST `/api/urls/shorten`
2. Provide: `original_url`, `expires_at`: future timestamp
3. Verify expiration set

**Expected Result:**
```json
Status: 201 Created
{
  "short_code": "abc123",
  ...
  "expires_at": "2024-12-31T23:59:59"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_shorten_with_expiration(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    url_data = {
        "original_url": "https://www.example.com",
        "expires_at": future_date
    }
    response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
    assert response.status_code == 201
```

---

### Test 3.6: Unauthenticated URL Shortening
**Description:** Cannot shorten URL without authentication
**Steps:**
1. POST `/api/urls/shorten` (no token)
2. Expect error

**Expected Result:**
```json
Status: 401 Unauthorized
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_shorten_url_unauthenticated(client):
    url_data = {
        "original_url": "https://www.example.com"
    }
    response = await client.post("/api/urls/shorten", json=url_data)
    assert response.status_code == 401
```

---

## URL Redirect Tests

### Test 4.1: Valid Redirect
**Description:** Successfully redirect from short code to original URL
**Pre-condition:** Short code exists and is active
**Steps:**
1. GET `/api/urls/{short_code}`
2. Verify redirect response

**Expected Result:**
```
Status: 307 Temporary Redirect
Location: https://www.example.com/very/long/path
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_redirect_success(client, sample_url):
    response = await client.get(
        f"/api/urls/{sample_url['short_code']}",
        follow_redirects=False
    )
    assert response.status_code == 307
    assert response.headers["location"] == sample_url["original_url"]
```

---

### Test 4.2: Non-existent Short Code
**Description:** Redirect fails for non-existent short code
**Steps:**
1. GET `/api/urls/nonexistent`
2. Expect 404 error

**Expected Result:**
```json
Status: 404 Not Found
{
  "detail": "Short code not found"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_redirect_not_found(client):
    response = await client.get("/api/urls/nonexistent", follow_redirects=False)
    assert response.status_code == 404
```

---

### Test 4.3: Expired URL Redirect
**Description:** Cannot redirect to expired URL
**Pre-condition:** URL expiration date has passed
**Steps:**
1. GET `/api/urls/{expired_short_code}`
2. Expect 410 error

**Expected Result:**
```json
Status: 410 Gone
{
  "detail": "This URL has expired"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_redirect_expired_url(client, db, sample_url):
    # Set expiration to past
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    await db["urls"].update_one(
        {"short_code": sample_url["short_code"]},
        {"$set": {"expires_at": past_date}}
    )
    
    response = await client.get(
        f"/api/urls/{sample_url['short_code']}",
        follow_redirects=False
    )
    assert response.status_code == 410
    assert "expired" in response.json()["detail"]
```

---

### Test 4.4: Inactive URL Redirect
**Description:** Cannot redirect to deactivated URL
**Pre-condition:** URL marked as inactive
**Steps:**
1. GET `/api/urls/{inactive_short_code}`
2. Expect 404 error

**Expected Result:**
```json
Status: 404 Not Found
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_redirect_inactive_url(client, db, sample_url):
    # Deactivate URL
    await db["urls"].update_one(
        {"short_code": sample_url["short_code"]},
        {"$set": {"is_active": False}}
    )
    
    response = await client.get(
        f"/api/urls/{sample_url['short_code']}",
        follow_redirects=False
    )
    assert response.status_code == 404
```

---

### Test 4.5: Click Count Increment
**Description:** Click count increments on each redirect
**Pre-condition:** URL exists with click_count = 0
**Steps:**
1. GET `/api/urls/{short_code}` (first redirect)
2. GET `/api/urls/{short_code}` (second redirect)
3. GET `/api/urls/stats/{short_code}`
4. Verify click_count = 2

**Expected Result:**
```json
{
  "click_count": 2,
  ...
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_click_count_increment(client, sample_url):
    # First redirect
    await client.get(f"/api/urls/{sample_url['short_code']}", follow_redirects=False)
    # Second redirect
    await client.get(f"/api/urls/{sample_url['short_code']}", follow_redirects=False)
    
    # Check stats
    response = await client.get(f"/api/urls/stats/{sample_url['short_code']}")
    assert response.json()["click_count"] == 2
```

---

## URL Statistics Tests

### Test 5.1: Get URL Statistics
**Description:** Retrieve statistics for a shortened URL
**Steps:**
1. GET `/api/urls/stats/{short_code}`
2. Verify statistics returned

**Expected Result:**
```json
Status: 200 OK
{
  "short_code": "abc123",
  "original_url": "https://www.example.com",
  "click_count": 42,
  "created_at": "2024-01-15T10:30:00",
  "is_active": true
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_get_url_stats(client, sample_url):
    response = await client.get(f"/api/urls/stats/{sample_url['short_code']}")
    assert response.status_code == 200
    stats = response.json()
    assert stats["short_code"] == sample_url["short_code"]
    assert "click_count" in stats
    assert "created_at" in stats
```

---

### Test 5.2: Stats for Non-existent URL
**Description:** Getting stats for non-existent URL fails
**Steps:**
1. GET `/api/urls/stats/nonexistent`
2. Expect 404

**Expected Result:**
```json
Status: 404 Not Found
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_get_stats_not_found(client):
    response = await client.get("/api/urls/stats/nonexistent")
    assert response.status_code == 404
```

---

## Authorization & Security Tests

### Test 6.1: Cannot Access Others' URLs
**Description:** User cannot view statistics for URLs created by other users
**Pre-condition:** URL created by user2, accessing as user1
**Steps:**
1. User1 login
2. Try to access stats for user2's URL
3. Expect error

**Expected Result:**
```json
Status: 401/403 Unauthorized/Forbidden
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_cannot_access_others_urls(client, user1_token, user2_sample_url):
    headers = {"Authorization": f"Bearer {user1_token}"}
    response = await client.get(
        f"/api/urls/{user2_sample_url['url_id']}/details",
        headers=headers
    )
    # Depending on implementation: 403 or error message
    assert response.status_code >= 400
```

---

### Test 6.2: Can Delete Own URLs
**Description:** User can delete their own URLs
**Pre-condition:** URL created by user
**Steps:**
1. User login
2. DELETE `/api/urls/{url_id}`
3. Verify deletion

**Expected Result:**
```json
Status: 200 OK
{
  "message": "URL deleted successfully"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_delete_own_url(client, auth_token, sample_url):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.delete(f"/api/urls/{sample_url['url_id']}", headers=headers)
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]
```

---

### Test 6.3: Cannot Delete Others' URLs
**Description:** User cannot delete URLs created by others
**Steps:**
1. User1 login
2. Try to DELETE user2's URL
3. Expect error

**Expected Result:**
```json
Status: 403 Forbidden
{
  "detail": "Not authorized to delete this URL"
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_cannot_delete_others_urls(client, user1_token, user2_sample_url):
    headers = {"Authorization": f"Bearer {user1_token}"}
    response = await client.delete(
        f"/api/urls/{user2_sample_url['url_id']}",
        headers=headers
    )
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]
```

---

### Test 6.4: Password Security
**Description:** Passwords are hashed and not stored as plaintext
**Steps:**
1. Register user
2. Query database directly
3. Verify password is hashed

**Expected Result:**
```
Hashed password starts with "$2b$" (bcrypt format)
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_password_hashing(db, sample_user):
    user_doc = await db["users"].find_one({"_id": ObjectId(sample_user["_id"])})
    assert user_doc["hashed_password"].startswith("$2b$")
    assert user_doc["hashed_password"] != "demo_password"
```

---

### Test 6.5: SQL Injection Prevention
**Description:** SQL/NoSQL injection attempts are safely handled
**Steps:**
1. Try to inject malicious code in email field
2. Verify it's treated as literal string

**Expected Result:**
```
No injection, treated as invalid email or user not found
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_injection_prevention(client):
    login_data = {
        "email": "admin@example.com'; DROP TABLE users; --",
        "password": "anypassword"
    }
    response = await client.post("/api/auth/login", json=login_data)
    # Should fail with 401, not cause database damage
    assert response.status_code == 401
```

---

## Error Handling Tests

### Test 7.1: Database Connection Error
**Description:** Graceful error handling when database is unavailable
**Pre-condition:** Database connection fails
**Steps:**
1. Make request with DB down
2. Expect error response

**Expected Result:**
```json
Status: 500 Internal Server Error
{
  "detail": "Database connection failed" (or generic error)
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_database_error_handling(client, monkeypatch):
    # Mock database failure
    async def mock_connect(*args, **kwargs):
        raise Exception("Connection refused")
    
    # Apply mock and test
    response = await client.post("/api/auth/register", json={...})
    assert response.status_code == 500
```

---

### Test 7.2: Redis Connection Error
**Description:** App continues working if Redis (cache) is unavailable
**Pre-condition:** Redis connection fails
**Steps:**
1. Try to shorten URL
2. URL should still be created (just without cache)

**Expected Result:**
```json
Status: 201 Created
(URL shortened successfully without cache)
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_redis_unavailable_graceful_fallback(client, auth_token):
    # Simulate Redis failure
    headers = {"Authorization": f"Bearer {auth_token}"}
    url_data = {"original_url": "https://www.example.com"}
    
    # Should still work (warning logged but operation succeeds)
    response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
    assert response.status_code == 201
```

---

### Test 7.3: Invalid Request Format
**Description:** Proper validation of request format
**Steps:**
1. POST with malformed JSON
2. Expect validation error

**Expected Result:**
```json
Status: 422 Unprocessable Entity
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_invalid_json_format(client):
    response = await client.post(
        "/api/auth/register",
        data="invalid json{",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
```

---

### Test 7.4: Rate Limiting (Future)
**Description:** API enforces rate limits to prevent abuse
**Steps:**
1. Make 100+ requests in short time
2. Expect 429 error

**Expected Result:**
```json
Status: 429 Too Many Requests
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_rate_limiting(client):
    for _ in range(101):
        response = await client.get("/health")
    
    # 101st request should be rate limited
    response = await client.get("/health")
    assert response.status_code == 429
```

---

## Performance & Edge Case Tests

### Test 8.1: Very Long URL
**Description:** Handle extremely long URLs (up to URL length limits)
**Steps:**
1. Create URL with 2000+ characters
2. Verify it's shortened correctly

**Expected Result:**
```json
Status: 201 Created
(Successfully shortened)
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_very_long_url(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    long_url = "https://www.example.com/" + "a" * 2000
    url_data = {"original_url": long_url}
    
    response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
    assert response.status_code == 201
    # Verify original URL is preserved
    assert response.json()["original_url"] == long_url
```

---

### Test 8.2: Special Characters in URL
**Description:** Handle URLs with special characters and unicode
**Steps:**
1. Shorten URL with special chars: `?`, `&`, `#`, `%20`, etc.
2. Redirect and verify original URL returned

**Expected Result:**
```
Characters preserved correctly
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_special_characters_in_url(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    special_url = "https://www.example.com/search?q=hello%20world&lang=en#results"
    url_data = {"original_url": special_url}
    
    response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
    assert response.status_code == 201
    assert response.json()["original_url"] == special_url
```

---

### Test 8.3: Concurrent Requests
**Description:** Handle multiple simultaneous requests correctly
**Steps:**
1. Launch 10 concurrent URL shortening requests
2. Verify all succeed with unique short codes

**Expected Result:**
```
All requests succeed with different short codes
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_concurrent_url_shortening(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    async def shorten_url(index):
        url_data = {"original_url": f"https://www.example.com/{index}"}
        return await client.post("/api/urls/shorten", json=url_data, headers=headers)
    
    # Create 10 concurrent requests
    tasks = [shorten_url(i) for i in range(10)]
    responses = await asyncio.gather(*tasks)
    
    # All should succeed
    short_codes = [r.json()["short_code"] for r in responses if r.status_code == 201]
    assert len(short_codes) == 10
    # All unique
    assert len(set(short_codes)) == 10
```

---

### Test 8.4: Cache Behavior
**Description:** Cache hits work correctly and don't affect correctness
**Steps:**
1. Redirect to URL (cache miss)
2. Redirect again (cache hit)
3. Verify both return same URL

**Expected Result:**
```
Both redirects succeed with same URL
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_cache_behavior(client, sample_url):
    # First access (cache miss)
    response1 = await client.get(
        f"/api/urls/{sample_url['short_code']}",
        follow_redirects=False
    )
    
    # Second access (cache hit)
    response2 = await client.get(
        f"/api/urls/{sample_url['short_code']}",
        follow_redirects=False
    )
    
    assert response1.headers["location"] == response2.headers["location"]
```

---

### Test 8.5: Empty Result Pagination
**Description:** Pagination works correctly with empty results
**Steps:**
1. GET `/api/urls/user/list?skip=1000`
2. Verify empty response

**Expected Result:**
```json
Status: 200 OK
{
  "total": 5,
  "urls": [],
  "skip": 1000
}
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_pagination_empty_results(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.get(
        "/api/urls/user/list?skip=1000&limit=50",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["urls"] == []
```

---

## Integration Tests

### Test 9.1: Complete User Journey
**Description:** Test full workflow: Register → Login → Shorten URL → Redirect → View Stats
**Steps:**
1. Register new user
2. Login to get token
3. Shorten a URL
4. Redirect via short code (verify increment)
5. Get statistics

**Expected Result:**
```
All steps succeed; click count incremented
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_complete_user_journey(client):
    # 1. Register
    register_data = {
        "email": "journey@example.com",
        "username": "journeyuser",
        "password": "testpass123"
    }
    reg_response = await client.post("/api/auth/register", json=register_data)
    assert reg_response.status_code == 201
    
    # 2. Login
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    login_response = await client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 3. Shorten URL
    headers = {"Authorization": f"Bearer {token}"}
    url_data = {"original_url": "https://www.example.com/long/path"}
    shorten_response = await client.post(
        "/api/urls/shorten",
        json=url_data,
        headers=headers
    )
    assert shorten_response.status_code == 201
    short_code = shorten_response.json()["short_code"]
    
    # 4. Redirect
    redirect_response = await client.get(
        f"/api/urls/{short_code}",
        follow_redirects=False
    )
    assert redirect_response.status_code == 307
    
    # 5. Get stats
    stats_response = await client.get(f"/api/urls/stats/{short_code}")
    assert stats_response.status_code == 200
    assert stats_response.json()["click_count"] >= 1
```

---

### Test 9.2: Multiple Users Interaction
**Description:** Test isolation between different users
**Steps:**
1. Create 2 users
2. Each shortens different URLs
3. Verify users can only see their own URLs

**Expected Result:**
```
Each user only sees their URLs
```

**Test Code:**
```python
@pytest.mark.asyncio
async def test_multi_user_isolation(client):
    # Register and login user1
    user1_register = {
        "email": "user1@example.com",
        "username": "user1",
        "password": "pass123user1"
    }
    await client.post("/api/auth/register", json=user1_register)
    user1_login = await client.post("/api/auth/login", json={
        "email": user1_register["email"],
        "password": user1_register["password"]
    })
    user1_token = user1_login.json()["access_token"]
    
    # Register and login user2
    user2_register = {
        "email": "user2@example.com",
        "username": "user2",
        "password": "pass123user2"
    }
    await client.post("/api/auth/register", json=user2_register)
    user2_login = await client.post("/api/auth/login", json={
        "email": user2_register["email"],
        "password": user2_register["password"]
    })
    user2_token = user2_login.json()["access_token"]
    
    # User1 shortens URL
    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    user1_shorten = await client.post(
        "/api/urls/shorten",
        json={"original_url": "https://user1.com"},
        headers=user1_headers
    )
    user1_code = user1_shorten.json()["short_code"]
    
    # User2 shortens URL
    user2_headers = {"Authorization": f"Bearer {user2_token}"}
    user2_shorten = await client.post(
        "/api/urls/shorten",
        json={"original_url": "https://user2.com"},
        headers=user2_headers
    )
    user2_code = user2_shorten.json()["short_code"]
    
    # User1 lists their URLs (should only see user1's URL)
    user1_list = await client.get("/api/urls/user/list", headers=user1_headers)
    user1_urls = user1_list.json()["urls"]
    assert any(u["short_code"] == user1_code for u in user1_urls)
    assert not any(u["short_code"] == user2_code for u in user1_urls)
```

---

## Test Fixtures Setup

### Recommended Conftest.py

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone
from bson import ObjectId
from app.main import app
from app.core.database import get_mongodb, connect_db, close_db

@pytest.fixture
async def client():
    """Async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def db():
    """MongoDB connection for tests"""
    await connect_db()
    db = get_mongodb()
    
    # Clear collections before test
    await db["users"].delete_many({})
    await db["urls"].delete_many({})
    
    yield db
    
    # Cleanup
    await db["users"].delete_many({})
    await db["urls"].delete_many({})
    await close_db()

@pytest.fixture
async def sample_user(client, db):
    """Create a sample user for testing"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "demo_password"
    }
    response = await client.post("/api/auth/register", json=user_data)
    user = response.json()
    
    # Get actual user document with hashed password
    user_doc = await db["users"].find_one({"email": user_data["email"]})
    return {**user, **user_doc}

@pytest.fixture
async def auth_token(client, sample_user):
    """Get authentication token for sample user"""
    response = await client.post("/api/auth/login", json={
        "email": sample_user["email"],
        "password": "demo_password"
    })
    return response.json()["access_token"]

@pytest.fixture
async def sample_url(client, db, auth_token, sample_user):
    """Create a sample shortened URL"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    url_data = {
        "original_url": "https://www.geeksforgeeks.org/system-design/"
    }
    response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
    url = response.json()
    
    # Get actual document
    url_doc = await db["urls"].find_one({"short_code": url["short_code"]})
    return {**url, **url_doc}
```

---

## Running Tests

### Command Lines

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_register_user_success

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# Run async tests only
pytest tests/ -m asyncio

# Run with print statements
pytest tests/ -s

# Run and stop on first failure
pytest tests/ -x

# Run last failed tests
pytest tests/ --lf

# Generate test report
pytest tests/ --html=report.html --self-contained-html
```

---

## Test Coverage Goals

| Module | Target Coverage | Current |
|--------|------------------|---------|
| auth routes | 95% | - |
| url routes | 90% | - |
| user service | 90% | - |
| url service | 90% | - |
| repositories | 85% | - |
| utils | 80% | - |
| **Overall** | **90%** | - |

---

## Notes

- All tests should be async (`@pytest.mark.asyncio`)
- Use fixtures for common setup
- Mock external services (Redis, Mail)
- Test both happy path and error cases
- Include edge cases
- Keep tests isolated and independent
- Use meaningful test names
- Add docstrings to complex tests
