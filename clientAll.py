import zmq  # type: ignore
import json

def make_request(socket, request_message):
    """Send request to the server and receive a response."""
    try:
        print("\nSending request to the server...")  # Feedback for the user
        socket.send_json(request_message)
        response = socket.recv_json()
        print("Response received from the server!")  # Feedback for the user
        return response
    except Exception as e:
        print(f"Error: Failed to communicate with the server. Details: {str(e)}")
        return {"Error": "Communication failed with the server."}

def initialize_sockets(context):
    """Initialize and connect to all microservices."""
    try:
        print("Initializing sockets and connecting to microservices...")  # Feedback for the user
        auth_socket = context.socket(zmq.REQ)
        auth_socket.connect("tcp://localhost:6001")  # User Authentication

        recipe_manage_socket = context.socket(zmq.REQ)
        recipe_manage_socket.connect("tcp://localhost:6002")  # Recipe Management

        recipe_interact_socket = context.socket(zmq.REQ)
        recipe_interact_socket.connect("tcp://localhost:6003")  # Recipe Interaction

        general_socket = context.socket(zmq.REQ)
        general_socket.connect("tcp://localhost:5555")  # General Recipe Server

        print("All sockets initialized and connected successfully!")  # Feedback for the user
        return auth_socket, recipe_manage_socket, recipe_interact_socket, general_socket
    except Exception as e:
        print(f"Error: Unable to initialize sockets. Details: {str(e)}")
        raise

def display_help():
    """
    Recipe Catalog App - Help Information

    1. User Authentication:
       - Register: Create a new account by providing a username and password.
       - Login: Access your account using existing credentials.

    2. Recipe Management:
       - Create Recipe: Add a new recipe by entering its ID, name, ingredients, and instructions.
       - Edit Recipe: Update an existing recipe using its ID and updated details.

    3. Recipe Interaction:
       - Rate Recipe: Give a rating (1-5) to a recipe by specifying its ID.
       - Tag Recipe: Add descriptive tags to organize or search for recipes more effectively.

    4. Recipe Search and Retrieval:
       - Get Recipe by ID: Retrieve a specific recipe by providing its unique ID.
       - Search Recipes: Use keywords to look for recipes (e.g., 'pasta' or 'chicken').
       - Browse All Recipes: See a list of all recipes available in the catalog.
       - View Recipe Details: Access full details, including ingredients and instructions, for a recipe.

    5. Exit:
       - Select this option to close the application securely. You will be prompted for confirmation.

    If you experience any issues, ensure all required fields are filled out correctly and try again.
    """
    print("\nDisplaying help information...")
    print(display_help.__doc__)

def validate_non_empty(*args):
    """Helper function to validate non-empty input fields."""
    for value in args:
        if not value or (isinstance(value, list) and not any(value)):
            return False
    return True

