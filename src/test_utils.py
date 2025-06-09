import unittest
from utils import extract_title

class TestExtractTitle(unittest.TestCase):
    def test_simple_h1(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_h1_with_whitespace(self):
        self.assertEqual(extract_title("   #   World   "), "World")

    def test_first_h1_only(self):
        md = "# First title\n# Second title"
        self.assertEqual(extract_title(md), "First title")

    def test_h1_in_middle(self):
        md = "Not a title\n# Title in middle"
        self.assertEqual(extract_title(md), "Title in middle")

    def test_no_h1_header(self):
        md = "## Not an h1\nNo header here"
        with self.assertRaises(Exception):
            extract_title(md)

if __name__ == "__main__":
    unittest.main()