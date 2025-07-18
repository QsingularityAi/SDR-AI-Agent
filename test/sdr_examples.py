#!/usr/bin/env python3
"""
SDR AI Agent - Sales Development Representative Examples
Demonstrates structured JSON responses for lead research and outreach
"""

import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agent import app

# SDR-specific examples with proper data types
SDR_EXAMPLES = [
    {
        "title": "Company Summary for Lead Research",
        "json_request": {
            "format": "json",
            "fields": {
                "company_name": "string",
                "industry": "string", 
                "hq_location": "string",
                "short_description": "string"
            }
        },
        "context": "Give me a short company summary for Stripe",
        "expected_fields": ["company_name", "industry", "hq_location", "short_description"]
    },
    {
        "title": "Contact Info Enrichment",
        "json_request": {
            "format": "json",
            "fields": {
                "full_name": "string",
                "position": "string",
                "company": "string",
                "email": "string"
            }
        },
        "context": "Find contact information for the VP of Sales at HubSpot",
        "expected_fields": ["full_name", "position", "company", "email"]
    },
    {
        "title": "LinkedIn Profile Enrichment",
        "json_request": {
            "format": "json",
            "fields": {
                "full_name": "string",
                "position": "string",
                "company": "string",
                "years_of_experience": "integer",
                "industry_expertise": "string"
            }
        },
        "context": "Research the Head of Growth at Notion for outreach",
        "expected_fields": ["full_name", "position", "company", "years_of_experience", "industry_expertise"]
    },
    {
        "title": "Outreach Personalization",
        "json_request": {
            "format": "json",
            "fields": {
                "first_name": "string",
                "personalized_hook": "string",
                "company": "string",
                "role": "string"
            }
        },
        "context": "Create personalized outreach for a Marketing Lead at Salesforce",
        "expected_fields": ["first_name", "personalized_hook", "company", "role"]
    },
    {
        "title": "Job Posting Lead Qualification",
        "json_request": {
            "format": "json",
            "fields": {
                "company": "string",
                "role": "string",
                "location": "string",
                "focus_area": "string"
            }
        },
        "context": "Find recent job posting for Head of Partnerships at Shopify",
        "expected_fields": ["company", "role", "location", "focus_area"]
    }
]

async def test_sdr_example(example):
    """Test a single SDR example"""
    print(f"\n🔍 {example['title']}")
    print(f"Context: {example['context']}")
    print(f"Expected Fields: {', '.join(example['expected_fields'])}")
    print("-" * 50)
    
    # Construct the query
    query = json.dumps(example['json_request']) + f"\n\n{example['context']}"
    
    try:
        initial_state = {
            "input": query,
            "chat_history": [],
            "agent_outcome": None,
            "intermediate_steps": []
        }
        
        result = await app.ainvoke(initial_state)
        response = result["agent_outcome"].return_values["output"]
        
        print(f"📝 Raw Response:")
        print(response)
        print()
        
        # Validate JSON structure and data types
        try:
            parsed = json.loads(response)
            print("✅ Valid JSON structure!")
            
            # Check all required fields
            missing_fields = []
            present_fields = []
            type_issues = []
            
            for field in example['expected_fields']:
                if field in parsed:
                    present_fields.append(field)
                    # Check data type
                    expected_type = example['json_request']['fields'][field]
                    actual_value = parsed[field]
                    
                    if expected_type == "string" and not isinstance(actual_value, str):
                        type_issues.append(f"{field}: expected string, got {type(actual_value)}")
                    elif expected_type == "integer" and not isinstance(actual_value, int):
                        # Try to convert if it's a numeric string
                        if isinstance(actual_value, str) and actual_value.isdigit():
                            parsed[field] = int(actual_value)
                        else:
                            type_issues.append(f"{field}: expected integer, got {type(actual_value)}")
                else:
                    missing_fields.append(field)
            
            # Report results
            print(f"📊 Field Analysis:")
            print(f"  ✅ Present: {len(present_fields)}/{len(example['expected_fields'])}")
            for field in present_fields:
                value = parsed[field]
                display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                print(f"    - {field}: {display_value}")
            
            if missing_fields:
                print(f"  ❌ Missing: {', '.join(missing_fields)}")
            
            if type_issues:
                print(f"  ⚠️ Type Issues: {', '.join(type_issues)}")
            
            if not missing_fields and not type_issues:
                print("🌟 Perfect SDR response!")
            elif len(present_fields) >= len(example['expected_fields']) * 0.8:
                print("✅ Good SDR response!")
            else:
                print("⚠️ Needs improvement")
                
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                print("🔍 Found JSON-like content, attempting to parse...")
                try:
                    extracted = json_match.group()
                    parsed = json.loads(extracted)
                    print("✅ Extracted JSON successfully!")
                    print(json.dumps(parsed, indent=2))
                except:
                    print("❌ Could not parse extracted content")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("=" * 50)

