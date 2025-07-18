#!/usr/bin/env python3
"""
Test script to verify LangSmith tracing is working properly
"""
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the main app
from main import setup_langsmith, process_single_query

async def test_langsmith_tracing():
    """Test that LangSmith tracing is properly configured and working"""
    
    print("🧪 Testing LangSmith Tracing Configuration")
    print("=" * 50)
    
    # Check environment variables
    print("📋 Environment Check:")
    print(f"  LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
    print(f"  LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
    print(f"  LANGCHAIN_API_KEY: {'✅ Set' if os.getenv('LANGCHAIN_API_KEY') else '❌ Not set'}")
    print(f"  LANGSMITH_API_KEY: {'✅ Set' if os.getenv('LANGSMITH_API_KEY') else '❌ Not set'}")
    print()
    
    # Setup LangSmith
    setup_langsmith()
    print()
    
    # Test queries with different types
    test_queries = [
        "What is Google's main business?",
        '{"format": "json", "fields": {"company_name": "string", "industry": "string"}} Find information about Tesla'
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 Test Query {i}: {query[:50]}...")
        try:
            await process_single_query(query)
            print(f"✅ Query {i} completed successfully")
        except Exception as e:
            print(f"❌ Query {i} failed: {e}")
        print("-" * 30)
    
    print("🎉 LangSmith tracing test completed!")
    print("Check your LangSmith dashboard to see the traced runs.")

if __name__ == "__main__":
    asyncio.run(test_langsmith_tracing())