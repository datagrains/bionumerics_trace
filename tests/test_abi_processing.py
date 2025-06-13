import unittest
import logging
from common.abi_processing import extract_base64_data  # Replace with your actual module name

class TestExtractBase64Data(unittest.TestCase):

    def test_valid_data(self):
        block = "<Data>U29tZSB2YWxpZCBiYXNlNjQ=</Data>"
        result = extract_base64_data(block)
        self.assertEqual(result, "U29tZSB2YWxpZCBiYXNlNjQ=")

    def test_missing_data_tag(self):
        block = "<NotData>abc</NotData>"
        result = extract_base64_data(block)
        self.assertEqual(result, "")

    def test_invalid_chars_removed(self):
        block = "<Data>U29tZSB2!@#YWxpZCBiYXNlNjQ=</Data>"
        result = extract_base64_data(block)
        self.assertEqual(result, "U29tZSB2YWxpZCBiYXNlNjQ=")

    def test_padding_added(self):
        block = "<Data>YWJjZA</Data>"  # 'abcd' base64 without padding
        result = extract_base64_data(block)
        self.assertEqual(result, "YWJjZA==")

    def test_no_padding_needed(self):
        block = "<Data>YWJjZA==</Data>"  # Already aligned
        result = extract_base64_data(block)
        self.assertEqual(result, "YWJjZA==")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
