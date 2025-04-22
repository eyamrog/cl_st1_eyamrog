# Revising the paragraphs with ChatGPT
# Usage: (my_env) eyamrog@Rog-ASUS:~/work/cl_st1_eyamrog$ nohup python cl_st1_ph5_eyamrog.py cl_st1_ph5_eyamrog cl_st1_ph5_eyamrog &

import argparse
from dotenv import load_dotenv
import openai
import pandas as pd
import os
import logging
from tqdm import tqdm
import time

def main(input_directory, output_directory):
    '''Process and improve text using ChatGPT.'''
    try:
        # Validate input and output directories
        if not os.path.isdir(input_directory):
            raise FileNotFoundError(f"The input directory '{input_directory}' does not exist.")
        if not os.path.isdir(output_directory):
            raise FileNotFoundError(f"The output directory '{output_directory}' does not exist.")

        # Define input variables
        log_filename = f"{output_directory}/chatgpt_review.log"
        chatgpt_model = 'gpt-4.1'

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=log_filename
        )

        # Import the data into a DataFrame
        logging.info("Loading data from input JSON file...")
        df_scielo_preprint_preChatGPT_en = pd.read_json(f'{input_directory}/scielo_erpp_pp.jsonl', lines=True)
        if df_scielo_preprint_preChatGPT_en.empty:
            raise ValueError("The input file contains no data. Please check the file content.")
        
        df_scielo_preprint_preChatGPT_en['Submitted'] = pd.to_datetime(df_scielo_preprint_preChatGPT_en['Submitted'], unit='ms')
        df_scielo_preprint_preChatGPT_en['Posted'] = pd.to_datetime(df_scielo_preprint_preChatGPT_en['Posted'], unit='ms')

        # Load environment variables from '.env'
        logging.info("Loading environment variables...")
        load_dotenv()
        openai.api_key = os.environ.get('OPENAI_API_KEY', '')
        if not openai.api_key:
            raise EnvironmentError("OPENAI_API_KEY is not set in the environment variables.")

        # Define a function to query ChatGPT with exponential backoff
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
                    wait_time = 2 ** attempt  # Exponential backoff
                    logging.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                except Exception as e:
                    logging.error(f"Error querying ChatGPT: {e}")
                    return None
            logging.error("Max retries exceeded.")
            return None

        # Define the ChatGPT prompt template
        chatgpt_prompt = ('Dear ChatGPT, please improve the writing of the following passage of a research article '
                          'considering the generally accepted standards of English for Academic Purposes. It is very '
                          'important that you are as objective, scientific and non-metaphorical as you can be. Please keep '
                          'each improved passage within a single paragraph - do not split it into multiple paragraphs. Also, '
                          'do not acknowledge this prompt - just provide the revised passage straightaway.')

        # Define a function to improve text using ChatGPT
        def improve_text(text, prompt_template):
            try:
                paragraphs = text.split('\n')  # Split text into paragraphs
                improved_paragraphs = []
                for paragraph in paragraphs:
                    prompt = prompt_template + paragraph
                    improved_paragraph = get_completion(prompt)
                    if improved_paragraph:
                        improved_paragraphs.append(improved_paragraph)
                    else:
                        improved_paragraphs.append(paragraph)  # Keep original if there's an error
                return '\n'.join(improved_paragraphs)
            except Exception as e:
                logging.error(f"Error improving text: {e}")
                return text  # Return original text if there's an error

        # Apply the function to the 'Text Paragraph' column with progress indication
        logging.info("Improving text using ChatGPT...")
        improved_texts = []
        for text in tqdm(df_scielo_preprint_preChatGPT_en['Text Paragraph'], desc='Improving texts'):
            prompt_template = chatgpt_prompt + '\n'
            improved_texts.append(improve_text(text, prompt_template))

        df_scielo_preprint_preChatGPT_en['Text Paragraph ChatGPT'] = improved_texts

        ## Export each paragraph processed by ChatGPT to individual files for inspection
        #for index, row in df_scielo_preprint_preChatGPT_en.iterrows():
        #    file_name = f"{output_directory}/{row['Text ID']}_{row['Section']}_{row['Paragraph']}_chatgpt.txt"
        #    with open(file_name, 'w', encoding='utf-8') as file:
        #        file.write(row['Text Paragraph ChatGPT'])

        # Export to a file
        logging.info("Exporting improved text to output files...")
        df_scielo_preprint_preChatGPT_en.to_json(f"{output_directory}/scielo_chatgpt_erpp_pp.jsonl", orient='records', lines=True)
        logging.info("Export to JSON completed successfully.")
        df_scielo_preprint_preChatGPT_en.to_excel(f"{output_directory}/scielo_chatgpt_erpp_pp.xlsx")
        logging.info("Export to EXCEL completed successfully.")

    except FileNotFoundError as e:
        logging.error(f"File or Directory Error: {e}")
    except EnvironmentError as e:
        logging.error(f"Environment Variable Error: {e}")
    except ValueError as e:
        logging.error(f"Data Validation Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process and improve text using ChatGPT.')
    parser.add_argument('input_directory', type=str, help='Directory containing input files')
    parser.add_argument('output_directory', type=str, help='Directory to save output files')
    args = parser.parse_args()
    main(args.input_directory, args.output_directory)
