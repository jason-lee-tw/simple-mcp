import logging

from mcp_config.mcp_server import mcp_server
import mcp_config.tools


def main():
    logger = logging.Logger(mcp_server.name)
    
    mcp_server.run(transport='stdio')
    logger.log(
        level=30,
        msg="MCP server initialized"
    )


if __name__ == "__main__":
    main()
