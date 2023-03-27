import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm, trange
import json

# Load the URLs from url.txt
with open('url.txt', 'r', encoding='utf-8') as f:
    urls = f.read().splitlines()

# Define a function to filter the URLs to only include Shopify sites
def filter_urls(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Check for Shopify CDN domain
        if 'cdn.shopify.com' in url or 'checkout.shopify.com' in url:
            return url
        # Check for Shopify checkout pages
        elif '/checkouts/' in url:
            return url
        # Check for Shopify favicon
        elif soup.find('link', {'rel': 'shortcut icon', 'href': '/favicon.ico'}) is not None:
            return url
        # Check for Shopify logo
        elif soup.find('img', {'alt': 'Shopify'}) is not None:
            return url
        # Check for Shopify scripts
        elif soup.find('script', {'src': '/shopify_common.js'}) is not None:
            return url
        elif soup.find('script', {'src': '/shopify_pay.js'}) is not None:
            return url
        # Check for Shopify apps
        elif 'shopify_app' in url or 'shopify_plus' in url:
            return url
        # Check for Shopify meta tags
        elif soup.find('meta', {'name': 'generator', 'content': 'Shopify'}) is not None:
            return url
    except:
        pass

# Filter the URLs to only include Shopify sites using multiple threads
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(filter_urls, url) for url in urls]

    # Initialize the progress bar
    pbar = tqdm(total=len(urls), desc='Filtering URLs', unit='urls')

    # Iterate over the completed futures
    shopify_urls = []
    for future in as_completed(futures):
        url = future.result()
        if url:
            shopify_urls.append(url)
        pbar.update(1)
        pbar.set_postfix({'Shopify URLs': len(shopify_urls)})
    pbar.close()

# Save the Shopify URLs to shopify_urls.txt
with open('shopify_urls.txt', 'w', encoding='utf-8') as f:
    # Initialize the progress bar
    pbar = tqdm(total=len(shopify_urls), desc='Saving Shopify URLs', unit='urls')

    # Iterate over the Shopify URLs
    for url in shopify_urls:
        f.write(url + '\n')
        pbar.update(1)
    pbar.close()

# Save the Shopify URLs to a JSON file
shopify_dict = {'shopify_urls': shopify_urls}
with open('shopify_urls.json', 'w', encoding='utf-8') as f:
    json.dump(shopify_dict, f, ensure_ascii=False, indent=4)
