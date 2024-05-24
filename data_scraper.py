

import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
import easyocr

# Create a directory to save the scraped images
if not os.path.exists('scraped_images'):
    os.makedirs('scraped_images')

def save_image(image_url, image_name, folder='scraped_images'):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            image_path = os.path.join(folder, image_name)
            with open(image_path, 'wb') as file:
                file.write(response.content)
            print(f'Saved image: {image_name}')
        else:
            print(f'Failed to retrieve image: {image_url}')
    except Exception as e:
        print(f'Error saving image {image_name}: {e}')

def extract_text_from_image(image_url, use_gpu=True):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            # Use GPU if available
            reader = easyocr.Reader(['en'], gpu=use_gpu)
            result = reader.readtext(img, detail=0)
            text = " ".join(result)
            return text
        else:
            print(f'Failed to retrieve image for OCR: {image_url}')
            return ""
    except Exception as e:
        print(f'Error extracting text from image {image_url}: {e}')
        return ""

def scrape_images(url, patterns):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f'Scraping images from: {url}')
            soup = BeautifulSoup(response.content, 'html.parser')
            images = soup.find_all('img')
            print(f'Found {len(images)} images')
            
            count = 1
            for img in images:
                img_url = img.get('src')
                if img_url:
                    img_url = urljoin(url, img_url)
                    print(f'Processing image URL: {img_url}')
                    text = extract_text_from_image(img_url, use_gpu=True)
                    for pattern in patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            print(f'Found relevant image: {img_url}')
                            img_extension = img_url.split(".")[-1].split("?")[0]
                            img_name = f'web2_{count}.{img_extension}'
                            save_image(img_url, img_name)
                            count += 1
                            break
                        else:
                            print(f'No match for pattern: {pattern} in text: {text[:30]}...')
        else:
            print(f'Failed to retrieve webpage: {url}')
    except Exception as e:
        print(f'Error scraping {url}: {e}')

# Example usage
# target_url = 'https://www.plateshack.com/y2k/Mauritania/mauritaniay2k.htm'
target_url = 'https://www.voursa.com/Index.cfm?PN=4&gct=1&sct=11&gv=13'

patterns = [
    r'RIM | R.I.M',  # Pattern to match 'R.I.M' or 'RIM'
    r'\d{4}[a-zA-Z]{2}\d{2}',  # Pattern to match '3120AC00', '7800AA07', etc.
    r'\d{4} [a-zA-Z]{2}\d{2}', # Pattern to match '3120 AC00', '7800 AA07', etc.
    r'\d{4}[a-zA-Z]{2} \d{2}', # Pattern to match '3120AC 00', '7800AA 07', etc.
    r'\d{4} [a-zA-Z]{2} \d{2}', # Pattern to match '3120 AC 00', '7800 AA 07', etc.
    r'(ASNA|CC|CD|IF|IT|ONU|SCC|SG|SP|TT|WT)[ ]?\d{3,6}',  # Pattern to match government plates with specific prefixes
]


scrape_images(target_url, patterns)












