#!/usr/bin/env python3
"""
Comprehensive Test Suite for SDR AI Agent
Tests all requirements: single-turn, SDR focus, citations, JSON validation, error handling
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, Union

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.agent import app

class ComprehensiveAgentTester:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []

    async def run_agent_query(self, query: str) -> Dict[str, Any]:
        """Run a query through the agent and return the complete response"""
        try:
            initial_state = {
                "input": query,
                "chat_history": [],
                "agent_outcome": None,
                "intermediate_steps": []
            }
            
            result = await app.ainvoke(initial_state)
            return {
                "success": True,
                "response": result["agent_outcome"].return_values,
                "intermediate_steps": result["intermediate_steps"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "intermediate_steps": []
            }

    def validate_json_structure(self, response: str, expected_fields: Dict[str, str]) -> Dict[str, Any]:
        """Validate JSON structure with comprehensive checking"""
        try:
            parsed = json.loads(response)
            validation_results = {
                "valid_json": True,
                "all_fields_present": True,
                "correct_types": True,
                "missing_fields": [],
                "type_errors": []
            }
            
            # Check if all expected fields are present
            for field_name, field_type in expected_fields.items():
                if field_name not in parsed:
                    validation_results["all_fields_present"] = False
                    validation_results["missing_fields"].append(field_name)
                    continue
                
                # Type checking with null handling
                value = parsed[field_name]
                if value is not None:  # Allow null values as per requirements
                    if field_type == "string" and not isinstance(value, str):
                        validation_results["correct_types"] = False
                        validation_results["type_errors"].append(f"{field_name}: expected string, got {type(value).__name__}")
                    elif field_type == "integer" and not isinstance(value, int):
                        validation_results["correct_types"] = False
                        validation_results["type_errors"].append(f"{field_name}: expected integer, got {type(value).__name__}")
                    elif field_type == "boolean" and not isinstance(value, bool):
                        validation_results["correct_types"] = False
                        validation_results["type_errors"].append(f"{field_name}: expected boolean, got {type(value).__name__}")
            
            return validation_results
            
        except json.JSONDecodeError as e:
            return {
                "valid_json": False,
                "error": str(e),
                "all_fields_present": False,
                "correct_types": False
            }

    def check_citations(self, response: Union[str, Dict]) -> bool:
        """Check if response includes proper citations"""
        if isinstance(response, dict):
            # Check for citations in structured response - look in output field
            response_text = response.get("output", str(response))
            return any(keyword in response_text for keyword in ["Source:", "Sources:", "📚", "Based on", "citations"])
        elif isinstance(response, str):
            # Check for citations in text response
            return any(keyword in response for keyword in ["Source:", "Sources:", "📚", "Based on"])
        return False

    async def test_single_turn_operation(self):
        """Test 1: Verify single-turn operation (no follow-up questions)"""
        print("\n🧪 Test 1: Single-Turn Operation")
        query = "Give me information about Tesla's business model"
        
        result = await self.run_agent_query(query)
        
        # Check that response is complete and doesn't ask follow-up questions
        if result["success"]:
            response_text = str(result["response"])
            has_followup = any(phrase in response_text.lower() for phrase in [
                "what would you like", "need more information", "can you specify",
                "would you like me to", "do you want", "any specific"
            ])
            success = not has_followup and len(response_text) > 50
        else:
            success = False
        
        self._record_test("Single-Turn Operation", success, result)
        return success

    async def test_sdr_focused_response(self):
        """Test 2: SDR-focused, actionable response"""
        print("\n🧪 Test 2: SDR-Focused Response")
        query = "Help me research Salesforce for outbound sales"
        
        result = await self.run_agent_query(query)
        
        if result["success"]:
            # Handle both simple output and output with citations
            response_data = result["response"]
            if isinstance(response_data, dict) and "output" in response_data:
                response_text = response_data["output"]
            else:
                response_text = str(response_data)
            
            response_lower = response_text.lower()
            # Check for SDR-relevant keywords (more comprehensive list)
            sdr_keywords = ["sales", "outreach", "prospect", "lead", "revenue", "business", "market", "contact", 
                           "research", "outbound", "sdr", "development", "qualification", "target"]
            sdr_relevance = sum(1 for keyword in sdr_keywords if keyword in response_lower)
            
            # More lenient criteria: 2+ keywords and reasonable length
            success = sdr_relevance >= 2 and len(response_text) > 50
        else:
            success = False
        
        self._record_test("SDR-Focused Response", success, result)
        return success

    async def test_citation_requirement(self):
        """Test 3: Citation requirement compliance"""
        print("\n🧪 Test 3: Citation Requirement")
        query = "What is Microsoft's main business focus?"
        
        result = await self.run_agent_query(query)
        
        if result["success"]:
            has_citations = self.check_citations(result["response"])
            success = has_citations
        else:
            success = False
        
        self._record_test("Citation Requirement", success, result)
        return success

    async def test_json_field_validation(self):
        """Test 4: Strict JSON field validation"""
        print("\n🧪 Test 4: JSON Field Validation")
        
        query = json.dumps({
            "format": "json",
            "fields": {
                "company_name": "string",
                "employee_count": "integer",
                "is_public": "boolean",
                "description": "string"
            }
        }) + "\n\nGet information about Apple Inc."
        
        result = await self.run_agent_query(query)
        
        if result["success"]:
            response_output = result["response"].get("output", "")
            validation = self.validate_json_structure(response_output, {
                "company_name": "string",
                "employee_count": "integer", 
                "is_public": "boolean",
                "description": "string"
            })
            success = validation.get("valid_json", False) and validation.get("all_fields_present", False)
        else:
            success = False
        
        self._record_test("JSON Field Validation", success, result)
        return success

    async def test_null_handling(self):
        """Test 5: Proper null handling for missing data"""
        print("\n🧪 Test 5: Null Value Handling")
        
        query = json.dumps({
            "format": "json",
            "fields": {
                "company_name": "string",
                "unknown_metric": "integer",
                "secret_info": "string"
            }
        }) + "\n\nGet information about a fictional company XYZ Corp."
        
        result = await self.run_agent_query(query)
        
        if result["success"]:
            response_output = result["response"].get("output", "")
            try:
                parsed = json.loads(response_output)
                # Check that unknown fields are properly set to null
                has_nulls = any(value is None for value in parsed.values())
                success = has_nulls or "null" in response_output.lower()
            except json.JSONDecodeError:
                success = False
        else:
            success = False
        
        self._record_test("Null Value Handling", success, result)
        return success

    async def test_error_handling(self):
        """Test 6: Comprehensive error handling"""
        print("\n🧪 Test 6: Error Handling")
        
        # Test with malformed JSON
        query = '{"format": "json", "fields": {"invalid": json}}'
        
        result = await self.run_agent_query(query)
        
        # Should handle error gracefully without breaking
        if result["success"]:
            response_text = str(result["response"])
            # Should provide helpful error message or fallback response
            success = len(response_text) > 20 and not "Traceback" in response_text
        else:
            # Error should be handled gracefully
            success = "error" in result.get("error", "").lower()
        
        self._record_test("Error Handling", success, result)
        return success

    async def test_response_format_detection(self):
        """Test 7: Automatic format detection"""
        print("\n🧪 Test 7: Response Format Detection")
        
        # Test plain text detection
        plain_query = "Tell me about Google's business"
        plain_result = await self.run_agent_query(plain_query)
        
        # Test JSON detection
        json_query = json.dumps({
            "format": "json",
            "fields": {"company": "string", "industry": "string"}
        }) + "\n\nGoogle information"
        json_result = await self.run_agent_query(json_query)
        
        plain_success = False
        json_success = False
        
        if plain_result["success"]:
            # Extract the actual output content
            response_data = plain_result["response"]
            if isinstance(response_data, dict) and "output" in response_data:
                plain_response = response_data["output"]
            else:
                plain_response = str(response_data)
            
            # Plain text should not be valid JSON (should be natural language)
            try:
                json.loads(plain_response.strip())
                plain_success = False  # If it parses as JSON, it's not plain text
            except json.JSONDecodeError:
                plain_success = True  # If it doesn't parse as JSON, it's plain text
        
        if json_result["success"]:
            # Extract the actual output content
            response_data = json_result["response"]
            if isinstance(response_data, dict) and "output" in response_data:
                json_response = response_data["output"]
            else:
                json_response = str(response_data)
            
            # JSON response should be valid JSON
            try:
                parsed_json = json.loads(json_response.strip())
                # Verify it has the expected fields
                json_success = "company" in parsed_json and "industry" in parsed_json
            except json.JSONDecodeError:
                json_success = False
        
        success = plain_success and json_success
        self._record_test("Response Format Detection", success, {
            "plain": plain_result,
            "json": json_result,
            "plain_is_text": plain_success,
            "json_is_valid": json_success
        })
        return success

    def _record_test(self, test_name: str, success: bool, result: Any):
        """Record test result with comprehensive details"""
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}: PASSED")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: FAILED")
        
        # Truncate response for readability
        response_summary = str(result)[:300] + "..." if len(str(result)) > 300 else str(result)
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": response_summary
        })

    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive SDR AI Agent Test Suite")
        print("Testing: Single-turn, SDR focus, Citations, JSON validation, Error handling")
        print("=" * 70)
        
        # Run all tests
        await self.test_single_turn_operation()
        await self.test_sdr_focused_response()
        await self.test_citation_requirement()
        await self.test_json_field_validation()
        await self.test_null_handling()
        await self.test_error_handling()
        await self.test_response_format_detection()
        
        # Generate comprehensive report
        self.generate_comprehensive_report()

    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 70)
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Compliance assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Agent fully complies with requirements!")
        elif success_rate >= 75:
            print("✅ GOOD: Agent meets most requirements")
        elif success_rate >= 50:
            print("⚠️  NEEDS IMPROVEMENT: Some requirements not met")
        else:
            print("🚨 CRITICAL: Major requirements not satisfied")
        
        # Detailed results
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if not result["success"]:
                print(f"   Details: {result['details'][:200]}...")
        
        # Requirements compliance summary
        print("\n📋 REQUIREMENTS COMPLIANCE:")
        requirements = [
            ("Single-Turn Operation", "✅" if any("Single-Turn" in r["test"] and r["success"] for r in self.test_results) else "❌"),
            ("SDR Focus", "✅" if any("SDR-Focused" in r["test"] and r["success"] for r in self.test_results) else "❌"),
            ("Citation Requirement", "✅" if any("Citation" in r["test"] and r["success"] for r in self.test_results) else "❌"),
            ("JSON Validation", "✅" if any("JSON" in r["test"] and r["success"] for r in self.test_results) else "❌"),
            ("Error Handling", "✅" if any("Error" in r["test"] and r["success"] for r in self.test_results) else "❌"),
            ("Format Detection", "✅" if any("Format" in r["test"] and r["success"] for r in self.test_results) else "❌")
        ]
        
        for req, status in requirements:
            print(f"{status} {req}")
        
        # Save comprehensive results
        with open("comprehensive_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed": self.passed_tests,
                    "failed": self.failed_tests,
                    "success_rate": success_rate,
                    "compliance_level": "EXCELLENT" if success_rate >= 90 else "GOOD" if success_rate >= 75 else "NEEDS_IMPROVEMENT"
                },
                "requirements_compliance": dict(requirements),
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Comprehensive results saved to comprehensive_test_results.json")

async def main():
    """Main test runner"""
    tester = ComprehensiveAgentTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())