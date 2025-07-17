import os
import json
import asyncio
from typing import TypedDict, List, Union, Dict, Any
from dotenv import load_dotenv
import contextlib

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langsmith import traceable

try:
    from .brightdata_client import BrightDataMCPClient
except ImportError:
    from brightdata_client import BrightDataMCPClient

# --- Environment and Client Setup ---
load_dotenv()

# Global client instance - will be properly initialized
_brightdata_client = None

async def get_brightdata_client():
    """Get or create connected BrightData client instance"""
    global _brightdata_client
    if _brightdata_client is None:
        _brightdata_client = BrightDataMCPClient()
        await _brightdata_client.connect()
    return _brightdata_client

# --- Enhanced Agent State with Tool Tracking ---
class AgentState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: list[tuple[AgentAction, str]]
    # NEW: Track tools used and their purposes
    tools_used: list[Dict[str, Any]]
    tool_analysis: Dict[str, Any]

# --- Enhanced Tools with Better Descriptions and Categories ---
@tool
async def search_web(query: str) -> dict:
    """🔍 Web Search (MCP): Searches the web for current information, news, trends, and real-time data using BrightData's web search capabilities."""
    try:
        client = await get_brightdata_client()
        print(f"🔍 Searching web for: {query}")
        
        # Use the search_engine tool directly with correct parameters
        result = await client.call_tool("search_engine", {
            "query": query,
            "engine": "google"
        })
        
        # Check if we got meaningful results
        if result.get("success") and result.get("data"):
            data = result.get("data")
            print(f"✅ Web search found results for: {query} ({len(str(data))} chars)")
            
            # Process and extract meaningful information
            if isinstance(data, str) and len(data) > 100:
                # Extract key information from search results
                lines = data.split('\n')
                search_snippets = []
                
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 30:  # Skip short lines
                        # Look for relevant content
                        query_words = query.lower().split()
                        if any(word in line.lower() for word in query_words):
                            if not line.startswith('#') and not line.startswith('http'):
                                search_snippets.append(line[:250])  # Limit snippet length
                
                # Add processed results
                result["search_snippets"] = search_snippets[:8]  # Top 8 relevant snippets
                result["snippet_count"] = len(search_snippets)
                result["data_preview"] = data[:500] + "..." if len(data) > 500 else data
                
                print(f"📊 Extracted {len(search_snippets)} relevant snippets")
            
            # Add tool metadata to result
            result["_tool_info"] = {
                "tool_name": "search_web",
                "tool_category": "Web Intelligence", 
                "mcp_provider": "BrightData",
                "purpose": f"Searched the web for: {query}",
                "data_type": "Processed web search results"
            }
            return result
        else:
            error_msg = result.get("error", "No results found")
            print(f"❌ Web search failed: {error_msg}")
            return {
                "success": False,
                "error": f"Web search failed: {error_msg}",
                "query": query,
                "_tool_info": {
                    "tool_name": "search_web",
                    "tool_category": "Web Intelligence",
                    "mcp_provider": "BrightData",
                    "purpose": f"Attempted web search for: {query}",
                    "status": "failed"
                }
            }
            
    except Exception as e:
        print(f"❌ Web search error: {str(e)}")
        return {
            "success": False,
            "error": f"Web search failed: {str(e)}",
            "query": query,
            "_tool_info": {
                "tool_name": "search_web",
                "tool_category": "Web Intelligence",
                "mcp_provider": "BrightData",
                "purpose": f"Attempted web search for: {query}",
                "status": "failed"
            }
        }

@tool
async def scrape_url(url: str) -> dict:
    """📄 URL Scraper (MCP): Extracts content from specific web pages in markdown format using BrightData's web scraping technology."""
    try:
        client = await get_brightdata_client()
        result = await client.scrape_url(url, format="markdown")
        
        result["_tool_info"] = {
            "tool_name": "scrape_url",
            "tool_category": "Content Extraction",
            "mcp_provider": "BrightData", 
            "purpose": f"Extracted content from: {url}",
            "data_type": "Webpage content (markdown)"
        }
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"URL scraping failed: {str(e)}",
            "tool": "scrape_url",
            "_tool_info": {
                "tool_name": "scrape_url",
                "tool_category": "Content Extraction",
                "mcp_provider": "BrightData",
                "purpose": f"Attempted to scrape: {url}",
                "status": "failed"
            }
        }

@tool
async def get_linkedin_profile(profile_url: str) -> dict:
    """👤 LinkedIn Profile (MCP): Retrieves detailed LinkedIn profile information including professional background, experience, and connections using BrightData's LinkedIn data extraction."""
    try:
        client = await get_brightdata_client()
        result = await client.get_linkedin_profile(profile_url)
        
        result["_tool_info"] = {
            "tool_name": "get_linkedin_profile",
            "tool_category": "Professional Intelligence",
            "mcp_provider": "BrightData",
            "purpose": f"Retrieved LinkedIn profile: {profile_url}",
            "data_type": "Professional profile data"
        }
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"LinkedIn profile fetch failed: {str(e)}",
            "tool": "get_linkedin_profile",
            "_tool_info": {
                "tool_name": "get_linkedin_profile", 
                "tool_category": "Professional Intelligence",
                "mcp_provider": "BrightData",
                "purpose": f"Attempted LinkedIn profile fetch: {profile_url}",
                "status": "failed"
            }
        }

