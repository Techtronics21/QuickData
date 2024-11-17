def format_data(data):
    # Function to format data for presentation
    return [str(item).strip() for item in data]

def handle_error(error):
    # Function to log and handle errors
    print(f"Error: {error}")

def validate_input(data):
    # Function to validate user input
    if not data:
        raise ValueError("Input data cannot be empty.")
    return True