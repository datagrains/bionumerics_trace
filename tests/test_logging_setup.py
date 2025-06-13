
import unittest
import os
import tempfile
import logging
from unittest import mock
from common.logging_setup import setup_logging


class TestLoggingSetup(unittest.TestCase):

    def test_logger_creation_and_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = "test.log"
            logger = setup_logging(log_dir=tmpdir, log_file=log_file)
            self.assertEqual(logger.level, logging.INFO)
            log_path = os.path.join(tmpdir, log_file)

            logger.info("Test log message")

            with open(log_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Test log message", content)

    def test_handlers_added_once(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_dir=tmpdir, log_file="test.log")
            initial_handler_count = len(logger.handlers)

            # Call again; shouldn't add duplicate handlers
            logger = setup_logging(log_dir=tmpdir, log_file="test.log")
            self.assertEqual(len(logger.handlers), initial_handler_count)

    @mock.patch("logging.StreamHandler")
    @mock.patch("logging.FileHandler")
    def test_handlers_are_attached(self, mock_file_handler_cls, mock_stream_handler_cls):
        mock_file_handler = mock.Mock()
        mock_stream_handler = mock.Mock()

        mock_file_handler_cls.return_value = mock_file_handler
        mock_stream_handler_cls.return_value = mock_stream_handler

        logger = setup_logging(log_dir="dummy_logs", log_file="dummy.log")

        self.assertIn(mock_file_handler, logger.handlers)
        self.assertIn(mock_stream_handler, logger.handlers)


if __name__ == "__main__":
    unittest.main()