@tool
async def get_company_info(company_name: str, platform: str = "auto") -> dict:
    """🏢 Company Intelligence (MCP): Gathers comprehensive company information from LinkedIn, Crunchbase, or ZoomInfo using BrightData's business intelligence platform."""
    try:
        client = await get_brightdata_client()
        
        # Define platform priority for auto mode
        platforms_to_try = []
        if platform == "auto":
            platforms_to_try = ["linkedin", "crunchbase", "zoominfo"]
        else:
            platforms_to_try = [platform]
        
        last_error = None
        
        # Try each platform until we get results
        for platform_name in platforms_to_try:
            try:
                print(f"🔍 Searching for {company_name} {platform_name} URL...")
                
                # Step 1: Search for the company's URL on the specific platform
                if platform_name == "linkedin":
                    search_query = f"{company_name} site:linkedin.com/company"
                    tool_name = "web_data_linkedin_company_profile"
                elif platform_name == "crunchbase":
                    search_query = f"{company_name} site:crunchbase.com/organization"
                    tool_name = "web_data_crunchbase_company"
                elif platform_name == "zoominfo":
                    search_query = f"{company_name} site:zoominfo.com/c"
                    tool_name = "web_data_zoominfo_company_profile"
                else:
                    continue
                
                # Search for the URL
                search_result = await client.call_tool("search_engine", {
                    "query": search_query,
                    "num_results": 5
                })
                
                if not search_result.get("success") or not search_result.get("data"):
                    print(f"⚠️ No search results for {platform_name}")
                    last_error = f"{platform_name}: No search results found"
                    continue
                
                # Extract URLs from search results
                search_data = search_result["data"]
                urls = []
                
                # Simple URL extraction from search results
                import re
                if platform_name == "linkedin":
                    url_pattern = r'https?://[a-zA-Z0-9.-]*linkedin\.com/company/[^\s<>"\']*'
                elif platform_name == "crunchbase":
                    url_pattern = r'https?://[a-zA-Z0-9.-]*crunchbase\.com/organization/[^\s<>"\']*'
                elif platform_name == "zoominfo":
                    url_pattern = r'https?://[a-zA-Z0-9.-]*zoominfo\.com/c/[^\s<>"\']*'
                
                found_urls = re.findall(url_pattern, search_data)
                if found_urls:
                    # Use the first URL found and clean it up
                    company_url = found_urls[0].rstrip('/').rstrip(')').rstrip(',').rstrip('.')
                    print(f"✅ Found {platform_name} URL: {company_url}")
                    
                    # Step 2: Use the URL to get company data
                    print(f"📊 Extracting data from {platform_name}...")
                    result = await client.call_tool(tool_name, {
                        "url": company_url
                    })
                    
                    # Check if we got meaningful data
                    if result.get("success") and result.get("data"):
                        data = result.get("data")
                        # Check if data is not empty
                        if isinstance(data, dict) and data:
                            result["_tool_info"] = {
                                "tool_name": "get_company_info",
                                "tool_category": "Business Intelligence",
                                "mcp_provider": "BrightData",
                                "purpose": f"Retrieved {company_name} data from {platform_name}",
                                "data_type": f"Company intelligence from {platform_name}",
                                "source_platform": platform_name,
                                "source_url": company_url
                            }
                            print(f"✅ Successfully retrieved data from {platform_name}")
                            return result
                        elif isinstance(data, str) and len(data.strip()) > 0:
                            result["_tool_info"] = {
                                "tool_name": "get_company_info",
                                "tool_category": "Business Intelligence",
                                "mcp_provider": "BrightData",
                                "purpose": f"Retrieved {company_name} data from {platform_name}",
                                "data_type": f"Company intelligence from {platform_name}",
                                "source_platform": platform_name,
                                "source_url": company_url
                            }
                            print(f"✅ Successfully retrieved data from {platform_name}")
                            return result
                        else:
                            print(f"⚠️ {platform_name} returned empty data for {company_name}")
                            last_error = f"{platform_name} returned empty data"
                    else:
                        error_msg = result.get("error", "Unknown error")
                        print(f"❌ {platform_name} data extraction failed: {error_msg}")
                        last_error = f"{platform_name}: {error_msg}"
                else:
                    print(f"⚠️ No {platform_name} URLs found for {company_name}")
                    last_error = f"{platform_name}: No URLs found"
                    
            except Exception as e:
                print(f"❌ Error with {platform_name}: {str(e)}")
                last_error = f"{platform_name}: {str(e)}"
                continue
        
        # If all platforms failed, return failure with details
        return {
            "success": False,
            "error": f"All platforms failed to retrieve data for {company_name}. Last error: {last_error}",
            "company_name": company_name,
            "platforms_tried": platforms_to_try,
            "_tool_info": {
                "tool_name": "get_company_info",
                "tool_category": "Business Intelligence",
                "mcp_provider": "BrightData",
                "purpose": f"Attempted to get {company_name} data from multiple sources",
                "status": "failed",
                "platforms_tried": platforms_to_try
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Company info fetch failed: {str(e)}",
            "company_name": company_name,
            "_tool_info": {
                "tool_name": "get_company_info",
                "tool_category": "Business Intelligence", 
                "mcp_provider": "BrightData",
                "purpose": f"Attempted to get {company_name} data",
                "status": "failed"
            }
        }

@tool
async def search_jobs(query: str, location: str = "") -> dict:
    """💼 Job Intelligence (MCP): Searches LinkedIn for job listings, hiring trends, and employment opportunities using BrightData's job market data."""
    try:
        client = await get_brightdata_client()
        result = await client.search_jobs(query, location)
        
        result["_tool_info"] = {
            "tool_name": "search_jobs",
            "tool_category": "Job Market Intelligence",
            "mcp_provider": "BrightData",
            "purpose": f"Searched jobs: {query}" + (f" in {location}" if location else ""),
            "data_type": "Job listings and hiring data"
        }
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Job search failed: {str(e)}",
            "tool": "search_jobs",
            "_tool_info": {
                "tool_name": "search_jobs",
                "tool_category": "Job Market Intelligence",
                "mcp_provider": "BrightData", 
                "purpose": f"Attempted job search: {query}",
                "status": "failed"
            }
        }

