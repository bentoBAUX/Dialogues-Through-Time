import uvicorn, os, uuid, asyncio, redis
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

from dotenv import load_dotenv

load_dotenv()
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

app = FastAPI()

# Connect to Redis
r = redis.StrictRedis(host='msai.redis.cache.windows.net', port=6380, password=REDIS_PASSWORD, ssl=True)


## get unique id for saving
@app.get("/get_unique_id")
def get_unique_id():
    unique_id = str(uuid.uuid4())  # Generate a random UUID
    return {"id": unique_id}

## Stream the response of gpt
async def stream_generator(unity_id: str):
    print("start")
    start = int(r.get(unity_id) or 0)
    print("redis get")
    for i in range(start, start + 10):
        yield f"data: {i}\n\n"
        await asyncio.sleep(1)
    r.set(unity_id, start + 10)
    

@app.get("/chat")
async def read_stream(unity_id: str = Query(..., alias="unityid")):
    return StreamingResponse(stream_generator(unity_id), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run("server:app",host="0.0.0.0",port=5000)