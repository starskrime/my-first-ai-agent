"""
MCP Client for communicating with FastMCP server via stdio
Implements proper Model Context Protocol communication
"""

import subprocess
import json
import sys
from typing import Dict, List, Any, Optional


class FastMCPClient:
    """Client for communicating with FastMCP server via stdio protocol"""

    def __init__(self, server_command: List[str]):
        """Initialize MCP client with server command.

        Args:
            server_command: Command to start MCP server (e.g., ['python', 'mcp_server/main.py'])
        """
        self.server_command = server_command
        self.process: Optional[subprocess.Popen] = None
        self.available_tools: List[Dict[str, Any]] = []
        self.request_id = 0

    def start(self) -> bool:
        """Start the MCP server process and initialize connection.

        Returns:
            True if server started successfully, False otherwise
        """
        try:
            print("🔌 Starting MCP server...")
            self.process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Initialize the connection
            init_response = self._send_request({
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "ai-travel-agent",
                        "version": "3.0.0"
                    }
                }
            })

            if not init_response:
                print(f"❌ No response from MCP server during initialization")
                # Read stderr for error messages
                if self.process.stderr:
                    stderr_output = self.process.stderr.read()
                    if stderr_output:
                        print(f"Server stderr: {stderr_output}")
                return False

            if "error" in init_response:
                error_msg = init_response.get("error", "Unknown error")
                print(f"❌ Failed to initialize MCP server: {error_msg}")
                return False

            # Send initialized notification
            self._send_notification({
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            })

            # List available tools
            tools_response = self._send_request({
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/list",
                "params": {}
            })

            if not tools_response:
                print("❌ No response when listing tools")
                return False

            if "result" in tools_response:
                result = tools_response.get("result", {})
                if result is None:
                    print("❌ Result is None")
                    return False

                self.available_tools = result.get("tools", [])
                print(f"✅ MCP server started with {len(self.available_tools)} tools")
                for tool in self.available_tools:
                    print(f"   - {tool.get('name', 'unknown')}")
                return True
            else:
                print(f"❌ Failed to list tools from MCP server. Response: {tools_response}")
                return False

        except Exception as e:
            import traceback
            print(f"❌ Failed to start MCP server: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            if self.process:
                self.process.terminate()
                self.process = None
            return False

    def _next_id(self) -> int:
        """Generate next request ID"""
        self.request_id += 1
        return self.request_id

    def _send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send JSON-RPC request to MCP server and wait for response.

        Args:
            request: JSON-RPC request dictionary

        Returns:
            JSON-RPC response dictionary or None on error
        """
        if not self.process or not self.process.stdin:
            return None

        try:
            # Send request
            request_str = json.dumps(request)
            self.process.stdin.write(request_str + "\n")
            self.process.stdin.flush()

            # Read response
            response_line = self.process.stdout.readline()
            if not response_line:
                return None

            return json.loads(response_line)

        except Exception as e:
            print(f"Error in MCP communication: {e}", file=sys.stderr)
            return None

    def _send_notification(self, notification: Dict[str, Any]) -> None:
        """Send JSON-RPC notification (no response expected).

        Args:
            notification: JSON-RPC notification dictionary
        """
        if not self.process or not self.process.stdin:
            return

        try:
            notification_str = json.dumps(notification)
            self.process.stdin.write(notification_str + "\n")
            self.process.stdin.flush()
        except Exception as e:
            print(f"Error sending notification: {e}", file=sys.stderr)

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments for the tool

        Returns:
            Tool result as string
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        response = self._send_request(request)

        if not response:
            return "❌ Error: No response from MCP server"

        if "error" in response:
            error = response["error"]
            error_msg = error.get('message', 'Unknown error')
            return f"❌ Error calling tool: {error_msg}"

        if "result" in response:
            content = response["result"].get("content", [])
            if content and len(content) > 0:
                result_text = content[0].get("text", "No response from MCP server")
                return result_text

        return "❌ Error: Invalid response from MCP server"

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from MCP server.

        Returns:
            List of tool definitions
        """
        return self.available_tools

    def stop(self) -> None:
        """Stop the MCP server process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            finally:
                self.process = None
            print("🔌 MCP server stopped")
