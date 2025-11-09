# AI Travel Agent with MCP Server Integration

> **Version 3.0** - A powerful AI travel assistant powered by Claude Sonnet 4.5 with **Model Context Protocol (MCP)** server integration using **FastMCP**. Combines traditional tool calling with modular MCP servers to provide complete travel intelligence including real-time flight search, weather forecasts, and local news.

## ✨ Features

### Core Capabilities
- **Conversational AI**: Natural chat with Claude Sonnet 4.5
- **Dynamic Tool Execution**: Automatically invokes tools when needed
- **Conversation Memory**: Maintains full conversation history with context
- **Optimized System Prompt**: Intelligent travel planning assistant
- **Bordered Output**: Clean, professional response formatting with `#` borders
- **Modular Architecture**: Clean separation between traditional tools and MCP servers

### Traditional LangChain Tools
- `tool_time`: Get current date and time
- `tool_calc`: Perform mathematical calculations with advanced math functions
- `search_flights`: Search real-time airline tickets using Google Flights data via SerpApi

### MCP Server Tools (FastMCP)
**Modular MCP Server** provides travel intelligence through:
- **Weather Forecasts**: `get_weather` - Real-time weather + 5-day forecast for any location (OpenWeatherMap API)
- **News Headlines**: `get_local_news` - Breaking news and current events for destinations (NewsAPI)

**Why MCP with FastMCP?**
- **True Client-Server Architecture**: MCP server runs as separate process with JSON-RPC communication
- **Location Independent**: Server can run on different machines (local, remote, containerized)
- **Simplified Development**: FastMCP auto-discovers tools from function signatures and docstrings
- **Modular Architecture**: Each tool in its own file (weather.py, news.py)
- **Dynamic Tool Discovery**: Agent discovers available tools at runtime via MCP protocol
- **Separation of Concerns**: Clean, focused modules with single responsibilities
- **Easy to Extend**: Add new tools by creating new Python files with decorated functions
- **Industry Standard**: Implements Model Context Protocol specification for AI tool integration

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- **Anthropic API key** - For Claude Sonnet 4.5
- **SerpApi API key** - For flight search functionality
- **OpenWeatherMap API key** - For weather forecasts (free tier: 1,000 calls/day)
- **NewsAPI key** - For news headlines (free tier: 100 requests/day)

### Installation

