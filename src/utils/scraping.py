from bs4 import BeautifulSoup
import requests

def scrape_website(url):
    """Scrapes the content of a given website URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()  # Return the text content of the page
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_reliable_sources(urls):
    """Extracts content from a list of reliable sources."""
    contents = {}
    for url in urls:
        content = scrape_website(url)
        if content:
            contents[url] = content
    return contents