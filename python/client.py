import requests, json


s = requests.session()
unique_id = s.get("http://127.0.0.1:5000/get_unique_id").json()["id"]
print(unique_id)
while True:
    # Assuming you want to make a request to the stream endpoint
    inpt = input("You: ")
    data = {"user_msg": inpt,"unique_id":unique_id}
    if (inpt == "exit"):
        data["end_conversation"] = True
        
    stream_response = s.post(f"http://127.0.0.1:5000/chat", stream=True,json=data)

    # You should also handle streaming the response here if that's your intent
    try:
        prev_lines = 0
        for line in stream_response.iter_lines():
            if line:
                data_string  = line.decode('utf-8')
                #print(data_string,end="\n", flush=True)

                # Remove 'data:' prefix
                if ("data:" in data_string):
                    json_string = data_string.split(":", 1)[1].strip()
                else:
                    json_string = data_string

                # Convert JSON string to dictionary
                data_dict = json.loads(json_string)

                if "ai_speaking" in data_dict:
                    message = "AI: " + data_dict["ai_speaking"]
                    print(message)

    except KeyboardInterrupt:
        # Handling a keyboard interrupt to stop the script
        break
