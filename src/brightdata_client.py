"""
BrightData MCP Client Integration
Handles communication with BrightData MCP server for web data extraction
"""

import mcp
from mcp.client.streamable_http import streamablehttp_client
import json
import base64
import asyncio
import logging
import os
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class BrightDataMCPClient:
    
    
    def __init__(self):
        self.config = {
            "browserZone": "mcp_browser",
            "webUnlockerZone": "mcp_unlocker", 
            "apiToken": os.getenv("BRIGHTDATA_API_TOKEN")
        }
        
        
        config_b64 = base64.b64encode(json.dumps(self.config).encode()).decode()
        
        # Create server URL
        self.url = f"https://server.smithery.ai/@luminati-io/brightdata-mcp/mcp?config={config_b64}&api_key={os.getenv('SMITHERY_API_KEY')}&profile=substantial-locust-oYZMoh"
        
        self.session = None
        self.available_tools = []
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        
        try:
            
            mcp_logger = logging.getLogger('root')
            original_level = mcp_logger.level
            mcp_logger.setLevel(logging.ERROR)
            
            self.client_streams = streamablehttp_client(self.url)
            self.read_stream, self.write_stream, _ = await self.client_streams.__aenter__()
            self.session = mcp.ClientSession(self.read_stream, self.write_stream)
            await self.session.__aenter__()
            
            
            await self.session.initialize()
            
            
            tools_result = await self.session.list_tools()
            self.available_tools = [tool.name for tool in tools_result.tools]
            
            
            mcp_logger.setLevel(original_level)
            
            logger.info(f"Connected to BrightData MCP. Available tools: {len(self.available_tools)}")
            
        except Exception as e:
            logger.error(f"Failed to connect to BrightData MCP: {e}")
            raise
    
    async def disconnect(self):
        
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self.client_streams:
                await self.client_streams.__aexit__(None, None, None)
        except Exception as e:
            logger.error(f"Error disconnecting from BrightData MCP: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        
        if not self.session:
            raise ValueError("Not connected to MCP server")
        
        
        actual_tool_name = self._map_tool_name(tool_name)
        
        if actual_tool_name not in self.available_tools:
            logger.error(f"Tool '{tool_name}' (mapped to '{actual_tool_name}') not available. Available tools: {self.available_tools}")
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not available. Available tools: {self.available_tools}",
                "tool": tool_name
            }
        
        try:
            
            result = await asyncio.wait_for(
                self.session.call_tool(actual_tool_name, arguments),
                timeout=30.0  # 30 second timeout
            )
            
            
            logger.info(f"Raw MCP result type: {type(result)}")
            logger.info(f"Raw MCP result: {str(result)[:200]}...")
            
            
            data = None
            
            if hasattr(result, 'content'):
                content = result.content
                logger.info(f"Content type: {type(content)}, length: {len(content) if isinstance(content, list) else 'N/A'}")
                
                if isinstance(content, list) and len(content) > 0:
                    # Extract text content from MCP response
                    if hasattr(content[0], 'text'):
                        data = content[0].text
                        logger.info(f"Extracted text data, length: {len(data) if isinstance(data, str) else 'N/A'}")
                        
                        # Try to parse as JSON if it looks like JSON
                        if isinstance(data, str) and (data.strip().startswith('{') or data.strip().startswith('[')):
                            try:
                                import json
                                data = json.loads(data)
                                logger.info("Successfully parsed as JSON")
                            except json.JSONDecodeError:
                                logger.info("Could not parse as JSON, keeping as string")
                    else:
                        data = content[0] if len(content) > 0 else content
                else:
                    data = content
            else:
                data = result
            
            
            if data is None:
                logger.warning("No data extracted from MCP response")
                data = {"messages": [], "raw_result": str(result)}
            
            return {
                "success": True,
                "data": data,
                "tool": actual_tool_name,
                "raw_response_type": str(type(result))
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout calling tool '{actual_tool_name}'")
            return {
                "success": False,
                "error": f"Tool '{actual_tool_name}' timed out after 30 seconds",
                "tool": actual_tool_name
            }
        except Exception as e:
            logger.error(f"Error calling tool '{actual_tool_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": actual_tool_name
            }
    
    def _map_tool_name(self, tool_name: str) -> str:
        
        # Mapping for backward compatibility
        tool_mappings = {
            "crunchbase_company": "web_data_crunchbase_company",
            "linkedin_person_profile": "web_data_linkedin_person_profile", 
            "linkedin_company_profile": "web_data_linkedin_company_profile",
            "linkedin_job_listings": "web_data_linkedin_job_listings",
            "linkedin_posts": "web_data_linkedin_posts",
            "zoominfo_company_profile": "web_data_zoominfo_company_profile",
            "amazon_product": "web_data_amazon_product",
            "amazon_product_search": "web_data_amazon_product_search"
        }
        
        return tool_mappings.get(tool_name, tool_name)
    
    async def search_web(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        
        return await self.call_tool("search_engine", {
            "query": query,
            "num_results": num_results
        })
    
    async def scrape_url(self, url: str, format: str = "markdown") -> Dict[str, Any]:
        
        tool_name = f"scrape_as_{format}"
        return await self.call_tool(tool_name, {"url": url})
    
    async def get_linkedin_profile(self, profile_url: str) -> Dict[str, Any]:
        
        return await self.call_tool("web_data_linkedin_person_profile", {
            "profile_url": profile_url
        })
    
    async def get_company_info(self, company_name: str, platform: str = "linkedin") -> Dict[str, Any]:
        
        if platform == "linkedin":
            return await self.call_tool("web_data_linkedin_company_profile", {
                "company_name": company_name
            })
        elif platform == "crunchbase":
            return await self.call_tool("web_data_crunchbase_company", {
                "company_name": company_name
            })
        elif platform == "zoominfo":
            return await self.call_tool("web_data_zoominfo_company_profile", {
                "company_name": company_name
            })
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    async def search_jobs(self, query: str, location: str = "") -> Dict[str, Any]:
        
        return await self.call_tool("web_data_linkedin_job_listings", {
            "query": query,
            "location": location
        })
    
    async def get_product_info(self, product_query: str, platform: str = "amazon") -> Dict[str, Any]:
        
        platform_tools = {
            "amazon": "web_data_amazon_product_search",
            "walmart": "web_data_walmart_product", 
            "ebay": "web_data_ebay_product",
            "bestbuy": "web_data_bestbuy_products"
        }
        
        tool_name = platform_tools.get(platform)
        if not tool_name:
            raise ValueError(f"Unsupported e-commerce platform: {platform}")
        
        return await self.call_tool(tool_name, {"query": product_query})
    
    async def get_social_profile(self, username: str, platform: str) -> Dict[str, Any]:
        
        platform_tools = {
            "instagram": "web_data_instagram_profiles",
            "tiktok": "web_data_tiktok_profiles", 
            "youtube": "web_data_youtube_profiles"
        }
        
        tool_name = platform_tools.get(platform)
        if not tool_name:
            raise ValueError(f"Unsupported social platform: {platform}")
        
        return await self.call_tool(tool_name, {"username": username})
    
    def get_available_tools(self) -> List[str]:
       
        return self.available_tools.copy()

# Singleton instance
_brightdata_client = None

def get_brightdata_client() -> BrightDataMCPClient:
    
    return BrightDataMCPClient()