@tool
async def get_product_info(product_query: str, platform: str = "amazon") -> dict:
    """🛒 Product Intelligence (MCP): Retrieves product information, pricing, and market data from e-commerce platforms using BrightData's retail intelligence."""
    try:
        client = await get_brightdata_client()
        result = await client.get_product_info(product_query, platform)
        
        result["_tool_info"] = {
            "tool_name": "get_product_info",
            "tool_category": "Retail Intelligence",
            "mcp_provider": "BrightData",
            "purpose": f"Retrieved product info: {product_query} from {platform}",
            "data_type": f"Product data from {platform}"
        }
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Product info fetch failed: {str(e)}",
            "tool": "get_product_info",
            "_tool_info": {
                "tool_name": "get_product_info",
                "tool_category": "Retail Intelligence",
                "mcp_provider": "BrightData",
                "purpose": f"Attempted product search: {product_query}",
                "status": "failed"
            }
        }

@tool
async def research_company_web(company_name: str) -> dict:
    """🔍 Company Web Research (MCP): Falls back to web search for company information when direct company tools fail."""
    try:
        client = await get_brightdata_client()
        
        # Try multiple search queries for comprehensive company information
        search_queries = [
            f"{company_name} company information",
            f"{company_name} business model revenue",
            f"{company_name} headquarters employees industry",
            f"{company_name} about company profile"
        ]
        
        all_results = []
        successful_searches = 0
        
        for query in search_queries:
            try:
                print(f"🔍 Web searching: {query}")
                result = await client.call_tool("search_engine", {
                    "query": query,
                    "num_results": 5
                })
                
                if result.get("success") and result.get("data"):
                    all_results.append({
                        "query": query,
                        "data": result["data"]
                    })
                    successful_searches += 1
                    print(f"✅ Found results for: {query}")
                else:
                    print(f"⚠️ No results for: {query}")
                    
            except Exception as e:
                print(f"❌ Search failed for '{query}': {str(e)}")
                continue
        
        if successful_searches > 0:
            return {
                "success": True,
                "data": {
                    "company_name": company_name,
                    "search_results": all_results,
                    "total_searches": len(search_queries),
                    "successful_searches": successful_searches
                },
                "_tool_info": {
                    "tool_name": "research_company_web",
                    "tool_category": "Business Intelligence",
                    "mcp_provider": "BrightData",
                    "purpose": f"Web research for {company_name} company information",
                    "data_type": "Web search company data"
                }
            }
        else:
            return {
                "success": False,
                "error": f"No web search results found for {company_name}",
                "company_name": company_name,
                "_tool_info": {
                    "tool_name": "research_company_web",
                    "tool_category": "Business Intelligence",
                    "mcp_provider": "BrightData",
                    "purpose": f"Attempted web research for {company_name}",
                    "status": "failed"
                }
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Company web research failed: {str(e)}",
            "company_name": company_name,
            "_tool_info": {
                "tool_name": "research_company_web",
                "tool_category": "Business Intelligence",
                "mcp_provider": "BrightData",
                "purpose": f"Attempted web research for {company_name}",
                "status": "failed"
            }
        }

# List of tools for the agent
tools = [search_web, scrape_url, get_linkedin_profile, get_company_info, search_jobs, get_product_info, research_company_web]

# Create a ToolNode to handle tool execution
tool_node = ToolNode(tools)

