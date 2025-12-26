#!/usr/bin/env python3
"""
Database setup script for KnockXPrime AI
Run this script to initialize your Neon database with required tables and data.
"""
import asyncio
import sys
from app.core.database import init_db
from app.core.neon_utils import test_neon_connection
from app.core.config import settings


async def main():
    print("🚀 KnockXPrime AI Database Setup")
    print("=" * 50)
    
    # Check configuration
    if not settings.neon_api_key:
        print("❌ Error: NEON_API_KEY not found in environment variables")
        print("Please set your Neon API key in the .env file")
        sys.exit(1)
    
    if not settings.neon_api_url:
        print("❌ Error: NEON_API_URL not found in environment variables")
        sys.exit(1)
    
    print(f"📡 Neon API URL: {settings.neon_api_url}")
    print(f"🔑 API Key: {'*' * 20}{settings.neon_api_key[-8:]}")
    
    # Test connection
    print("\n🔍 Testing Neon database connection...")
    connection_result = await test_neon_connection()
    
    if connection_result["status"] == "error":
        print(f"❌ Connection failed: {connection_result['message']}")
        sys.exit(1)
    
    print("✅ Connection successful!")
    
    # Initialize database
    print("\n📊 Initializing database tables...")
    try:
        await init_db()
        print("✅ Database initialized successfully!")
        
        print("\n📋 Created tables:")
        print("  • plans (subscription plans)")
        print("  • users (user accounts)")
        print("  • usage (usage tracking)")
        print("  • sessions (optional session storage)")
        
        print("\n💳 Default subscription plans:")
        print("  • Baby Free: $0/month - 1,000 tokens, 10 requests/day")
        print("  • Leveler: $4/month - 5,000 tokens, 100 requests/day")
        print("  • Log Min: $10/month - 20,000 tokens, 500 requests/day")
        print("  • High Max: $100/month - 100,000 tokens, 2,000 requests/day")
        
        print("\n🎉 Setup complete! Your KnockXPrime AI database is ready.")
        print("\nNext steps:")
        print("1. Set your GROK_API_KEY in the .env file")
        print("2. Run: uvicorn app.main:app --reload")
        print("3. Visit: http://localhost:8000/docs for API documentation")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())