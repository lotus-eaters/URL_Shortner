"""
Comprehensive test suite for URL Shortener API
Tests cover: authentication, URL shortening, redirects, authorization, and error handling
"""

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from httpx import AsyncClient

from app.main import app
from app.core.database import get_mongodb, connect_db, close_db
from app.models.models import User, URL
from app.utils.security import SecurityUtils


# ==================== FIXTURES ====================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


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
        "password": "demo_password123"
    }
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    user = response.json()
    
    # Get actual user document
    user_doc = await db["users"].find_one({"email": user_data["email"]})
    return {**user, "_id": str(user_doc["_id"]), **user_doc}


@pytest.fixture
async def auth_token(client, sample_user):
    """Get authentication token for sample user"""
    response = await client.post("/api/auth/login", json={
        "email": sample_user["email"],
        "password": "demo_password123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def sample_url(client, db, auth_token):
    """Create a sample shortened URL"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    url_data = {
        "original_url": "https://www.geeksforgeeks.org/system-design-url-shortening/"
    }
    response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
    assert response.status_code == 201
    url = response.json()
    
    # Get actual document
    url_doc = await db["urls"].find_one({"short_code": url["short_code"]})
    return {**url, **url_doc}


# ==================== USER REGISTRATION TESTS ====================

class TestUserRegistration:
    """Test cases for user registration"""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, client, db):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepass123"
        }
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, sample_user):
        """Test registration fails with duplicate email"""
        user_data = {
            "email": sample_user["email"],
            "username": "anotheruser",
            "password": "securepass123"
        }
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """Test registration fails with invalid email"""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "securepass123"
        }
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_short_password(self, client):
        """Test registration fails with short password"""
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "short"
        }
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "8 characters" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client):
        """Test registration fails with missing fields"""
        user_data = {
            "email": "user@example.com",
            # Missing username
            "password": "securepass123"
        }
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422


# ==================== USER AUTHENTICATION TESTS ====================

class TestUserAuthentication:
    """Test cases for user authentication"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client, sample_user):
        """Test successful login"""
        login_data = {
            "email": sample_user["email"],
            "password": "demo_password123"
        }
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == sample_user["email"]
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client, sample_user):
        """Test login fails with wrong password"""
        login_data = {
            "email": sample_user["email"],
            "password": "wrongpassword"
        }
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        """Test login fails for non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client, db, sample_user):
        """Test login fails for inactive user"""
        # Deactivate user
        await db["users"].update_one(
            {"_id": ObjectId(sample_user["_id"])},
            {"$set": {"is_active": False}}
        )
        
        login_data = {
            "email": sample_user["email"],
            "password": "demo_password123"
        }
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "inactive" in response.json()["detail"]


# ==================== JWT TOKEN TESTS ====================

class TestJWTToken:
    """Test cases for JWT token handling"""
    
    @pytest.mark.asyncio
    async def test_jwt_token_valid(self, client, auth_token):
        """Test valid token grants access to protected endpoints"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_jwt_token_invalid(self, client):
        """Test invalid token rejected"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_missing_auth_header(self, client):
        """Test missing token denied access"""
        response = await client.get("/api/auth/profile")
        
        assert response.status_code == 403


# ==================== URL SHORTENING TESTS ====================

class TestURLShortening:
    """Test cases for URL shortening"""
    
    @pytest.mark.asyncio
    async def test_shorten_url_success(self, client, auth_token):
        """Test successful URL shortening"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        url_data = {
            "original_url": "https://www.example.com/very/long/path"
        }
        response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "short_code" in data
        assert data["original_url"] == url_data["original_url"]
        assert "url_id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_shorten_invalid_url(self, client, auth_token):
        """Test shortening invalid URL fails"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        url_data = {
            "original_url": "not a valid url"
        }
        response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
        
        assert response.status_code == 400
        assert "Invalid URL" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_shorten_with_custom_alias(self, client, auth_token):
        """Test shortening with custom short code"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        url_data = {
            "original_url": "https://www.example.com",
            "custom_alias": "mycustom"
        }
        response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
        
        assert response.status_code == 201
        assert response.json()["short_code"] == "mycustom"
    
    @pytest.mark.asyncio
    async def test_duplicate_short_code(self, client, db, auth_token, sample_url):
        """Test cannot use duplicate short code"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        url_data = {
            "original_url": "https://another.com",
            "custom_alias": sample_url["short_code"]
        }
        response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_shorten_with_expiration(self, client, auth_token):
        """Test shortening URL with custom expiration"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        url_data = {
            "original_url": "https://www.example.com",
            "expires_at": future_date
        }
        response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
        
        assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_shorten_unauthenticated(self, client):
        """Test cannot shorten without authentication"""
        url_data = {
            "original_url": "https://www.example.com"
        }
        response = await client.post("/api/urls/shorten", json=url_data)
        
        assert response.status_code == 401


