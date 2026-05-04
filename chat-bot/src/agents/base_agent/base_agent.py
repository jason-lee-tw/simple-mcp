from langchain.chat_models import BaseChatModel
from langchain.agents import create_agent


class BaseAgent:
  __model: BaseChatModel
  __system_prompt: str

  def __init__(self, model: BaseChatModel, system_prompt: str = ''):
    self.__system_prompt = system_prompt
    self.__model = model

  def chat(self, user_message: str) -> str:
    messages = [
      {
        'role': 'system',
        'content': self.__system_prompt
      },
      {
        'role': 'user',
        'content': user_message
      }
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