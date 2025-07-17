import asyncio
import json
from src.agent import app

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
    try:
        # Handle both plain text and JSON structured queries
        query = user_input
        
        # Check if input looks like JSON for structured output
        if user_input.strip().startswith('{') and '"format"' in user_input:
            try:
                json_input = json.loads(user_input)
                if json_input.get("format") == "json" and "fields" in json_input:
                    # This is a structured JSON request - pass it as-is to the agent
                    query = user_input
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
        
        # Use ainvoke instead of astream for simpler handling
        result = await app.ainvoke(inputs)
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