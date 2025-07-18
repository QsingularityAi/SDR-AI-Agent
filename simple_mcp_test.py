#!/usr/bin/env python3
"""
Simple MCP connection test using the same approach as the agent
"""

import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()

async def test_mcp_tools():
    """Test MCP tools loading and basic functionality"""
    
    print("🔧 Testing MCP Tools Connection...")
    print(f"📋 Environment variables:")
    print(f"   API_TOKEN: {'✅ Set' if os.getenv('API_TOKEN') else '❌ Missing'}")
    print(f"   BROWSER_AUTH: {'✅ Set' if os.getenv('BROWSER_AUTH') else '❌ Missing'}")
    print(f"   WEB_UNLOCKER_ZONE: {'✅ Set' if os.getenv('WEB_UNLOCKER_ZONE') else '❌ Missing'}")
    
    # Initialize the server parameters
    server_params = StdioServerParameters(
        command="npx",
        env={
            "API_TOKEN": os.getenv("API_TOKEN"),
            "BROWSER_AUTH": os.getenv("BROWSER_AUTH"),
            "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE"),
        },
        args=["@brightdata/mcp"],
    )
    
    try:
        print("🔌 Connecting to MCP server...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ Connected to MCP server")
                
                # Initialize the session
                await session.initialize()
                print("✅ Session initialized")
                
                # Load the tools
                tools = await load_mcp_tools(session)
                print(f"🛠️ Loaded {len(tools)} tools:")
                
                for i, tool in enumerate(tools[:10], 1):  # Show first 10 tools
                    print(f"   {i}. {tool.name}: {tool.description[:100]}...")
                
                if len(tools) > 10:
                    print(f"   ... and {len(tools) - 10} more tools")
                
                # Test a simple tool call
                print("\n🔍 Testing search_engine tool...")
                search_tool = next((tool for tool in tools if tool.name == "search_engine"), None)
                
                if search_tool:
                    print(f"✅ Found search_engine tool")
                    print(f"   Description: {search_tool.description}")
                    print(f"   Args schema: {search_tool.args}")
                    
                    # Try to invoke the tool
                    try:
                        result = await search_tool.ainvoke({
                            "query": "Tesla company news",
                            "engine": "google"
                        })
                        print(f"✅ Tool call successful!")
                        print(f"   Result type: {type(result)}")
                        print(f"   Result length: {len(str(result)) if result else 0}")
                        if result:
                            print(f"   Result preview: {str(result)[:200]}...")
                    except Exception as tool_error:
                        print(f"❌ Tool call failed: {tool_error}")
                else:
                    print("❌ search_engine tool not found")
                
                print("✅ MCP test completed successfully")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())