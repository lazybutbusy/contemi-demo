import os
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

def get_content(source_url):
    urls = set()

    def scan(full_name, parent):
        # Skip processing elements in the side area
        if parent.get('id') == "qodef-side-area":
            return None

        # Ignore style, script, head, meta, or document elements
        if parent.name in ['style', 'script', 'head', 'meta', '[document]']:
            return None

        # Skip elements with no text or only whitespace
        if parent.text is None or parent.text.strip() == '':
            return None

        # Check for child elements
        children = parent.find_all(recursive=False)
        if len(children) == 0:
            link = None
            if parent.name == 'a' and 'href' in parent.attrs:
                link = parent['href']
            if parent.parent.name == 'a' and 'href' in parent.parent.attrs:
                link = parent.parent['href']
            if link is not None:
                urls.add(link)
                return {'key': parent.name, 'value': parent.text.strip(), 'link': link}
            return {'key': parent.name, 'value': parent.text.strip()}

        # Process child elements recursively
        lst = []
        for child in children:
            value_child = scan(parent.name + "." + child.name, child)
            if value_child is not None:
                lst.append(value_child)
        if len(lst) > 0:
            return {'key': parent.name, 'value': lst}

    def parse(data, pad=0):
        key     = data['key']
        value   = data['value']
        link    = data['link'] if 'link' in data else None
        if not isinstance(value, list):
            return " "*pad + f"{key} : {value} {'('+link+')' if link is not None else ''}"
        else:
            if len(value) == 1:
                return parse(value[0], pad)
            else:
                lreturn = []
                lreturn.append(" "*pad + key + ":")
                for elem in value:
                    lreturn.append(parse(elem, pad+1))
                
                return "\n".join(lreturn)

    try:
        response = requests.get(source_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body

        if not body:
            return None, set()
        
        data = scan(body.name, body)
        text = f"URL: {source_url}\n" + parse(data)
        return text, urls
    except requests.RequestException as e:
        print(f"Error while fetching content from {source_url}: {e}")
        return None, set()


def save_content_to_file(url, content):
    os.makedirs("website_content", exist_ok=True)  # Create directory if it doesn't exist

    parsed_url = urlparse(url)
    file_name = parsed_url.path.strip('/').replace('/', '_') or "index"
    file_path = os.path.join("website_content", f"{file_name}.txt")

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
        print(f"Saved content from {url} to {file_path}")


def crawl_website(start_url):
    visited = set()  # To track visited URLs
    to_visit = [start_url]  # List of URLs to visit

    while to_visit:
        url = to_visit.pop(0)
        if url in visited:
            continue  # Skip if URL has already been visited

        print(f"Processing URL: {url}")
        content, new_urls = get_content(url)

        if content:
            save_content_to_file(url, content)
            visited.add(url)
            # Add only URLs within the same domain
            base_domain = urlparse(start_url).netloc
            for new_url in new_urls:
                full_url = urljoin(url, new_url)
                if urlparse(full_url).netloc == base_domain and full_url not in visited:
                    to_visit.append(full_url)

        print(f"Finished processing URL: {url}")

    print("Crawl completed!")


# Base URL of the website to crawl
website = "https://nova.contemi.com/"

# Start website crawling
crawl_website(website)