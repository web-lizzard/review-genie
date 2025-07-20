import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "bootstrap.web_app:bootstrap_web_api",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        factory=True,
    )
