from fastapi import FastAPI
from modules.root.root_controller import router as root_router

app = FastAPI()
app.include_router(root_router)
