import concurrent.futures
import time
import httpx
from selectolax.parser import HTMLParser
import dataclasses


@dataclasses.dataclass
class Product:
    name: str | None
    price: str | None
    saving: str | None


def get_html(page_url, headers_dict):
    """ Returns the HTML of the page_url  """
    resp = httpx.get(page_url, headers=headers_dict, follow_redirects=True)
    if resp.status_code == 200:  # 200 - OK
        return HTMLParser(resp.text)
    return None


def get_value(html_element, selector):
    """Returns the value of the selector in the html_element """
    try:
        return html_element.css_first(selector).text()
    except AttributeError:
        return None


def get_values(html_element, selector):
    """Returns multiple values of the selector in the html_element """
    try:
        return html_element.css(selector).text()
    except AttributeError:
        return None


def get_prod_urls(html_doc):
    """Returns the list of product urls from given multiple products page"""
    products = html_doc.css('li.VcGDfKKy_dvNbxUqm29K')
    main_url = 'https://www.rei.com'
    for product in products:
        yield main_url + product.css_first("a").attributes['href']


def get_prod_info(html_doc):
    """Get desired product information from a single product page"""
    product_info = Product(
        name=get_value(html_doc, 'h1#product-page-title'),
        price=get_value(html_doc, 'span#buy-box-price'),
        saving=get_value(html_doc, 'span.price-component__price-saving-percent')
    )
    return product_info


if __name__ == '__main__':
    num_pages = 1
    products_page_base_url = 'https://www.rei.com/c/camping-and-hiking/f/scd-deals?page='
    full_products_urls = [products_page_base_url + str(page_num) for page_num in range(1, num_pages + 1)]
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                      '(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    # Using multiple threads to get HTMLs of multiple products pages
    with concurrent.futures.ThreadPoolExecutor() as executor:
        pages = list(executor.map(get_html, full_products_urls, [headers for header in range(1, num_pages + 1)]))
        all_prod_urls_generators = list(executor.map(get_prod_urls, pages))

    # Get all product urls from all pages
    prod_urls = []
    for url_generator in all_prod_urls_generators:
        for url in url_generator:
            prod_urls.append(url)

    # Obtain product information from multiple product pages using single thread and measure time
    start_time_1 = time.perf_counter()
    for url in prod_urls:
        html_doc = get_html(url, headers)
        print(get_prod_info(html_doc))
    end_time_1 = time.perf_counter()

    # Obtain product information from multiple product pages using multiple threads and measure time
    start_time_2 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        html_docs = list(executor.map(get_html, prod_urls, [headers for num in range(len(prod_urls))]))
    for html_doc in html_docs:
        print(get_prod_info(html_doc))
    end_time_2 = time.perf_counter()

    print(f'\nTime required with single thread: {end_time_1 - start_time_1}')
    print(f'Time required with multiple threads: {end_time_2 - start_time_2}')
