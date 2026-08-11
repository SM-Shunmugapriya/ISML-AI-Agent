from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "ISML AI Agent is running"
    }