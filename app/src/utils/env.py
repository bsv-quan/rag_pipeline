import os
import dotenv
dotenv.load_dotenv()

def getEnvVariable(variable_name: str, default_value: str = None) -> str:
    """
    Get the value of an environment variable.
    If the variable is not set, return the default value.
    """
    return os.getenv(variable_name, default_value)

def setEnvronVariable(variable_name: str, value: str):
    """
    Set the value of an environment variable.
    """
    os.environ[variable_name] = value