import unittest
import unittest.mock as mock
import main.checker.jmty as jmty_checker
import os.path
import re

from bs4 import BeautifulSoup


class TestSearchHasNextPage(unittest.TestCase):

    def _get_soup_of_local_file(self, filename):
        this_files_dir = os.path.dirname(os.path.abspath(__file__))
        test_html_filepath = os.path.join(this_files_dir, filename)
        with open(test_html_filepath, encoding='utf-8') as f:
            return BeautifulSoup(f, 'html.parser')

    def test_when_only_one_page_results_then_false(self):
        soup = self._get_soup_of_local_file('results_total_one_page.html')
        self.assertFalse(jmty_checker._search_has_next_page(soup))

    def test_when_no_results_then_false(self):
        soup = self._get_soup_of_local_file('results_empty.html')
        self.assertFalse(jmty_checker._search_has_next_page(soup))

    def test_when_multiple_pages_and_current_is_not_last_then_true(self):
        soup = self._get_soup_of_local_file('results_many_pages_current_not_last.html')
        self.assertTrue(jmty_checker._search_has_next_page(soup))

    def test_when_multiple_pages_and_current_is_last_then_false(self):
        soup = self._get_soup_of_local_file('results_many_pages_current_is_last.html')
        self.assertFalse(jmty_checker._search_has_next_page(soup))


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

        self.assertTrue(jmty_checker._page_contains_finished_ads(mock_adverts))

    def test_when_no_finished_ads_then_false(self):
        mock_adverts = [
            self._create_unfinished_advert(),
            self._create_unfinished_advert(),
            self._create_unfinished_advert(),
            self._create_unfinished_advert()
        ]

        self.assertFalse(jmty_checker._page_contains_finished_ads(mock_adverts))

    def test_when_no_ads_then_false(self):
        mock_adverts = []
        self.assertFalse(jmty_checker._page_contains_finished_ads(mock_adverts))


@mock.patch('main.checker.jmty.requests')
class TestCheck(unittest.TestCase):

    _finished_sales_ids = ['mockId2']

    def _file_as_string(self, filepath):
        this_files_dir = os.path.dirname(os.path.abspath(__file__))
        test_html_filepath = os.path.join(this_files_dir, filepath)
        with open(test_html_filepath, encoding='utf-8') as f:
            return f.read().replace('\n', ' ')

    def _is_article_request(self, url):
        """Actual article being requested rather than search results"""
        return '/sale-' in url and '/article-' in url

    def _create_mock_response(self, url):
        # TODO tidy this up
        if self._is_article_request(url):
            id_ = jmty_checker._extract_id(url)
            if id_ in TestCheck._finished_sales_ids:
                return MockResponse(200, self._file_as_string('mock_finished_sale_article.html'))
            else:  # assume it is an unfinished sale
                return MockResponse(200, self._file_as_string('mock_unfinished_sale_article.html'))
        else:
            return mock.DEFAULT

    def _map_by_article_id(self, items):
        return {item['id']: item for item in items}

    def _assert_values_equal(self, result: dict, **kwargs):
        """Assert that the values given in kwargs are present in `result` and match."""
        for arg_key in kwargs:
            self.assertEqual(result[arg_key], kwargs[arg_key])

    def test_when_one_applicable_page_then_correct_objects_returned(self, requests_mock):
        requests_mock.get.return_value = MockResponse(200, self._file_as_string('results_total_one_page.html'))
        requests_mock.get.side_effect = self._create_mock_response
        items = jmty_checker.check('road bike')
        self.assertEqual(len(items), 2)

        items_by_id = self._map_by_article_id(items)
        self._assert_values_equal(
            items_by_id['mockId1'],
            id='mockId1',
            is_finished=False,
            price=25000
        )
        self._assert_values_equal(
            items_by_id['mockId2'],
            id='mockId2',
            is_finished=True,
            price=100
        )


class MockResponse:
    """Mock response object from the requests module"""
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text