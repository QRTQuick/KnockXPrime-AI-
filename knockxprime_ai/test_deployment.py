#!/usr/bin/env python3
"""
Test script to verify backend deployment configuration
"""
import sys
import importlib.util
from pathlib import Path


def test_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        # Test main app import
        from app.main import app
        print("✅ Main app import successful")
        
        # Test middleware imports
        from app.middleware.security import SecurityHeadersMiddleware
        from app.middleware.logging import RequestLoggingMiddleware
        from app.middleware.rate_limiting import RateLimitMiddleware
        from app.middleware.cors import add_cors_middleware
        print("✅ Middleware imports successful")
        
        # Test core imports
        from app.core.config import settings
        from app.core.database import init_db
        print("✅ Core imports successful")
        
        # Test API imports
        from app.api.v1 import chat, users, usage, plans, admin
        print("✅ API imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_configuration():
    """Test configuration settings"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"Environment: {settings.environment}")
        print(f"Host: {settings.host}")
        print(f"Port: {settings.port}")
        print(f"Rate limit: {settings.rate_limit_requests} requests/minute")
        print(f"CORS origins: {len(settings.cors_origins)} configured")
        
        # Check required settings
        if not settings.neon_api_url:
            print("⚠️ Warning: NEON_API_URL not configured")
        else:
            print("✅ Neon API URL configured")
            
        if not settings.secret_key or settings.secret_key == "your-secret-key-change-in-production":
            print("⚠️ Warning: SECRET_KEY should be changed in production")
        else:
            print("✅ Secret key configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "app/main.py",
        "app/core/config.py",
        "app/core/database.py",
        "app/middleware/security.py",
        "app/middleware/logging.py",
        "app/middleware/rate_limiting.py",
        "app/middleware/cors.py",
        "requirements.txt",
        "render.yaml",
        "Procfile",
        "gunicorn.conf.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True


def main():
    """Run all tests"""
    print("🚀 KnockXPrime AI Backend Deployment Test")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_configuration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All tests passed! Backend is ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())