# Usage
# python chatgptwriting.py methodology_notes1.txt
#
# Output: cleaned up notes file; AI-composed paragraph file; log file

# Import the required libraries
import argparse
from dotenv import load_dotenv
import openai
import os
import logging
import time

def main(txt_file):
    '''Generate an academic paragraph from notes using ChatGPT.'''
    try:
        # Check if the file exists
        if not os.path.isfile(txt_file):
            raise FileNotFoundError(f"The file '{txt_file}' does not exist.")

        # Define input varibles
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

        # Clean up notes before sending them to ChatGPT
        def preprocess_notes(notes):
            # Process each line individually: strip leading/trailing spaces and remove duplicated spaces
            cleaned_lines = [' '.join(line.split()) for line in notes.splitlines() if line.strip()]
        
            # Preserve structure by joining lines with newline characters
            return '\n'.join(cleaned_lines)

        # Read notes from the file
        logging.info('Reading notes from file')
        with open(txt_file, 'r', encoding='utf-8') as file:
            notes = preprocess_notes(file.read())

        if not notes:
            raise ValueError('The file is empty or contains only whitespace.')

        # Save cleaned-up notes to file
        with open(output_filename1, 'w', encoding='utf-8') as file:
            file.write(notes)

        logging.info(f"Cleaned up notes saved to '{output_filename1}'")

        # Define ChatGPT prompt
        chatgpt_prompt = ('Dear ChatGPT, please write a piece of academic text based on the following notes considering '
                          'the generally accepted standards of English for Academic Purposes. It is very important that '
                          'you are as objective, scientific and non-metaphorical as you can be. Please keep '
                          'the text within a single paragraph - do not split it into multiple paragraphs. Also, '
                          'do not acknowledge this prompt - just provide the paragraph straightaway.')

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
    parser.add_argument('txt_file', type=str, help='Text file filename')
    args = parser.parse_args()
    main(args.txt_file)
