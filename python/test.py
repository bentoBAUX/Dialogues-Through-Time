import redis,os
from dotenv import load_dotenv

load_dotenv()
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


# Connect to Redis
r = redis.StrictRedis(host='msai.redis.cache.windows.net', port=6380, password=REDIS_PASSWORD, ssl=True)

# Test the connection
print(r.ping())
