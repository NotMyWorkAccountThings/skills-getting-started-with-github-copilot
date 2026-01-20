"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Competitive soccer team with regular practices and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Basketball Team": {
            "description": "Inter-school basketball team and training sessions",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Art Club": {
            "description": "Drawing, painting, and mixed-media workshops",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Drama Club": {
            "description": "Theatre productions, acting classes, and stagecraft",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": []
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking practice",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Math Club": {
            "description": "Problem solving, puzzles, and math competition prep",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
    
    def test_participants_is_list(self, client):
        """Test that participants is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Soccer Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds participant to activity"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Soccer Team/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Soccer Team"]["participants"]
    
    def test_signup_duplicate_participant_fails(self, client):
        """Test that signing up twice fails"""
        email = "newstudent@mergington.edu"
        
        # First signup
        response1 = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup for nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_with_existing_participant(self, client):
        """Test that existing participant can be signed up for different activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Soccer Team"]["participants"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant"""
        email = "michael@mergington.edu"
        
        client.post(f"/activities/Chess Club/unregister?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregister for nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_non_participant_fails(self, client):
        """Test that unregistering a non-participant fails"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
