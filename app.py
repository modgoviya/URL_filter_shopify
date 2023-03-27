import requests
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm, trange

def filter_urls(url):
    try:
        response = requests.get(url, timeout=5)
        if 'cdn.shopify.com' in url or 'checkout.shopify.com' in url:
            return url
        elif '/checkouts/' in url:
            return url
        elif response.headers.get('Content-Type', '').startswith('text/html'):
            if b'shopify_common.js' in response.content or b'shopify_pay.js' in response.content:
                return url
            elif b'shopify_app' in response.content or b'shopify_plus' in response.content:
                return url
            elif b'name="generator" content="Shopify"' in response.content:
                return url
    except:
        pass

def app():
    st.set_page_config(page_title='Shopify URL Filter', page_icon=':money_with_wings:')
    st.title('Shopify URL Filter')
    st.write('This app filters a list of URLs to only include Shopify sites.')
    input_file = st.sidebar.file_uploader('Choose a text file with one URL per line', type=['txt'])
    if input_file is not None:
        urls = input_file.read().splitlines()
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(filter_urls, url) for url in urls]
            shopify_urls = []
            progress = st.progress(0)
            remaining = len(urls)
            for i, future in enumerate(as_completed(futures)):
                url = future.result()
                if url:
                    shopify_urls.append(url)
                progress.progress((i + 1) / len(urls))
                remaining -= 1
                if i % 10 == 0:
                    st.write(f'{remaining} URLs remaining in {min(10, len(futures) - i)} threads')
            st.write(f'{len(shopify_urls)} Shopify URLs found:')
            for url in shopify_urls:
                st.write(url)
            output_file = st.file_uploader("Download Shopify URLs as text file")
            if output_file is not None:
                output_file.write('\n'.join(shopify_urls))

if __name__ == '__main__':
    app()
