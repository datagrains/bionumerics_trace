import unittest
import base64
import zlib
import logging
from io import StringIO
from unittest.mock import patch
from common.abi_processing import extract_base64_data, has_abi_header

class TestABIProcessing(unittest.TestCase):
    def SetUp(self):
        # Set up logging capture
        self.log_capture = StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        logging.getLogger().addHandler(self.handler)
        logging.getLogger().setLevel(logging.INFO)

    def TearDown(self):
        # Clean up logging
        logging.getLogger().removeHandler(self.handler)
        self.log_capture.close()
        
        result = extract_base64_data(block, try_decompress=False)
        self.assertEqual(result, original_data)
        self.assertIn("Base64 decoded successfully", self.log_capture.getvalue())
        self.assertNotIn("Zlib decompression", self.log_capture.getvalue())

    def test_has_abi_header_valid(self):
        # Test data with valid ABIF header
        data = b"ABIFSomeData"
        self.assertTrue(has_abi_header(data))

    def test_has_abi_header_invalid(self):
        # Test data without ABIF header
        data = b"XYZSomeData"
        self.assertFalse(has_abi_header(data))

    def test_has_abi_header_empty(self):
        # Test empty data
        data = b""
        self.assertFalse(has_abi_header(data))

    def test_has_abi_header_short(self):
        # Test data shorter than header
        data = b"AB"
        self.assertFalse(has_abi_header(data))

if __name__ == '__main__':
    unittest.main()