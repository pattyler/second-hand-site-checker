import unittest
import unittest.mock as mock
import main.checker as checker
import os.path
from bs4 import BeautifulSoup


def any_jmty_checker():
    return checker.Jmty("")


class TestSearchHasNextPage(unittest.TestCase):

    def _get_soup_of_local_file(self, filename):
        this_files_dir = os.path.dirname(os.path.abspath(__file__))
        test_html_filepath = os.path.join(this_files_dir, filename)
        with open(test_html_filepath, encoding='utf-8') as f:
            return BeautifulSoup(f, 'html.parser')

    def test_when_only_one_page_results_then_false(self):
        soup = self._get_soup_of_local_file('results_total_one_page.html')
        self.assertFalse(any_jmty_checker()._search_has_next_page(soup))

    def test_when_no_results_then_false(self):
        soup = self._get_soup_of_local_file('results_empty.html')
        self.assertFalse(any_jmty_checker()._search_has_next_page(soup))

    def test_when_multiple_pages_and_current_is_not_last_then_true(self):
        soup = self._get_soup_of_local_file('results_many_pages_current_not_last.html')
        self.assertTrue(any_jmty_checker()._search_has_next_page(soup))

    def test_when_multiple_pages_and_current_is_last_then_false(self):
        soup = self._get_soup_of_local_file('results_many_pages_current_is_last.html')
        self.assertFalse(any_jmty_checker()._search_has_next_page(soup))


class TestPageContainsFinishedAds(unittest.TestCase):

    def _create_unfinished_advert(self):
        return {"id": 'mock_id',
                "price": 100,
                "url": 'mock_url',
                "is_finished": False
                }

    def _create_finished_advert(self):
        return {"id": 'mock_id',
                "price": 100,
                "url": 'mock_url',
                "is_finished": True
                }

    def test_when_one_finished_ad_then_true(self):
        mock_adverts = [
            self._create_unfinished_advert(),
            self._create_unfinished_advert(),
            self._create_unfinished_advert(),
            self._create_finished_advert()
        ]

        self.assertTrue(any_jmty_checker()._page_contains_finished_ads(mock_adverts))

    def test_when_no_finished_ads_then_false(self):
        mock_adverts = [
            self._create_unfinished_advert(),
            self._create_unfinished_advert(),
            self._create_unfinished_advert(),
            self._create_unfinished_advert()
        ]

        self.assertFalse(any_jmty_checker()._page_contains_finished_ads(mock_adverts))

    def test_when_no_ads_then_false(self):
        mock_adverts = []
        self.assertFalse(any_jmty_checker()._page_contains_finished_ads(mock_adverts))


@mock.patch('main.checker.requests')
class TestCheck(unittest.TestCase):

    def _map_by_article_id(self, items):
        return {item.id: item for item in items}

    def _file_as_string(self, filepath):
        this_files_dir = os.path.dirname(os.path.abspath(__file__))
        test_html_filepath = os.path.join(this_files_dir, filepath)
        with open(test_html_filepath, encoding='utf-8') as f:
            return f.read().replace('\n', ' ')

    def _is_article_request(self, url):
        """Actual article being requested rather than search results"""
        return '/sale-' in url and '/article-' in url

    def _mock_get(self, url, **kwargs):
        if self._is_article_request(url):
            if 'mockId2' in url:
                return MockResponse(200, self._file_as_string('mock_finished_sale_article.html'))
            else:
                return MockResponse(200, self._file_as_string('mock_unfinished_sale_article.html'))
        else:
            return MockResponse(200, self._file_as_string('results_total_one_page.html'))

    def test_when_one_page_then_correct_objects_returned(self, requests_mock):
        requests_mock.get.side_effect = self._mock_get
        items = checker.Jmty('road bike').check()
        self.assertEqual(len(items), 2)

        items_by_id = self._map_by_article_id(items)
        self.assertEqual(items_by_id['mockId1'].id, 'mockId1')
        self.assertEqual(items_by_id['mockId1'].is_finished, False)
        self.assertEqual(items_by_id['mockId1'].price, 25000)

        self.assertEqual(items_by_id['mockId2'].id, 'mockId2')
        self.assertEqual(items_by_id['mockId2'].is_finished, True)
        self.assertEqual(items_by_id['mockId2'].price, 100)


class MockResponse:
    """Mock response object from the `requests` module"""

    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


class TestJmtyItem(unittest.TestCase):

    def test_when_ids_not_equal_then_objects_not_equal(self):
        item1 = checker._JmtyItem(id=1, price=0, url="", is_finished=False)
        item2 = checker._JmtyItem(id=2, price=0, url="", is_finished=False)
        self.assertFalse(item1 == item2)

    def test_when_ids_equal_then_objects_equal(self):
        item1 = checker._JmtyItem(id=1, price=0, url="", is_finished=False)
        item2 = checker._JmtyItem(id=1, price=999, url="www.something.com", is_finished=True)
        self.assertTrue(item1 == item2)

    def test_when_ids_equal_then_hashes_equal(self):
        item1 = checker._JmtyItem(id=1, price=0, url="", is_finished=False)
        item2 = checker._JmtyItem(id=1, price=999, url="www.something.com", is_finished=True)
        self.assertTrue(item1.__hash__() == item2.__hash__())
