#!/usr/bin/env python3
"""
LangSmith Prompt Engineering Framework for SDR AI Agent
Proper evaluator integration and real metrics processing
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Union
from datetime import datetime
from dotenv import load_dotenv

# LangSmith imports
from langsmith import Client
from langsmith.evaluation import aevaluate
from langsmith.schemas import Run, Example

# Agent import
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from agent import app

load_dotenv()

class EnhancedSDRAgentEvaluator:
    
    
    def __init__(self):
        self.client = Client()
        self.project_name = "sdr-agent-comprehensive-evaluation"
        
    async def create_comprehensive_datasets(self):
        """Create 20 comprehensive datasets for SDR agent evaluation"""
        
        datasets = {
            # Dataset 1: Company Research - Basic
            "company_research_basic": [
                {
                    "name": "stripe_company_summary",
                    "input": "Give me a company summary for Stripe",
                    "expected_format": "text",
                    "category": "company_research",
                    "difficulty": "basic"
                },
                {
                    "name": "salesforce_business_model",
                    "input": "What is Salesforce's business model?",
                    "expected_format": "text", 
                    "category": "company_research",
                    "difficulty": "basic"
                },
                {
                    "name": "microsoft_focus_areas",
                    "input": "What are Microsoft's main business focus areas?",
                    "expected_format": "text",
                    "category": "company_research", 
                    "difficulty": "basic"
                }
            ],
            
            # Dataset 2: Company Research - Structured JSON
            "company_research_structured": [
                {
                    "name": "apple_structured_info",
                    "input": json.dumps({
                        "format": "json",
                        "fields": {
                            "company_name": "string",
                            "industry": "string", 
                            "employee_count": "integer",
                            "headquarters": "string",
                            "founded_year": "integer"
                        }
                    }) + "\n\nGet information about Apple Inc.",
                    "expected_format": "json",
                    "category": "company_research",
                    "difficulty": "intermediate"
                },
                {
                    "name": "google_business_data",
                    "input": json.dumps({
                        "format": "json",
                        "fields": {
                            "company_name": "string",
                            "primary_business": "string",
                            "revenue_model": "string",
                            "target_market": "string"
                        }
                    }) + "\n\nAnalyze Google's business structure",
                    "expected_format": "json",
                    "category": "company_research",
                    "difficulty": "intermediate"
                }
            ],
            
            # Dataset 3: Lead Qualification
            "lead_qualification": [
                {
                    "name": "saas_company_qualification",
                    "input": "Help me qualify Notion as a potential lead for our B2B sales automation tool",
                    "expected_format": "text",
                    "category": "lead_qualification",
                    "difficulty": "intermediate"
                },
                {
                    "name": "enterprise_lead_assessment",
                    "input": "Assess Shopify as a lead for enterprise marketing solutions",
                    "expected_format": "text",
                    "category": "lead_qualification", 
                    "difficulty": "advanced"
                }
            ],
            
            # Dataset 4: Competitive Analysis
            "competitive_analysis": [
                {
                    "name": "crm_competitors",
                    "input": "Compare Salesforce vs HubSpot for mid-market companies",
                    "expected_format": "text",
                    "category": "competitive_analysis",
                    "difficulty": "advanced"
                },
                {
                    "name": "marketing_automation_landscape",
                    "input": "Analyze the marketing automation competitive landscape",
                    "expected_format": "text",
                    "category": "competitive_analysis",
                    "difficulty": "advanced"
                }
            ],
            
            # Dataset 5: Contact Information Generation
            "contact_generation": [
                {
                    "name": "executive_contact_structured",
                    "input": json.dumps({
                        "format": "json",
                        "fields": {
                            "full_name": "string",
                            "position": "string",
                            "company": "string",
                            "email": "string",
                            "linkedin_url": "string"
                        }
                    }) + "\n\nGenerate contact info for Sarah Chen, VP of Marketing at Zoom",
                    "expected_format": "json",
                    "category": "contact_generation",
                    "difficulty": "basic"
                }
            ],
            
            # Dataset 6: Outreach Personalization
            "outreach_personalization": [
                {
                    "name": "personalized_email_hook",
                    "input": json.dumps({
                        "format": "json", 
                        "fields": {
                            "prospect_name": "string",
                            "company": "string",
                            "personalization_hook": "string",
                            "value_proposition": "string"
                        }
                    }) + "\n\nCreate personalized outreach for David Kim, Head of Growth at Figma",
                    "expected_format": "json",
                    "category": "outreach_personalization",
                    "difficulty": "advanced"
                }
            ],
            
            # Dataset 7: Market Intelligence
            "market_intelligence": [
                {
                    "name": "fintech_market_trends",
                    "input": "What are the current trends in the fintech market for B2B payments?",
                    "expected_format": "text",
                    "category": "market_intelligence",
                    "difficulty": "advanced"
                },
                {
                    "name": "saas_market_analysis",
                    "input": "Analyze the current SaaS market opportunities for sales tools",
                    "expected_format": "text", 
                    "category": "market_intelligence",
                    "difficulty": "advanced"
                }
            ],
            
            # Dataset 8: Prospect Prioritization
            "prospect_prioritization": [
                {
                    "name": "lead_scoring_criteria",
                    "input": json.dumps({
                        "format": "json",
                        "fields": {
                            "company_name": "string",
                            "priority_score": "integer",
                            "reasoning": "string",
                            "next_action": "string"
                        }
                    }) + "\n\nPrioritize Slack as a prospect for our team collaboration tool",
                    "expected_format": "json",
                    "category": "prospect_prioritization",
                    "difficulty": "advanced"
                }
            ],
            
            # Dataset 9: Industry Analysis
            "industry_analysis": [
                {
                    "name": "healthcare_tech_analysis",
                    "input": "Analyze the healthcare technology industry for sales opportunities",
                    "expected_format": "text",
                    "category": "industry_analysis",
                    "difficulty": "advanced"
                }
            ],
            
            # Dataset 10: Error Handling & Edge Cases
            "error_handling": [
                {
                    "name": "malformed_json_request",
                    "input": '{"format": "json", "fields": {"invalid": json}}',
                    "expected_format": "error_handling",
                    "category": "error_handling",
                    "difficulty": "basic"
                },
                {
                    "name": "unknown_company_query",
                    "input": json.dumps({
                        "format": "json",
                        "fields": {
                            "company_name": "string",
                            "industry": "string",
                            "employee_count": "integer"
                        }
                    }) + "\n\nGet information about XYZ Fictional Corp",
                    "expected_format": "json",
                    "category": "error_handling",
                    "difficulty": "intermediate"
                }
            ],
            
            # Dataset 11: Multi-step Research
            "multi_step_research": [
                {
                    "name": "comprehensive_company_analysis",
                    "input": "Research Atlassian for a comprehensive sales approach including company info, key contacts, and competitive positioning",
                    "expected_format": "text",
                    "category": "multi_step_research",
                    "difficulty": "advanced"
                }
            ],
            
            # Dataset 12: Sales Intelligence
            "sales_intelligence": [
                {
                    "name": "revenue_model_analysis",
                    "input": json.dumps({
                        "format": "json",
                        "fields": {
                            "company": "string",
                            "revenue_model": "string",
                            "pricing_strategy": "string",
                            "sales_approach": "string"
                        }
                    }) + "\n\nAnalyze Dropbox's revenue model and sales strategy",
                    "expected_format": "json",
                    "category": "sales_intelligence",
                    "difficulty": "advanced"
                }
            ],
            
            # Dataset 13: Technology Stack Analysis
            "tech_stack_analysis": [
                {
                    "name": "company_tech_stack",
                    "input": "What technology stack does Airbnb likely use for their platform?",
                    "expected_format": "text",
                    "category": "tech_stack_analysis",
                    "difficulty": "intermediate"
                }
            ],
            
            # Dataset 14: Partnership Opportunities
            "partnership_opportunities": [
                {
                    "name": "integration_partnerships",
                    "input": "Identify potential partnership opportunities between Slack and CRM platforms",
                    "expected_format": "text",
                    "category": "partnership_opportunities",
                    "difficulty": "advanced"
                }
            ],
            
            # Dataset 15: Funding & Investment Analysis
            "funding_analysis": [
                {
                    "name": "startup_funding_research",
                    "input": json.dumps({
                        "format": "json",
                        "fields": {
                            "company": "string",
                            "funding_stage": "string",
                            "total_funding": "string",
                            "growth_indicators": "string"
                        }
                    }) + "\n\nAnalyze OpenAI's funding and growth trajectory",
                    "expected_format": "json",
                    "category": "funding_analysis",
                    "difficulty": "intermediate"
                }
            ],
            
            # Dataset 16: Customer Success Stories
            "customer_success": [
                {
                    "name": "case_study_analysis",
                    "input": "Find customer success stories or case studies for Zendesk",
                    "expected_format": "text",
                    "category": "customer_success",
                    "difficulty": "intermediate"
                }
            ],
            
            # Dataset 17: Executive Profiling
            "executive_profiling": [
                {
                    "name": "ceo_background_research",
                    "input": json.dumps({
                        "format": "json",
                        "fields": {
                            "executive_name": "string",
                            "current_position": "string",
                            "company": "string",
                            "background": "string",
                            "key_initiatives": "string"
                        }
                    }) + "\n\nProfile Satya Nadella, CEO of Microsoft",
                    "expected_format": "json",
                    "category": "executive_profiling",
                    "difficulty": "advanced"
                }
            ],
            
            # Dataset 18: Product Analysis
            "product_analysis": [
                {
                    "name": "product_feature_analysis",
                    "input": "Analyze Notion's key product features and target market",
                    "expected_format": "text",
                    "category": "product_analysis",
                    "difficulty": "intermediate"
                }
            ],
            
            # Dataset 19: Compliance & Regulations
            "compliance_analysis": [
                {
                    "name": "gdpr_compliance_research",
                    "input": "How does Salesforce handle GDPR compliance for European customers?",
                    "expected_format": "text",
                    "category": "compliance_analysis",
                    "difficulty": "advanced"
                }
            ],
            
            # Dataset 20: Performance Benchmarking
            "performance_benchmarking": [
                {
                    "name": "response_time_test",
                    "input": "Quick company summary for Tesla",
                    "expected_format": "text",
                    "category": "performance_benchmarking",
                    "difficulty": "basic"
                },
                {
                    "name": "complex_json_performance",
                    "input": json.dumps({
                        "format": "json",
                        "fields": {
                            "company_name": "string",
                            "industry": "string",
                            "competitors": "string",
                            "market_position": "string",
                            "growth_rate": "string",
                            "key_products": "string",
                            "target_customers": "string",
                            "revenue_model": "string"
                        }
                    }) + "\n\nComprehensive analysis of Amazon's business",
                    "expected_format": "json",
                    "category": "performance_benchmarking",
                    "difficulty": "advanced"
                }
            ]
        }
        
        # Create datasets in LangSmith
        created_datasets = {}
        for dataset_name, test_cases in datasets.items():
            try:
                # Try to get existing dataset
                dataset = self.client.read_dataset(dataset_name=f"sdr-agent-{dataset_name}")
                print(f"✅ Using existing dataset: sdr-agent-{dataset_name}")
            except:
                # Create new dataset
                dataset = self.client.create_dataset(
                    dataset_name=f"sdr-agent-{dataset_name}",
                    description=f"SDR Agent evaluation dataset for {dataset_name.replace('_', ' ').title()}"
                )
                print(f"🆕 Created new dataset: sdr-agent-{dataset_name}")
                
                # Add examples to dataset - FIXED: Use "question" instead of "query"
                for case in test_cases:
                    self.client.create_example(
                        dataset_id=dataset.id,
                        inputs={"question": case["input"]},  # ✅ FIXED: Using "question"
                        outputs={"expected_format": case["expected_format"]},
                        metadata={
                            "test_case": case["name"],
                            "category": case["category"],
                            "difficulty": case["difficulty"]
                        }
                    )
            
            created_datasets[dataset_name] = dataset
            
        return created_datasets
    
    async def run_agent_evaluation(self, question: str) -> Dict[str, Any]:
        
        try:
            initial_state = {
                "input": question,
                "chat_history": [],
                "agent_outcome": None,
                "intermediate_steps": []
            }
            
            result = await app.ainvoke(initial_state)
            
            # Handle different response formats
            if hasattr(result["agent_outcome"], 'return_values'):
                return_values = result["agent_outcome"].return_values
                output = return_values.get("output", "")
                citations = return_values.get("citations", [])
            else:
                output = str(result["agent_outcome"])
                citations = []
            
            return {
                "success": True,
                "output": output,
                "citations": citations,
                "intermediate_steps": result.get("intermediate_steps", [])
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": f"Error occurred: {str(e)}",
                "citations": [],
                "intermediate_steps": []
            }
    
    def create_evaluators(self):
        
        
        # CRITICAL FIX: Use proper function signature for LangSmith evaluators
        def sdr_accuracy_evaluator(run: Run, example: Example) -> Dict[str, Any]:
            
            try:
                # Get output from run - try different possible locations
                output = ""
                if hasattr(run, 'outputs') and run.outputs:
                    output = run.outputs.get("output", "")
                elif hasattr(run, 'output'):
                    output = str(run.output)
                
                if not output:
                    return {
                        "key": "sdr_accuracy",
                        "score": 0.0,
                        "reason": "No output found in run"
                    }
                
                # Get metadata from example
                metadata = example.metadata or {}
                category = metadata.get("category", "")
                
                # SDR-specific keywords by category
                category_keywords = {
                    "company_research": ["company", "business", "industry", "revenue", "employees"],
                    "lead_qualification": ["lead", "prospect", "qualification", "fit", "opportunity"],
                    "competitive_analysis": ["competitor", "comparison", "market", "advantage", "positioning"],
                    "outreach_personalization": ["personalized", "hook", "value", "proposition", "outreach"],
                    "market_intelligence": ["market", "trend", "opportunity", "growth", "analysis"]
                }
                
                relevant_keywords = category_keywords.get(category, ["business", "sales", "professional"])
                keyword_matches = sum(1 for keyword in relevant_keywords if keyword.lower() in output.lower())
                
                accuracy_score = min(1.0, keyword_matches / len(relevant_keywords))
                
                return {
                    "key": "sdr_accuracy",
                    "score": accuracy_score,
                    "reason": f"Category: {category}, Keywords matched: {keyword_matches}/{len(relevant_keywords)}"
                }
            except Exception as e:
                return {"key": "sdr_accuracy", "score": 0, "reason": f"Error: {str(e)}"}
        
        def json_structure_evaluator(run: Run, example: Example) -> Dict[str, Any]:
            
            try:
                # Get output from run
                output = ""
                if hasattr(run, 'outputs') and run.outputs:
                    output = run.outputs.get("output", "")
                elif hasattr(run, 'output'):
                    output = str(run.output)
                
                if not output:
                    return {
                        "key": "json_structure",
                        "score": 0.0,
                        "reason": "No output found in run"
                    }
                
                # Get expected format
                expected_format = ""
                if hasattr(example, 'outputs') and example.outputs:
                    expected_format = example.outputs.get("expected_format", "")
                
                if expected_format == "json":
                    try:
                        parsed_json = json.loads(output)
                        return {
                            "key": "json_structure",
                            "score": 1.0,
                            "reason": "Valid JSON structure"
                        }
                    except json.JSONDecodeError:
                        return {
                            "key": "json_structure", 
                            "score": 0.0,
                            "reason": "Invalid JSON structure"
                        }
                else:
                    # For non-JSON, check it's not accidentally JSON
                    try:
                        json.loads(output.strip())
                        return {
                            "key": "json_structure",
                            "score": 0.5,
                            "reason": "Unexpected JSON format for text request"
                        }
                    except json.JSONDecodeError:
                        return {
                            "key": "json_structure",
                            "score": 1.0,
                            "reason": "Correct non-JSON format"
                        }
            except Exception as e:
                return {"key": "json_structure", "score": 0, "reason": f"Error: {str(e)}"}
        
        def citation_compliance_evaluator(run: Run, example: Example) -> Dict[str, Any]:
            
            try:
                # Get output from run
                output = ""
                if hasattr(run, 'outputs') and run.outputs:
                    output = run.outputs.get("output", "")
                    citations = run.outputs.get("citations", [])
                elif hasattr(run, 'output'):
                    output = str(run.output)
                    citations = []
                else:
                    return {
                        "key": "citation_compliance",
                        "score": 0.0,
                        "reason": "No output found in run"
                    }
                
                # Check for citation indicators
                citation_indicators = ["Source:", "Sources:", "Based on", "📚", "General knowledge"]
                has_citations = any(indicator in output for indicator in citation_indicators) or len(citations) > 0
                
                score = 1.0 if has_citations else 0.0
                
                return {
                    "key": "citation_compliance",
                    "score": score,
                    "reason": f"Citations present: {has_citations}"
                }
            except Exception as e:
                return {"key": "citation_compliance", "score": 0, "reason": f"Error: {str(e)}"}
        
        def response_completeness_evaluator(run: Run, example: Example) -> Dict[str, Any]:
            
            try:
                # Get output from run
                output = ""
                if hasattr(run, 'outputs') and run.outputs:
                    output = run.outputs.get("output", "")
                elif hasattr(run, 'output'):
                    output = str(run.output)
                
                if not output:
                    return {
                        "key": "response_completeness",
                        "score": 0.0,
                        "reason": "No output found in run"
                    }
                
                # Get difficulty from metadata
                metadata = example.metadata or {}
                difficulty = metadata.get("difficulty", "basic")
                
                # Length expectations by difficulty
                min_lengths = {"basic": 50, "intermediate": 100, "advanced": 150}
                min_length = min_lengths.get(difficulty, 50)
                
                completeness_score = min(1.0, len(output) / min_length)
                
                return {
                    "key": "response_completeness",
                    "score": completeness_score,
                    "reason": f"Length: {len(output)} chars, Expected: {min_length}+ for {difficulty}"
                }
            except Exception as e:
                return {"key": "response_completeness", "score": 0, "reason": f"Error: {str(e)}"}
        
        def error_handling_evaluator(run: Run, example: Example) -> Dict[str, Any]:
            
            try:
                
                metadata = example.metadata or {}
                category = metadata.get("category", "")
                
                
                output = ""
                success = True
                if hasattr(run, 'outputs') and run.outputs:
                    output = run.outputs.get("output", "")
                    success = run.outputs.get("success", True)
                elif hasattr(run, 'output'):
                    output = str(run.output)
                
                if category == "error_handling":
                    
                    if "error" in output.lower() or "invalid" in output.lower() or not success:
                        return {
                            "key": "error_handling",
                            "score": 1.0,
                            "reason": "Graceful error handling"
                        }
                    else:
                        return {
                            "key": "error_handling",
                            "score": 0.5,
                            "reason": "Should handle error more explicitly"
                        }
                else:
                   
                    score = 1.0 if success else 0.0
                    return {
                        "key": "error_handling",
                        "score": score,
                        "reason": f"Success: {success}"
                    }
            except Exception as e:
                return {"key": "error_handling", "score": 0, "reason": f"Error: {str(e)}"}
        
        return [
            sdr_accuracy_evaluator,
            json_structure_evaluator, 
            citation_compliance_evaluator,
            response_completeness_evaluator,
            error_handling_evaluator
        ]
    
    def detailed_debug_first_result(self, results: Dict[str, Any]):
        
        print("\n🔬 DETAILED DEBUG OF FIRST RESULT:")
        print("=" * 60)
        
        for dataset_name, dataset_results in list(results.items())[:1]:  
            print(f"\n📊 Analyzing: {dataset_name}")
            
            if isinstance(dataset_results, dict):
                print("   Result is a dictionary (error case)")
                return
            
            # Get the actual results
            actual_results = list(dataset_results._results)
            if actual_results:
                first_result = actual_results[0]
                print(f"   First result type: {type(first_result)}")
                print(f"   First result: {first_result}")
                
                if isinstance(first_result, dict):
                    print(f"   Keys: {list(first_result.keys())}")
                    for key, value in first_result.items():
                        print(f"     {key}: {type(value)} = {str(value)[:100]}...")
        
        print("=" * 60)
    
    def process_real_evaluation_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        
        print("\n📊 PROCESSING REAL EVALUATION RESULTS:")
        print("=" * 50)
        
        all_scores = {}
        dataset_performance = {}
        total_experiments = 0
        successful_experiments = 0
        
        for dataset_name, dataset_results in results.items():
            print(f"\n📋 Processing: {dataset_name}")
            
            
            if isinstance(dataset_results, dict):
                if "error" in dataset_results:
                    print(f"   ❌ Error: {dataset_results['error']}")
                continue
            
            
            try:
                # Get results from AsyncExperimentResults
                actual_results = list(dataset_results._results)
                print(f"   📈 Found {len(actual_results)} results")
                
                dataset_scores = {
                    "sdr_accuracy": [],
                    "json_structure": [], 
                    "citation_compliance": [],
                    "response_completeness": [],
                    "error_handling": []
                }
                
                
                for i, result in enumerate(actual_results):
                    total_experiments += 1
                    print(f"   🔍 Processing result {i+1}: {type(result)}")
                    
                    
                    if isinstance(result, dict) and 'evaluation_results' in result:
                        eval_results_dict = result['evaluation_results']
                        print(f"     📊 Found evaluation_results: {type(eval_results_dict)}")
                        
                        
                        if isinstance(eval_results_dict, dict) and 'results' in eval_results_dict:
                            eval_results_list = eval_results_dict['results']
                            print(f"     📋 Found {len(eval_results_list)} evaluation results")
                            
                            
                            for eval_result in eval_results_list:
                                
                                if hasattr(eval_result, 'key') and hasattr(eval_result, 'score'):
                                    metric_key = eval_result.key
                                    score = eval_result.score
                                    
                                    if metric_key in dataset_scores:
                                        dataset_scores[metric_key].append(score)
                                        print(f"     ✅ {metric_key}: {score}")
                                
                                elif isinstance(eval_result, dict) and 'key' in eval_result and 'score' in eval_result:
                                    metric_key = eval_result['key']
                                    score = eval_result['score']
                                    
                                    if metric_key in dataset_scores:
                                        dataset_scores[metric_key].append(score)
                                        print(f"     ✅ {metric_key}: {score}")
                            
                            successful_experiments += 1
                        else:
                            print(f"     ⚠️  evaluation_results doesn't have 'results' key")
                            print(f"     📋 Available keys: {list(eval_results_dict.keys()) if isinstance(eval_results_dict, dict) else 'Not a dict'}")
                    else:
                        # No evaluation results found in this result
                        print(f"     ⚠️  No evaluation_results key found")
                        if isinstance(result, dict):
                            print(f"     📋 Available keys: {list(result.keys())}")
                
                # Calculate averages for this dataset
                dataset_avg_scores = {}
                for metric, scores in dataset_scores.items():
                    if scores:
                        avg_score = sum(scores) / len(scores)
                        dataset_avg_scores[metric] = avg_score
                        print(f"   📊 {metric}: {avg_score:.3f} (from {len(scores)} scores)")
                        
                        # Add to overall scores
                        if metric not in all_scores:
                            all_scores[metric] = []
                        all_scores[metric].extend(scores)
                    else:
                        dataset_avg_scores[metric] = 0.0
                
                dataset_performance[dataset_name] = dataset_avg_scores
                
            except Exception as e:
                print(f"   ❌ Error processing {dataset_name}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total Experiments: {total_experiments}")
        print(f"   Successful Experiments: {successful_experiments}")
        print(f"   Success Rate: {(successful_experiments/total_experiments*100):.1f}%" if total_experiments > 0 else "   Success Rate: 0%")
        
        return {
            "all_scores": all_scores,
            "dataset_performance": dataset_performance,
            "total_experiments": total_experiments,
            "successful_experiments": successful_experiments
        }
    
    async def run_comprehensive_evaluation(self):
        
        print("🚀 Starting Enhanced LangSmith SDR Agent Evaluation")
        print("📊 Evaluating across comprehensive datasets")
        print("=" * 70)
        
       
        print("📋 Creating comprehensive evaluation datasets...")
        datasets = await self.create_comprehensive_datasets()
        
        # Create evaluators
        evaluators = self.create_evaluators()
        print(f"✅ Created {len(evaluators)} evaluators")
        
        # Define the agent chain for evaluation
        async def sdr_agent_chain(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Chain function for SDR agent evaluation"""
            question = inputs.get("question") or inputs.get("query", "")
            if not question:
                raise ValueError("No question or query provided in inputs")
            
            result = await self.run_agent_evaluation(question)
            print(f"🤖 Agent result for '{question[:50]}...': success={result.get('success', False)}")
            return result
        
        # Run evaluation on each dataset
        all_results = {}
        total_datasets = len(datasets)
        
        for i, (dataset_name, dataset) in enumerate(datasets.items(), 1):
            print(f"\n⚡ Evaluating Dataset {i}/{total_datasets}: {dataset_name}")
            print(f"   📁 Dataset: sdr-agent-{dataset_name}")
            
            try:
                
                experiment_name = f"sdr_agent_eval_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                print("   🔄 Running aevaluate...")
                results = await aevaluate(
                    sdr_agent_chain,
                    data=f"sdr-agent-{dataset_name}",
                    evaluators=evaluators,
                    experiment_prefix=experiment_name,
                    description=f"SDR Agent evaluation for {dataset_name.replace('_', ' ').title()}"
                )
                
                all_results[dataset_name] = results
                print(f"   ✅ Completed: {dataset_name}")
                
            except Exception as e:
                print(f"   ❌ Failed: {dataset_name} - {str(e)}")
                all_results[dataset_name] = {"error": str(e)}
        
       
        self.detailed_debug_first_result(all_results)
        
        
        processed_results = self.process_real_evaluation_results(all_results)
        
        
        self.generate_simple_report(processed_results)
        
        return all_results
    
    def generate_simple_report(self, processed_results: Dict[str, Any]):
        
        print("\n" + "=" * 80)
        print("🎯 SDR AGENT EVALUATION RESULTS")
        print("=" * 80)
        
        all_scores = processed_results["all_scores"]
        dataset_performance = processed_results["dataset_performance"]
        total_experiments = processed_results["total_experiments"]
        successful_experiments = processed_results["successful_experiments"]
        
        
        aggregate_scores = {}
        for metric, scores in all_scores.items():
            if scores:
                aggregate_scores[metric] = sum(scores) / len(scores)
            else:
                aggregate_scores[metric] = 0.0
        
        overall_score = sum(aggregate_scores.values()) / len(aggregate_scores) if aggregate_scores else 0.0
        
        print(f"\n📊 EXPERIMENT SUMMARY:")
        print(f"   Total Experiments: {total_experiments}")
        print(f"   Successful Experiments: {successful_experiments}")
        print(f"   Success Rate: {(successful_experiments/total_experiments*100):.1f}%" if total_experiments > 0 else "   Success Rate: 0%")
        
        print(f"\n🏆 OVERALL PERFORMANCE SCORE: {overall_score:.3f}")
        
        if aggregate_scores and max(aggregate_scores.values()) > 0:
            print(f"\n📈 METRIC BREAKDOWN:")
            for metric, score in aggregate_scores.items():
                status = "🟢" if score >= 0.9 else "🟡" if score >= 0.8 else "🔴"
                metric_name = metric.replace("_", " ").title()
                print(f"   {status} {metric_name.ljust(25)}: {score:.3f}")
        else:
            print("\n⚠️  No evaluation scores found. This suggests:")
            print("   1. Evaluators are not being executed")
            print("   2. Results structure is different than expected")
            print("   3. There might be an issue with the evaluation pipeline")
        
        print("=" * 80)

async def main():
    
    evaluator = EnhancedSDRAgentEvaluator()
    await evaluator.run_comprehensive_evaluation()

if __name__ == "__main__":
    asyncio.run(main())





