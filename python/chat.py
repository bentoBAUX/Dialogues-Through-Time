import openai
from dotenv import load_dotenv
import os
from traceback import print_exc
from time import sleep

from prompts import *

load_dotenv()

TROLLING_LIMIT = 5


#openai.api_type = "azure"
#openai.api_base = "https://alagantgpt2.openai.azure.com/"
#openai.api_version = "2023-07-01-preview"
#openai.api_key = os.getenv("AZURE_API_KEY")
openai.api_key = os.getenv("API_KEY")

def chat_send(message,system_msg,chat_history,print_response=True):
    system_msg = {"role":"system","content":system_msg}
    user_msg = {"role":"user","content":message}
    chat_history = chat_history.copy()
    chat_history.append(user_msg)

    response = gpt_call([system_msg] + chat_history,print_response=print_response)
    if (response):
        chat_history.append({"role":"assistant","content":"".join(response)})
    else:
        chat_history.pop()

    return chat_history,response

def stream(content):
    print(content, end='',flush=True)

def gpt_call(messages,temperature=0.4,print_response=True):
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
                        if (print_response): stream(content)
                        response += content
            break
        except openai.error.RateLimitError:
            print("Rate limit exceeded, waiting")
            print_exc()
            sleep(10)
        except openai.error.InvalidRequestError:
            print_exc()
            print("Content policy violation")
            return None

    return response

if __name__ == "__main__":
    current_state = "introduction"
    user_msg = ""
    jazyk = "EN"
    memory = ""
    chat_history = []
    trolling = 0
    
    while True:
        flow = ENTITY_FLOW[current_state]
        system_msg = ENTITY_SYSTEM + "\n" + memory
        if (jazyk): system_msg += "\n" + LANGUAGES[jazyk]

        #trolling too much
        if ("trolling_up" in flow):
            trolling += max(0,flow["trolling_up"])
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


