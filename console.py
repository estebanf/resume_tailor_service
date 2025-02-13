import questionary
import subprocess
import sys
import os

def execute_script(script_name: str, args: list = None) -> None:
    """Execute a shell script with optional arguments."""
    try:
        command = [f"./{script_name}"]
        if args:
            command.extend(args)
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_name}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    # Available commands
    commands = {
        "Generate Embedding": {
            "script": "embedding.sh",
            "needs_input": True,
            "input_prompt": "Enter the text to generate embedding for:"
        },
        "Generate Company Research Prompt": {
            "script": "company.sh",
            "needs_input": False
        },
        "Save Company Data": {
            "script": "save_company_data.sh",
            "needs_input": False
        },
        "Generate Cover Letter Prompt": {
            "script": "cover_letter.sh",
            "needs_input": False
        },
        "Render Cover Letter": {
            "script": "print_cover.sh",
            "needs_input": False
        },
        "Record Job Application": {
            "script": "applied.sh",
            "needs_input": False
        },
        "Start Resume Generation": {
            "script": "start_resume.sh",
            "needs_input": False
        },
        "Retry Resume Generation": {
            "script": "retry_resume.sh",
            "needs_input": False
        },
        "Exit": None
    }

    while True:
        # Ask user to select a command
        choice = questionary.select(
            "What would you like to do?",
            choices=list(commands.keys())
        ).ask()

        if choice == "Exit":
            print("Goodbye!")
            sys.exit(0)

        command = commands[choice]
        if command["needs_input"]:
            # Get additional input if needed
            user_input = questionary.text(command["input_prompt"]).ask()
            execute_script(command["script"], [user_input])
        else:
            execute_script(command["script"])

if __name__ == "__main__":
    main() 