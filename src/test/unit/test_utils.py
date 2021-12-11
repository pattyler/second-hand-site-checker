import main.utils as utils
import unittest


class TestFlatten(unittest.TestCase):

    def test_when_empty_list_then_empty_list_returned(self):
        self.assertEqual(utils.flatten([]), [])

    def test_when_list_contains_non_list_object_then_error_raised(self):
        with self.assertRaises(ValueError):
            utils.flatten([[1,2], "not valid"])

    def test_when_single_list_then_single_list_returned(self):
        self.assertEqual(utils.flatten([[1,2]]), [1,2])

    def test_when_multiple_lists_then_single_list_returned(self):
        self.assertEqual(utils.flatten([[1,2], [3,4], [5,6]]), [1,2,3,4,5,6])

    def test_when_multiple_lists_with_sam_values_then_duplicate_values_exist(self):
        self.assertEqual(utils.flatten([[1,2], [1,2], [1,2]]), [1,2,1,2,1,2])
