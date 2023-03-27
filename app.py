import requests
from bs4 import BeautifulSoup
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm, trange

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

# Define the Streamlit app
def app():
    # Set the page title
    st.set_page_config(page_title='Shopify URL Filter', page_icon=':money_with_wings:')

    # Display the app header
    st.title('Shopify URL Filter')
    st.write('This app filters a list of URLs to only include Shopify sites.')

    # Create a file uploader for the input file
    st.sidebar.title('Upload Input File')
    input_file = st.sidebar.file_uploader('Choose a text file with one URL per line', type=['txt'])

    # Filter the URLs to only include Shopify sites using multiple threads
    if input_file is not None:
        urls = input_file.read().splitlines()
        with ThreadPoolExecutor(max_workers=100) as executor:
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

        # Display the filtered URLs in the app
        st.write(f'{len(shopify_urls)} Shopify URLs found:')
        for url in shopify_urls:
            st.write(url)

        # Allow the user to download the filtered URLs as a text file
        output_file = st.file_uploader("Download Shopify URLs as text file")
        if output_file is not None:
            output_file.write('\n'.join(shopify_urls))

# Run the app
if __name__ == '__main__':
    app()
