import os

from langchain_anthropic import ChatAnthropic

from agents.base_agent.base_agent import BaseAgent

class ClaudeAgent(BaseAgent):
  def __init__(
    self,
    system_prompt: str = '',
  ):
    ENV_NAME = 'ANTHROPIC_API_KEY'
    api_key = os.getenv(ENV_NAME)
    if api_key is None or len(api_key) == 0:
      raise ValueError(f'Missing required environment variable: {ENV_NAME}')
    
    model = ChatAnthropic(
      api_key=api_key,
      model_name='claude-sonnet-4-6',
      temperature=0.8,
    )

    super().__init__(
      model=model, 
      system_prompt=system_prompt
    )
