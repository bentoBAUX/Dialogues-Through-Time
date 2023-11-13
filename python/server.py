import uvicorn, os, uuid, asyncio, redis,json
import openai
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from dataclasses import dataclass, field

from prompts import *
load_dotenv()

TROLLING_LIMIT = 5

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
openai.api_key = os.getenv("API_KEY")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Connect to Redis
r = redis.StrictRedis(host='msai.redis.cache.windows.net', port=6380, password=REDIS_PASSWORD, ssl=True)

@dataclass
class ChatState:
    processing: bool = False
    current_state: str = "introduction"
    current_person: str = "entity"
    user_msg: str = ""
    system_msg: str = ""
    memory: str = ""
    jazyk: str = "EN"
    chat_history: list = field(default_factory=list)
    trolling: int = 0

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(json_data):
        data = json.loads(json_data)
        return ChatState(**data)
    
# Function to retrieve or initialize chat state
def get_or_create_chat_state(unique_id):
    json_data = r.get(unique_id)
    if json_data:
        return ChatState.from_json(json_data)
    else:
        chat_state = ChatState()
        set_chat_state(unique_id, chat_state)
        return chat_state 
    
def set_chat_state(unique_id, chat_state):
    r.set(unique_id, chat_state.to_json())

#chat flow
async def handle_chat(c:ChatState):
    flow = ENTITY_FLOW[current_state]
    system_msg = ENTITY_SYSTEM + "\n" + memory
    if (c.jazyk): system_msg += "\n" + LANGUAGES[c.jazyk]

    #trolling too much
    if ("trolling_up" in flow):
        c.trolling += max(0,flow["trolling_up"]) ###I FINISHED HERE, I NEED TO CONVERT EVERYTHING TO C.VARIABLE AND THEN START TO RETURN RIGHT MESSAGES, YEASHHHH
    if (trolling >= TROLLING_LIMIT):
        print("Trolling too much you fucking piece of shit. BYE. DONT COME BACK.")
        break

    #get input
    needs_input = "needs_user_input" in flow and flow["needs_user_input"]
    if (needs_input):
        user_msg = input("\nYou: ")
    
    #get gpt response
    print_response = "print_response" in flow and flow["print_response"]
    prompt = flow["prompt"].replace("{{user_msg}}",user_msg)
    chat_history_response,response = chat_send(prompt,system_msg,chat_history,print_response=print_response)
    if (not response):
        print("response whas null")
        continue

    #save to chat history
    if ("save_prompt" in flow and flow["save_prompt"]):
        chat_history.append({"role":"user","content":prompt})

    if ("save_ai_msg" in flow and flow["save_ai_msg"]):
        chat_history.append({"role":"assistant","content":response})

    #save extracted ai thing to memory
    if ("permanent_memory" in flow):
        memory += f"\n{flow['permanent_memory'].replace('{{ai_msg}}',response)}"

    #end conversation
    if ("end_conversation" in flow and flow["end_conversation"]):
        break
    
    #get next state
    for key, value in flow["choices"].items():
        if (len(key) == 0 or key.lower() in response.lower()):
            current_state = value
            break

    #save chat state
    chat_state = {"processing":False,"current_state": current_state, "current_person":current_person, "user_msg": user_msg, "system_msg": system_msg, "memory":memory, "jazyk":jazyk, "chat_history": chat_history, "trolling": trolling}

## get unique id for saving
@app.get("/get_unique_id")
def get_unique_id():
    unique_id = str(uuid.uuid4())  # Generate a random UUID
    return {"id": unique_id}

## Stream the response of gpt
async def stream_generator(unique_id: str):
    response = ""
    chat_state = get_or_create_chat_state(unique_id)
    if (chat_state["processing"]):
        print("processing")
        raise Exception("processing and got a streaming call")
    else:
        chat_state["processing"] = True
        set_chat_state(unique_id, chat_state)
        print("redis gott")

        for i in range(0, 10):
            print(i)
            response += str(i) + " "
            yield f"dd: {response}\n\n"
            await asyncio.sleep(1)
        chat_state["processing"] = False
        set_chat_state(unique_id, chat_state)
        print(chat_state)
    

@app.get("/chat/{unique_id}")
async def read_stream(unique_id: str, user_msg: str = Query(...)):
    return StreamingResponse(stream_generator(unique_id), media_type="text/event-stream")

@app.get("/chat_state/{unique_id}")
def get_chat_state(unique_id: str):
    return get_or_create_chat_state(unique_id)

if __name__ == "__main__":
    uvicorn.run("server:app",host="0.0.0.0",port=5000)