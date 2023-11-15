import uvicorn, os, uuid, asyncio, redis,json
import openai
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from dataclasses import dataclass, field
from time import sleep
from traceback import print_exc

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
    ai_msg: str = ""
    system_msg: str = ""
    memory: str = ""
    jazyk: str = "EN"
    chat_history: list = field(default_factory=list)
    trolling: int = 0
    end_reason: str = ""
    print_response: bool = True

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

##gpt calling
async def gpt_call(messages,temperature=0.4):
    while True:
        try:
            response = ""
            for chunk in openai.ChatCompletion.create(
                #engine="gpt-4",
                model="gpt-4-1106-preview",
                messages = messages,
                temperature=temperature,
                max_tokens=2000,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                stream=True,
            ):
                if (chunk["choices"]):
                    content = chunk["choices"][0].get("delta", {}).get("content")
                    if content is not None:
                        response += content
                        yield response
                        await asyncio.sleep(0.00001)
            break
        except openai.error.RateLimitError:
            print("Rate limit exceeded, waiting")
            print_exc()
            sleep(10)
        except openai.error.InvalidRequestError:
            print_exc()
            print("Content policy violation")
            yield None
            break

#chat flow
async def handle_chat(c:ChatState,usr_msg_sent:str):
    print(c.current_state)
    flow = ENTITY_FLOW[c.current_state]
    c.system_msg = ENTITY_SYSTEM + "\n" + c.memory
    if (c.jazyk): c.system_msg += "\n" + LANGUAGES[c.jazyk]

    #trolling too much
    if ("trolling_up" in flow):
        c.trolling += max(0,flow["trolling_up"])

    if (c.trolling >= TROLLING_LIMIT):
        print("Trolling too much. BYE. DONT COME BACK.")
        c.end_reason = "trolling"
        return

    #get input
    needs_input = "needs_user_input" in flow and flow["needs_user_input"]
    if (needs_input and c.end_reason != "needs_input"):
        c.end_reason = "needs_input"
        return
    else:
        print("got new input",usr_msg_sent)
        c.user_msg = usr_msg_sent
    
    #get gpt response
    c.print_response = "print_response" in flow and flow["print_response"]
    prompt = flow["prompt"].replace("{{user_msg}}",c.user_msg).replace("{{ai_msg}}",c.ai_msg)
    c.ai_msg = ""

    #handle chat send
    system_msg_dict = {"role":"system","content":c.system_msg}
    user_msg_dict = {"role":"user","content":prompt}
    chat_history_dict = c.chat_history.copy()
    chat_history_dict.append(user_msg_dict)

    async for response in gpt_call([system_msg_dict] + chat_history_dict):        
        c.ai_msg = response
        yield

    if (not response):
        print("response whas null")
        raise Exception("Response was null")

    #save to chat history
    if ("save_prompt" in flow and flow["save_prompt"]):
        c.chat_history.append({"role":"user","content":prompt})

    if ("save_ai_msg" in flow and flow["save_ai_msg"]):
        c.chat_history.append({"role":"assistant","content":response})

    #save extracted ai thing to memory
    if ("permanent_memory" in flow):
        c.memory += f"\n{flow['permanent_memory'].replace('{{ai_msg}}',response)}"

    #end conversation
    if ("end_conversation" in flow and flow["end_conversation"]):
        c.end_reason = "end_conversation"
    
    #get next state
    for key, value in flow["choices"].items():
        if (len(key) == 0 or key.lower() in response.lower()):
            c.current_state = value
            break

    c.end_reason = "forward"

## get unique id for saving
@app.get("/get_unique_id")
def get_unique_id():
    unique_id = str(uuid.uuid4())  # Generate a random UUID
    return {"id": unique_id}

## Stream the response of gpt
async def stream_generator(unique_id: str,user_msg):
    chat_state = get_or_create_chat_state(unique_id)
    if (chat_state.processing):
        print("processing")
        raise Exception("processing and got a streaming call")
    else:
        try:
            chat_state.processing = True
            set_chat_state(unique_id, chat_state)
           
            i = 0
            while (i == 0 or chat_state.end_reason == "" or chat_state.end_reason == "forward"):
                async for response in handle_chat(chat_state,user_msg):
                    response_data = json.dumps({"ai_speaking": chat_state.ai_msg})
                    i += 1
                    print(response_data)
                    if (chat_state.print_response):
                        yield f"data: {response_data}\n\n"  # Ensure SSE format

            chat_state.processing = False
            set_chat_state(unique_id, chat_state)
            response_data = json.dumps(chat_state.to_json())
            yield response_data.encode('utf-8') 

        #reset processing
        except Exception as e:
            chat_state.processing = False
            set_chat_state(unique_id, chat_state)
            print("exception")
            print_exc()
            raise e
        
@app.get("/chat/{unique_id}")
async def read_stream(unique_id: str, user_msg: str = Query(...)):
    return StreamingResponse(stream_generator(unique_id,user_msg), media_type="text/event-stream")

@app.get("/chat_state/{unique_id}")
def get_chat_state(unique_id: str):
    return get_or_create_chat_state(unique_id)

if __name__ == "__main__":
    uvicorn.run("server:app",host="0.0.0.0",port=5000)