# --- Enhanced Prompt with Tool Transparency ---
SDR_SYSTEM_PROMPT = """
You are an elite AI assistant specifically designed for Sales Development Representatives (SDRs). Your expertise lies in providing actionable, precise, and highly relevant information that directly supports outbound sales activities, lead qualification, and prospect research.

CORE SDR FOCUS AREAS:
- Lead research and qualification
- Company intelligence gathering  
- Contact information discovery
- Competitive analysis
- Outreach personalization
- Market intelligence
- Prospect prioritization

AVAILABLE MCP TOOLS:
{tools}

CRITICAL TOOL SELECTION RULES:
You MUST use MCP tools when the user query contains ANY of these indicators:
- "latest", "recent", "current", "news", "trends", "search" → Use search_web
- "company", "business", "organization" + info/data/research → Use get_company_info  
- "linkedin", "profile", "executive", "person" → Use get_linkedin_profile
- "jobs", "hiring", "employment" → Use search_jobs
- URLs starting with "http" → Use scrape_url
- "product", "pricing", "competitor" → Use get_product_info

TOOL SELECTION LOGIC:
User Question: {question}
Intermediate Steps: {intermediate_steps}

DECISION PROCESS:
1. IF this is initial request AND requires real-time/current data OR specific company/person research:
   RESPOND WITH EXACT FORMAT: {{"tool": "tool_name", "tool_input": {{"param": "value"}}}}
   
2. IF this is final response phase (intermediate_steps has results):
   Provide comprehensive response with citations and tool explanations

3. ONLY provide direct knowledge-based answers for general SDR advice/strategies that don't require current data

FOR TOOL SELECTION, USE THESE EXACT FORMATS:
- Web Search: {{"tool": "search_web", "tool_input": {{"query": "search terms here"}}}}
- Company Info: {{"tool": "get_company_info", "tool_input": {{"company_name": "Company Name", "platform": "auto"}}}}
- LinkedIn Profile: {{"tool": "get_linkedin_profile", "tool_input": {{"profile_url": "linkedin_url"}}}}
- Jobs: {{"tool": "search_jobs", "tool_input": {{"query": "job search terms", "location": "location"}}}}
- URL Scraping: {{"tool": "scrape_url", "tool_input": {{"url": "url_to_scrape"}}}}
- Product Info: {{"tool": "get_product_info", "tool_input": {{"product_query": "product search", "platform": "amazon"}}}}

Your response:
"""

prompt = PromptTemplate.from_template(SDR_SYSTEM_PROMPT)

llm = GoogleGenerativeAI(model=os.getenv("GOOGLE_MODEL", "gemini-2.5-Flash"), temperature=1.0)
agent_runnable = prompt | llm

# --- Helper Functions ---
def analyze_query_for_tools(user_input: str) -> Dict[str, Any]:
    """Analyze user query and predict which tools might be needed"""
    query_lower = user_input.lower()
    
    analysis = {
        "predicted_tools": [],
        "reasoning": [],
        "query_type": "unknown",
        "data_sources_needed": []
    }
    
    # Web search indicators
    if any(term in query_lower for term in ["latest", "recent", "current", "news", "trends", "search"]):
        analysis["predicted_tools"].append({
            "tool": "search_web",
            "reason": "Query requires current/recent information",
            "category": "Web Intelligence"
        })
        analysis["data_sources_needed"].append("Real-time web data")
    
    # Company intelligence indicators  
    if any(term in query_lower for term in ["company", "business", "organization", "firm", "corporation"]):
        analysis["predicted_tools"].append({
            "tool": "get_company_info", 
            "reason": "Query requires company/business information",
            "category": "Business Intelligence"
        })
        analysis["data_sources_needed"].append("Company databases")
    
    # LinkedIn profile indicators
    if any(term in query_lower for term in ["linkedin", "profile", "executive", "ceo", "founder", "person"]):
        analysis["predicted_tools"].append({
            "tool": "get_linkedin_profile",
            "reason": "Query involves professional profile research", 
            "category": "Professional Intelligence"
        })
        analysis["data_sources_needed"].append("LinkedIn professional data")
    
    # Job market indicators
    if any(term in query_lower for term in ["jobs", "hiring", "employment", "careers", "positions"]):
        analysis["predicted_tools"].append({
            "tool": "search_jobs",
            "reason": "Query relates to job market or hiring intelligence",
            "category": "Job Market Intelligence" 
        })
        analysis["data_sources_needed"].append("Job market data")
    
    # URL scraping indicators
    if any(term in query_lower for term in ["http", "www", "website", "page", "scrape"]):
        analysis["predicted_tools"].append({
            "tool": "scrape_url",
            "reason": "Query requires specific website content extraction",
            "category": "Content Extraction"
        })
        analysis["data_sources_needed"].append("Website content")
    
    # Product intelligence indicators
    if any(term in query_lower for term in ["product", "pricing", "competitor analysis", "market analysis"]):
        analysis["predicted_tools"].append({
            "tool": "get_product_info",
            "reason": "Query involves product or competitive intelligence",
            "category": "Retail Intelligence"
        })
        analysis["data_sources_needed"].append("Product/market data")
    
    # Determine query type
    if "json" in query_lower and "format" in query_lower:
        analysis["query_type"] = "structured_data_request"
    elif any(term in query_lower for term in ["analyze", "research", "investigate"]):
        analysis["query_type"] = "research_request"
    elif any(term in query_lower for term in ["find", "search", "get", "retrieve"]):
        analysis["query_type"] = "data_retrieval"
    else:
        analysis["query_type"] = "general_inquiry"
    
    return analysis

def format_tool_usage_summary(tools_used: List[Dict[str, Any]]) -> str:
    """Create a user-friendly summary of tools used"""
    if not tools_used:
        return "🤖 **AI Processing**: Response generated using built-in knowledge base"
    
    summary = "\n\n## 🛠️ **MCP Tools Used:**\n"
    
    categories = {}
    for tool_info in tools_used:
        category = tool_info.get("tool_category", "Unknown")
        if category not in categories:
            categories[category] = []
        categories[category].append(tool_info)
    
    for category, tool_list in categories.items():
        summary += f"\n### 📊 {category}\n"
        for tool_info in tool_list:
            icon = {
                "Web Intelligence": "🔍",
                "Business Intelligence": "🏢", 
                "Professional Intelligence": "👤",
                "Job Market Intelligence": "💼",
                "Content Extraction": "📄",
                "Retail Intelligence": "🛒"
            }.get(category, "🔧")
            
            summary += f"- {icon} **{tool_info.get('tool_name', 'Unknown')}**: {tool_info.get('purpose', 'Data collection')}\n"
            summary += f"  - *Provider*: {tool_info.get('mcp_provider', 'BrightData')}\n"
            summary += f"  - *Data Type*: {tool_info.get('data_type', 'Various')}\n"
    
    return summary

