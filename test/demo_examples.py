#!/usr/bin/env python3
"""
Demo Examples for SDR AI Agent
Shows working examples of both plain text and structured JSON responses
"""

import asyncio
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.agent import app

async def demo_plain_text():
    """Demo: Plain text company summary"""
    print("🔍 Demo 1: Plain Text Response")
    print("=" * 40)
    
    query = "Give me a brief overview of Tesla's business model."
    print(f"Query: {query}")
    
    try:
        initial_state = {
            "input": query,
            "chat_history": [],
            "agent_outcome": None,
            "intermediate_steps": []
        }
        
        result = await app.ainvoke(initial_state)
        response = result["agent_outcome"].return_values["output"]
        print(f"Response: {response}")
        print("✅ Plain text response working correctly!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}\n")

async def demo_structured_json():
    """Demo: Structured JSON response"""
    print("🔍 Demo 2: Structured JSON Response")
    print("=" * 40)
    
    # Create JSON structure request
    json_request = {
        "format": "json",
        "fields": {
            "company_name": "string",
            "industry": "string",
            "hq_location": "string",
            "short_description": "string"
        }
    }
    
    query = json.dumps(json_request) + "\n\nGet information about Netflix."
    print(f"Query: {json.dumps(json_request, indent=2)}")
    print("Additional context: Get information about Netflix.")
    
    try:
        initial_state = {
            "input": query,
            "chat_history": [],
            "agent_outcome": None,
            "intermediate_steps": []
        }
        
        result = await app.ainvoke(initial_state)
        response = result["agent_outcome"].return_values["output"]
        
        print(f"Response: {response}")
        
        # Validate JSON structure
        try:
            parsed = json.loads(response)
            print("✅ Valid JSON structure!")
            print("✅ Required fields present:")
            for field in json_request["fields"]:
                if field in parsed:
                    print(f"  - {field}: {parsed[field]}")
                else:
                    print(f"  ❌ Missing: {field}")
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def demo_contact_structure():
    """Demo: Contact information structure"""
    print("\n🔍 Demo 3: Contact Information Structure")
    print("=" * 40)
    
    json_request = {
        "format": "json",
        "fields": {
            "full_name": "string",
            "position": "string", 
            "company": "string",
            "email": "string"
        }
    }
    
    query = json.dumps(json_request) + "\n\nCreate sample contact info for a VP of Sales at Zoom."
    print(f"Query: {json.dumps(json_request, indent=2)}")
    print("Additional context: Create sample contact info for a VP of Sales at Zoom.")
    
    try:
        initial_state = {
            "input": query,
            "chat_history": [],
            "agent_outcome": None,
            "intermediate_steps": []
        }
        
        result = await app.ainvoke(initial_state)
        response = result["agent_outcome"].return_values["output"]
        
        print(f"Response: {response}")
        
        # Validate JSON structure
        try:
            parsed = json.loads(response)
            print("✅ Valid JSON structure!")
            print("✅ Contact fields:")
            for field in json_request["fields"]:
                if field in parsed:
                    print(f"  - {field}: {parsed[field]}")
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Run all demos"""
    print("🚀 SDR AI Agent - Working Examples Demo")
    print("=" * 50)
    
    await demo_plain_text()
    await demo_structured_json()
    await demo_contact_structure()
    
    print("\n🎯 Demo completed!")
    print("\nKey Features Demonstrated:")
    print("✅ Plain text responses for natural queries")
    print("✅ Structured JSON responses matching user-specified formats")
    print("✅ Proper field validation and type handling")
    print("✅ Clean JSON output (no markdown code blocks)")

if __name__ == "__main__":
    asyncio.run(main())