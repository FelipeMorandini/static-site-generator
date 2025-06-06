import unittest

from htmlnode import HtmlNode, LeafNode, ParentNode

class TestHtmlNode(unittest.TestCase):
    def test_eq(self):
        node = HtmlNode("div", "This is a div", [], {})
        node2 = HtmlNode("div", "This is a div", [], {})
        self.assertEqual(node, node2)

    def test_diff_tag(self):
        node = HtmlNode("div", "This is a div", [], {})
        node2 = HtmlNode("span", "This is a div", [], {})
        self.assertNotEqual(node, node2)

    def test_diff_value(self):
        node = HtmlNode("div", "This is a div", [], {})
        node2 = HtmlNode("div", "This is a different div", [], {})
        self.assertNotEqual(node, node2)

    def test_diff_children(self):
        node = HtmlNode("div", "This is a div", [], {})
        node2 = HtmlNode("div", "This is a div", ["This is a child"], {})
        self.assertNotEqual(node, node2)

    def test_diff_props(self):
        node = HtmlNode("div", "This is a div", [], {})
        node2 = HtmlNode("div", "This is a div", [], {"class": "container"})
        self.assertNotEqual(node, node2)

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_link(self):
        node = LeafNode("a", "Boot.dev", {"href": "https://www.boot.dev"})
        self.assertEqual(node.to_html(), '<a href="https://www.boot.dev">Boot.dev</a>')

    def test_leaf_none_value(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None)

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )