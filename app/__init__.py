from fastapi import FastAPI

app = FastAPI(
    title="Crypto Paper Trading Bot",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Crypto Paper Trading Bot is online 🚀"
    }