1. **Clone the repository**:
   ```bash
   git clone git@github.com:starskrime/my-first-ai-agent.git
   cd my-first-ai-agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   SERPAPI_API_KEY=your_serpapi_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   NEWS_API_KEY=your_newsapi_key_here
   ```

   **Getting API Keys**:
   - **Anthropic API**: Sign up at [Anthropic Console](https://console.anthropic.com/)
   - **SerpApi**: Get a free key (100 searches/month) at [SerpApi](https://serpapi.com/)
   - **OpenWeatherMap**: Free tier at [OpenWeatherMap](https://openweathermap.org/api) - Note: New keys may take 2-4 hours to activate
   - **NewsAPI**: Free tier at [NewsAPI](https://newsapi.org/) - 100 requests/day

### Usage


**Activate virtual environment manually**
- Activate virtual environment: `source venv/bin/activate`
- Run the agent: `python main.py`

Type your questions and the agent will respond with beautifully formatted bordered output.

Type `quit` to exit.

## 💡 Example Conversations

### Complete Travel Planning with MCP
Ask: "I want to visit Tokyo in December. Give me flight options from SFO, weather forecast, and recent news"

The agent will:
- Use `search_flights` to find flight options from SFO to Tokyo
- Use `get_weather` to fetch current conditions and 5-day forecast
- Use `get_local_news` to retrieve recent Tokyo news and events
- Combine all information into a comprehensive travel recommendation

### News Query
Ask: "Give me top 5 news about US government shutdown in New York"

The agent uses `get_local_news` to retrieve breaking news and current events for the specified location and topic.

### Weather Query
Ask: "What's the weather in Paris?"

The agent uses `get_weather` to provide current conditions (temperature, humidity, wind speed) and a 5-day forecast.

## 📁 Project Structure

```
my-first-ai-agent/
├── main.py                          # Main agent application
├── tools.py                         # Traditional LangChain tools
├── mcp_server/                      # MCP server (FastMCP)
│   ├── __init__.py
│   ├── main.py                      # FastMCP server entry point
│   ├── weather.py                   # Weather tools (modular)
│   └── news.py                      # News tools (modular)
├── requirements.txt                 # Python dependencies with versions
├── .env                             # Environment variables (not in repo)
└── README.md                        # This file
```

### Key Files Explained

**main.py** - Main application entry point
- Loads environment variables BEFORE importing MCP tools (critical!)
- Imports MCP tools directly (not via subprocess)
- Wraps MCP functions with LangChain `@tool` decorator
- Optimized system prompt for travel planning
- Bordered response formatting

**tools.py** - Traditional LangChain tools
- Time, calculator, and flight search tools
- Simple, in-process execution
- Good for basic operations

**mcp_server/main.py** - FastMCP server entry
- Ultra-simple: 23 lines of code
- Auto-registers tools from weather.py and news.py
- Can run standalone for testing: `python mcp_server/main.py`

**mcp_server/weather.py** - Weather functionality
- Refactored into 5 focused functions
- Geocoding + weather forecast from OpenWeatherMap
- Clean separation of concerns

**mcp_server/news.py** - News functionality
- Refactored into 7 focused functions
- Country code mapping for location queries
- NewsAPI integration with proper error handling

## 🏗️ Architecture

### Traditional Tools vs MCP Server

**Traditional LangChain Tools (tools.py)**
Flow: User Input → Claude → Tool Decision → Direct Function Call → Response
- Simple to implement, fast execution (in-process)
- Good for basic operations
- Limited separation of concerns

**MCP Server Tools (FastMCP) - Proper Client-Server Architecture**
Flow: User Input → Claude → Tool Decision → MCP Client → JSON-RPC → MCP Server (separate process) → Tool Execution → API Call → Response
- True separation: Server runs as separate process
- Location independent: Server can run on different machine
- Standard protocol: Uses JSON-RPC over stdio
- Modular architecture: Each tool in own file
- Easy to scale: Add servers without modifying agent
- Clean separation of concerns: Agent and tools completely isolated
- Industry-standard: Follows Model Context Protocol specification
- Better for complex operations: Multi-API integrations in isolated process

### MCP Client-Server Communication

The agent communicates with the MCP server using JSON-RPC protocol:

**1. Server Startup:**
Agent uses `FastMCPClient` to start MCP server as subprocess with command: `['python', 'mcp_server/main.py']`

**2. Tool Discovery:**
Agent sends `tools/list` request to discover available tools. Server responds with list of tool names and schemas.

**3. Tool Execution:**
Agent sends `tools/call` request with tool name and arguments. Server executes the tool and returns the result.

### Environment Variables

**Both the agent and MCP server need to load environment variables:**

**Agent (main.py):**
Calls `load_dotenv()` to load Anthropic API key for Claude

**MCP Server (mcp_server/main.py):**
Calls `load_dotenv()` to load OpenWeather and NewsAPI keys

This is necessary because the MCP server runs as a **separate process** with its own environment.

## 🔧 Configuration

### System Prompt Customization

The optimized system prompt in `main.py` defines the agent's behavior using `SYSTEM_PROMPT` variable.

The prompt instructs the agent to:
- Act as an intelligent travel planning assistant with access to real-time data tools
- Proactively combine weather, news, and flight data for comprehensive recommendations
- Use tools to provide accurate, up-to-date information
- Be concise and actionable in responses
- Consider weather and local events when dates are mentioned
- Present flight options with prices, duration, and airline details

### Adding New MCP Tools

To add a new tool to the MCP server:

1. **Create a new file** in `mcp_server/` (e.g., `restaurants.py`)
   - Define your function with proper docstring and type hints
   - Load any required API keys using `os.getenv()`

2. **Register in mcp_server/main.py**
   - Import your function
   - Register it using `mcp.tool()` decorator

3. **Import in main.py**
   - Import the function from mcp_server
   - Wrap it with LangChain `@tool` decorator

The agent will automatically discover and use your new tool through MCP protocol.

## 📦 Dependencies

**Key Libraries:**
- **anthropic** (0.72.0): Claude API client
- **langchain-anthropic** (1.0.2): LangChain integration for Anthropic
- **langchain-core** (1.0.4): Core LangChain functionality (messages, tools)
- **python-dotenv** (1.2.1): Environment variable management
- **fastmcp** (2.13.0.2): Simplified Model Context Protocol server
- **requests** (2.32.3): HTTP library for API calls

See [requirements.txt](requirements.txt) for complete dependency list.

## 💰 API Costs

All APIs offer generous free tiers perfect for development and demos:

| Service | Free Tier | Pricing |
|---------|-----------|---------|
| **Claude Sonnet 4.5** | Pay-as-you-go | ~$3 per million input tokens |
| **SerpApi** | 100 searches/month | [View pricing](https://serpapi.com/pricing) |
| **OpenWeatherMap** | 1,000 calls/day | Free forever on dev plan |
| **NewsAPI** | 100 requests/day | Free on developer plan |

**Cost Estimation for Demo:**
- 50 conversations with tools: < $1
- Weather checks: Free (well under daily limit)
- News queries: Free (well under daily limit)
- Flight searches: Free (under monthly limit)

## 🔍 How It Works

1. **User Input**: You type a message
2. **LLM Processing**: Claude Sonnet 4.5 analyzes and decides if tools are needed
3. **Tool Execution**: Required tools are executed automatically
   - Traditional tools: Direct function calls
   - MCP tools: Imported functions from mcp_server
4. **Response Generation**: Claude uses tool results to formulate comprehensive response
5. **History Tracking**: All messages stored for conversation context
6. **Formatted Output**: Response wrapped in professional `#` borders

## 🐛 Troubleshooting

### Environment Variables

**Issue**: `ANTHROPIC_API_KEY not found`
- **Solution**: Ensure `.env` file exists in project root with valid API key
- **Check**: `.env` file should NOT have quotes around values (unless the value itself contains them)

**Issue**: Weather/News tools return "API key not configured"
- **Solution**: API keys MUST be loaded before importing MCP tools
- **Check**: In `main.py`, ensure `load_dotenv()` is called BEFORE MCP imports

### API Issues

**Issue**: OpenWeatherMap returns 401 Unauthorized
- **Solution**: New API keys can take 2-4 hours to activate. Wait and try again.
- **Alternative**: Generate a new key at [OpenWeatherMap](https://openweathermap.org/api)

**Issue**: NewsAPI returns no articles
- **Solution**: This is normal for some location/category combinations
- **Try**: Use broader locations ("United States" instead of specific cities)

**Issue**: Flight search returns empty results
- **Solution**: Ensure dates are in YYYY-MM-DD format and use valid IATA airport codes
- **Examples**: JFK (New York), LAX (Los Angeles), ORD (Chicago), SFO (San Francisco)

### Documentation
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Tool Calling Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)

### API References
- [SerpApi Google Flights API](https://serpapi.com/google-flights-api)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [NewsAPI Documentation](https://newsapi.org/docs)

## 📝 What's New

### v3.0 - FastMCP Integration
- Added MCPServer integration
- Added News and Weather APIs
- Added smarter travel planning instructions (Flight+News+Weather)
- All AI responses wrapped in professional `#` borders

### v2.0 - Flight Search Integration
- Added real-time flight search using Google Flights data via SerpApi
- Organized tools into separate `tools.py` module
- Enhanced error handling and debugging
- Updated documentation with flight search examples

### v1.0 - Initial Release
- Basic conversational AI with Claude Sonnet 4.5
- Time and calculator tools
- Conversation memory and context tracking