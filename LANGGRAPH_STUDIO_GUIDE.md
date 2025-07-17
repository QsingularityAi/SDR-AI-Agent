# LangGraph Studio Setup Guide

## 🎯 Overview

This guide will help to run SDR AI Agent in LangGraph Studio for visual debugging, testing, and development. Agent is built with LangGraph's StateGraph and includes multiple MCP tools for comprehensive sales intelligence.

## 🏗️ Agent Architecture

Agent uses the following LangGraph components:

```python
# Core Components
- StateGraph with AgentState
- ToolNode with 7 MCP tools
- Agent node for decision making
- Action node for tool execution
- Conditional routing logic
```

### Agent Flow
```
Start → Agent (Decision) → Action (Tool Execution) → Agent → End
```

## 📋 Prerequisites

### 1. Install LangGraph Studio
```bash
# Install LangGraph Studio CLI
pip install langgraph-studio

# Or use the desktop app
# Download from: https://studio.langchain.com/
```

### 2. Environment Setup
Ensure your `.env` file contains all required API keys:

```bash
# Copy your production environment
cp .env.production .env

# Required keys for LangGraph Studio
GOOGLE_API_KEY=your_google_api_key
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=sdr-agent-studio



# BrightData MCP (if using)
MCP_ENABLED=true
BRIGHTDATA_API_TOKEN=your_brightdata_key
SMITHERY_API_KEY=your_SMITHERY_key
BRIGHTDATA_API_KEY=your_brightdata_key
```

### 3. Dependencies
```bash
# Install all requirements
pip install -r requirements.txt

# Ensure LangGraph Studio compatibility
pip install langgraph-studio langsmith
```

## 🚀 Running in LangGraph Studio

### Method 1: Studio CLI (Recommended)

1. **Navigate project directory:**
```bash
cd /path/to/your/sdr-ai-agent
```

2. **Create a studio configuration file:**
```bash
# This will be created automatically, you can customize it for yourself.
touch langgraph.json
```

3. **Start LangGraph Studio:**
```bash
# Start studio pointing to your agent
langgraph studio --file agent.py --graph app

# Or with specific port
langgraph studio --file agent.py --graph app --port 8123
```

4. **Access the Studio:**
Open your browser to: `http://localhost:8123`

### Method 2: Desktop App

1. **Open LangGraph Studio Desktop App**

2. **Import Your Project:**
   - Click "Open Project"
   - Navigate to your project directory
   - Select `agent.py` as the main file
   - Set graph variable to `app`

3. **Configure Environment:**
   - Studio will automatically detect your `.env` file
   - Verify all API keys are loaded

## 🔧 Studio Configuration

### Create `langgraph.json` (Optional)
```json
{
  "dependencies": [
    "langchain",
    "langchain-google-genai", 
    "langgraph",
    "langsmith",
    "python-dotenv",
    "httpx",
    "aiohttp"
  ],
  "graphs": {
    "agent": {
      "file": "agent.py",
      "variable": "app",
      "description": "SDR AI Agent with MCP Tools"
    }
  },
  "env": ".env"
}
```

## 🛠️ Available Tools in Studio

Your agent includes these MCP-powered tools that will be visible in Studio:

### 1. 🔍 Web Intelligence
- **search_web**: Real-time web search via BrightData
- **scrape_url**: Website content extraction

### 2. 🏢 Business Intelligence  
- **get_company_info**: Company data from LinkedIn/Crunchbase/ZoomInfo
- **research_company_web**: Fallback web research for companies

### 3. 👤 Professional Intelligence
- **get_linkedin_profile**: LinkedIn profile extraction

### 4. 💼 Job Market Intelligence
- **search_jobs**: Job listings and hiring trends

### 5. 🛒 Retail Intelligence
- **get_product_info**: Product and competitive analysis

## 🧪 Testing in Studio

### 1. Basic Query Testing
```json
{
  "input": "Research Stripe for outbound sales",
  "chat_history": [],
  "agent_outcome": null,
  "intermediate_steps": []
}
```

### 2. Structured JSON Testing
```json
{
  "input": "{\"query\": \"Research Salesforce\", \"format\": \"json\", \"fields\": {\"company_name\": \"string\", \"industry\": \"string\", \"employee_count\": \"integer\", \"headquarters\": \"string\", \"revenue\": \"string\"}}",
  "chat_history": [],
  "agent_outcome": null, 
  "intermediate_steps": []
}
```

