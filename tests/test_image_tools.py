import unittest
import tempfile
import os
from unittest import mock
from common.image_tools import save_binary_output, render_grayscale_image, find_embedded_image


class TestImageTools(unittest.TestCase):

    def test_save_binary_output(self):
        data = b"test binary content"
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            path = tmp.name

        mock_announce = mock.Mock()
        save_binary_output(path, data, announce=mock_announce,
                           label="unit test binary")

        with open(path, "rb") as f:
            self.assertEqual(f.read(), data)

        mock_announce.assert_called_once()
        os.remove(path)

    def test_render_grayscale_image(self):
        width = 4
        data = bytes(range(16))  # 4x4 grayscale image
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            path = tmp.name

        mock_announce = mock.Mock()
        render_grayscale_image(data, path, width, announce=mock_announce)

        self.assertTrue(os.path.exists(path))
        mock_announce.assert_called_once()
        os.remove(path)

    def test_render_grayscale_image_empty(self):
        with self.assertRaises(RuntimeError) as context:
            render_grayscale_image(b"", "dummy.png", 10)
        self.assertIn("Grayscale rendering error", str(context.exception))

    def test_find_embedded_image_png(self):
        sample = b"prefix" + b"\x89PNG\r\n\x1a\n" + b"imagecontentIEND"
        ext, blob = find_embedded_image(sample)
        self.assertEqual(ext, "png")
        self.assertTrue(blob.startswith(b"\x89PNG"))

    def test_find_embedded_image_no_match(self):
        ext, blob = find_embedded_image(b"no signature here")
        self.assertIsNone(ext)
        self.assertIsNone(blob)


if __name__ == "__main__":
    unittest.main()
