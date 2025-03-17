import zmq  # type: ignore
import json

recipes_file = "recipes.json"

def load_recipes():
    """Load recipes from JSON file."""
    try:
        with open(recipes_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File '{recipes_file}' not found. Creating a new file.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{recipes_file}': {e}")
        return {}

def save_recipes(recipes):
    """Save recipes to JSON file."""
    try:
        with open(recipes_file, 'w') as file:
            json.dump(recipes, file, indent=2)
        print(f"Recipes saved successfully to '{recipes_file}'.")
    except Exception as e:
        print(f"Error saving recipes to file '{recipes_file}': {e}")

def create_recipe(data):
    """Create a new recipe."""
    print("Received create request:", data)
    recipes = load_recipes()
    print("Loaded recipes:", json.dumps(recipes, indent=2))

    # Ensure recipes is a list
    if not isinstance(recipes, list):
        print("Invalid recipes.json format: Expected a list.")
        return {"Error": "Invalid recipes.json format: Expected a list."}

    # Check if the recipe ID already exists
    recipe_id = data.get("id")
    for recipe in recipes:
        if recipe.get("id") == recipe_id:
            print(f"Recipe ID '{recipe_id}' already exists.")
            return {"Error": "Recipe ID already exists."}

    # Validate input fields
    if not data.get("name") or not data.get("ingredients") or not data.get("instructions") or not data.get("cooking_time"):
        print("Invalid data. Name, ingredients, instructions, and cooking time are required.")
        return {"Error": "Invalid data. Name, ingredients, instructions, and cooking time are required."}

    # Create the new recipe and append it to the list
    new_recipe = {
        "id": recipe_id,
        "name": data.get("name"),
        "ingredients": data.get("ingredients"),
        "instructions": data.get("instructions"),
        "cooking_time": data.get("cooking_time")
    }
    recipes.append(new_recipe)

    print("Updated recipes:", json.dumps(recipes, indent=2))
    save_recipes(recipes)
    print(f"Recipe '{recipe_id}' saved successfully.")
    return {"Message": f"Recipe '{recipe_id}' created successfully."}

def edit_recipe(data):
    """Edit an existing recipe."""
    print("Received edit request:", data)
    recipes = load_recipes()
    print("Loaded recipes:", json.dumps(recipes, indent=2))

    # Ensure recipes is a list
    if not isinstance(recipes, list):
        print("Invalid recipes.json format: Expected a list.")
        return {"Error": "Invalid recipes.json format: Expected a list."}

    # Find the recipe to edit
    recipe_id = data.get("id")
    for recipe in recipes:
        if recipe.get("id") == recipe_id:
            # Validate input fields
            if not data.get("name") or not data.get("ingredients") or not data.get("instructions") or not data.get("cooking_time"):
                print("Invalid data. Name, ingredients, instructions, and cooking time are required.")
                return {"Error": "Invalid data. Name, ingredients, instructions, and cooking time are required."}

            # Update the recipe details
            recipe.update({
                "name": data.get("name"),
                "ingredients": data.get("ingredients"),
                "instructions": data.get("instructions"),
                "cooking_time": data.get("cooking_time")
            })

            print("Updated recipes:", json.dumps(recipes, indent=2))
            save_recipes(recipes)
            print(f"Recipe '{recipe_id}' updated successfully.")
            return {"Message": f"Recipe '{recipe_id}' updated successfully."}

    print(f"Recipe ID '{recipe_id}' not found.")
    return {"Error": "Recipe not found."}

def main():
    """Run the Recipe Management Microservice."""
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:6002")  # Port for Microservice C

    print("Microservice C (Recipe Management) is running...")

    while True:
        try:
            request = socket.recv_json()  # Receive request
            print("Received request:", json.dumps(request, indent=2))
            
            action = request.get("action")
            if action == "create":
                response = create_recipe(request)
            elif action == "edit":
                response = edit_recipe(request)
            else:
                response = {"Error": "Invalid action specified."}
            
            socket.send_json(response)
            print("Response sent:", json.dumps(response, indent=2))
        except Exception as e:
            print(f"Error processing request: {e}")
            socket.send_json({"Error": f"An error occurred: {e}"})

if __name__ == "__main__":
    main()