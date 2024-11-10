# Validating the section and paragraph mapping
# (my_env) eyamrog@Rog-ASUS:~/work/cl_st1_eyamrog/cl_st1_ph5_eyamrog$ clear && python section_paragraph_mapping_validate.py
# "Abstract, Introduction, Literature Review, Methodology, Results, Discussion, Conclusion, Acknowledgements"

import pandas as pd
import json

def main(input_directory, output_directory):
    # Importing the data into a DataFrame
    df_scielo_preprint_preChatGPT_en = pd.read_json(f'{input_directory}/scielo_erpp_pp.jsonl', lines=True)
    df_scielo_preprint_preChatGPT_en['Submitted'] = pd.to_datetime(df_scielo_preprint_preChatGPT_en['Submitted'], unit='ms')
    df_scielo_preprint_preChatGPT_en['Posted'] = pd.to_datetime(df_scielo_preprint_preChatGPT_en['Posted'], unit='ms')

    # Reading the JSON file containing the dictionary 'section_paragraph_mapping'
    with open(f"{output_directory}/section_paragraph_mapping.json", 'r') as json_file:
        section_paragraph_mapping = json.load(json_file)

    # Iterating through the existing DataFrame with progress tracking
    for index, row in df_scielo_preprint_preChatGPT_en.iterrows():
        text_id = row['Text ID']
        paragraphs = row['Text Paragraphs'].split('\n')

        if text_id in section_paragraph_mapping:
            sections = section_paragraph_mapping[text_id]
            dict_paragraph_count = sum(len(paragraphs) for paragraphs in sections.values())

            if dict_paragraph_count > len(paragraphs):
                print(f"Text ID: {text_id} - Dictionary has more paragraphs ({dict_paragraph_count}) than text ({len(paragraphs)})")
            elif dict_paragraph_count < len(paragraphs):
                print(f"Text ID: {text_id} - Text has more paragraphs ({len(paragraphs)}) than dictionary ({dict_paragraph_count}). The remaining paragraphs in the text will be left unprocessed.")
            else:
                print(f"Text ID: {text_id} - Dictionary and text have the same number of paragraphs ({len(paragraphs)})")

        else:
            print(f"{text_id} not found in section_paragraph_mapping")

if __name__ == "__main__":
    input_directory = '../cl_st1_ph4_eyamrog'
    output_directory = '.'
    main(input_directory, output_directory)
