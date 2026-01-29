import os
import sys

from dotenv import load_dotenv

from google import genai
from google.genai import types

from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file_content import schema_write_file
from functions.call_function import call_function, available_functions

from prompts import system_prompt

def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith('--'):
            args.append(arg)
    
    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I fix the calculator?"')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    generate_content_loop(client, messages, verbose)


def generate_content_loop(client, messages, verbose, max_iterations=20):
    config = types.GenerateContentConfig(
        tools = [available_functions], system_instruction = system_prompt
    )

    for iteration in range(max_iterations):
        try:
            response = client.models.generate_content(
                model = 'gemini-2.5-flash',
                contents = messages,
                config = config
            )
            if verbose:
                print("Prompt tokens: ", response.usage_metadata.prompt_token_count)
                print("Response tokens: ", response.usage_metadata.candidates_token_count)
            
            # add model response to conversation
            for candidate in response.candidates:
                messages.append(candidate.content)

            # check if we have a final text response
            if response.text:
                print("Final response: ")
                print(response.text)
                break

            # handle function calls
            if response.function_calls:
                function_responses = []
                for function_call_part in response.function_calls:
                    function_call_result = call_function(function_call_part, verbose)
                    if(
                        not function_call_result.parts
                        or not function_call_result.parts[0].function_response
                    ):
                        raise Exception("empty function call result")
                    if verbose:
                        print(f"-> {function_call_result.parts[0].function_response.response}")
                    function_responses.append(function_call_result.parts[0])
                
                if function_responses:
                    messages.append(types.Content(role="user", parts=function_responses))
                else:
                    raise Exception("no function responses generated, exiting.")

        except Exception as e:
            print(f"Error: {e}")
            break
    else:
        print(f"Reached maximum iterations ({max_iterations}). Agent may not have completed the task.")

if __name__ == "__main__":
    main()