# Keep existing helper functions (clean_json_response, validate_json_fields, extract_json_structure)
def clean_json_response(response: str) -> str:
    """Clean JSON response by extracting only the JSON object"""
    response = response.strip()
    
    # Remove markdown code blocks first
    if '```json' in response:
        start = response.find('```json') + 7
        end = response.find('```', start)
        if end != -1:
            response = response[start:end].strip()
    elif '```' in response:
        start = response.find('```') + 3
        end = response.find('```', start)
        if end != -1:
            response = response[start:end].strip()
    
    # More aggressive JSON extraction using regex
    import re
    
    # Try to find a complete JSON object
    json_patterns = [
        r'\{(?:[^{}]|{[^{}]*})*\}',  # Simple nested object
        r'\{[^}]*\}',  # Simple object
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            # Return the first valid JSON match
            for match in matches:
                try:
                    # Test if it's valid JSON
                    json.loads(match)
                    return match.strip()
                except json.JSONDecodeError:
                    continue
    
    # If no valid JSON found, try to extract from the beginning
    if response.startswith('{'):
        # Find the matching closing brace
        brace_count = 0
        for i, char in enumerate(response):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    potential_json = response[:i+1]
                    try:
                        json.loads(potential_json)
                        return potential_json
                    except json.JSONDecodeError:
                        continue
    
    return response.strip()

def validate_json_fields(response: str, requested_fields: Dict[str, str]) -> str:
    """Validate and fix JSON response to match requested fields and types"""
    try:
        parsed = json.loads(response)
        validated_response = {}
        
        for field_name, field_type in requested_fields.items():
            if field_name in parsed:
                value = parsed[field_name]
                # Type validation and conversion
                if field_type == "string" and not isinstance(value, str):
                    validated_response[field_name] = str(value) if value is not None else None
                elif field_type == "integer":
                    try:
                        validated_response[field_name] = int(value) if value is not None else None
                    except (ValueError, TypeError):
                        validated_response[field_name] = None
                elif field_type == "boolean":
                    validated_response[field_name] = bool(value) if value is not None else None
                else:
                    validated_response[field_name] = value
            else:
                # Field missing - set to null as per requirements
                validated_response[field_name] = None
        
        return json.dumps(validated_response)
    except json.JSONDecodeError:
        # If JSON is invalid, create null response for all fields
        null_response = {field: None for field in requested_fields.keys()}
        return json.dumps(null_response)

def extract_json_structure(user_input: str) -> Dict[str, Any]:
    """Extract JSON structure from user input"""
    try:
        # Try to parse the entire input as JSON first
        parsed = json.loads(user_input)
        if parsed.get("format") == "json" and "fields" in parsed:
            return parsed
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON structure within the input - more flexible regex
    import re
    
    # Look for JSON objects that contain "format": "json"
    json_patterns = [
        r'\{[^{}]*"format"\s*:\s*"json"[^{}]*\}',  # Simple object
        r'\{(?:[^{}]|{[^{}]*})*"format"\s*:\s*"json"(?:[^{}]|{[^{}]*})*\}',  # Nested object
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, user_input, re.DOTALL)
        for match in matches:
            try:
                parsed = json.loads(match)
                if parsed.get("format") == "json" and "fields" in parsed:
                    return parsed
            except json.JSONDecodeError:
                continue
    
    # Try to extract JSON from the first line if it looks like JSON
    lines = user_input.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                parsed = json.loads(line)
                if parsed.get("format") == "json" and "fields" in parsed:
                    return parsed
            except json.JSONDecodeError:
                continue
    
    return {}

@traceable(name="sdr_agent_decision")
def run_agent(state):
    """Enhanced SDR Agent decision logic with tool transparency"""
    user_input = state["input"]
    intermediate_steps = state["intermediate_steps"]
    
    # Initialize tool tracking if not present
    if "tools_used" not in state:
        state["tools_used"] = []
    if "tool_analysis" not in state:
        state["tool_analysis"] = {}
    
    # Analyze query for tool prediction
    if not intermediate_steps:  # Only analyze on first run
        state["tool_analysis"] = analyze_query_for_tools(user_input)
    
    # Extract JSON structure if present
    json_structure = extract_json_structure(user_input)
    is_json_request = bool(json_structure.get("format") == "json" and json_structure.get("fields"))
    
    # Check if we have intermediate steps (tool results) to process
    if intermediate_steps:
        # Extract tool usage information from results
        tools_used = []
        citations = []
        tool_results = []
        
        for action, observation in intermediate_steps:
            tool_results.append(f"Tool: {action.tool}\nResult: {observation}")
            citations.append(f"Source: {action.tool} - {action.tool_input}")
            
            # Extract tool info from observation if available
            try:
                if isinstance(observation, str):
                    obs_dict = json.loads(observation)
                elif isinstance(observation, dict):
                    obs_dict = observation
                else:
                    obs_dict = {"tool": action.tool}
                
                if "_tool_info" in obs_dict:
                    tools_used.append(obs_dict["_tool_info"])
                else:
                    # Fallback tool info
                    tools_used.append({
                        "tool_name": action.tool,
                        "tool_category": "Data Collection",
                        "mcp_provider": "BrightData",
                        "purpose": f"Executed {action.tool} with input: {action.tool_input}",
                        "data_type": "Various"
                    })
            except:
                # Fallback for any parsing errors
                tools_used.append({
                    "tool_name": action.tool,
                    "tool_category": "Data Collection", 
                    "mcp_provider": "BrightData",
                    "purpose": f"Executed {action.tool}",
                    "data_type": "Various"
                })
        
        # Store tools used in state
        state["tools_used"] = tools_used
        
        if is_json_request:
            # Create JSON response with citations
            final_prompt = f"""
You are an SDR AI assistant. Based on the tool results, create a JSON response matching the user's exact field specification.

User's JSON Structure Request: {json_structure}
Tool Results: {tool_results}

CRITICAL REQUIREMENTS:
1. Return ONLY valid JSON matching the exact field names and types specified
2. Use null for any field where data cannot be determined
3. Ensure data types match exactly (string, integer, boolean)
4. NO markdown formatting, NO code blocks, NO additional text, ONLY pure JSON
5. Do not include any explanatory text before or after the JSON

JSON Response:
"""
        else:
            # Create plain text response with citations and tool transparency
            tool_summary = format_tool_usage_summary(tools_used)
            final_prompt = f"""
You are an SDR AI assistant. Based on the tool results, provide a concise, actionable response for sales development activities.

User Query: {user_input}
Tool Results: {tool_results}

Requirements:
1. Provide actionable insights relevant to SDR activities
2. Be concise and professional
3. Include source citations at the end
4. Explain how the MCP tools helped gather this information

Response:
"""
        
        final_response = llm.invoke(final_prompt)
        
        if is_json_request:
            # Validate JSON structure
            validated_response = validate_json_fields(
                clean_json_response(final_response), 
                json_structure["fields"]
            )
            # Add citations as metadata
            return {"agent_outcome": AgentFinish({
                "output": validated_response,
                "citations": citations,
                "tools_used": tools_used
            }, log=final_response)}
        else:
            # Add citations and tool summary to plain text response
            citation_text = "\n\nSources:\n" + "\n".join(f"• {cite}" for cite in citations)
            tool_summary = format_tool_usage_summary(tools_used)
            return {"agent_outcome": AgentFinish({
                "output": final_response + citation_text + tool_summary
            }, log=final_response)}
    
    else:
        # Decide if we need tools or can answer directly
        tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in tools])
        
        # Enhanced tool detection logic with predictions
        analysis = state.get("tool_analysis", {})
        predicted_tools = [t["tool"] for t in analysis.get("predicted_tools", [])]
        
        # Show user what tools might be used
        if predicted_tools:
            print(f"🔮 Predicted MCP tools for this query: {', '.join(predicted_tools)}")
            print(f"📊 Query type: {analysis.get('query_type', 'unknown')}")
            print(f"📈 Data sources needed: {', '.join(analysis.get('data_sources_needed', []))}")
        
        needs_web_search = any([
            "search" in user_input.lower(),
            "find" in user_input.lower() and ("recent" in user_input.lower() or "news" in user_input.lower()),
            "latest" in user_input.lower(),
            "current" in user_input.lower()
        ])
        
        needs_linkedin = any([
            "linkedin" in user_input.lower(),
            "profile" in user_input.lower() and ("person" in user_input.lower() or "executive" in user_input.lower())
        ])
        
        needs_company_info = any([
            "company info" in user_input.lower(),
            "company data" in user_input.lower(),
            "business information" in user_input.lower(),
            "company summary" in user_input.lower(),
            "company" in user_input.lower() and any(word in user_input.lower() for word in ["about", "information", "summary", "profile", "details", "research"]),
            "analyze" in user_input.lower() and ("company" in user_input.lower() or "business" in user_input.lower())
        ])
        
        needs_scraping = "scrape" in user_input.lower() or "http" in user_input.lower()
        
        needs_job_search = any([
            "job" in user_input.lower() and "search" in user_input.lower(),
            "job listings" in user_input.lower(),
            "hiring" in user_input.lower()
        ])
        
        if needs_web_search or needs_linkedin or needs_company_info or needs_scraping or needs_job_search:
            # Use tools for data gathering - be more explicit about tool selection
            tool_prompt = f"""
You are an SDR AI assistant. The user query requires MCP tool usage for real-time data.

User Query: {user_input}
Available Tools: {tool_descriptions}

CRITICAL: You MUST respond with EXACTLY this JSON format for tool selection:
{{"tool": "tool_name", "tool_input": {{"param": "value"}}}}

Based on the query, determine which tool to use:
- For "latest", "recent", "current", "news", "trends" → use "search_web" 
- For company research → use "get_company_info"
- For LinkedIn profiles → use "get_linkedin_profile"
- For job searches → use "search_jobs"
- For URL scraping → use "scrape_url"
- For product research → use "get_product_info"

Query analysis:
- Contains "latest": {'"latest"' in user_input.lower()}
- Contains "news": {'"news"' in user_input.lower()}
- Contains "current": {'"current"' in user_input.lower()}
- Contains "recent": {'"recent"' in user_input.lower()}
- Web search needed: {needs_web_search}

Your tool selection (JSON only):
"""
            
            raw_response = llm.invoke(tool_prompt)
            print(f"🧠 LLM raw response: {raw_response}")
            
            try:
                if raw_response.strip().startswith('{') and '"tool"' in raw_response:
                    response = json.loads(clean_json_response(raw_response))
                    action = AgentAction(
                        tool=response["tool"],
                        tool_input=response["tool_input"],
                        log=raw_response
                    )
                    
                    # Show user which tool is being executed
                    tool_name = response["tool"]
                    tool_input = response["tool_input"]
                    print(f"🛠️ Executing MCP tool: {tool_name}")
                    print(f"📝 Tool input: {tool_input}")
                    
                    return {"agent_outcome": action}
                else:
                    # If LLM doesn't return proper JSON, force tool selection based on analysis
                    print(f"⚠️ LLM didn't return proper tool JSON. Forcing tool selection...")
                    if needs_web_search:
                        action = AgentAction(
                            tool="search_web",
                            tool_input={"query": user_input},
                            log=f"Forced web search for: {user_input}"
                        )
                        print(f"🔧 Forcing web search tool")
                        return {"agent_outcome": action}
                    elif needs_company_info:
                        # Extract company name from query
                        company_name = user_input.lower().replace("company", "").replace("info", "").replace("about", "").strip()
                        action = AgentAction(
                            tool="get_company_info",
                            tool_input={"company_name": company_name, "platform": "auto"},
                            log=f"Forced company info search for: {company_name}"
                        )
                        print(f"🔧 Forcing company info tool")
                        return {"agent_outcome": action}
            except (json.JSONDecodeError, KeyError) as e:
                # Force tool selection as backup
                print(f"❌ Tool selection error: {str(e)}. Forcing tool selection...")
                if needs_web_search:
                    action = AgentAction(
                        tool="search_web",
                        tool_input={"query": user_input},
                        log=f"Backup web search for: {user_input}"
                    )
                    print(f"🔧 Backup: Using web search")
                    return {"agent_outcome": action}
                else:
                    error_msg = f"Tool selection failed: {str(e)}"
                    return {"agent_outcome": AgentFinish({"output": error_msg}, log=error_msg)}
        
        # Provide direct answer based on knowledge
        if is_json_request:
            direct_prompt = f"""
You are an SDR AI assistant. Provide information based on your knowledge in the exact JSON format requested.

User's JSON Structure: {json_structure}
Query Context: {user_input}

CRITICAL REQUIREMENTS:
1. Return ONLY valid JSON matching exact field names and types
2. Use null for fields where information is not available
3. Ensure data types match specification (string, integer, boolean)
4. NO markdown formatting, NO code blocks, NO explanatory text
5. ONLY return the JSON object, nothing else

Example format: {{"field1": "value1", "field2": "value2"}}

JSON Response:
"""
        else:
            direct_prompt = f"""
You are an SDR AI assistant. Answer the query with actionable insights for sales development.

User Query: {user_input}

Requirements:
1. Provide concise, actionable information relevant to SDR activities
2. Be professional and helpful
3. Note that response is based on general knowledge
4. Include relevant context for sales development

Response:
"""
        
        try:
            direct_response = llm.invoke(direct_prompt)
            
            if is_json_request:
                validated_response = validate_json_fields(
                    clean_json_response(direct_response),
                    json_structure["fields"]
                )
                return {"agent_outcome": AgentFinish({
                    "output": validated_response,
                    "citations": ["Source: General knowledge base"],
                    "tools_used": []
                }, log=direct_response)}
            else:
                citation_note = "\n\nSource: General knowledge base"
                tool_summary = format_tool_usage_summary([])  # Empty list for no tools
                return {"agent_outcome": AgentFinish({
                    "output": direct_response + citation_note + tool_summary
                }, log=direct_response)}
                
        except Exception as e:
            # Comprehensive error handling
            error_msg = f"Response generation error: {str(e)}. Please try rephrasing your query."
            return {"agent_outcome": AgentFinish({"output": error_msg}, log=str(e))}

