import unittest
from common.block_utils import parse_blocks, safe_get


class TestBlockUtils(unittest.TestCase):

    def test_single_block(self):
        text = "-1\tNULL\tCTG start\n<Tracefile>\ndata\n</Tracefile>"
        blocks = parse_blocks(text)
        self.assertEqual(len(blocks), 1)
        self.assertIn("<Tracefile>", blocks[0])
        self.assertIn("</Tracefile>", blocks[0])

    def test_multiple_blocks(self):
        text = (
            "-1\tNULL\tCTG start\n<FileName>file1</FileName>\n</Tracefile>\n"
            "-1\tNULL\tCTG start\nTracefile something\n</Tracefile>"
        )
        blocks = parse_blocks(text)
        self.assertEqual(len(blocks), 2)

    def test_ignores_non_tracefile_blocks(self):
        text = "-1\tNULL\tCTG start\nNo valid trace here\nMore invalid stuff"
        blocks = parse_blocks(text)
        self.assertEqual(blocks, [])

    def test_partial_block_at_end(self):
        text = "-1\tNULL\tCTG start\n<FileName>file2</FileName>"
        blocks = parse_blocks(text)
        self.assertEqual(len(blocks), 1)

    def test_safe_get_matches(self):
        block = "<Tag>Hello world</Tag>"
        result = safe_get(r"<Tag>(.*?)</Tag>", block)
        self.assertEqual(result, "Hello world")

    def test_safe_get_no_match(self):
        block = "No match here"
        result = safe_get(r"<Missing>(.*?)</Missing>", block)
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
