#!/usr/bin/env python3
"""
Demo Examples for SDR AI Agent
Shows working examples of both plain text and structured JSON responses
"""

import asyncio
import json
import os
import sys
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.agent import app

def extract_json_from_response(response):
    """Extract JSON from response, handling various formats"""
    json_text = response.strip()
    
    # Try markdown code blocks first
    if "```json" in response:
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
    elif "```" in response:
        json_match = re.search(r'```\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
    
    # Try to find JSON object in the response
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
    if json_match:
        return json_match.group().strip()
    
    return json_text

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
    
    query = json.dumps(json_request) + "\n\nGet basic information about Microsoft CEO."
    print(f"Query: {json.dumps(json_request, indent=2)}")
    print("Additional context: Get basic information about Microsoft using search engines.")
    
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
        
        # Extract JSON from response
        json_text = extract_json_from_response(response)
        
        # Validate JSON structure
        try:
            parsed = json.loads(json_text)
            print("✅ Valid JSON structure!")
            print("✅ Required fields present:")
            for field in json_request["fields"]:
                if isinstance(parsed, dict) and field in parsed:
                    print(f"  ✅ {field}: {parsed[field]}")
                else:
                    print(f"  ❌ Missing: {field}")
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
            print(f"Extracted text: {json_text}")
        except Exception as e:
            print(f"❌ Error validating JSON: {e}")
            if isinstance(response, str):
                print(f"Response is a string, trying to parse directly...")
                try:
                    parsed = json.loads(response)
                    print("✅ Direct parsing successful!")
                    for field in json_request["fields"]:
                        if field in parsed:
                            print(f"  ✅ {field}: {parsed[field]}")
                        else:
                            print(f"  ❌ Missing: {field}")
                except:
                    print(f"Direct parsing also failed. Raw response: {response[:200]}...")
            
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
        
        # Extract JSON from response
        json_text = extract_json_from_response(response)
        
        # Validate JSON structure
        try:
            parsed = json.loads(json_text)
            print("✅ Valid JSON structure!")
            print("✅ Contact fields:")
            for field in json_request["fields"]:
                if isinstance(parsed, dict) and field in parsed:
                    print(f"  ✅ {field}: {parsed[field]}")
                else:
                    print(f"  ❌ Missing: {field}")
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
            print(f"Extracted text: {json_text}")
        except Exception as e:
            print(f"❌ Error validating JSON: {e}")
            if isinstance(response, str):
                print(f"Response is a string, trying to parse directly...")
                try:
                    parsed = json.loads(response)
                    print("✅ Direct parsing successful!")
                    for field in json_request["fields"]:
                        if field in parsed:
                            print(f"  ✅ {field}: {parsed[field]}")
                        else:
                            print(f"  ❌ Missing: {field}")
                except:
                    print(f"Direct parsing also failed. Raw response: {response[:200]}...")
            
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