import unittest
import main.checker.jmty as jmty_checker
import os.path
from bs4 import BeautifulSoup


class TestSearchHasNextPage(unittest.TestCase):

    def _get_soup_of_local_file(self, filename):
        this_files_dir = os.path.dirname(os.path.abspath(__file__))
        test_html_filepath = os.path.join(this_files_dir, filename)
        with open(test_html_filepath) as f:
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
        return { "id": 'mock_id',
            "price": 100,
            "url": 'mock_url',
            "is_finished": False
        }

    def _create_finished_advert(self):
        return { "id": 'mock_id',
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
