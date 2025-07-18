#!/usr/bin/env python3
"""
Comprehensive Evaluation Suite for SDR AI Agent
Tests all requirements and generates detailed performance metrics
"""

import asyncio
import json
import time
from typing import Dict, Any, List
from src.agent import app

class SDRAgentEvaluator:
    def __init__(self):
        self.test_results = []
        self.performance_metrics = {
            "response_times": [],
            "token_usage": [],
            "accuracy_scores": [],
            "citation_compliance": []
        }

    async def evaluate_accuracy(self, query: str, expected_keywords: List[str]) -> float:
        """Evaluate response accuracy based on expected keywords"""
        start_time = time.time()
        
        result = await self.run_query(query)
        response_time = time.time() - start_time
        self.performance_metrics["response_times"].append(response_time)
        
        if not result["success"]:
            return 0.0
        
        response_text = str(result["response"]).lower()
        keyword_matches = sum(1 for keyword in expected_keywords if keyword in response_text)
        accuracy = keyword_matches / len(expected_keywords) if expected_keywords else 0.0
        
        self.performance_metrics["accuracy_scores"].append(accuracy)
        return accuracy

    async def evaluate_helpfulness(self, query: str, sdr_context: str) -> Dict[str, Any]:
        """Evaluate response helpfulness for SDR activities"""
        result = await self.run_query(query)
        
        if not result["success"]:
            return {"helpfulness_score": 0.0, "actionable": False, "relevant": False}
        
        response_text = str(result["response"]).lower()
        
        # SDR-specific helpfulness criteria
        actionable_indicators = ["contact", "reach out", "approach", "strategy", "next steps", "recommend"]
        relevant_indicators = ["sales", "revenue", "business", "market", "prospect", "lead", "opportunity"]
        
        actionable_score = sum(1 for indicator in actionable_indicators if indicator in response_text)
        relevant_score = sum(1 for indicator in relevant_indicators if indicator in response_text)
        
        helpfulness_score = (actionable_score + relevant_score) / (len(actionable_indicators) + len(relevant_indicators))
        
        return {
            "helpfulness_score": helpfulness_score,
            "actionable": actionable_score > 0,
            "relevant": relevant_score > 0,
            "response_length": len(response_text)
        }

    async def evaluate_json_compliance(self, json_structure: Dict, context: str) -> Dict[str, Any]:
        """Evaluate JSON structure compliance"""
        query = json.dumps(json_structure) + f"\n\n{context}"
        result = await self.run_query(query)
        
        if not result["success"]:
            return {"compliant": False, "error": result.get("error", "Unknown error")}
        
        response_output = result["response"].get("output", "")
        
        try:
            parsed_json = json.loads(response_output)
            expected_fields = json_structure.get("fields", {})
            
            compliance_results = {
                "compliant": True,
                "all_fields_present": True,
                "correct_types": True,
                "field_analysis": {}
            }
            
            for field_name, field_type in expected_fields.items():
                if field_name not in parsed_json:
                    compliance_results["all_fields_present"] = False
                    compliance_results["field_analysis"][field_name] = "missing"
                    continue
                
                value = parsed_json[field_name]
                if value is not None:  # Allow null values
                    expected_python_type = {
                        "string": str,
                        "integer": int,
                        "boolean": bool
                    }.get(field_type, str)
                    
                    if not isinstance(value, expected_python_type):
                        compliance_results["correct_types"] = False
                        compliance_results["field_analysis"][field_name] = f"wrong_type_{type(value).__name__}"
                    else:
                        compliance_results["field_analysis"][field_name] = "correct"
                else:
                    compliance_results["field_analysis"][field_name] = "null"
            
            compliance_results["compliant"] = compliance_results["all_fields_present"] and compliance_results["correct_types"]
            return compliance_results
            
        except json.JSONDecodeError as e:
            return {"compliant": False, "error": f"Invalid JSON: {str(e)}"}

    async def evaluate_citation_quality(self, query: str) -> Dict[str, Any]:
        """Evaluate citation quality and presence"""
        result = await self.run_query(query)
        
        if not result["success"]:
            return {"has_citations": False, "citation_quality": 0.0}
        
        response = result["response"]
        citation_indicators = ["source:", "sources:", "based on", "according to", "📚"]
        
        # Check for citations in response
        response_text = str(response).lower()
        has_citations = any(indicator in response_text for indicator in citation_indicators)
        
        # Check for structured citations
        structured_citations = isinstance(response, dict) and "citations" in response
        
        citation_quality = 1.0 if (has_citations or structured_citations) else 0.0
        self.performance_metrics["citation_compliance"].append(citation_quality)
        
        return {
            "has_citations": has_citations or structured_citations,
            "citation_quality": citation_quality,
            "structured_citations": structured_citations
        }

    async def run_query(self, query: str) -> Dict[str, Any]:
        """Run a query and return structured result"""
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
                "error": str(e)
            }

    async def run_comprehensive_evaluation(self):
        """Run comprehensive evaluation suite"""
        print("🔍 Starting Comprehensive SDR AI Agent Evaluation")
        print("=" * 60)
        
        # Test cases for different evaluation criteria
        test_cases = [
            {
                "name": "Company Research Accuracy",
                "query": "Tell me about Microsoft's business model",
                "expected_keywords": ["microsoft", "software", "cloud", "business", "technology"],
                "type": "accuracy"
            },
            {
                "name": "SDR Helpfulness - Outreach",
                "query": "How should I approach Salesforce for a sales meeting?",
                "sdr_context": "outreach strategy",
                "type": "helpfulness"
            },
            {
                "name": "JSON Compliance - Company Info",
                "json_structure": {
                    "format": "json",
                    "fields": {
                        "company_name": "string",
                        "industry": "string",
                        "employee_count": "integer",
                        "is_public": "boolean"
                    }
                },
                "context": "Get information about Tesla",
                "type": "json_compliance"
            },
            {
                "name": "Citation Quality",
                "query": "What is Google's main revenue source?",
                "type": "citation"
            },
            {
                "name": "SDR Helpfulness - Lead Qualification",
                "query": "I need to qualify a fintech lead for our B2B SaaS solution. Please research this prospect and provide a comprehensive qualification framework including: company background, decision-maker identification, pain point analysis, buying signals, competitive landscape, and personalized outreach strategy. Focus on BANT criteria (Budget, Authority, Need, Timeline) and provide specific talking points for discovery calls",
                "sdr_context": "lead qualification",
                "type": "helpfulness"
            },
            {
                "name": "JSON Compliance - Contact Info",
                "json_structure": {
                    "format": "json",
                    "fields": {
                        "full_name": "string",
                        "position": "string",
                        "company": "string",
                        "email": "string"
                    }
                },
                "context": "Create sample contact info for a VP of Sales at Zoom",
                "type": "json_compliance"
            }
        ]
        
        # Run evaluations
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: {test_case['name']}")
            
            if test_case["type"] == "accuracy":
                score = await self.evaluate_accuracy(test_case["query"], test_case["expected_keywords"])
                result = {"accuracy_score": score}
                
            elif test_case["type"] == "helpfulness":
                result = await self.evaluate_helpfulness(test_case["query"], test_case["sdr_context"])
                
            elif test_case["type"] == "json_compliance":
                result = await self.evaluate_json_compliance(test_case["json_structure"], test_case["context"])
                
            elif test_case["type"] == "citation":
                result = await self.evaluate_citation_quality(test_case["query"])
            
            # Record results
            self.test_results.append({
                "test_name": test_case["name"],
                "test_type": test_case["type"],
                "result": result
            })
            
            # Display results
            if test_case["type"] == "accuracy":
                print(f"   Accuracy Score: {result['accuracy_score']:.2f}")
            elif test_case["type"] == "helpfulness":
                print(f"   Helpfulness Score: {result['helpfulness_score']:.2f}")
                print(f"   Actionable: {'✅' if result['actionable'] else '❌'}")
                print(f"   Relevant: {'✅' if result['relevant'] else '❌'}")
            elif test_case["type"] == "json_compliance":
                print(f"   Compliant: {'✅' if result['compliant'] else '❌'}")
                if not result['compliant']:
                    print(f"   Error: {result.get('error', 'Structure mismatch')}")
            elif test_case["type"] == "citation":
                print(f"   Has Citations: {'✅' if result['has_citations'] else '❌'}")
                print(f"   Citation Quality: {result['citation_quality']:.2f}")
        
        # Generate final report
        self.generate_evaluation_report()

    def generate_evaluation_report(self):
        """Generate comprehensive evaluation report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE EVALUATION REPORT")
        print("=" * 60)
        
        # Calculate overall metrics
        accuracy_scores = [r["result"].get("accuracy_score", 0) for r in self.test_results if "accuracy_score" in r["result"]]
        helpfulness_scores = [r["result"].get("helpfulness_score", 0) for r in self.test_results if "helpfulness_score" in r["result"]]
        compliance_scores = [1 if r["result"].get("compliant", False) else 0 for r in self.test_results if "compliant" in r["result"]]
        citation_scores = [r["result"].get("citation_quality", 0) for r in self.test_results if "citation_quality" in r["result"]]
        
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
        avg_helpfulness = sum(helpfulness_scores) / len(helpfulness_scores) if helpfulness_scores else 0
        avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
        avg_citations = sum(citation_scores) / len(citation_scores) if citation_scores else 0
        
        avg_response_time = sum(self.performance_metrics["response_times"]) / len(self.performance_metrics["response_times"]) if self.performance_metrics["response_times"] else 0
        
        print(f"📈 PERFORMANCE METRICS:")
        print(f"   Average Accuracy Score: {avg_accuracy:.2f}")
        print(f"   Average Helpfulness Score: {avg_helpfulness:.2f}")
        print(f"   JSON Compliance Rate: {avg_compliance:.2f}")
        print(f"   Citation Compliance Rate: {avg_citations:.2f}")
        print(f"   Average Response Time: {avg_response_time:.2f}s")
        
        # Overall assessment
        overall_score = (avg_accuracy + avg_helpfulness + avg_compliance + avg_citations) / 4
        print(f"\n🎯 OVERALL SCORE: {overall_score:.2f}")
        
        if overall_score >= 0.9:
            print("🎉 EXCELLENT: Agent exceeds requirements!")
        elif overall_score >= 0.75:
            print("✅ GOOD: Agent meets requirements well")
        elif overall_score >= 0.6:
            print("⚠️  ACCEPTABLE: Agent meets basic requirements")
        else:
            print("🚨 NEEDS IMPROVEMENT: Agent requires optimization")
        
        # Detailed breakdown
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            test_name = result["test_name"]
            test_result = result["result"]
            
            if "accuracy_score" in test_result:
                score = test_result["accuracy_score"]
                status = "✅" if score >= 0.7 else "⚠️" if score >= 0.5 else "❌"
                print(f"   {status} {test_name}: {score:.2f}")
            elif "helpfulness_score" in test_result:
                score = test_result["helpfulness_score"]
                status = "✅" if score >= 0.6 else "⚠️" if score >= 0.4 else "❌"
                print(f"   {status} {test_name}: {score:.2f}")
            elif "compliant" in test_result:
                compliant = test_result["compliant"]
                status = "✅" if compliant else "❌"
                print(f"   {status} {test_name}: {'Compliant' if compliant else 'Non-compliant'}")
            elif "has_citations" in test_result:
                has_citations = test_result["has_citations"]
                status = "✅" if has_citations else "❌"
                print(f"   {status} {test_name}: {'Citations present' if has_citations else 'No citations'}")
        
        # Save evaluation results
        evaluation_data = {
            "summary": {
                "overall_score": overall_score,
                "avg_accuracy": avg_accuracy,
                "avg_helpfulness": avg_helpfulness,
                "avg_compliance": avg_compliance,
                "avg_citations": avg_citations,
                "avg_response_time": avg_response_time
            },
            "detailed_results": self.test_results,
            "performance_metrics": self.performance_metrics
        }
        
        with open("evaluation_results.json", "w") as f:
            json.dump(evaluation_data, f, indent=2)
        
        print(f"\n💾 Evaluation results saved to evaluation_results.json")

async def main():
    """Run comprehensive evaluation"""
    evaluator = SDRAgentEvaluator()
    await evaluator.run_comprehensive_evaluation()

if __name__ == "__main__":
    asyncio.run(main())