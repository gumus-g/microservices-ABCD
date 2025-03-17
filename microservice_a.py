import zmq # type: ignore
import json

# Filepath to the JSON file containing recipes
filepath = "./recipes.json"

def get_recipes(filepath):
    """Load recipes from a JSON file."""
    with open(filepath, 'r') as recipe_file:
        return json.load(recipe_file)

def process_request(request, recipes):
    """Process client request and determine response."""
    recipe_id = request.get("recipeID", "")
    search_query = request.get("searchQuery", "").lower()
    browse = request.get("browse", False)
    recipe_details_id = request.get("recipeDetailsID", "")

    if recipe_id:
        return get_recipe_by_id(recipe_id, recipes)
    elif search_query:
        return search_recipes(search_query, recipes)
    elif browse:
        return browse_recipes(recipes)
    elif recipe_details_id:
        return view_recipe_details(recipe_details_id, recipes)
    else:
        return {"Error": "No valid recipe ID, search query, browse request, or recipe details ID was provided."}

def get_recipe_by_id(recipe_id, recipes):
    """Retrieve a recipe by its ID."""
    for recipe in recipes:
        if recipe["id"] == recipe_id:
            return recipe
    return {"Error": "Could not find specified recipe."}

def search_recipes(search_query, recipes):
    """Search recipes by name or ingredients."""
    search_results = []
    for recipe in recipes:
        if search_query in recipe["name"].lower() or any(search_query in ingredient.lower() for ingredient in recipe["ingredients"]):
            search_results.append(recipe)
    if search_results:
        return search_results
    else:
        return {"Message": "No matching recipes found."}

def browse_recipes(recipes):
    """Return all recipes."""
    return recipes

def view_recipe_details(recipe_id, recipes):
    """Return detailed information for a specific recipe."""
    for recipe in recipes:
        if recipe["id"] == recipe_id:
            return {
                "name": recipe["name"],
                "ingredients": recipe["ingredients"],
                "instructions": recipe["instructions"]
            }
    return {"Error": "Could not find specified recipe details."}

def main():
    recipes = get_recipes(filepath)
    context = zmq.Context()
    socket = context.socket(zmq.REP)  # Reply socket
    socket.bind("tcp://*:5555")  # Bind the server to a port

    print("Server is running and waiting for requests...")

    while True:
        request = socket.recv_json()  # Receive JSON request from client
        print(f"Received request: {json.dumps(request, indent=2)}")
        response = process_request(request, recipes)
        socket.send_json(response)  # Send JSON response back to client
        print(f"Sent response: {json.dumps(response, indent=2)}")

if __name__ == "__main__":
    main()