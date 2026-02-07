#!/usr/bin/env python3
"""
Backend API Testing for Research Paper Discovery System
Tests all CRUD operations, authentication, and paper management features
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class ResearchAPITester:
    def __init__(self, base_url="https://arxiv-hub.preview.emergentagent.com"):
        """Initialize tester with base URL (production endpoint)"""
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    expected_status: int = 200) -> tuple[bool, Dict]:
        """Make HTTP request and validate response"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text, "status_code": response.status_code}
            
            if not success:
                response_data["expected_status"] = expected_status
                response_data["actual_status"] = response.status_code
            
            return success, response_data

        except Exception as e:
            return False, {"error": str(e)}

    def test_health_check(self):
        """Test API health endpoint"""
        success, response = self.make_request('GET', '/api/health')
        
        if success and response.get('status') == 'healthy':
            self.log_result("Health Check", True, f"Neo4j: {response.get('neo4j')}, DB: {response.get('database')}")
        else:
            self.log_result("Health Check", False, f"Response: {response}")

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"testuser_{timestamp}@example.com",
            "username": f"testuser_{timestamp}",
            "password": "testpass123",
            "full_name": f"Test User {timestamp}"
        }
        
        success, response = self.make_request('POST', '/api/auth/register', user_data)
        
        if success and response.get('access_token'):
            self.token = response['access_token']
            self.user_id = response['user']['id']
            self.log_result("User Registration", True, f"User ID: {self.user_id}")
        else:
            self.log_result("User Registration", False, f"Response: {response}")

    def test_user_login(self):
        """Test user login with existing test user"""
        login_data = {
            "email": "test@arxiv.com",
            "password": "test123456"
        }
        
        success, response = self.make_request('POST', '/api/auth/login', login_data)
        
        if success and response.get('access_token'):
            self.token = response['access_token']
            self.user_id = response['user']['id']
            self.log_result("User Login", True, f"User: {response['user']['username']}")
        else:
            self.log_result("User Login", False, f"Response: {response}")

    def test_get_current_user(self):
        """Test getting current user info"""
        if not self.token:
            self.log_result("Get Current User", False, "No auth token available")
            return
            
        success, response = self.make_request('GET', '/api/auth/me')
        
        if success and response.get('id'):
            self.log_result("Get Current User", True, f"User: {response.get('username')}")
        else:
            self.log_result("Get Current User", False, f"Response: {response}")

    def test_get_interests(self):
        """Test getting available interests"""
        success, response = self.make_request('GET', '/api/users/interests')
        
        if success and isinstance(response, list) and len(response) > 0:
            self.log_result("Get Interests", True, f"Found {len(response)} interests")
            return response
        else:
            self.log_result("Get Interests", False, f"Response: {response}")
            return []

    def test_update_user_interests(self, interests):
        """Test updating user interests"""
        if not self.token or not interests:
            self.log_result("Update User Interests", False, "No auth token or interests available")
            return
            
        # Select first 3 interests
        interest_ids = [interest['id'] for interest in interests[:3]]
        data = {"interest_ids": interest_ids}
        
        success, response = self.make_request('POST', '/api/users/interests', data)
        
        if success and response.get('has_completed_onboarding'):
            self.log_result("Update User Interests", True, f"Selected {len(interest_ids)} interests")
        else:
            self.log_result("Update User Interests", False, f"Response: {response}")

    def test_browse_papers(self):
        """Test browsing papers"""
        if not self.token:
            self.log_result("Browse Papers", False, "No auth token available")
            return []
            
        success, response = self.make_request('GET', '/api/papers/browse?limit=10')
        
        if success and isinstance(response, list):
            self.log_result("Browse Papers", True, f"Found {len(response)} papers")
            return response
        else:
            self.log_result("Browse Papers", False, f"Response: {response}")
            return []

    def test_search_papers(self):
        """Test searching papers by title"""
        if not self.token:
            self.log_result("Search Papers", False, "No auth token available")
            return []
            
        # Search for papers with "neural" in title
        params = {"title": "neural", "limit": 5}
        success, response = self.make_request('GET', '/api/papers/search', params)
        
        if success and isinstance(response, list):
            self.log_result("Search Papers by Title", True, f"Found {len(response)} papers")
            return response
        else:
            self.log_result("Search Papers by Title", False, f"Response: {response}")
            return []

    def test_search_papers_by_author(self):
        """Test searching papers by author"""
        if not self.token:
            self.log_result("Search Papers by Author", False, "No auth token available")
            return []
            
        # Search for papers by author
        params = {"author": "Smith", "limit": 5}
        success, response = self.make_request('GET', '/api/papers/search', params)
        
        if success and isinstance(response, list):
            self.log_result("Search Papers by Author", True, f"Found {len(response)} papers")
            return response
        else:
            self.log_result("Search Papers by Author", False, f"Response: {response}")
            return []

    def test_get_paper_details(self, papers):
        """Test getting paper details"""
        if not self.token or not papers:
            self.log_result("Get Paper Details", False, "No auth token or papers available")
            return None
            
        paper_id = papers[0]['paper_id']
        success, response = self.make_request('GET', f'/api/papers/{paper_id}')
        
        if success and response.get('paper_id'):
            self.log_result("Get Paper Details", True, f"Paper: {response.get('title', 'Unknown')[:50]}...")
            return response
        else:
            self.log_result("Get Paper Details", False, f"Response: {response}")
            return None

    def test_like_paper(self, paper_id):
        """Test liking a paper"""
        if not self.token or not paper_id:
            self.log_result("Like Paper", False, "No auth token or paper ID available")
            return False
            
        success, response = self.make_request('POST', f'/api/papers/{paper_id}/like')
        
        if success and response.get('is_liked'):
            self.log_result("Like Paper", True, "Paper liked successfully")
            return True
        else:
            self.log_result("Like Paper", False, f"Response: {response}")
            return False

    def test_unlike_paper(self, paper_id):
        """Test unliking a paper"""
        if not self.token or not paper_id:
            self.log_result("Unlike Paper", False, "No auth token or paper ID available")
            return
            
        success, response = self.make_request('DELETE', f'/api/papers/{paper_id}/like')
        
        if success and not response.get('is_liked', True):
            self.log_result("Unlike Paper", True, "Paper unliked successfully")
        else:
            self.log_result("Unlike Paper", False, f"Response: {response}")

    def test_view_paper(self, paper_id):
        """Test tracking paper view"""
        if not self.token or not paper_id:
            self.log_result("View Paper", False, "No auth token or paper ID available")
            return
            
        success, response = self.make_request('POST', f'/api/papers/{paper_id}/view')
        
        if success and response.get('message'):
            self.log_result("View Paper", True, "View tracked successfully")
        else:
            self.log_result("View Paper", False, f"Response: {response}")

    def test_get_recommendations(self):
        """Test getting paper recommendations"""
        if not self.token:
            self.log_result("Get Recommendations", False, "No auth token available")
            return []
            
        success, response = self.make_request('GET', '/api/papers/recommendations?limit=5')
        
        if success and isinstance(response, list):
            self.log_result("Get Recommendations", True, f"Found {len(response)} recommendations")
            return response
        else:
            self.log_result("Get Recommendations", False, f"Response: {response}")
            return []

    def test_get_favorites(self):
        """Test getting user's favorite papers"""
        if not self.token:
            self.log_result("Get Favorites", False, "No auth token available")
            return []
            
        success, response = self.make_request('GET', '/api/papers/me/favorites')
        
        if success and isinstance(response, list):
            self.log_result("Get Favorites", True, f"Found {len(response)} favorites")
            return response
        else:
            self.log_result("Get Favorites", False, f"Response: {response}")
            return []

    def test_get_recent_views(self):
        """Test getting user's recent views"""
        if not self.token:
            self.log_result("Get Recent Views", False, "No auth token available")
            return []
            
        success, response = self.make_request('GET', '/api/papers/me/recent-views')
        
        if success and isinstance(response, list):
            self.log_result("Get Recent Views", True, f"Found {len(response)} recent views")
            return response
        else:
            self.log_result("Get Recent Views", False, f"Response: {response}")
            return []

    def test_change_password(self):
        """Test changing user password"""
        if not self.token:
            self.log_result("Change Password", False, "No auth token available")
            return
            
        password_data = {
            "current_password": "test123",
            "new_password": "newtest123"
        }
        
        success, response = self.make_request('POST', '/api/auth/change-password', password_data)
        
        if success and response.get('message'):
            self.log_result("Change Password", True, "Password changed successfully")
            
            # Change it back
            password_data = {
                "current_password": "newtest123",
                "new_password": "test123"
            }
            self.make_request('POST', '/api/auth/change-password', password_data)
        else:
            self.log_result("Change Password", False, f"Response: {response}")

    def test_update_profile(self):
        """Test updating user profile"""
        if not self.token:
            self.log_result("Update Profile", False, "No auth token available")
            return
            
        profile_data = {
            "full_name": "Updated Test User",
            "username": "updated_testuser"
        }
        
        success, response = self.make_request('PUT', '/api/auth/me', profile_data)
        
        if success and response.get('full_name') == profile_data['full_name']:
            self.log_result("Update Profile", True, "Profile updated successfully")
        else:
            self.log_result("Update Profile", False, f"Response: {response}")

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Starting Research Paper Discovery API Tests")
        print("=" * 60)
        
        # Basic health and auth tests
        self.test_health_check()
        self.test_user_login()  # Use existing test user
        self.test_get_current_user()
        
        # Interest management
        interests = self.test_get_interests()
        if interests:
            self.test_update_user_interests(interests)
        
        # Paper discovery and search
        papers = self.test_browse_papers()
        search_results = self.test_search_papers()
        author_results = self.test_search_papers_by_author()
        
        # Paper details and interactions
        if papers:
            paper_detail = self.test_get_paper_details(papers)
            if paper_detail:
                paper_id = paper_detail['paper_id']
                self.test_view_paper(paper_id)
                
                # Test like/unlike cycle
                if self.test_like_paper(paper_id):
                    self.test_unlike_paper(paper_id)
        
        # Recommendations and user data
        self.test_get_recommendations()
        self.test_get_favorites()
        self.test_get_recent_views()
        
        # Profile management
        self.test_change_password()
        self.test_update_profile()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"✨ Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed < self.tests_run:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = ResearchAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/test_reports/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_tests': tester.tests_run,
                'passed_tests': tester.tests_passed,
                'success_rate': (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
                'timestamp': datetime.now().isoformat()
            },
            'results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())