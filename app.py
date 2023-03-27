import requests
import streamlit as st
import re
import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def filter_urls(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None

        # Check for Shopify using global variable
        if 'Shopify' in response.text:
            return url

        # Check for Shopify subdomain
        if re.search(r'shopify\.io$', url):
            return url

        # Check for Shopify CDN domain
        if 'cdn.shopify.com' in url or 'checkout.shopify.com' in url:
            return url

        # Check for Shopify checkout pages
        if '/checkouts/' in url:
            return url

        # Check for Shopify favicon
        if re.search(r'/favicon\.ico$', url):
            return url

        # Check for Shopify logo
        if re.search(r'/logo\.svg$', url):
            return url

        # Check for Shopify scripts
        if re.search(r'shopify_common\.js$', response.text) or re.search(r'shopify_pay\.js$', response.text):
            return url

        # Check for Shopify apps
        if re.search(r'shopify_app|shopify_plus', url):
            return url

        # Check for Shopify meta tags
        if re.search(r'<meta.*shopify.*>', response.text):
            return url

    except Exception as e:
        logging.error(f'Error while filtering URL {url}: {e}')
        pass

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
            pbar = st.progress(0)

            # Initialize the log view
            log_view = st.empty()

            # Iterate over the completed futures
            shopify_urls = []
            errors = []
            count = 0
            for future in as_completed(futures):
                count += 1
                pbar.progress(count / len(urls))

                # Display the live status in the log view
                log_view.write(f'{count} / {len(urls)} urls checked')

                url = future.result()
                if url:
                    shopify_urls.append(url)
                else:
                    errors.append(urls[count - 1])
            
            # Display the filtered URLs in the app
            st.write(f'{len(shopify_urls)} Shopify URLs found:')
            for url in shopify_urls:
                st.write(url)

            # Allow the user to download the filtered URLs as a text file
            output_file = st.file_uploader("Download Shopify URLs as text file")
            if output_file is not None:
                output_file.write('\n'.join(shopify_urls))

            # Display any errors
            if errors:
                st.write(f'{len(errors)} errors found:')
                for error in errors:
                    st.write(error)

# Run the app
if __name__ == '__main__':
    app()
