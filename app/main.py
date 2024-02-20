from fastapi import FastAPI
import uvicorn
from routers.api_v1.api import api_router

app = FastAPI()
app.include_router(api_router)


@app.get("/")
async def index():
    return {"message": "Root page"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
