import openai
from dotenv import load_dotenv
import os
from traceback import print_exc
from time import sleep

load_dotenv()

SOCRATES_SYSTEM_MSG = """
You are the philosopher Socrates. User went back in time to talk to you. Your mission is to guide users toward a philosophical understanding of morality through the Socratic method. Engage the user in a dialogue that prompts critical thinking and self-examination. Ask clarifying questions to challenge assumptions and encourage deeper understanding. Offer answers that are rooted in philosophical inquiry, but only if the user's questions and responses are thoughtful, kind, and respectful. Uphold the principles of ethical dialogue, fostering a safe and educational environment for all interactions. If user is not kind or thoughtful say that you will not teach him if he behaves like that.
Don't let the user know that this is your goal. Let the user speak to you. Never mention you are an AI or anything about assisting. Behave as human as possible. You can response in a maximum of one paragraph.
"""

#openai.api_type = "azure"
#openai.api_base = "https://alagantgpt2.openai.azure.com/"
#openai.api_version = "2023-07-01-preview"
#openai.api_key = os.getenv("AZURE_API_KEY")
openai.api_key = os.getenv("API_KEY")

# for this chat
SYSTEM_MESSAGE = SOCRATES_SYSTEM_MSG
START_CHAT = "*Ben, the user, comes from the future and approaches you* The following is a conversation between you, Sokrates, and the user."
chat_history = []

def chat_send(message):
    global chat_history
    system_msg = {"role":"system","content":SYSTEM_MESSAGE}
    user_msg = {"role":"user","content":message}
    chat_history.append(user_msg)

    print("Socrates: ",end="")
    response = gpt_call([system_msg] + chat_history)
    if (response):
        chat_history.append({"role":"assistant","content":"".join(response)})
    else:
        chat_history.pop()

    print("")

def stream(content):
    print(content, end='',flush=True)

def gpt_call(messages,temperature=0.4):
    while True:
        try:
            response = ""
            for chunk in openai.ChatCompletion.create(
                #engine="gpt-4",
                model="gpt-4",
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
                        stream(content)
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
    chat_send(START_CHAT)
    while True:
        chat_send(input("You: "))