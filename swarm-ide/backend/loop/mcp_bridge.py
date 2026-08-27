import asyncio
import json
import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

class MCPBridge:
    def __init__(self, workspace_path):
        self.config_path = os.path.join(workspace_path, "mcp.json")
    
    def get_config(self):
        if not os.path.exists(self.config_path):
            return {}
        try:
            with open(self.config_path, "r") as f:
                return json.load(f).get("mcpServers", {})
        except Exception:
            return {}

    async def _get_tools(self):
        servers = self.get_config()
        all_tools = []
        for name, config in servers.items():
            cmd = config.get("command")
            args = config.get("args", [])
            env = config.get("env", {})
            full_env = {**os.environ, **env}
            
            server_params = StdioServerParameters(command=cmd, args=args, env=full_env)
            try:
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        result = await session.list_tools()
                        for tool in result.tools:
                            all_tools.append({
                                "server": name,
                                "name": tool.name,
                                "description": tool.description,
                                "inputSchema": tool.inputSchema
                            })
            except Exception as e:
                print(f"Error loading MCP tools from {name}: {e}")
        return all_tools

    def get_tools_sync(self):
        return asyncio.run(self._get_tools())

    async def _call_tool(self, server_name, tool_name, tool_args):
        servers = self.get_config()
        if server_name not in servers:
            return f"Error: MCP Server '{server_name}' not found."
            
        config = servers[server_name]
        cmd = config.get("command")
        args = config.get("args", [])
        env = config.get("env", {})
        full_env = {**os.environ, **env}
        
        server_params = StdioServerParameters(command=cmd, args=args, env=full_env)
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    out = []
                    for c in result.content:
                        if c.type == "text":
                            out.append(c.text)
                    return "\n".join(out)
        except Exception as e:
            return f"MCP Tool execution failed: {e}"

    def call_tool_sync(self, server_name, tool_name, tool_args):
        return asyncio.run(self._call_tool(server_name, tool_name, tool_args))

_bridge = None
def get_mcp_bridge(workspace_path):
    global _bridge
    if _bridge is None:
        _bridge = MCPBridge(workspace_path)
    _bridge.config_path = os.path.join(workspace_path, "mcp.json")
    return _bridge
