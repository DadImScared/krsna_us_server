
import unittest

from .utils import format_title


class FormatTests(unittest.TestCase):

    def test_format_title(self):
        test_string = '11 02 97 some stuff some stuff'
        result = format_title(test_string)
        expected_result = '1997 11 02 some stuff some stuff'
        self.assertEqual(expected_result, result)

    def test_format_title_with_four_digit_year(self):
        test_string = 'stuff 02 25 2007 more stuff'
        result = format_title(test_string)
        expected_result = 'stuff 2007 02 25 more stuff'
        self.assertEqual(expected_result, result)

    def test_format_title_with_date_at_end(self):
        test_string = 'stuff awoidjawoidj 11 2 poajwd 02 11 08'
        result = format_title(test_string)
        expected_result = 'stuff awoidjawoidj 11 2 poajwd 2008 02 11'
        self.assertEqual(expected_result, result)

    def test_format_title_with_four_digit_year_at_end(self):
        test_string = 'stuff awoidjawoidj 11 2 poajwd 02 11 2008'
        result = format_title(test_string)
        expected_result = 'stuff awoidjawoidj 11 2 poajwd 2008 02 11'
        self.assertEqual(expected_result, result)
