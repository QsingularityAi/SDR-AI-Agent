import asyncio
import json
import os
from src.agent import app

# Initialize LangSmith tracing
def setup_langsmith():
    """Setup LangSmith tracing configuration"""
    # Set environment variables for LangSmith if not already set
    if not os.getenv("LANGCHAIN_TRACING_V2"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
    
    # Use project name from env or default
    if not os.getenv("LANGCHAIN_PROJECT"):
        project_name = os.getenv("LANGSMITH_PROJECT", "sdr-ai-agent-optimization")
        os.environ["LANGCHAIN_PROJECT"] = project_name
    
    # Ensure API key is set
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
    if langsmith_api_key and langsmith_api_key != "your_api_key_here":
        os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
        print(f"🔍 LangSmith tracing enabled for project: {os.getenv('LANGCHAIN_PROJECT')}")
    else:
        print("⚠️  LangSmith API key not configured - tracing disabled")

# Initialize LangSmith on import
setup_langsmith()

async def single_query_mode():
    """Single query mode - processes one query and exits"""
    import sys
    
    if len(sys.argv) > 1:
        # Command line query
        user_input = " ".join(sys.argv[1:])
    else:
        # Interactive single query
        print("🤖 SDR AI Agent - Single-Turn Mode")
        print("Enter your query (plain text or JSON structure):")
        try:
            user_input = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            return
    
    await process_single_query(user_input)

async def interactive_mode():
    """Interactive mode for testing and development"""
    print("🤖 SDR AI Agent - Interactive Mode")
    print("Enter your query. For structured JSON output, provide a JSON object.")
    print("Type 'exit' or 'quit' to stop, or press Ctrl+C")

    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ["exit", "quit"]:
                break
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break
        
        await process_single_query(user_input)

async def process_single_query(user_input: str):
    """Process a single query with comprehensive error handling"""
    from langsmith import traceable
    from datetime import datetime
    
    try:
        # Handle both plain text and JSON structured queries
        query = user_input
        query_type = "plain_text"
        
        # Check if input looks like JSON for structured output
        if user_input.strip().startswith('{') and '"format"' in user_input:
            try:
                json_input = json.loads(user_input)
                if json_input.get("format") == "json" and "fields" in json_input:
                    # This is a structured JSON request - pass it as-is to the agent
                    query = user_input
                    query_type = "structured_json"
                    print("📋 Detected structured JSON request")
                else:
                    query = user_input
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as plain text
                query = user_input
                print("💬 Processing as plain text query")
        else:
            print("💬 Processing as plain text query")

        inputs = {"input": query, "chat_history": [], "agent_outcome": None, "intermediate_steps": []}
        
        # Create a unique run name for this query
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_preview = query[:50] + "..." if len(query) > 50 else query
        run_name = f"SDR_Query_{timestamp}_{query_preview.replace(' ', '_')}"
        
        # Add metadata for better tracking
        config = {
            "run_name": run_name,
            "metadata": {
                "query_type": query_type,
                "query_length": len(query),
                "timestamp": datetime.now().isoformat(),
                "mode": "single_query"
            },
            "tags": ["sdr-agent", query_type]
        }
        
        print(f"🔍 Tracking query in LangSmith as: {run_name}")
        
        # Use ainvoke with config for proper tracing
        result = await app.ainvoke(inputs, config=config)
        final_result = result["agent_outcome"]
        
        print("\n--- SDR AI Agent Response ---")
        
        # Handle both simple output and output with citations
        if isinstance(final_result.return_values, dict) and "output" in final_result.return_values:
            print(final_result.return_values["output"])
            
            # Show citations if available
            if "citations" in final_result.return_values:
                print("\n--- Sources ---")
                for citation in final_result.return_values["citations"]:
                    print(f"📚 {citation}")
        else:
            # Fallback for simple string output
            print(final_result.return_values.get("output", str(final_result.return_values)))
        
        # Show tool usage if any
        if result["intermediate_steps"]:
            print("\n--- Tools Used ---")
            for action, observation in result["intermediate_steps"]:
                print(f"🔧 Tool: {action.tool}")
                print(f"📥 Input: {action.tool_input}")
                
                # Better handling of observation output
                if isinstance(observation, dict):
                    if 'data' in observation and isinstance(observation['data'], str):
                        # For search results, show a meaningful preview
                        data_preview = observation['data'][:500] + "..." if len(observation['data']) > 500 else observation['data']
                        print(f"📤 Result: Found {len(observation['data'])} characters of search data")
                        print(f"📄 Preview: {data_preview}")
                    else:
                        print(f"📤 Result: {observation}")
                else:
                    print(f"📤 Result: {str(observation)[:200]}...")
        
        # Log completion to LangSmith with additional metadata
        print(f"✅ Query completed and traced in LangSmith project: {os.getenv('LANGCHAIN_PROJECT')}")
        print("----------------------------")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your input format and try again.")

async def main():
    """Main entry point - defaults to single query mode for production"""
    import os
    
    # Check if running in interactive mode (for development)
    if os.getenv("SDR_AGENT_MODE") == "interactive":
        await interactive_mode()
    else:
        # Default to single-turn mode (production behavior)
        await single_query_mode()

if __name__ == "__main__":
    asyncio.run(main())