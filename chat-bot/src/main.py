import uvicorn
from server_config.server import app


def main():
    uvicorn.run(app, host="localhost", port=3001)


if __name__ == "__main__":
    main()
