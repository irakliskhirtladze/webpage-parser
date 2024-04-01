import httpx
from selectolax.parser import HTMLParser


def get_html():
    url = 'https://www.rei.com/c/camping-and-hiking/f/scd-deals'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                      '(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    resp = httpx.get(url, headers=headers)
    html = HTMLParser(resp.text)
    return html


def get_value(html_element, selector):
    try:
        return html_element.css_first(selector).text()
    except AttributeError:
        return None


def parse_page(html):
    products = html.css('li.VcGDfKKy_dvNbxUqm29K')
    for product in products:
        price = get_value(product, "span[data-ui=full-price]") if not None \
            else get_value(product, "span[data-ui=sale-price]")
        # print(price)

        product_info = {
            'name': get_value(product, "span.nL0nEPe34KFncpRNS29I"),
            'description': get_value(product, "span.Xpx0MUGhB7jSm5UvK2EY"),
            'price': price,
            'savings': get_value(product, "div[data-ui=savings-percent-variant2]")
        }
        print(product_info)
        print('\n')
