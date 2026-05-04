import uvicorn
import dotenv

from server_config.server import start_app
from server_config.tracer import register_phoenix_tracer


def main():
    dotenv.load_dotenv()
    register_phoenix_tracer()
    app = start_app()
    uvicorn.run(app, host='localhost', port=3001)


if __name__ == '__main__':
    main()