def main():
    # Initialize ZeroMQ context and sockets
    context = zmq.Context()
    try:
        auth_socket, recipe_manage_socket, recipe_interact_socket, general_socket = initialize_sockets(context)
    except Exception:
        return

    while True:
        # Main menu
        print("\n" + "-" * 100)
        print("🌟 Welcome to the Recipe Catalog App! 🌟")
        print("\nAbout the Recipe Catalog App:")
        print("Discover a world of culinary inspiration! Explore recipes, manage your own creations,")
        print("and interact with a diverse collection of dishes. Whether you're an aspiring chef")
        print("or just looking for your next favorite meal, we've got something for everyone.\n")
        print("🔔 Please Note:")
        print("1. An active internet connection is required to browse, search, or view recipes.")
        print("2. Remember to save your work to avoid losing any important data.\n")
        print("Navigate through the app using the options below:")

        print("\nMain Menu:")
        print("1. 🛠 User Authentication (Register/Login)")
        print("2. 🍳 Recipe Management (Create/Edit Recipes)")
        print("3. ⭐ Recipe Interaction (Rate/Tag Recipes)")
        print("4. 🔍 Recipe Search and Retrieval")
        print("5. 📖 Help (How to Use the App)")
        print("6. 🚪 Exit\n")

        # Prompt user for their choice
        choice = input("👉 Enter your choice (1-6): ").strip()

        # Validation for invalid input
        if choice not in ["1", "2", "3", "4", "5", "6"]:
            print("❌ Invalid choice. Please select a valid option from the menu.")            

        if choice == "1":
            print("\nUSER AUTHENTICATION")
            print("1. Register")
            print("2. Login")
            auth_action = input("Enter your choice (1-2): ").strip()
            if auth_action in ["1", "2"]:
                username = input("Enter username: ").strip()
                password = input("Enter password: ").strip()
                if not validate_non_empty(username, password):
                    print("Error: Username and password cannot be empty. Please try again.")
                    continue
                action = "register" if auth_action == "1" else "login"
                response = make_request(auth_socket, {"action": action, "username": username, "password": password})
                print(f"Response:\n{json.dumps(response, indent=2)}")
            else:
                print("Invalid choice. Returning to the main menu.")

        elif choice == "2":
            print("\nRECIPE MANAGEMENT")
            print("1. Create Recipe")
            print("2. Edit Recipe")
            manage_action = input("Enter your choice (1-2): ").strip()
            if manage_action in ["1", "2"]:
                recipe_id = input("Enter Recipe ID: ").strip()
                name = input("Enter Recipe Name: ").strip()
                ingredients = input("Enter Ingredients (comma-separated): ").strip().split(',')
                instructions = input("Enter Instructions: ").strip()
                cooking_time = input("Enter Cooking Time (e.g., '30 minutes'): ").strip()
                if not validate_non_empty(recipe_id, name, ingredients, instructions, cooking_time):
                    print("Error: All fields are required. Please try again.")
                    continue
                action = "create" if manage_action == "1" else "edit"
                response = make_request(recipe_manage_socket, {
                    "action": action,
                    "id": recipe_id,
                    "name": name,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "cooking_time": cooking_time
                })
                print(f"Response:\n{json.dumps(response, indent=2)}")
            else:
                print("Invalid choice. Returning to the main menu.")

        elif choice == "3":
            print("\nRECIPE INTERACTION")
            print("1. Rate a Recipe")
            print("2. Tag a Recipe")
            interact_action = input("Enter your choice (1-2): ").strip()
            if interact_action == "1":
                recipe_id = input("Enter Recipe ID: ").strip()
                try:
                    rating = int(input("Enter Rating (1-5): ").strip())
                    if rating < 1 or rating > 5:
                        raise ValueError("Rating must be between 1 and 5.")
                except ValueError as e:
                    print(f"Error: {str(e)} Please try again.")
                    continue
                response = make_request(recipe_interact_socket, {"action": "rate", "id": recipe_id, "rating": rating})
            elif interact_action == "2":
                recipe_id = input("Enter Recipe ID: ").strip()
                tag = input("Enter Tag: ").strip()
                if not validate_non_empty(recipe_id, tag):
                    print("Error: Recipe ID and tag cannot be empty. Please try again.")
                    continue
                response = make_request(recipe_interact_socket, {"action": "tag", "id": recipe_id, "tag": tag})
            else:
                print("Invalid choice. Returning to the main menu.")
            print(f"Response:\n{json.dumps(response, indent=2)}")

        elif choice == "4":
            print("\nRECIPE SEARCH AND RETRIEVAL")
            print("1. Get a recipe by ID")
            print("2. Search for recipes by name or ingredient")
            print("3. Browse all recipes")
            print("4. View recipe details by ID")
            general_action = input("Enter your choice (1-4): ").strip()
            if general_action == "1":
                recipe_id = input("Enter Recipe ID to fetch: ").strip()
                response = make_request(general_socket, {"recipeID": recipe_id})
            elif general_action == "2":
                search_query = input("Enter a search term: ").strip().lower()
                response = make_request(general_socket, {"searchQuery": search_query})
            elif general_action == "3":
                response = make_request(general_socket, {"browse": True})
            elif general_action == "4":
                recipe_id = input("Enter Recipe ID to view details: ").strip()
                response = make_request(general_socket, {"recipeDetailsID": recipe_id})
            else:
                print("Invalid choice. Returning to the main menu.")
            print(f"Response:\n{json.dumps(response, indent=2)}")

        elif choice == "5":
            display_help()

        elif choice == "6":
            confirm_exit = input("Are you sure you want to exit? (yes/no): ").strip().lower()
            if confirm_exit in ["yes", "y"]:
                print("Exiting the client. Goodbye!")
                break
            elif confirm_exit in ["no", "n"]:
                print("Returning to the main menu.")
                continue
            else:
                print("Invalid input. Returning to the main menu.")

        else:
            print("Invalid choice. Please select a valid option.")

    # Close sockets and terminate context
    for sock in [auth_socket, recipe_manage_socket, recipe_interact_socket, general_socket]:
        sock.close()
    context.term()

if __name__ == "__main__":
    main()