import requests
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

# Define a function to check if a URL is using Shopify
def check_shopify(url):
    try:
        response = requests.get(url)
        # Check for the global Shopify JavaScript variable
        if 'Shopify' in response.text:
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

    # Check if URLs are using Shopify using multiple threads
    if input_file is not None:
        urls = input_file.read().splitlines()
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(check_shopify, url) for url in urls]

            # Initialize the progress bar
            total_urls = len(urls)
            pbar = st.progress(0)

            # Iterate over the completed futures
            shopify_urls = []
            for i, future in enumerate(as_completed(futures)):
                url = future.result()
                if url:
                    shopify_urls.append(url)
                # Update the progress bar every 10% or for the last URL
                if (i+1) % (total_urls//10) == 0 or i+1 == total_urls:
                    pbar.progress((i+1)/total_urls)
            pbar.empty()

        # Display the URLs using Shopify in the app
        st.write(f'{len(shopify_urls)} Shopify URLs found:')
        for url in shopify_urls:
            st.write(url)

        # Allow the user to download the URLs using Shopify as a text file
        output_file = st.file_uploader("Download Shopify URLs as text file")
        if output_file is not None:
            output_file.write('\n'.join(shopify_urls))

# Run the app
if __name__ == '__main__':
    app()
