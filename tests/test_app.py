import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestActivities:
    """Test suite for activities endpoints"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_root_redirect(self):
        """Test that root redirects to static page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignup:
    """Test suite for signup functionality"""

    def test_signup_successful(self):
        """Test successful signup for an activity"""
        email = "test@example.com"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_signup_duplicate_email(self):
        """Test that signing up with duplicate email fails"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signup for non-existent activity"""
        email = "test@example.com"
        activity = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_adds_participant(self):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        activity = "Art Club"
        
        # Get initial participant count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity]["participants"])
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
        )
        assert response.status_code == 200
        
        # Verify participant was added
        response_after = client.get("/activities")
        final_count = len(response_after.json()[activity]["participants"])
        assert final_count == initial_count + 1
        assert email in response_after.json()[activity]["participants"]


class TestUnregister:
    """Test suite for unregister functionality"""

    def test_unregister_successful(self):
        """Test successful unregister from an activity"""
        email = "henry@mergington.edu"
        activity = "Drama Society"
        
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}",
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_not_registered(self):
        """Test unregistering someone not signed up fails"""
        email = "notregistered@example.com"
        activity = "Drama Society"
        
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}",
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregister from non-existent activity"""
        email = "test@example.com"
        activity = "Nonexistent Activity"
        
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}",
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        # First sign up a test user
        email = "unregister_test@mergington.edu"
        activity = "Science Club"
        
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get participant count before unregister
        response_before = client.get("/activities")
        before_count = len(response_before.json()[activity]["participants"])
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}",
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        response_after = client.get("/activities")
        after_count = len(response_after.json()[activity]["participants"])
        assert after_count == before_count - 1
        assert email not in response_after.json()[activity]["participants"]
