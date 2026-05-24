import subprocess 

def runpestsuit(command):
    try:
        # Run the command
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        # Print the output
        print("Command output:\n", result.stdout)
        # If there are any errors, they will be printed as well
        if result.stderr:
            print("Error:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        # Handle errors in command execution
        print(f"Error encountered while running the command: {e}")
