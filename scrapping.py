import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/",
    "DNT": "1",  # Do Not Track Request Header
    "Connection": "keep-alive"
}

def scrape_content(url):
    # Send a request to the URL
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Check for request errors

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove headers and footers if they are identifiable
    for tag in soup(['header', 'footer', 'nav', 'aside']):
        tag.decompose()  # Remove these tags and their content

    # Identify the main content based on common HTML tags
    content = soup.find('main') or soup.find('article') or soup.body
    text_content = content.get_text(separator='\n', strip=True) if content else "No main content found."

    # Extract and clean the title
    title = soup.title.string.strip() if soup.title else "No title found."

    # Extract and clean meta description
    meta_description = soup.find('meta', attrs={'name': 'description'})
    meta_description_content = meta_description['content'].strip() if meta_description and meta_description.get('content') else "No meta description found."

    # Extract and clean meta tags (keywords)
    meta_keywords = soup.find('meta', attrs={'name': re.compile(r'(?i)keywords')}) or \
                soup.find('meta', attrs={'property': re.compile(r'(?i)keywords')})

    meta_keywords_content = [tag.strip() for tag in meta_keywords['content'].split(',')] if meta_keywords and meta_keywords.get('content') else []

    # Construct JSON output
    result = {
        'Title': title,
        'Description': meta_description_content,
        'Tags': meta_keywords_content,
        'Content': text_content
    }

    return json.dumps(result, indent=4)


# Example usage
url = "https://www.robi.com.bd/en/personal/roaming/what-you-need-to-know/high-data-rate-country-list"  # Replace with the target URL
content = scrape_content(url)
print(content)