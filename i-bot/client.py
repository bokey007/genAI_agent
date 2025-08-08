import requests

session_id = "my-session"

while True:
    message = input("You: ")
    if message.lower() == "exit":
        break

    response = requests.post("http://127.0.0.1:8000/chat", json={"session_id": session_id, "message": message})
    print(f"Bot: {response.json()['response']}")

    feedback = input("Satisfied? (y/n): ")
    satisfied = feedback.lower() == "y"
    requests.post("http://127.0.0.1:8000/feedback", json={"session_id": session_id, "satisfied": satisfied})