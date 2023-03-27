import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

# Set the app title and favicon
st.set_page_config(page_title='Shopify URL Filter', page_icon=':money_with_wings:')

# Define a function to filter the URLs to only include Shopify sites
def filter_urls(urls):
    shopify_urls = []
    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Check for Shopify CDN domain
            if 'cdn.shopify.com' in url or 'checkout.shopify.com' in url:
                shopify_urls.append(url)
            # Check for Shopify checkout pages
            elif '/checkouts/' in url:
                shopify_urls.append(url)
            # Check for Shopify favicon
            elif soup.find('link', {'rel': 'shortcut icon', 'href': '/favicon.ico'}) is not None:
                shopify_urls.append(url)
            # Check for Shopify logo
            elif soup.find('img', {'alt': 'Shopify'}) is not None:
                shopify_urls.append(url)
            # Check for Shopify scripts
            elif soup.find('script', {'src': '/shopify_common.js'}) is not None:
                shopify_urls.append(url)
            elif soup.find('script', {'src': '/shopify_pay.js'}) is not None:
                shopify_urls.append(url)
            # Check for Shopify apps
            elif 'shopify_app' in url or 'shopify_plus' in url:
                shopify_urls.append(url)
            # Check for Shopify meta tags
            elif soup.find('meta', {'name': 'generator', 'content': 'Shopify'}) is not None:
                shopify_urls.append(url)
        except:
            pass
    return shopify_urls

# Set the app title and description
st.title('Shopify URL Filter')
st.write('Filter a list of URLs to only include Shopify sites')

# Allow users to upload an input file
st.sidebar.title('Upload Input File')
input_file = st.sidebar.file_uploader('Choose a file', type=['txt', 'csv'])

# Allow users to download the output file
st.sidebar.title('Download Output File')
output_format = st.sidebar.selectbox('Select output file format', ['txt', 'json'])
if output_format == 'txt':
    output_file = st.sidebar.empty()
else:
    output_file = st.sidebar.download_button('Download JSON', None, file_name='shopify_urls.json')

# Filter the URLs to only include Shopify sites
if input_file:
    with input_file:
        urls = input_file.read().splitlines()

    shopify_urls = filter_urls(urls)

    # Display the number of Shopify URLs found
    st.write('### Results')
    st.write(f'Found {len(shopify_urls)} Shopify URLs')

    # Display the Shopify URLs
    if len(shopify_urls) > 0:
        st.write('#### Shopify URLs')
        for url in shopify_urls:
            st.write(url)

# Save the Shopify URLs to an output file
if output_format == 'txt':
    output_file.text('\n'.join(shopify_urls))
    st.sidebar.success('Output file saved!')
else:
    shopify_dict = {'shopify_urls': shopify_urls}
    output_file.data = json.dumps(shopify_dict, ensure_ascii=False, indent=4).encode('utf-8')
    st.sidebar.success('Output file saved!')
