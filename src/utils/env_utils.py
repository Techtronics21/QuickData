import os

def load_env_variables():
    """Load environment variables from .env file."""
    from dotenv import load_dotenv
    load_dotenv()
    

def get_env_variable(var_name: str) -> str:
    """Get environment variable value."""
    return os.getenv(var_name)