### 3. Company Research Testing
```json
{
  "input": "Get detailed information about Notion including competitors and key contacts",
  "chat_history": [],
  "agent_outcome": null,
  "intermediate_steps": []
}
```

## 📊 Studio Features You Can Use

### 1. **Visual Graph View**
- See your StateGraph visually
- Track state transitions
- Monitor tool execution flow

### 2. **Step-by-Step Debugging**
- Pause execution at any node
- Inspect state at each step
- Modify state values during execution

### 3. **Tool Execution Monitoring**
- Watch MCP tool calls in real-time
- See tool inputs and outputs
- Debug tool failures

### 4. **State Inspection**
- View AgentState at each step
- Monitor intermediate_steps accumulation
- Track tools_used and tool_analysis

### 5. **Performance Profiling**
- Measure execution time per node
- Track token usage
- Monitor API call patterns

## 🔍 Debugging Common Issues

### 1. **MCP Connection Issues**
```python
# Check if BrightData client connects
async def test_mcp_connection():
    from brightdata_client import BrightDataMCPClient
    client = BrightDataMCPClient()
    await client.connect()
    print("✅ MCP Connected")
```

### 2. **Tool Execution Failures**
- Check API keys in Studio environment panel
- Verify tool parameters in Studio tool inspector
- Use Studio's tool testing feature

### 3. **State Management Issues**
- Use Studio's state inspector
- Check AgentState type definitions
- Verify state transitions in graph view

### 4. **JSON Response Issues**
- Test structured queries in Studio
- Use Studio's response formatter
- Debug JSON parsing in tool outputs

## 📈 Advanced Studio Usage

### 1. **Custom Evaluation in Studio**
```python
# Create evaluation datasets in Studio
evaluation_cases = [
    {
        "input": "Research Tesla for B2B sales",
        "expected_tools": ["get_company_info", "search_web"],
        "expected_format": "structured_analysis"
    }
]
```

### 2. **A/B Testing Different Prompts**
- Use Studio's prompt comparison feature
- Test different system prompts
- Compare tool selection strategies

### 3. **Performance Optimization**
- Use Studio's performance profiler
- Identify bottleneck nodes
- Optimize tool execution order

## 🎯 Studio Workflow for SDR Agent

### 1. **Development Workflow**
```bash
# 1. Start Studio
langgraph studio --file agent.py --graph app

# 2. Test basic functionality
# 3. Debug tool integrations  
# 4. Optimize prompt engineering
# 5. Validate JSON responses
```

### 2. **Testing Workflow**
1. **Unit Testing**: Test individual tools
2. **Integration Testing**: Test full agent workflows
3. **Performance Testing**: Monitor execution times
4. **Evaluation Testing**: Run evaluation datasets

### 3. **Debugging Workflow**
1. **Visual Debugging**: Use graph view to track execution
2. **State Debugging**: Inspect state at each node
3. **Tool Debugging**: Monitor MCP tool calls
4. **Response Debugging**: Validate output formats

## 🚀 Production Deployment from Studio

### 1. **Export Configuration**
```bash
# Export your tested configuration
langgraph export --file agent.py --graph app --output production_config.json
```

### 2. **Deploy to Production**
```bash
# Use your existing deployment script
./deploy.sh

# Or deploy with Studio configuration
langgraph deploy --config production_config.json
```

## 📚 Additional Resources

### Agent-Specific Resources
- `README.md`: Full agent documentation
- `enhanced_langsmith_evaluation.py`: Evaluation framework
- `test_agent.py`: Unit tests

## 🆘 Troubleshooting

### Common Studio Issues

1. **Graph Not Loading**
```bash
# Check your agent.py syntax
python -c "from src.agent import app; print('✅ Agent loads successfully')"
```

2. **Environment Variables Not Loading**
```bash
# Verify .env file
cat .env | grep -E "(GOOGLE_API_KEY|LANGSMITH_API_KEY)"
```

3. **MCP Tools Not Working**
```bash
# Test MCP connection outside Studio
python -c "
import asyncio
from brightdata_client import BrightDataMCPClient

async def test():
    client = BrightDataMCPClient()
    await client.connect()
    print('✅ MCP Connected')

asyncio.run(test())
"
```

4. **Studio Performance Issues**
```bash
# Start with minimal configuration
langgraph studio --file agent.py --graph app --no-browser --port 8123
```

---

**🎉 You're Ready!** Your SDR AI Agent is now ready to run in LangGraph Studio for visual debugging, testing, and development. The Studio environment will give you powerful insights into your agent's decision-making process and tool execution patterns.