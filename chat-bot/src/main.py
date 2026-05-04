import uvicorn
import dotenv
from server_config.server import start_app


def main():
    dotenv.load_dotenv()
    app = start_app()
    uvicorn.run(app, host="localhost", port=3001)


if __name__ == "__main__":
    main()
