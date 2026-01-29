import os
from config import MAX_CHARS

from google.genai import types

def get_file_content(working_directory, file_path):
    abs_workdir = os.path.abspath(working_directory)
    abs_file_path= os.path.abspath(os.path.join(working_directory, file_path))
    if not abs_file_path.startswith(abs_workdir):
        return f'Error: cannot list "{file_path}" as it is outside of the working directory'
    if not os.path.isfile(abs_file_path):
        return f'Error: "{file_path}" is not a valid file or not found'
    try:
        with open(abs_file_path, "r") as f:
            content = f.read(MAX_CHARS)
            if os.path.getsize(abs_file_path) > MAX_CHARS:
                content += (
                    f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
                )

        return content
    
    except Exception as e:
        return f'Error reading file "{file_path}": {e}'

    
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description=f"Reads and returns the first {MAX_CHARS} characters of the content from a specified file within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file whose content should be read, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)