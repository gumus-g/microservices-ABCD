import zmq # type: ignore # type: ignore
import json
from hashlib import sha256

users_file = "users.json"

def load_users():
    """Load user data from JSON file."""
    try:
        with open(users_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users):
    """Save user data to JSON file."""
    with open(users_file, 'w') as file:
        json.dump(users, file, indent=2)

def register_user(data):
    users = load_users()
    username = data.get("username")
    password = data.get("password")
    if username in users:
        return {"Error": "User already exists."}
    hashed_password = sha256(password.encode()).hexdigest()
    users[username] = hashed_password
    save_users(users)
    return {"Message": f"User '{username}' registered successfully."}

def login_user(data):
    users = load_users()
    username = data.get("username")
    password = data.get("password")
    hashed_password = sha256(password.encode()).hexdigest()
    if users.get(username) == hashed_password:
        return {"Message": f"User '{username}' logged in successfully."}
    return {"Error": "Invalid credentials."}

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:6001")  # Port for Microservice B

    print("Microservice B (User Authentication) is running...")

    while True:
        request = socket.recv_json()  # Receive request
        action = request.get("action")
        if action == "register":
            response = register_user(request)
        elif action == "login":
            response = login_user(request)
        else:
            response = {"Error": "Invalid action specified."}
        socket.send_json(response)

if __name__ == "__main__":
    main()