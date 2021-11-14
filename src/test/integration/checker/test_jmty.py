import unittest
import main.checker.jmty as jmty_checker

class TestIsSaleFinished(unittest.TestCase):

	def test_when_finished_then_true(self):
		finished_sale_url = 'https://jmty.jp/kanagawa/sale-toy/article-jb6of'
		self.assertTrue(jmty_checker.is_sale_finished(finished_sale_url))

	def test_when_not_finished_then_false(self):
		# Skip for now, need to get an advert dynamically. Even then, not guaranteed to be non-finished...
		pass