# The tool execution node is now async
async def execute_tools(state):
    """Executes the chosen tool with enhanced logging."""
    agent_action = state["agent_outcome"]
    
    # Log tool execution for transparency
    print(f"🔧 Executing: {agent_action.tool}")
    print(f"📊 Parameters: {agent_action.tool_input}")
    
    # We use the ToolNode's ainvoke method for async execution
    observation = await tool_node.ainvoke(agent_action)
    
    # Log completion
    print(f"✅ Completed: {agent_action.tool}")
    
    return {"intermediate_steps": [(agent_action, str(observation))]}

def should_continue(state):
    """Determines whether to continue the process or end."""
    if isinstance(state["agent_outcome"], AgentFinish):
        return "end"
    return "continue"

# --- Graph Definition ---
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("agent", run_agent)
workflow.add_node("action", execute_tools)

# Set the entry point
workflow.set_entry_point("agent")

# Add conditional edges
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)

# Add a regular edge from the action back to the agent
workflow.add_edge("action", "agent")

# Compile the graph
app = workflow.compile()

# --- User Interface Functions ---

def show_query_analysis(user_input: str) -> None:
    """Show user what the agent predicts for their query"""
    analysis = analyze_query_for_tools(user_input)
    
    print("\n" + "="*60)
    print("🤖 AGENT QUERY ANALYSIS")
    print("="*60)
    print(f"📝 Query: {user_input}")
    print(f"🔍 Query Type: {analysis['query_type'].replace('_', ' ').title()}")
    
    if analysis['predicted_tools']:
        print(f"\n🛠️ Predicted MCP Tools:")
        for tool_pred in analysis['predicted_tools']:
            print(f"   • {tool_pred['tool']} ({tool_pred['category']})")
            print(f"     └─ Reason: {tool_pred['reason']}")
    
    if analysis['data_sources_needed']:
        print(f"\n📊 Data Sources Needed:")
        for source in analysis['data_sources_needed']:
            print(f"   • {source}")
    
    print("="*60)

