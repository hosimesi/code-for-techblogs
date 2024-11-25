from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def health():
    a = 1
    b = 2
    return {"Hello": "World", "result": a + b}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
