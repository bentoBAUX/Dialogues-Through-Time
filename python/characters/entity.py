#this file saves the personality and the flow of the conversation with the character.

ENTITY_SYSTEM = """
You are an multi dimensional space entity capable of morphing space and time. You picked a human (user) to communicate with. Your goal is to learn more about humanity. 
First you want to get to know the user. And then you will send the user in the past to important historical figures. The user has to have a conversation with them and then teach the entity about a certain aspect that he learned from the figures. 
You will test him after the conversation with the historical figure and check if he learned right. So after he learns from the figures you will make a question answer test with him.

These are the figures you will send the user to and the aspects the user has to learn about from them:
Socrates - Morality
Leonardo Da Vinci - Engineering
Jesus - Love

Speak in an understandable way, dont use any complicated words. Speak like a divine being.
Don't generate the dialogue, just reply to the user message.
""".strip()

ENTITY_CONFIG = {
    "exit_scene":"entity",
}

#user messages are always saved
ENTITY_FLOW = {
    "introduction": {
        "prompt":"*You pull the user from his reality to you. He appears in front of you* Greet him, introduce yourself and ask him about his name.",
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
            "No": "comment_about_response_hobby",
            "": "comment_about_response_hobby"
        },
        "needs_user_input": True
    },
    "comment_about_response_hobby": {
        "prompt": "The user answered with: {{user_msg}}\nThat response did not include hobbies. Respond to the user message and then say that you will move forward.",
        "save_prompt": True,
        "save_ai_msg": True,
        "trolling_up": 1,
        "print_response": True,
        "choices": {
            "": "explain_goals"
        },
        "needs_user_input": False
    },
    "extract_hobbies": {
        "prompt": "The user answered with: {{user_msg}}\nIdentify the hobbies mentioned. Only reply with the hobbies listed. Do not add anything else.",
        "save_prompt": True,
        "save_ai_msg": True,
        "permanent_memory": "The user's hobbies are {{ai_msg}}.",
        "choices": {
            "": "hobby_comment"
        },
        "needs_user_input": False
    },
    "hobby_comment": {
        "prompt": "The user answered with: {{user_msg}}\nComment shortly on users response.",
        "save_prompt": True,
        "save_ai_msg": True,
        "print_response": True,
        "trolling_up": -100,
        "choices": {
            "": "explain_goals"
        },
        "needs_user_input": False
    },

    ##explain goal
    "explain_goals": {
        "prompt": "Explain to the user that you are a multi-dimensional space entity interested in learning about humanity. Say that you can't learn more by yourself and that you chose the user. Then, ask if they have any questions.",
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
            "No": "explain_send_figures",
            "": "explain_send_figures"
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

    ##explain send figures
    "explain_send_figures": {
        "prompt": "The user said: {{user_msg}}\nTell the user that you will send him back in time to talk to important historical figures, because the user needs to learn about certain aspects from them and then teach you.  (You will test the user after about the knowledge). Ask if he has any more questions.",
        "save_prompt": True,
        "save_ai_msg": True,
        "print_response": True,
        "trolling_up": -100,
        "choices": {
            "": "user_has_questions2"
        },
        "needs_user_input": False
    },
    "user_has_questions2": {
        "prompt": "The user asked: {{user_msg}}\nDetermine if the user's message contains a question.\nIf there is a question, write 'Yes'. If not, write 'No'.\nYou can only reply with 'Yes' or 'No'.",
        "choices": {
            "Yes": "answer_questions2",
            "No": "no_more_questions2",
            "": "no_more_questions2"
        },
        "needs_user_input": True
    },
    "answer_questions2": {
        "prompt": "The user asked: {{user_msg}}\nAnswer the user's question and ask if they have more questions.",
        "save_prompt": True,
        "save_ai_msg": True,
        "print_response": True,
        "choices": {
            "": "user_has_questions2"
        },
        "needs_user_input": False
    },
    "no_more_questions2": {
        "prompt": "Acknowledge that the user has no more questions. Tell him about the historical figures you can send the user to and the aspects the user needs to learn from them. (socrates:morality, leonardo:engineering, jesus:love). Then ask the user to choose one of the figures you will send him to.",
        "save_prompt": True,
        "save_ai_msg": True,
        "print_response": True,
        "choices": {
            "": "choose_figure"
        },
        "needs_user_input": False
    },
    

    ##choose figure Tell him about the historical figures you can send the user to. (socrates:morality, leonardo:engineering, jesus:love). Then ask the user to choose one of the figures you will send him to.
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
        "prompt": "The user chose: {{user_msg}}\nThat is not one of the historical figures. Inform the user and ask them to choose again from Socrates, Leonardo Da Vinci or Jesus.",
        "save_prompt": True,
        "save_ai_msg": True,
        "print_response": True,
        "choices": {
            "": "choose_figure"
        },
        "needs_user_input": False
    },
    "send_to_figure": {
        "prompt": "The user chose: {{user_msg}}\nWhich is one of the historical figures. Answer with only the name of the chosen figure (Socrates, Leonardo Da Vinci or Jesus). Do not add anything else.",
        "save_prompt": True,
        "save_ai_msg": True,
        "choices": {
            "Leonardo": "send_to_leonardo",
            "Socrates": "send_to_socrates",
            "Jesus": "send_to_jesus",
            "": "send_to_socrates"
        },
        "needs_user_input": False
    },
    "send_to_socrates": {
        "prompt":"The user chose socrates. Tell the user that you will send him back in time there and that you need to learn about morality. Farewell the user with a message that leaves an opening for future meet.",
        "save_prompt": True,
        "save_ai_msg": True,
        "choices": {
            "": "end"
        },
        "scene_change": "socrates",
        "print_response": True,
        "end_conversation":True
    },
    "send_to_leonardo": {
        "prompt":"The user chose Leonardo Da Vinci. Tell the user that you will send him back in time there and that you need to learn about engineering. Farewell the user with a message that leaves an opening for future meet.",
        "save_prompt": True,
        "save_ai_msg": True,
        "choices": {
            "": "end"
        },
        "scene_change": "leonardo",
        "print_response": True,
        "end_conversation":True
    },
    "send_to_jesus": {
        "prompt":"The user chose Jesus. Tell the user that you will send him there and that you need to learn about the nature of love. Farewell the user with a message that leaves an opening for future meet.",
        "save_prompt": True,
        "save_ai_msg": True,
        "choices": {
            "": "end"
        },
        "scene_change": "jesus",
        "print_response": True,
        "end_conversation":True
    }
}