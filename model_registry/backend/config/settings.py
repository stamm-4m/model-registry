import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

def check_env_var(var_name):
    value = os.getenv(var_name)
    if value is None or value.strip() == "":
        raise ValueError(f"The environment variable '{var_name}' is not defined or is empty.")
    return value

API_BASE_URL = check_env_var("API_BASE_URL")
# --   - IBISBA HUB config ---  
MODEL2SEEK_API_TOKEN = check_env_var("MODEL2SEEK_API_TOKEN")
MODEL2SEEK_BASE_URL = check_env_var("MODEL2SEEK_BASE_URL")
