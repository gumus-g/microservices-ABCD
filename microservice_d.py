import zmq # type: ignore
import json

interactions_file = "interactions.json"

def load_interactions():
    """Load interactions (ratings and tags) from JSON file."""
    try:
        with open(interactions_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_interactions(data):
    """Save interactions (ratings and tags) to JSON file."""
    with open(interactions_file, 'w') as file:
        json.dump(data, file, indent=2)

def rate_recipe(data):
    interactions = load_interactions()
    recipe_id = data.get("id")
    rating = data.get("rating")
    if recipe_id not in interactions:
        interactions[recipe_id] = {"ratings": [], "tags": []}
    interactions[recipe_id]["ratings"].append(rating)
    avg_rating = sum(interactions[recipe_id]["ratings"]) / len(interactions[recipe_id]["ratings"])
    save_interactions(interactions)
    return {"Message": f"Recipe '{recipe_id}' rated successfully.", "Average Rating": avg_rating}

def tag_recipe(data):
    interactions = load_interactions()
    recipe_id = data.get("id")
    tag = data.get("tag")
    if recipe_id not in interactions:
        interactions[recipe_id] = {"ratings": [], "tags": []}
    interactions[recipe_id]["tags"].append(tag)
    save_interactions(interactions)
    return {"Message": f"Tag '{tag}' added to recipe '{recipe_id}'."}

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:6003")  # Port for Microservice D

    print("Microservice D (Recipe Interaction) is running...")

    while True:
        request = socket.recv_json()  # Receive request
        action = request.get("action")
        if action == "rate":
            response = rate_recipe(request)
        elif action == "tag":
            response = tag_recipe(request)
        else:
            response = {"Error": "Invalid action specified."}
        socket.send_json(response)

if __name__ == "__main__":
    main()