async def demo_sdr_workflows():
    """Demonstrate all SDR workflows"""
    print("🚀 SDR AI Agent - Sales Development Examples")
    print("=" * 60)
    print("Testing structured JSON responses for lead research and outreach")
    print("=" * 60)
    
    for i, example in enumerate(SDR_EXAMPLES, 1):
        print(f"\n📋 SDR Example {i}/{len(SDR_EXAMPLES)}")
        await test_sdr_example(example)
        
        # Small delay between requests
        await asyncio.sleep(1)

async def interactive_sdr_mode():
    """Interactive mode for testing custom SDR queries"""
    print("\n🎯 Interactive SDR Mode")
    print("=" * 50)
    print("Test your own SDR queries with structured JSON output")
    print("Format: Paste your JSON schema, then describe what you need")
    print("Type 'examples' to see templates, 'exit' to quit")
    print("-" * 50)
    
    templates = [
        {
            "name": "Company Research",
            "json": '{"format": "json", "fields": {"company_name": "string", "industry": "string", "employee_count": "string", "recent_news": "string"}}',
            "context": "Research [COMPANY_NAME] for outreach"
        },
        {
            "name": "Contact Enrichment", 
            "json": '{"format": "json", "fields": {"full_name": "string", "title": "string", "linkedin_url": "string", "company": "string"}}',
            "context": "Find contact info for [ROLE] at [COMPANY]"
        },
        {
            "name": "Competitive Analysis",
            "json": '{"format": "json", "fields": {"competitor_1": "string", "competitor_2": "string", "key_differentiator": "string", "market_position": "string"}}',
            "context": "Compare [COMPANY] with main competitors"
        }
    ]
    
    while True:
        try:
            user_input = input("\n🤔 Your SDR query (or command): ").strip()
            
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            elif user_input.lower() == 'examples':
                print("\n📚 SDR Query Templates:")
                for i, template in enumerate(templates, 1):
                    print(f"\n{i}. {template['name']}")
                    print(f"   JSON: {template['json']}")
                    print(f"   Context: {template['context']}")
                continue
            elif not user_input:
                continue
            
            print(f"\n🔍 Processing SDR Query...")
            print("-" * 50)
            
            initial_state = {
                "input": user_input,
                "chat_history": [],
                "agent_outcome": None,
                "intermediate_steps": []
            }
            
            result = await app.ainvoke(initial_state)
            response = result["agent_outcome"].return_values["output"]
            
            print(f"📊 SDR RESULT:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

async def main():
    """Main SDR demo function"""
    print("🚀 SDR AI Agent - Complete Demo Suite")
    print("=" * 60)
    
    # Run all SDR examples
    await demo_sdr_workflows()
    
    # Summary
    print("\n📊 SDR Use Case Summary:")
    print("=" * 50)
    print("✅ Company research and lead qualification")
    print("✅ Contact information enrichment")
    print("✅ LinkedIn profile analysis")
    print("✅ Personalized outreach preparation")
    print("✅ Job posting analysis for targeting")
    print("✅ Structured JSON output with proper data types")
    
    # Ask for interactive mode
    try:
        choice = input("\n🎯 Try interactive SDR mode? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            await interactive_sdr_mode()
    except KeyboardInterrupt:
        pass
    
    print("\n🎯 SDR Demo Complete!")
    print("Your agent is ready for sales development workflows!")

if __name__ == "__main__":
    asyncio.run(main())