async def run_agent_with_transparency(user_input: str) -> Dict[str, Any]:
    """Run the agent with full transparency about tool usage"""
    
    # Show initial analysis
    show_query_analysis(user_input)
    
    # Initialize state
    initial_state = {
        "input": user_input,
        "chat_history": [],
        "agent_outcome": None,
        "intermediate_steps": [],
        "tools_used": [],
        "tool_analysis": {}
    }
    
    print(f"\n🚀 Starting agent execution...")
    
    # Run the agent
    result = await app.ainvoke(initial_state)
    
    # Show final tool usage summary
    tools_used = result.get("tools_used", [])
    if tools_used:
        print(f"\n📈 FINAL TOOL USAGE SUMMARY:")
        print(f"   Tools executed: {len(tools_used)}")
        for i, tool_info in enumerate(tools_used, 1):
            print(f"   {i}. {tool_info.get('tool_name', 'Unknown')} ({tool_info.get('tool_category', 'Unknown')})")
            print(f"      Purpose: {tool_info.get('purpose', 'Data collection')}")
    else:
        print(f"\n🧠 No MCP tools used - response from knowledge base")
    
    return result

# Enhanced wrapper for simple usage
async def ask_sdr_agent(question: str, show_analysis: bool = True) -> str:
    """Simple interface to ask the SDR agent a question with tool transparency"""
    
    if show_analysis:
        result = await run_agent_with_transparency(question)
    else:
        # Quick execution without detailed analysis
        initial_state = {
            "input": question,
            "chat_history": [],
            "agent_outcome": None,
            "intermediate_steps": [],
            "tools_used": [],
            "tool_analysis": {}
        }
        result = await app.ainvoke(initial_state)
    
    # Extract the response
    if hasattr(result["agent_outcome"], 'return_values'):
        return result["agent_outcome"].return_values.get("output", "No response generated")
    else:
        return str(result["agent_outcome"])