# ==================== URL REDIRECT TESTS ====================

class TestURLRedirect:
    """Test cases for URL redirection"""
    
    @pytest.mark.asyncio
    async def test_redirect_success(self, client, sample_url):
        """Test successful redirect"""
        response = await client.get(
            f"/api/urls/{sample_url['short_code']}",
            follow_redirects=False
        )
        
        assert response.status_code == 307
        assert response.headers["location"] == sample_url["original_url"]
    
    @pytest.mark.asyncio
    async def test_redirect_not_found(self, client):
        """Test redirect fails for non-existent code"""
        response = await client.get(
            "/api/urls/nonexistent",
            follow_redirects=False
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_redirect_expired_url(self, client, db, sample_url):
        """Test cannot redirect to expired URL"""
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
    
    @pytest.mark.asyncio
    async def test_redirect_inactive_url(self, client, db, sample_url):
        """Test cannot redirect to inactive URL"""
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


# ==================== CLICK COUNT TESTS ====================

class TestClickCount:
    """Test cases for click count tracking"""
    
    @pytest.mark.asyncio
    async def test_click_count_increment(self, client, sample_url):
        """Test click count increments on redirects"""
        # First redirect
        await client.get(
            f"/api/urls/{sample_url['short_code']}",
            follow_redirects=False
        )
        
        # Second redirect
        await client.get(
            f"/api/urls/{sample_url['short_code']}",
            follow_redirects=False
        )
        
        # Check stats
        response = await client.get(f"/api/urls/stats/{sample_url['short_code']}")
        
        assert response.status_code == 200
        assert response.json()["click_count"] >= 2


# ==================== URL STATISTICS TESTS ====================

class TestURLStatistics:
    """Test cases for URL statistics"""
    
    @pytest.mark.asyncio
    async def test_get_url_stats(self, client, sample_url):
        """Test retrieving URL statistics"""
        response = await client.get(f"/api/urls/stats/{sample_url['short_code']}")
        
        assert response.status_code == 200
        stats = response.json()
        assert stats["short_code"] == sample_url["short_code"]
        assert "click_count" in stats
        assert "created_at" in stats
        assert "is_active" in stats
    
    @pytest.mark.asyncio
    async def test_get_stats_not_found(self, client):
        """Test getting stats for non-existent URL"""
        response = await client.get("/api/urls/stats/nonexistent")
        
        assert response.status_code == 404


# ==================== SECURITY & AUTHORIZATION TESTS ====================

class TestSecurity:
    """Test cases for security and authorization"""
    
    @pytest.mark.asyncio
    async def test_password_hashing(self, db, sample_user):
        """Test passwords are hashed"""
        user_doc = await db["users"].find_one({"_id": ObjectId(sample_user["_id"])})
        
        assert user_doc["hashed_password"].startswith("$2b$")
        assert user_doc["hashed_password"] != "demo_password123"
    
    @pytest.mark.asyncio
    async def test_injection_prevention(self, client):
        """Test SQL/NoSQL injection prevention"""
        login_data = {
            "email": "admin@example.com'; DROP TABLE users; --",
            "password": "anypassword"
        }
        response = await client.post("/api/auth/login", json=login_data)
        
        # Should fail gracefully, not cause damage
        assert response.status_code == 401


# ==================== EDGE CASE TESTS ====================

class TestEdgeCases:
    """Test cases for edge cases and performance"""
    
    @pytest.mark.asyncio
    async def test_very_long_url(self, client, auth_token):
        """Test handling very long URLs"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        long_url = "https://www.example.com/" + "a" * 2000
        url_data = {"original_url": long_url}
        
        response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
        
        assert response.status_code == 201
        assert response.json()["original_url"] == long_url
    
    @pytest.mark.asyncio
    async def test_special_characters_in_url(self, client, auth_token):
        """Test handling special characters in URLs"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        special_url = "https://www.example.com/search?q=hello%20world&lang=en#results"
        url_data = {"original_url": special_url}
        
        response = await client.post("/api/urls/shorten", json=url_data, headers=headers)
        
        assert response.status_code == 201
        assert response.json()["original_url"] == special_url
    
    @pytest.mark.asyncio
    async def test_concurrent_url_shortening(self, client, auth_token):
        """Test handling concurrent requests"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def shorten_url(index):
            url_data = {"original_url": f"https://www.example.com/test{index}"}
            return await client.post("/api/urls/shorten", json=url_data, headers=headers)
        
        # Create concurrent requests
        tasks = [shorten_url(i) for i in range(10)]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        short_codes = [r.json()["short_code"] for r in responses if r.status_code == 201]
        assert len(short_codes) == 10
        # All unique
        assert len(set(short_codes)) == 10


# ==================== HEALTH CHECK TEST ====================

class TestHealthCheck:
    """Test cases for health check endpoint"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
