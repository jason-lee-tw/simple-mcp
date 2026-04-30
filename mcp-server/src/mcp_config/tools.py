from memory_management.entities.memory_entity import MemoryEntry
from mcp_config.mcp_server import mcp_server
from memory_management.service import MemoryManagementService

@mcp_server.tool()
def add_memory(content: str) -> None:
  """
    Save content into memory.
    
    Args:
        content: Content in string format that to be saved into memory.
        
    Returns:
        None.
    """
  memory = MemoryManagementService()
  memory.save_memory(content)


@mcp_server.tool()
def get_memory(query: str, limit: int = 3) -> list[MemoryEntry]:
  """
    Fetch content from memory.

    Args:
        query: The query used to search for related content.
        limit: The max number of memory content required. Default is 3.

    Returns:
        A list of memory entry.
  """

  memory = MemoryManagementService()
  return memory.get_memory(query, limit)