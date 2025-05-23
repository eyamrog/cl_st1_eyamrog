# Usage
# python docxscrape.py filename.docx

import os
import re
import logging
import argparse
from docx import Document
from tqdm import tqdm

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def replace_extension(filename, extension):
    # Extracting the base filename without the extension
    base_filename = re.match(r'^([A-Za-z0-9-_,\s]+)\.[A-Za-z]{1,5}$', filename).group(1)
    # Adding the new filename extension
    new_filename = f"{base_filename}.{extension}"
    return new_filename

def scrape_docx(docx_path, output_txt):
    try:
        # Opening the DOCX file
        doc = Document(docx_path)
        # Initialising an empty list to store the text
        text_list = []
        # Iterating through all the paragraphs and extracting text
        for paragraph in tqdm(doc.paragraphs, desc='Extracting text from DOCX'):
            text_list.append(paragraph.text)
        
        text = '\n'.join(text_list)

        # Writing the extracted text to a text file in UTF-8 encoding
        with open(output_txt, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)
        logging.info(f"Successfully saved extracted text to: {output_txt}")
    except Exception as e:
        logging.error(f"Error processing file {docx_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Extract text from a DOCX file and save it to a text file.')
    parser.add_argument('input_filename', type=str, help='The path to the input DOCX file.')
    #parser.add_argument('output_extension', type=str, help='The extension for the output text file (e.g., 'txt').')
    args = parser.parse_args()

    input_filename = args.input_filename
    #output_extension = args.output_extension
    output_extension = 'txt'

    output_filename = replace_extension(input_filename, output_extension)
    scrape_docx(input_filename, output_filename)

if __name__ == "__main__":
    main()
