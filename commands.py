import argparse
import subprocess
import numpy as np
from embeddings import get_embeddings
from dotenv import load_dotenv
from company import get_company_prompt,save_company_data
from cover_letter import get_cover_letter_prompt,render_cover
from google_sheets import append_job_application
from resume_builder import process_job_post, analyse_job_post
import asyncio

load_dotenv()

def copy_to_clipboard(text):
    """Copy text to clipboard using pbcopy on macOS"""
    process = subprocess.Popen('pbcopy', stdin=subprocess.PIPE)
    process.communicate(text.encode('utf-8'))

def get_embedding_and_copy(text: str):
    """Generate embedding for a given text and copy to clipboard"""
    # Generate embedding using OpenAI
    embedding = get_embeddings(text)
    
    # # Convert to numpy array for consistent formatting
    # embedding_array = np.array(embedding)
    
    # # Convert to string
    # embedding_str = np.array2string(embedding_array, separator=',', precision=8)
    
    # Copy to clipboard
    copy_to_clipboard(f"[{', '.join(map(str, embedding))}]")
    print(f"Embedding has been copied to clipboard. Length: {len(embedding)}")

def company_prompt():
    
    get_company_prompt()
    with open('prompts/company.txt', 'r') as file:
        file_content = file.read()
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(input=file_content.encode('utf-8'))

def cover_letter_prompt():
    get_cover_letter_prompt()
    with open('prompts/cover_letter.md', 'r') as file:
        file_content = file.read()
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(input=file_content.encode('utf-8'))

def main():
    parser = argparse.ArgumentParser(description='Text processing utilities')
    parser.add_argument('--text', type=str, required=False, help='Text to process')
    parser.add_argument('--command', type=str, required=True, 
                      choices=['embedding', 'company', 'save_company_data', 'cover_letter', 'applied', 'print_cover', 'start_resume', 'retry_resume'], 
                      help='Command to execute')

    args = parser.parse_args()
    print(args)

    if args.command == 'embedding':
        get_embedding_and_copy(args.text)
    if args.command == 'company':
        company_prompt()
    if args.command == 'save_company_data':
        save_company_data()
    if args.command == 'cover_letter':
        cover_letter_prompt()
    if args.command == 'applied':
        append_job_application()
    if args.command == 'print_cover':
        render_cover()
    if args.command == 'start_resume':
        asyncio.run(analyse_job_post())
    if args.command == 'retry_resume':
        asyncio.run(process_job_post())

if __name__ == "__main__":
    main() 