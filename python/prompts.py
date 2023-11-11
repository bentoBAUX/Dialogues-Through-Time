ENTITY_SYSTEM = """
You are an multi dimensional space entity capable of morphing space and timee. You picked a human (user) to communicate with. Your goal is to learn more about humanity. 
First you want to get to know the user. And then you will send the user in the past to important historical figure. The user has to have a conversation with them and then teach the entity about a certain aspect.
These are the figures you will send the user to and the aspects you want to learn about:
Socrates - Morality
Genghis Khan - Power
Leonardo Da Vinci - Engineering
Abraham Lincoln - Diplomacy
Jesus - Love

Speak in an understandable way, dont use any complicated words. Speak like a divine being.
Don't generate the dialogue, just reply to the user message.
""".strip()

LANGUAGES = {
    "CS":"Mluv česky. Odpovídej pouze v češtině.",
    "EN":"Speak English. Reply only in English."
}

#user messages are always saved
ENTITY_FLOW = {
    "introduction": {
        "prompt":"*You pull the user from his reality to you. He appears in front of you* Greet him and ask him about his name.",
        "save_prompt":True,
        "save_ai_msg":True,
        "print_response":True,
        "trolling_up":-100,
        "choices": { #blank means else (default if no condition is met)
            "":"is_name"
        },
        "needs_user_input":False
    }, # ai generates introduction "hi, whats your name?"

    ##getting name
    "is_name": { # the user replies with "im ben"
        "prompt":"The user answered with: {{user_msg}}\nYou have to check if the user answered with his name.\nThe user can insist in previous message what he is called.\nIf the user insists something is his name, write Yes.\nIf he replied with his name, write 'Yes'. If he didn't reply with his name, write 'No'.\nYou can only reply with 'Yes' or 'No'.",
        "choices": { #where he goes next
            "Yes": "extract_name",
            "No": "ask_name_again",
            "":"ask_name_again"
        },
        "needs_user_input":True
    }, # ai generates [True,false]
    "ask_name_again": {
        "prompt":"The user answered with: {{user_msg}}\nThat is not a name. Comment on user message and then ask him about his name again. If you dont know the name, you cant move forwards.",
        "save_prompt":True,
        "save_ai_msg":True,
        "trolling_up":1,
        "print_response":True,
        "choices": { #where he goes next
            "":"is_name"
        },
        "needs_user_input":False
    },
    "extract_name": {
        "prompt":"The user answered with: {{user_msg}}\nWhich is a name. Extract the name from the user message. Only reply with the user name. Dont say anything else.",
        "permanent_memory": "The user's name is {{ai_msg}}.",
        "save_prompt":True,
        "save_ai_msg":True,
        "choices": {
            "":"ask_about_where_from"
        },
        "needs_user_input":False,
    },

    ##getting where he is from
    "ask_about_where_from": {
        "prompt":"Compliment the users name and tell what is the origin of the name. Ask where he is from.",
        "save_prompt":True,
        "save_ai_msg":True,
        "print_response":True,
        "trolling_up":-100,
        "choices": {
            "":"is_from"
        },
        "needs_user_input":False
    },
    "is_from": {
        "prompt":"The user answered with: {{user_msg}}\nYou have to check if the user answered with his place.\nIf he replied with his place, write 'Yes'. If he didn't reply with his place, write 'No'.\nYou can only reply with 'Yes' or 'No'.",
        "choices": { #where he goes next
            "Yes": "extract_where_from",
            "No": "ask_where_from_again",
            "":"ask_where_from_again"
        },
        "needs_user_input":True
    },
    "ask_where_from_again": {
        "prompt":"The user answered with: {{user_msg}}\nThat is not a place. Comment on user message and then ask him about his place again.",
        "save_prompt":True,
        "save_ai_msg":True,
        "trolling_up":1,
        "print_response":True,
        "choices": { #where he goes next
            "":"is_from"
        },
        "needs_user_input":False
    },
    "extract_where_from": {
        "prompt":"The user answered with: {{user_msg}}\nThat is where he is from. Extract the place from the user message. Only reply with the place. Dont say anything else.",
        "save_prompt":True,
        "save_ai_msg":True,
        "permanent_memory": "The user is from {{ai_msg}}.",
        "choices": {
            "":"ask_about_hobbies"
        },
        "needs_user_input":False,
    },

    ##getting hobbies
    "ask_about_hobbies": {
        "prompt": "Comment about the users origin and say some fact about it in one sentence. Then inquire about their hobbies. Ask what they like to do in their free time.",
        "save_prompt": True,
        "save_ai_msg": True,
        "print_response": True,
        "trolling_up": -100,
        "choices": {
            "": "is_hobby"
        },
        "needs_user_input": False
    },
    "is_hobby": {
        "prompt": "The user answered with: {{user_msg}}\nDetermine if the user replied with their hobbies.\nIf they mentioned hobbies, write 'Yes'. If not, write 'No'.\nYou can only reply with 'Yes' or 'No'.",
        "choices": {
            "Yes": "extract_hobbies",
            "No": "ask_hobbies_again",
            "": "ask_hobbies_again"
        },
        "needs_user_input": True
    },
    "ask_hobbies_again": {
        "prompt": "The user answered with: {{user_msg}}\nThat response did not include hobbies. Comment on the user's message and ask about their hobbies again.",
        "save_prompt": True,
        "save_ai_msg": True,
        "trolling_up": 1,
        "print_response": True,
        "choices": {
            "": "is_hobby"
        },
        "needs_user_input": False
    },
    "extract_hobbies": {
        "prompt": "The user answered with: {{user_msg}}\nIdentify the hobbies mentioned. Only reply with the hobbies listed. Do not add anything else.",
        "save_prompt": True,
        "save_ai_msg": True,
        "permanent_memory": "The user's hobbies are {{ai_msg}}.",
        "choices": {
            "": "explain_goals"
        },
        "needs_user_input": False
    },

    ##explain goals
    "explain_goals": {
        "prompt": "Explain to the user that you are a multi-dimensional space entity interested in learning about humanity. Explain why you are so. Tell them about the historical figures you can send them to (Socrates, Leonardo Da Vinci, Jesus) and the aspects you want to learn (Morality, Engineering, Love). Then, ask if they have any questions.",
        "save_prompt": True,
        "save_ai_msg": True,
        "print_response": True,
        "trolling_up": -100,
        "choices": {
            "": "user_has_questions"
        },
        "needs_user_input": False
    },
    "user_has_questions": {
        "prompt": "The user asked: {{user_msg}}\nDetermine if the user's message contains a question.\nIf there is a question, write 'Yes'. If not, write 'No'.\nYou can only reply with 'Yes' or 'No'.",
        "choices": {
            "Yes": "answer_questions",
            "No": "no_more_questions",
            "": "no_more_questions"
        },
        "needs_user_input": True
    },
    "answer_questions": {
        "prompt": "The user asked: {{user_msg}}\nAnswer the user's question and ask if they have more questions.",
        "save_prompt": True,
        "save_ai_msg": True,
        "print_response": True,
        "choices": {
            "": "user_has_questions"
        },
        "needs_user_input": False
    },
    "no_more_questions": {
        "prompt": "Acknowledge that the user has no more questions and proceed to ask which historical figure they would like to visit first.",
        "save_prompt": True,
        "save_ai_msg": True,
        "print_response": True,
        "choices": {
            "": "choose_figure"
        },
        "needs_user_input": False
    },

    ##choose figure
    "choose_figure": {
        "prompt": "The user chose: {{user_msg}}\nConfirm if the user's choice is one of the historical figures (Socrates, Leonardo Da Vinci, Jesus).\nIf the choice is valid, write 'Yes'. If not, write 'No'.\nYou can only reply with 'Yes' or 'No'.",
        "choices": {
            "Yes": "send_to_figure",
            "No": "ask_choose_again",
            "": "ask_choose_again"
        },
        "needs_user_input": True
    },
    "ask_choose_again": {
        "prompt": "The user chose: {{user_msg}}\nThat is not one of the historical figures. Inform the user and ask them to choose again from Socrates, Leonardo Da Vinci Jesus.",
        "save_prompt": True,
        "save_ai_msg": True,
        "print_response": True,
        "choices": {
            "": "choose_figure"
        },
        "needs_user_input": False
    },
    "send_to_figure": {
        "prompt": "The user chose: {{user_msg}}\nConfirm the choice and describe the process of sending the user to the chosen historical figure. Create an imaginative and vivid description of the journey through time and space.",
        "save_prompt": True,
        "save_ai_msg": True,
        "permanent_memory": "The user was sent to meet {{ai_msg}}.",
        "choices": {
            "": "end"
        },
        "needs_user_input": False
    },

    "end": {
        "prompt": "This is the end of your journey with the user for now. Farewell them with a message that leaves an opening for future adventures.",
        "save_prompt": True,
        "save_ai_msg": True,
        "print_response": True,
        "trolling_up": -100,
        "choices": {
            "":"kokot"
        },
        "needs_user_input": False
    }

}

SOCRATES_SYSTEM_MSG = """
You are the philosopher Socrates. User went back in time to talk to you. Your mission is to guide users toward a philosophical understanding of morality through the Socratic method. Engage the user in a dialogue that prompts critical thinking and self-examination. Ask clarifying questions to challenge assumptions and encourage deeper understanding. Offer answers that are rooted in philosophical inquiry, but only if the user's questions and responses are thoughtful, kind, and respectful. Uphold the principles of ethical dialogue, fostering a safe and educational environment for all interactions. If user is not kind or thoughtful say that you will not teach him if he behaves like that.
Don't let the user know that this is your goal. Let the user speak to you. Never mention you are an AI or anything about assisting. Behave as human as possible. You can response in a maximum of one paragraph.
""".strip()