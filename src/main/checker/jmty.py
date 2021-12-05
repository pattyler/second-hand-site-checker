import requests
import re
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


def _extract_price(raw_price_string):
    expr = re.compile("\d+,?\d*")
    price_string = expr.search(raw_price_string).group()
    return int(price_string.replace(",", ""))


def _extract_id(raw_url_string):
    expr = re.compile(".*-(\w+)")
    return expr.search(raw_url_string).group(1)


def _search_has_next_page(soup):
    page_list = soup.find("div", class_="page_list")
    if page_list is None:
        return False

    return page_list.parent.find("div", class_="last") is not None


def _page_contains_finished_ads(listed_items):
    return True in list(map(lambda x: x['is_finished'], listed_items))


def _is_sale_finished(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception

    soup = BeautifulSoup(resp.text, "html.parser")
    p_tags = soup.find("div", id="items").find("div", class_="clearfix").find("p")
    text_after_br_tag = len(p_tags.contents) > 2
    if not text_after_br_tag:
        return False

    return "終了いたしました" in p_tags.contents[2]


def _get_search_html_response(search_term, page_num=1):
    resp = requests.get(
        f'https://jmty.jp/all/sale/p-{page_num}',
        params={"keyword": search_term}
    )
    if resp.status_code != 200:
        raise Exception # TODO raise proper exception

    return resp.text


def _get_souped_search_results(soup):
    return soup.find_all("li", class_="p-articles-list-item")


def _process_soup_list_item(soup_list_item):
    url = soup_list_item.find("div", class_="p-item-content-info").find("a")["href"]
    return {
        "id": _extract_id(soup_list_item.find("h2", "p-item-title").a["href"]),
        "price": _extract_price(soup_list_item.find("div", class_="p-item-most-important").string),
        "url": url,
        "is_finished": _is_sale_finished(url)
    }


def _run(search_term, current_page_num=1):
    logger.info(f'Searching page {current_page_num}')
    full_html_resp = _get_search_html_response(current_page_num)
    soup = BeautifulSoup(full_html_resp, "html.parser")
    soup_results = _get_souped_search_results(soup)
    listed_items = [_process_soup_list_item(soup_result) for soup_result in soup_results]
    if (_search_has_next_page(soup)
            and not _page_contains_finished_ads(listed_items)):
        listed_items += _run(search_term, current_page_num + 1)

    return listed_items


def check(search_term):
    """Check Jmty for the given `search_term`. Returns a list of article IDs, prices, etc."""
    return _run(search_term)