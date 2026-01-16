"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from src import app as app_module
    
    # Save original state
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
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu", "sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu"]
        },
        "Theater Production": {
            "description": "Perform in school plays and musicals",
            "schedule": "Thursdays and Saturdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["avery@mergington.edu", "jordan@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["grace@mergington.edu"]
        },
        "Science Lab": {
            "description": "Conduct experiments and explore advanced scientific concepts",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        }
    }
    
    # Reset activities
    app_module.activities.clear()
    app_module.activities.update(original_activities)
    
    yield
    
    # Cleanup (reset after test)
    app_module.activities.clear()
    app_module.activities.update(original_activities)


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_all_activities(self, client, reset_activities):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activity_structure(self, client, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_initial_participants(self, client, reset_activities):
        """Test that initial participants are present"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_duplicate_signup_rejected(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        # Try to sign up someone already registered
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signing up for a nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_updates_participants(self, client, reset_activities):
        """Test that signup actually adds participant to the list"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Gym Class"]["participants"])
        
        # Sign up
        client.post(
            "/activities/Gym Class/signup?email=newstudent@mergington.edu",
            follow_redirects=True
        )
        
        # Check updated count
        response = client.get("/activities")
        new_count = len(response.json()["Gym Class"]["participants"])
        assert new_count == initial_count + 1
        assert "newstudent@mergington.edu" in response.json()["Gym Class"]["participants"]


class TestUnregisterEndpoint:
    """Test the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client, reset_activities):
        """Test successfully unregistering from an activity"""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from a nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregistering someone not registered"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant from the list"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Unregister
        client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu",
            follow_redirects=True
        )
        
        # Check updated count
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1
        assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]


class TestSignupAndUnregisterFlow:
    """Test signup and unregister together"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        email = "testflow@mergington.edu"
        activity = "Programming Class"
        
        # Signup
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Verify in list
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}",
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Verify not in list
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
    
    def test_signup_unregister_signup_again(self, client, reset_activities):
        """Test signing up, unregistering, and signing up again"""
        email = "testflow2@mergington.edu"
        activity = "Basketball Team"
        
        # Signup
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}",
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Signup again (should work)
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            follow_redirects=True
        )
        assert response.status_code == 200
