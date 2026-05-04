import os
import json

from logging import Logger
from typing import List

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain.chat_models import BaseChatModel

from agents.base_agent.chat_message import ChatMessage

_MCP_SERVER_DIR = os.path.abspath(
  os.path.join(os.path.dirname(__file__), '../../../../mcp-server')
)

server_params = StdioServerParameters(
  command='uv',
  args=['--directory', _MCP_SERVER_DIR, 'run', 'src/main.py'],
  env=None,
)


async def run_mcp_chat(messages: List[ChatMessage], model: BaseChatModel, max_tool_run: int = 8) -> str:
  logger = Logger(run_mcp_chat.__name__)
  async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # 1. Discover available MCP tools before the chat starts
        tools_response = await session.list_tools()
        tool_list = [
          {
            "type": "function",
            "function": {
              "name": t.name,
              "description": t.description or "",
              "parameters": t.inputSchema,
            },
          }
          for t in tools_response.tools
        ]

        model_with_tools = model.bind_tools(tool_list)

        # 2. Tool-calling loop: execute tools and pass results back to LLM
        for _ in range(max_tool_run):
          response = await model_with_tools.ainvoke(messages)
          messages.append(response)

          if not response.tool_calls:
            return response.content

          for tool_call in response.tool_calls:
            logger.log(
              level=30,
              msg=f'Tool {tool_call["name"]} is called with arguments: {tool_call['args']}'
            )
            
            result = await session.call_tool(
              tool_call["name"],
              arguments=tool_call["args"],
            )

            result_contents = result.content

            logger.log(30, f'Tool {tool_call['name']} result: {result_contents}')

            tool_content = "\n".join(
              item.text for item in result_contents if hasattr(item, "text")
            )

            if result.isError:
              messages.append(ToolMessage(
                content=f'Failed to call tool {tool_call["name"]}: {tool_content}',
                tool_call_id=tool_call['id']
              ))
              
              continue
            
            messages.append(ToolMessage(
              content=tool_content,
              tool_call_id=tool_call["id"],
            ))