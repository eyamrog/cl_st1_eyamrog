# Revising the paragraphs with ChatGPT
# Usage: (my_env) eyamrog@Rog-ASUS:~/work/cl_st1_eyamrog$ nohup python cl_st1_ph4_eyamrog.py cl_st1_ph4_eyamrog cl_st1_ph4_eyamrog &

import argparse
from dotenv import load_dotenv
import openai
import pandas as pd
import os
import logging
from tqdm import tqdm
import time

def main(input_directory, output_directory):
    # Configuring logging
    logging.basicConfig(
        filename=f"{output_directory}/chatgpt_review_log.txt",
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Importing the data into a DataFrame
    df_scielo_preprint_preChatGPT_en = pd.read_json(f'{input_directory}/scielo_erpp_pp.jsonl', lines=True)
    df_scielo_preprint_preChatGPT_en['Submitted'] = pd.to_datetime(df_scielo_preprint_preChatGPT_en['Submitted'], unit='ms')
    df_scielo_preprint_preChatGPT_en['Posted'] = pd.to_datetime(df_scielo_preprint_preChatGPT_en['Posted'], unit='ms')

    # Loading all environment variables from `.env` into `os.environ`
    load_dotenv()

    # Importing the required programme variables from the environment
    openai.api_key = os.environ.get('OPENAI_API_KEY', '')
    assert openai.api_key

    # Defining a function to query ChatGPT with exponential backoff
    def get_completion(prompt, model='gpt-3.5-turbo', max_retries=5):
        client = openai.OpenAI()
        messages = [{'role': 'user', 'content': prompt}]
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0
                )
                return response.choices[0].message.content
            except openai.error.RateLimitError as e:
                wait_time = 2 ** attempt  # Exponential backoff
                logging.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            except Exception as e:
                logging.error(f"Error querying ChatGPT: {e}")
                return None
        logging.error("Max retries exceeded.")
        return None

    # Defining the ChatGPT prompt template
    prompt_template = 'Dear ChatGPT, would it be possible for you to improve the writing of the following passage of a research article considering the generally accepted standards of English for Academic Purposes? Please keep each improved passage within a single paragraph - do not split it into multiple paragraphs. OK?\n'

    # Defining a function to improve text using ChatGPT
    def improve_text(text):
        paragraphs = text.split('\n')  # Split text into paragraphs
        improved_paragraphs = []
        for paragraph in paragraphs:
            prompt = prompt_template + paragraph
            try:
                improved_paragraph = get_completion(prompt)
                if improved_paragraph:
                    improved_paragraphs.append(improved_paragraph)
                else:
                    improved_paragraphs.append(paragraph)  # Keep original if there's an error
            except Exception as e:
                print(f"Error improving paragraph: {e}")
                improved_paragraphs.append(paragraph)  # Keep original if there's an error
        return '\n'.join(improved_paragraphs)

    # Applying the function to the 'Text' column with progress indication
    improved_texts = []
    for text in tqdm(df_scielo_preprint_preChatGPT_en['Text Paragraphs'], desc='Processing texts'):
        improved_texts.append(improve_text(text))

    df_scielo_preprint_preChatGPT_en['Text ChatGPT'] = improved_texts

    # Exporting each article processed by ChatGPT to individual files for inspection
    for index, row in df_scielo_preprint_preChatGPT_en.iterrows():
        file_name = f"{output_directory}/{row['Text ID']}_chatgpt.txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(row['Text ChatGPT'])

    # Exporting to a file
    df_scielo_preprint_preChatGPT_en.to_json(f"{output_directory}/scielo_chatgpt_erpp_pp.jsonl", orient='records', lines=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process and improve text using ChatGPT.')
    parser.add_argument('input_directory', type=str, help='Directory containing input files')
    parser.add_argument('output_directory', type=str, help='Directory to save output files')
    args = parser.parse_args()
    main(args.input_directory, args.output_directory)