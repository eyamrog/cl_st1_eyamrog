# Usage
# python getwebpageselenium.py wwf_index_sample https://www.worldwildlife.org/stories?page=1&threat_id=effects-of-climate-change

import argparse
import validators
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main(file_id, url):
    """Fetch a web page using Selenium, save it as an HTML file, and extract 'h' and 'p' tags' text."""
    
    # Validate URL
    if not validators.url(url):
        print("Invalid URL. Please provide a valid URL.")
        return
    
    # Set up the WebDriver (make sure you have downloaded the Microsoft Edge WebDriver executable)
    # https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

    service = Service(r'C:\Users\eyamr\OneDrive\00-Technology\laelgelc\edgedriver_win64\msedgedriver.exe')
    driver = webdriver.Edge(service=service)

    try:
        # Navigate to the URL
        driver.get(url)
        
        # Wait for page to load (adjust as needed for better stability)
        wait = WebDriverWait(driver, 10)
        #time.sleep(15)  # Waits for 15 seconds
        #wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        # Extra reliability check: Wait until the page source stops changing
        max_wait_time = 30  # Max time in seconds
        start_time = time.time()
        previous_html = ''
        while True:
            current_html = driver.page_source
            if current_html == previous_html or time.time() - start_time > max_wait_time:
                break  # Exit loop if page stops changing or max wait time is exceeded
            previous_html = current_html
            time.sleep(2)  # Short delay before checking again
        
        # Now, the page is fully loaded - extract content!
        
        # Get the full page source
        page_source = driver.page_source

        # Save the HTML content to a file
        html_file_path = f"{file_id}.html"
        with open(html_file_path, 'w', encoding='utf-8') as html_file:
            html_file.write(page_source)
        print(f"Successfully saved HTML to {html_file_path}")

        # Extract text from 'h' and 'p' tags
        soup = BeautifulSoup(page_source, 'lxml')
        text_content = [tag.get_text(strip=True) for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])]

        # Save the extracted text to a file
        text_file_path = f"{file_id}.txt"
        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            text_file.write("\n".join(text_content))
        print(f"Successfully saved extracted text to {text_file_path}")

    finally:
        # Close the WebDriver
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get a web page with Selenium, save its HTML, and extract 'h' and 'p' tags' text.")
    parser.add_argument('file_id', type=str, help="Web page's filename (without extension)")
    parser.add_argument('url', type=str, help="Web page's URL")
    args = parser.parse_args()
    main(args.file_id, args.url)
