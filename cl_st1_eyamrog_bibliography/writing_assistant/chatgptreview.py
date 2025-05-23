# Usage
# python chatgptreview.py t000194_tokenised.txt
#
# Manually edit the text file according to the following format:
# Text ID: t000000
# 
# Title: The Pedagogy of Multiliteracies Applied to English Teaching
# 
# Section: Introduction
# The teaching of foreign languages ...
# The concept of multiliteracies, ...
# <other paragraphs>
# 
# Section: Body
# The Pedagogy of Multiliteracies is ...
# The Pedagogy of Multiliteracies ...
# <other paragraphs>
# 
# Section: Conclusion
# The Pedagogy of Multiliteracies emerges ...
# The creation of fanfictions within ...
# <other paragraphs>

# Import the required libraries
import argparse
from dotenv import load_dotenv
import openai
import pandas as pd
import os
import logging
from tqdm import tqdm
import time

def main(txt_file):
    '''Get a text file and review its paragraphs with ChatGPT.'''
    try:
        # Check if the file exists
        if not os.path.isfile(txt_file):
            raise FileNotFoundError(f"The file '{txt_file}' does not exist.")

        # Define input variables
        filename = txt_file.lower()  # Convert to lowercase
        filename = filename.replace(' ', '_')  # Replace spaces with underscores
        filename = os.path.splitext(filename)[0]  # Strip the extension
        log_filename = f"{filename}.log"
        df_filename1 = f"{filename}_df1"
        df_filename2 = f"{filename}_df2"
        chatgpt_model = 'gpt-4.1'

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=log_filename
        )

        # Import the text into a DataFrame
        text_id = None
        title = None
        section = None
        paragraph_count = 0
        data = []

        logging.info('Starting to read the file')
        with open(txt_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = ' '.join(line.split())  # Removing duplicated spaces
                line = line.strip()

                # Capture 'Text ID'
                if line.startswith('Text ID:'):
                    text_id = line.split(': ')[1]
                    logging.info(f"Captured Text ID: {text_id}")

                # Capture 'Title'
                elif line.startswith('Title:'):
                    title = line.split(': ')[1]
                    logging.info(f"Captured Title: {title}")

                # Capture 'Section'
                elif line.startswith('Section:'):
                    section = line.split(': ')[1]
                    paragraph_count = 0  # Resetting paragraph count for new section
                    logging.info(f"Starting new section: {section}")

                # Capture 'Paragraph Text'
                elif line:
                    paragraph_count += 1
                    data.append({
                        'Text ID': text_id,
                        'Title': title,
                        'Section': section,
                        'Paragraph': f"Paragraph {paragraph_count}",
                        'Text Paragraph': line
                    })
                    logging.info(f"Captured Paragraph {paragraph_count} in Section: {section}")

        # Create DataFrame
        df_text = pd.DataFrame(data)
        logging.info('DataFrame created successfully')

        # Export to a file
        df_text.to_json(f"{df_filename1}.jsonl", orient='records', lines=True)

        # Revise the paragraphs with ChatGPT
        chatgpt_prompt = ('Dear ChatGPT, please improve the writing of the following passage of a research article '
                          'considering the generally accepted standards of English for Academic Purposes. It is very '
                          'important that you are as objective, scientific and non-metaphorical as you can be. Please keep '
                          'each improved passage within a single paragraph - do not split it into multiple paragraphs. Also, '
                          'do not acknowledge this prompt - just provide the revised passage straightaway.')

        load_dotenv()

        openai.api_key = os.environ.get('OPENAI_API_KEY', '')
        if not openai.api_key:
            raise EnvironmentError('OPENAI_API_KEY is not set in the environment variables.')

        def get_completion(prompt, model=chatgpt_model, max_retries=5):
            for attempt in range(max_retries):
                try:
                    client = openai.OpenAI()
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{'role': 'user', 'content': prompt}],
                        temperature=0
                    )
                    return response.choices[0].message.content
                except openai.error.RateLimitError:
                    wait_time = 2 ** attempt
                    logging.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                except Exception as e:
                    logging.error(f"Error querying ChatGPT: {e}")
                    return None
            logging.error('Max retries exceeded.')
            return None

        def process_text(text, prompt_template):
            try:
                paragraphs = text.split('\n')
                processed_paragraphs = []
                for paragraph in paragraphs:
                    prompt = prompt_template + paragraph
                    processed_paragraph = get_completion(prompt)
                    if processed_paragraph:
                        processed_paragraphs.append(processed_paragraph)
                    else:
                        processed_paragraphs.append(paragraph)
                return '\n'.join(processed_paragraphs)
            except Exception as e:
                logging.error(f"Error improving text: {e}")
                return text  # Return original text if there's an error

        logging.info('Improving text using ChatGPT...')
        processed_texts = []
        for index, row in tqdm(df_text.iterrows(), total=len(df_text), desc='Processing texts'):
            prompt_template = chatgpt_prompt + '\n'
            processed_texts.append(process_text(row['Text Paragraph'], prompt_template))

        df_text['Text Paragraph ChatGPT'] = processed_texts

        # Export to a file
        df_text.to_json(f"{df_filename2}.jsonl", orient='records', lines=True)
        df_text.to_excel(f"{df_filename2}.xlsx", index=False)

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except EnvironmentError as e:
        print(f"Environment Variable Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get a text file and review its paragraphs with ChatGPT.')
    parser.add_argument('txt_file', type=str, help='Text file filename')
    args = parser.parse_args()
    main(args.txt_file)
