import unittest

from textnode import (
    TextNode,
    TextType,
    text_node_to_html_node,
    split_nodes_delimiter,
    extract_markdown_links,
    extract_markdown_images,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    markdown_to_blocks,
    block_to_block_type,
    BlockType,
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_diff_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a different text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_diff_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_diff_link(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD, "https://www.boot.dev")
        self.assertNotEqual(node, node2)

    def test_text(self):
        node = TextNode("This is a text node", TextType.NORMAL)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code_single(self):
        node = TextNode("try `code` now", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("try ", TextType.NORMAL),
                TextNode("code", TextType.CODE),
                TextNode(" now", TextType.NORMAL)
            ]
        )

    def test_bold_double(self):
        node = TextNode("**bold** in the middle", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("", TextType.NORMAL),  # Before first **
                TextNode("bold", TextType.BOLD),
                TextNode(" in the middle", TextType.NORMAL)
            ]
        )

    def test_italic_underscore(self):
        node = TextNode("Hello _italic_ world", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("Hello ", TextType.NORMAL),
                TextNode("italic", TextType.ITALIC),
                TextNode(" world", TextType.NORMAL)
            ]
        )

    def test_multiple_delimiters(self):
        node = TextNode("A `b` and `c` and `d`", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("A ", TextType.NORMAL),
                TextNode("b", TextType.CODE),
                TextNode(" and ", TextType.NORMAL),
                TextNode("c", TextType.CODE),
                TextNode(" and ", TextType.NORMAL),
                TextNode("d", TextType.CODE),
                TextNode("", TextType.NORMAL)
            ]
        )

    def test_no_delimiter(self):
        node = TextNode("No delimiter here", TextType.NORMAL)
        new_nodes = split_nodes_delimiter([node], "*", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [TextNode("No delimiter here", TextType.NORMAL)]
        )

    def test_non_normal_type_node(self):
        node = TextNode("Bold text", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [node])

    def test_node_list_with_mixed_types(self):
        nodes = [
            TextNode("before `code` after", TextType.NORMAL),
            TextNode("no delimiter", TextType.NORMAL),
            TextNode("special", TextType.BOLD),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("before ", TextType.NORMAL),
                TextNode("code", TextType.CODE),
                TextNode(" after", TextType.NORMAL),
                TextNode("no delimiter", TextType.NORMAL),
                TextNode("special", TextType.BOLD),
            ]
        )


class TestMarkdownExtraction(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual(
            [("image", "https://i.imgur.com/zjjcJKZ.png")], matches
        )

    def test_extract_multiple_images(self):
        text = "![a](url1) and ![b](url2)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("a", "url1"), ("b", "url2")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "Link to [Boot](https://boot.dev) and [YT](https://yt.com)"
        )
        self.assertListEqual(
            [("Boot", "https://boot.dev"), ("YT", "https://yt.com")], matches
        )

    def test_extract_links_no_false_image_hits(self):
        text = "![alt](img) and [real](site)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("real", "site")], matches)

    def test_extract_no_matches(self):
        self.assertListEqual(extract_markdown_links("no links here"), [])
        self.assertListEqual(extract_markdown_images("no images here"), [])

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.NORMAL),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.NORMAL),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.NORMAL),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.NORMAL),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_split_image_no_image(self):
        node = TextNode("No images here!", TextType.NORMAL)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_link_no_link(self):
        node = TextNode("No links here!", TextType.NORMAL)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_non_normal_type(self):
        node = TextNode("[link](url)", TextType.CODE)
        self.assertListEqual([node], split_nodes_link([node]))
        node2 = TextNode("![img](url)", TextType.BOLD)
        self.assertListEqual([node2], split_nodes_image([node2]))

    def test_split_multiple_nodes(self):
        node1 = TextNode("A [b](c)!", TextType.NORMAL)
        node2 = TextNode("![alt](url)", TextType.NORMAL)
        node3 = TextNode("Just text", TextType.NORMAL)
        split_links = split_nodes_link([node1, node2, node3])
        self.assertEqual(split_links[0], TextNode("A ", TextType.NORMAL))
        self.assertEqual(split_links[1], TextNode("b", TextType.LINK, "c"))
        self.assertEqual(split_links[2], TextNode("!", TextType.NORMAL))
        self.assertEqual(split_links[3], node2)
        self.assertEqual(split_links[4], node3)

    def test_text_to_textnodes_basic(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.NORMAL),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.NORMAL),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.NORMAL),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.NORMAL),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.NORMAL),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_text_to_textnodes_no_md(self):
        text = "Just plain text here."
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("Just plain text here.", TextType.NORMAL)],
            nodes,
        )

    def test_text_to_textnodes_order(self):
        text = "before ![img](url) after [l](w) **b** _i_ `c`"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("before ", TextType.NORMAL),
                TextNode("img", TextType.IMAGE, "url"),
                TextNode(" after ", TextType.NORMAL),
                TextNode("l", TextType.LINK, "w"),
                TextNode(" ", TextType.NORMAL),
                TextNode("b", TextType.BOLD),
                TextNode(" ", TextType.NORMAL),
                TextNode("i", TextType.ITALIC),
                TextNode(" ", TextType.NORMAL),
                TextNode("c", TextType.CODE),
            ],
            nodes,
        )

class TestMarkdownBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = (
            "This is **bolded** paragraph\n\n"
            "This is another paragraph with _italic_ text and `code` here\n"
            "This is the same paragraph on a new line\n\n"
            "- This is a list\n"
            "- with items\n"
        )
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )


class TestBlockType(unittest.TestCase):
    def test_heading_block(self):
        self.assertEqual(
            block_to_block_type("# Hello World"), BlockType.HEADING
        )
        self.assertEqual(
            block_to_block_type("###### Smallest heading"), BlockType.HEADING
        )

    def test_code_block(self):
        code = "```\nprint('hi')\n```"
        self.assertEqual(
            block_to_block_type(code), BlockType.CODE
        )

    def test_quote_block(self):
        self.assertEqual(
            block_to_block_type("> quote"), BlockType.QUOTE
        )
        self.assertEqual(
            block_to_block_type("> first\n> second"), BlockType.QUOTE
        )

    def test_unordered_list_block(self):
        self.assertEqual(
            block_to_block_type("- item 1\n- item 2"), BlockType.UNORDERED_LIST
        )

    def test_ordered_list_block(self):
        self.assertEqual(
            block_to_block_type("1. First\n2. Second\n3. Third"), BlockType.ORDERED_LIST
        )

    def test_paragraph_block(self):
        self.assertEqual(
            block_to_block_type("Some text here!\nSomething else."),
            BlockType.PARAGRAPH,
        )
        self.assertEqual(
            block_to_block_type("Just a normal line."), BlockType.PARAGRAPH
        )


if __name__ == "__main__":
    unittest.main()