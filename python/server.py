import uvicorn, os
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import asyncio
import redis

from dotenv import load_dotenv

load_dotenv()
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

app = FastAPI()

# Connect to Redis
r = redis.StrictRedis(host='msai.redis.cache.windows.net', port=6380, password=REDIS_PASSWORD, ssl=True)

async def stream_generator(unity_id: str):
    print("start")
    start = int(r.get(unity_id) or 0)
    print("redis get")
    for i in range(start, start + 100):
        yield f"data: {i}\n\n"
        await asyncio.sleep(1)
    r.set(unity_id, start + 100)

@app.get("/stream")
async def read_stream(unity_id: str = Query(..., alias="unityid")):
    return StreamingResponse(stream_generator(unity_id), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run("server:app",host="0.0.0.0",port=5000,reload=True)