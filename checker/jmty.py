import requests
import re
from bs4 import BeautifulSoup


search_obj = {
    "search_term": "marin bike"
}


def get_search_html_response():
    resp = requests.get(
            "https://jmty.jp/all/sale",
            params = { "keyword": search_obj["search_term"]  }
        )
    if resp.status_code != 200:
        raise Exception

    return resp.text

def get_souped_search_results(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all("li", class_="p-articles-list-item")

def _extract_price(raw_price_string):
    expr = re.compile("\d+,?\d*")
    price_string = expr.search(raw_price_string).group()
    return int(price_string.replace(",",""))

def _extract_id(raw_url_string):
    expr = re.compile(".*-(\w+)")
    return expr.search(raw_url_string).group(1)

def process_soup_list_item(soup_list_item):
    return {
            "id": _extract_id(soup_list_item.find("h2", "p-item-title").a["href"]),
            "price": _extract_price(soup_list_item.find("div", class_="p-item-most-important").string)
    }


def process_html(html):
    soup_results = get_souped_search_results(html)
    listed_items = [process_soup_list_item(soup_result) for soup_result in soup_results]
    return listed_items

if __name__ == "__main__":
    full_html_resp = get_search_html_response()
    items = process_html(full_html_resp)
    print(items)
