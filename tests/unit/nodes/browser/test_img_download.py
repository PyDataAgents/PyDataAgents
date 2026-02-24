import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def test_000():
    # Website URL
    url = "https://example.com"

    # Folder to save images
    folder = os.path.dirname(__file__) + os.sep + "images"
    os.makedirs(folder, exist_ok=True)

    # Fetch HTML
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all <img> tags
    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("src")

        # Skip invalid or empty src
        if not img_url:
            continue

        # Resolve relative URLs
        img_url = urljoin(url, img_url)

        # Get filename
        filename = os.path.basename(urlparse(img_url).path)

        if not filename:
            filename = "image_" + str(abs(hash(img_url))) + ".jpg"

        filename = os.path.dirname(__file__) + os.sep + "images" + os.sep + filename

        # Download image
        print(f"Downloading {img_url} -> {filename}")
        try:
            img_data = requests.get(img_url).content
            with open(filename, "wb") as f:
                f.write(img_data)
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")