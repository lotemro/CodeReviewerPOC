import os

def get_file_extension(filename: str) -> str:
    """
    Extracts the file extension from a given filename string.
    """
    _, extension = os.path.splitext(filename)
    return extension

def check_is_python_file(filename: str) -> bool:
    """Checks if a file has a .py extension."""
    return get_file_extension(filename).lower() == ".py"
