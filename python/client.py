import requests

s = requests.session()
unique_id = s.get("http://127.0.0.1:5000/get_unique_id").json()["id"]
print(unique_id)
while True:
    # Assuming you want to make a request to the stream endpoint
    stream_response = s.get(f"http://127.0.0.1:5000/stream?unityid={unique_id}", stream=True)

    # You should also handle streaming the response here if that's your intent
    try:
        for line in stream_response.iter_lines():
            if line:
                print(line.decode('utf-8'))
    except KeyboardInterrupt:
        # Handling a keyboard interrupt to stop the script
        break

    input()