# --- Tool Usage Analytics ---
class ToolUsageAnalytics:
    """Track and analyze tool usage patterns"""
    
    def __init__(self):
        self.usage_history = []
    
    def log_usage(self, query: str, tools_used: List[Dict[str, Any]], success: bool = True):
        """Log tool usage for analytics"""
        self.usage_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "tools_used": tools_used,
            "success": success,
            "tool_count": len(tools_used)
        })
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        if not self.usage_history:
            return {"message": "No usage data available"}
        
        tool_counts = {}
        category_counts = {}
        total_queries = len(self.usage_history)
        successful_queries = sum(1 for entry in self.usage_history if entry["success"])
        
        for entry in self.usage_history:
            for tool_info in entry["tools_used"]:
                tool_name = tool_info.get("tool_name", "unknown")
                category = tool_info.get("tool_category", "unknown")
                
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
                category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "success_rate": successful_queries / total_queries if total_queries > 0 else 0,
            "most_used_tools": sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_used_categories": sorted(category_counts.items(), key=lambda x: x[1], reverse=True),
            "average_tools_per_query": sum(entry["tool_count"] for entry in self.usage_history) / total_queries if total_queries > 0 else 0
        }
    
    def print_usage_report(self):
        """Print a formatted usage report"""
        stats = self.get_usage_stats()
        
        print("\n" + "="*60)
        print("📊 MCP TOOL USAGE ANALYTICS")
        print("="*60)
        print(f"Total Queries: {stats.get('total_queries', 0)}")
        print(f"Success Rate: {stats.get('success_rate', 0):.1%}")
        print(f"Avg Tools per Query: {stats.get('average_tools_per_query', 0):.1f}")
        
        print(f"\n🏆 Most Used Tools:")
        for tool, count in stats.get('most_used_tools', []):
            print(f"   • {tool}: {count} times")
        
        print(f"\n📈 Most Used Categories:")
        for category, count in stats.get('most_used_categories', []):
            print(f"   • {category}: {count} times")
        
        print("="*60)

# Global analytics instance
analytics = ToolUsageAnalytics()

# Cleanup function for graceful shutdown
async def cleanup():
    """Cleanup MCP connections on shutdown"""
    global _brightdata_client
    if _brightdata_client:
        await _brightdata_client.disconnect()
        _brightdata_client = None

# Register cleanup on exit
import atexit
atexit.register(lambda: asyncio.run(cleanup()))