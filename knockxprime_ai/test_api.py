#!/usr/bin/env python3
"""
API Testing Script for KnockXPrime AI
Run this script to test the main API endpoints
"""
import asyncio
import httpx
import json
from datetime import datetime


class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_key = None
        self.user_data = None
    
    async def test_health_endpoints(self):
        """Test health check endpoints"""
        print("🏥 Testing Health Endpoints")
        print("-" * 40)
        
        async with httpx.AsyncClient() as client:
            # Basic health check
            response = await client.get(f"{self.base_url}/health/")
            print(f"Health Check: {response.status_code}")
            if response.status_code == 200:
                print(f"  Response: {response.json()}")
            
            # Database health check
            response = await client.get(f"{self.base_url}/health/database")
            print(f"Database Health: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                db_status = result.get('database', {}).get('status', 'unknown')
                print(f"  Database Status: {db_status}")
    
    async def test_user_registration(self):
        """Test user registration"""
        print("\n👤 Testing User Registration")
        print("-" * 40)
        
        test_user = {
            "username": f"testuser_{int(datetime.now().timestamp())}",
            "email": f"test_{int(datetime.now().timestamp())}@example.com",
            "password": "securepassword123",
            "plan_name": "Leveler"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/users/register",
                json=test_user
            )
            
            print(f"Registration: {response.status_code}")
            if response.status_code == 200:
                self.user_data = response.json()
                print(f"  User ID: {self.user_data['id']}")
                print(f"  Username: {self.user_data['username']}")
                print(f"  Plan: {self.user_data['plan_name']}")
                return True
            else:
                print(f"  Error: {response.text}")
                return False
    
    async def test_user_login(self):
        """Test user login"""
        if not self.user_data:
            print("❌ No user data available for login test")
            return False
        
        print("\n🔐 Testing User Login")
        print("-" * 40)
        
        login_data = {
            "username": self.user_data['username'],
            "password": "securepassword123"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/users/login",
                json=login_data
            )
            
            print(f"Login: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  Access Token: {result['access_token'][:20]}...")
                return True
            else:
                print(f"  Error: {response.text}")
                return False
    
    async def test_get_profile_with_api_key(self):
        """Test getting user profile with API key"""
        if not self.api_key:
            print("❌ No API key available for profile test")
            return False
        
        print("\n📋 Testing User Profile")
        print("-" * 40)
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/users/profile",
                headers=headers
            )
            
            print(f"Profile: {response.status_code}")
            if response.status_code == 200:
                profile = response.json()
                print(f"  Username: {profile['username']}")
                print(f"  Plan: {profile['plan_name']}")
                print(f"  Max Tokens: {profile['max_tokens']}")
                return True
            else:
                print(f"  Error: {response.text}")
                return False
    
    async def test_plans_endpoint(self):
        """Test plans listing"""
        print("\n💳 Testing Plans Endpoint")
        print("-" * 40)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/v1/plans/")
            
            print(f"Plans List: {response.status_code}")
            if response.status_code == 200:
                plans = response.json()
                print(f"  Available Plans: {len(plans)}")
                for plan in plans:
                    print(f"    - {plan['name']}: ${plan['price']}/month ({plan['max_tokens']} tokens)")
                return True
            else:
                print(f"  Error: {response.text}")
                return False
    
    async def test_chat_without_grok_key(self):
        """Test chat endpoint (will fail without Grok API key)"""
        if not self.api_key:
            print("❌ No API key available for chat test")
            return False
        
        print("\n💬 Testing Chat Endpoint")
        print("-" * 40)
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        chat_request = {
            "messages": [
                {"role": "user", "content": "Hello, this is a test message"}
            ],
            "max_tokens": 50
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/chat/completions",
                headers=headers,
                json=chat_request
            )
            
            print(f"Chat Request: {response.status_code}")
            if response.status_code == 200:
                print("  ✅ Chat endpoint working (Grok API key configured)")
                return True
            else:
                error_text = response.text
                if "GROK_API_KEY" in error_text or "grok" in error_text.lower():
                    print("  ⚠️  Chat endpoint accessible but Grok API key needed")
                else:
                    print(f"  Error: {error_text}")
                return False
    
    async def get_api_key_for_testing(self):
        """Get API key by registering a user and extracting from profile"""
        print("\n🔑 Getting API Key for Testing")
        print("-" * 40)
        
        # Register user first
        success = await self.test_user_registration()
        if not success:
            return False
        
        # Login to get JWT token
        login_data = {
            "username": self.user_data['username'],
            "password": "securepassword123"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/users/login",
                json=login_data
            )
            
            if response.status_code == 200:
                result = response.json()
                jwt_token = result['access_token']
                
                # Get profile to extract API key
                headers = {"Authorization": f"Bearer {jwt_token}"}
                profile_response = await client.get(
                    f"{self.base_url}/api/v1/users/profile",
                    headers=headers
                )
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    self.api_key = profile['api_key']
                    print(f"  API Key obtained: {self.api_key[:20]}...")
                    return True
        
        return False
    
    async def run_all_tests(self):
        """Run all API tests"""
        print("🚀 KnockXPrime AI API Testing")
        print("=" * 50)
        
        # Test health endpoints
        await self.test_health_endpoints()
        
        # Test plans endpoint (no auth required)
        await self.test_plans_endpoint()
        
        # Get API key for authenticated tests
        api_key_success = await self.get_api_key_for_testing()
        
        if api_key_success:
            # Test authenticated endpoints
            await self.test_get_profile_with_api_key()
            await self.test_chat_without_grok_key()
        
        print("\n" + "=" * 50)
        print("🎉 API Testing Complete!")
        print("\nNext steps:")
        print("1. Add your GROK_API_KEY to .env file")
        print("2. Test chat completions with a real API key")
        print("3. Set up your frontend application")


async def main():
    tester = APITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())