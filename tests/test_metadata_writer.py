import unittest
import tempfile
import os
import csv
from unittest import mock
from common.metadata_writer import write_metadata


class TestMetadataWriter(unittest.TestCase):

    def test_write_metadata_creates_file_with_correct_content(self):
        metadata = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        with tempfile.NamedTemporaryFile(delete=False, mode="r", encoding="utf-8") as tmp:
            path = tmp.name

        mock_announce = mock.Mock()
        write_metadata(metadata, path, announce=mock_announce)

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            rows = list(reader)
            self.assertEqual(rows, [{"name": "Alice", "age": "30"}, {
                             "name": "Bob", "age": "25"}])

        mock_announce.assert_called_once_with(f"Metadata written to {path}")
        os.remove(path)

    def test_write_metadata_empty_input_does_nothing(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            path = tmp.name

        mock_announce = mock.Mock()
        write_metadata([], path, announce=mock_announce)

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertEqual(content, "")

        mock_announce.assert_not_called()
        os.remove(path)


if __name__ == "__main__":
    unittest.main()
