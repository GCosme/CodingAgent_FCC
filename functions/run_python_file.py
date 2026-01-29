import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path, args=[]):
    abs_workdir = os.path.abspath(working_directory)
    abs_file_path= os.path.abspath(os.path.join(working_directory, file_path))
    if not abs_file_path.startswith(abs_workdir):
        return f'Error: cannot list "{file_path}" as it is outside of the working directory'
    if not os.path.exists(abs_file_path):
        return f'Error: "{file_path}" is not a valid file or not found'
    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        commands = ["python", abs_file_path]
        if args:
            commands.extend(args)
        result = subprocess.run(
            commands,
            capture_output = True,
            text = True,
            timeout = 30,
            cwd = abs_workdir
        )
        output = []

        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        if result.returncode != 0:
            output.append(f"Process exited wiht code {result.returncode}")
        return "\n".join(output) if output else "No output produced."
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
    
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run the Python file, constrained the working directory and to Python only.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the the Python file to execute, relative to the working directory.",
            ),
        "args": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.STRING,
                description = "Optional arguments to pass to the Python file.",
            ),
            description = "Optional arguments to pass to the Python file.",
            ),
        },
        required=["file_path"],
    ),
)