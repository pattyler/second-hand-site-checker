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

    _finished_sales_ids = ['m5q5d']

    def _assert_number_finished_sales(self, items, number_finished):
        filtered_items = list(filter(lambda item: item['is_finished'] is True, items))
        self.assertEqual(len(filtered_items), number_finished)

    def _assert_number_unfinished_sales(self, items, number_unfinished):
        filtered_items = list(filter(lambda item: item['is_finished'] is False, items))
        self.assertEqual(len(filtered_items), number_unfinished)

    def _assert_contains_ids(self, items, ids):
        filtered_items = set([x['id'] for x in filter(lambda item: item['id'] in ids, items)])
        self.assertEqual(len(filtered_items), len(ids))

    def _file_as_string(self, filepath):
        this_files_dir = os.path.dirname(os.path.abspath(__file__))
        test_html_filepath = os.path.join(this_files_dir, filepath)
        with open(test_html_filepath, encoding='utf-8') as f:
            return f.read().replace('\n', ' ')

    def _create_mock_response(self, url, **kwargs):
        # TODO tidy this up
        if '/sale-' in url and '/article-' in url: # actual article is being requested
            id_ = re.search('.*/article-(.*)', url).group(1)
            if id_ in TestCheck._finished_sales_ids:
                return MockResponse(200, self._file_as_string('mock_finished_sale_article.html'))
            else: # assume it is an unfinished sale
                return MockResponse(200, self._file_as_string('mock_unfinished_sale_article.html'))
        else:
            return mock.DEFAULT

    def test_when_one_applicable_page_then_correct_objects_returned(self, requests_mock):
        requests_mock.get.return_value = MockResponse(200, self._file_as_string('results_total_one_page.html'))
        requests_mock.get.side_effect = self._create_mock_response
        items = jmty_checker.check('road bike')

        self._assert_number_unfinished_sales(items, 1)
        self._assert_number_finished_sales(items, 19)
        self._assert_contains_ids(items, ['m5q5d', 'm86ld'])


class MockResponse:
    """Mock response object from the requests module"""
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text