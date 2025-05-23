# Usage
# python chatgptgeneric.py writing.prompt methodology_notes1.txt
#
# Output: cleaned up notes file; AI response file; log file

# Import the required libraries
import argparse
from dotenv import load_dotenv
import openai
import os
import logging
import time

def main(prompt_file, txt_file):
    '''Generate an academic paragraph from notes using ChatGPT.'''
    try:
        # Check if both files exist
        if not os.path.isfile(prompt_file):
            raise FileNotFoundError(f"The prompt file '{prompt_file}' does not exist.")
        if not os.path.isfile(txt_file):
            raise FileNotFoundError(f"The text file '{txt_file}' does not exist.")

        # Define input variables
        filename = txt_file.lower().replace(' ', '_').split('.')[0]
        output_filename1 = f"{filename}_cleaned_up.txt"
        output_filename2 = f"{filename}_ai_composed.txt"
        chatgpt_model = 'gpt-4.1'

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=f"{filename}.log"
        )

        # Read prompt from the first file
        logging.info(f'Reading prompt from {prompt_file}')
        with open(prompt_file, 'r', encoding='utf-8') as file:
            chatgpt_prompt = file.read().strip()

        if not chatgpt_prompt:
            raise ValueError(f"The prompt file '{prompt_file}' is empty or contains only whitespace.")

        # Clean up notes before sending them to ChatGPT
        def preprocess_notes(notes):
            cleaned_lines = [' '.join(line.split()) for line in notes.splitlines() if line.strip()]
            return '\n'.join(cleaned_lines)

        # Read notes from the second file
        logging.info(f'Reading notes from {txt_file}')
        with open(txt_file, 'r', encoding='utf-8') as file:
            notes = preprocess_notes(file.read())

        if not notes:
            raise ValueError(f"The text file '{txt_file}' is empty or contains only whitespace.")

        # Save cleaned-up notes to file
        with open(output_filename1, 'w', encoding='utf-8') as file:
            file.write(notes)

        logging.info(f"Cleaned-up notes saved to '{output_filename1}'")

        # Load OpenAI API key
        load_dotenv()
        openai.api_key = os.environ.get('OPENAI_API_KEY', '')
        if not openai.api_key:
            raise EnvironmentError('OPENAI_API_KEY is not set in the environment variables.')

        # Function to get completion from ChatGPT
        def get_completion(prompt, model=chatgpt_model, max_retries=5):
            for attempt in range(max_retries):
                try:
                    client = openai.OpenAI()
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{'role': 'user', 'content': prompt}],
                        temperature=0
                    )
                    return response.choices[0].message.content.strip()
                except openai.error.RateLimitError:
                    wait_time = 2 ** attempt
                    logging.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                except Exception as e:
                    logging.error(f"Error querying ChatGPT: {e}")
                    return None
            logging.error('Max retries exceeded.')
            return None

        # Get AI-generated paragraph
        logging.info('Generating academic text using ChatGPT...')
        ai_prompt = chatgpt_prompt + '\n\n' + notes
        ai_paragraph = get_completion(ai_prompt)
        if not ai_paragraph:
            raise RuntimeError('Failed to generate text from ChatGPT.')

        # Save output to file
        with open(output_filename2, 'w', encoding='utf-8') as file:
            file.write(ai_paragraph)

        logging.info(f"AI-generated text saved to '{output_filename2}'")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except EnvironmentError as e:
        print(f"Environment Variable Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate an academic paragraph from notes using ChatGPT.')
    parser.add_argument('prompt_file', type=str, help='Prompt file filename')
    parser.add_argument('txt_file', type=str, help='Text file filename')
    args = parser.parse_args()
    main(args.prompt_file, args.txt_file)
