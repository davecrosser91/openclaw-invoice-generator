import uvicorn
from src.API.DocumentGenAPI import app

print("Starting HTTP Endpoint.")
uvicorn.run(app, host="0.0.0.0", port=8000)
