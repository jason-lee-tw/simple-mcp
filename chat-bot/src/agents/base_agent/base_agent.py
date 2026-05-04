import asyncio
from logging import Logger
from typing import List

from langchain.chat_models import BaseChatModel
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from agents.base_agent.chat_message import ChatMessage
from agents.tools.memory_mcp import run_mcp_chat, server_params


class BaseAgent:
  __model: BaseChatModel
  __system_prompt: str
  logger: Logger

  def __init__(self, model: BaseChatModel, system_prompt: str = ''):
    self.__system_prompt = system_prompt
    self.__model = model
    self.logger = Logger(__name__)

  def chat(self, user_message: str) -> str:
    messages: List[ChatMessage] = [
      ChatMessage(role='system', content=self.__system_prompt),
      ChatMessage(role='user', content=user_message),
    ]

    agent = create_agent(self.__model)

    try:
      response = agent.invoke({
        'messages': messages
      })

      result = response['messages'][-1].content

      return result
    except Exception as error:
      error_message = f"Error: Agent API request failed:\n{str(error)}"
      return error_message

  def chat_with_mcp(self, user_message: str) -> str:
    messages: List[ChatMessage] = [
      ChatMessage(role='system', content=self.__system_prompt),
      ChatMessage(role='user', content=user_message)
    ]
    
    try:
      return asyncio.run(
        run_mcp_chat(
          messages=messages,
          model=self.__model
        )
      )
    except Exception as error:
      return f"Error: Agent API request failed:\n{str(error)}"