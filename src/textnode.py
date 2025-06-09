from enum import Enum

from htmlnode import LeafNode, ParentNode
import re


class TextType(Enum):
    NORMAL = "Normal Text"
    BOLD = "Bold Text"
    ITALIC = "Italic Text"
    CODE = "Code Text"
    LINK = "Link"
    IMAGE = "Image"

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


class TextNode:
    def __init__(self, text: str, text_type: TextType, link: str = None):
        self.text = text
        self.text_type = text_type
        self.link = link

    def __eq__(self, other):
        return self.text == other.text and self.text_type == other.text_type and self.link == other.link

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.link})"

def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    if text_node.text_type == TextType.NORMAL:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode('b', text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode('i', text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode('code', text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode('a', text_node.text, {'href': text_node.link})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode('img', None, {'src': text_node.link, 'alt': text_node.text})
    else:
        raise ValueError(f"Invalid text type: {text_node.text_type}")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Splits normal text nodes in old_nodes on delimiter,
    switching between NORMAL and text_type.
    """
    new_nodes = []
    for node in old_nodes:
        if not isinstance(node, TextNode) or node.text_type != TextType.NORMAL:
            new_nodes.append(node)
            continue

        segments = node.text.split(delimiter)
        # If delimiter not found, keep the node as is
        if len(segments) == 1:
            new_nodes.append(node)
            continue

        for i, segment in enumerate(segments):
            if i % 2 == 0:
                new_nodes.append(TextNode(segment, TextType.NORMAL))
            else:
                new_nodes.append(TextNode(segment, text_type))
    return new_nodes

def extract_markdown_images(text):
    """
    Extracts all markdown images from the given text.
    Returns a list of (alt_text, url) tuples.
    """
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)

def extract_markdown_links(text):
    """
    Extracts all markdown links from the given text, ignoring images.
    Returns a list of (anchor_text, url) tuples.
    """
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)

def split_nodes_image(old_nodes):
    """
    Splits normal text nodes in old_nodes on markdown images,
    converting them to IMAGE type nodes and surrounding text as TEXT.
    """
    new_nodes = []
    for node in old_nodes:
        if not isinstance(node, TextNode) or node.text_type != TextType.NORMAL:
            new_nodes.append(node)
            continue

        text = node.text
        matches = extract_markdown_images(text)
        if not matches:
            new_nodes.append(node)
            continue

        # For each image, split and build nodes
        pos = 0
        for alt, url in matches:
            md_img = f"![{alt}]({url})"
            idx = text.find(md_img, pos)
            if idx == -1:
                continue  # Shouldn't happen, but safety

            before = text[pos:idx]
            if before:
                new_nodes.append(TextNode(before, TextType.NORMAL))
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))
            pos = idx + len(md_img)
        # Any trailing text after the last image
        after = text[pos:]
        if after:
            new_nodes.append(TextNode(after, TextType.NORMAL))
    return new_nodes

def split_nodes_link(old_nodes):
    """
    Splits normal text nodes in old_nodes on markdown links,
    converting them to LINK type nodes and surrounding text as TEXT.
    """
    new_nodes = []
    for node in old_nodes:
        if not isinstance(node, TextNode) or node.text_type != TextType.NORMAL:
            new_nodes.append(node)
            continue

        text = node.text
        matches = extract_markdown_links(text)
        if not matches:
            new_nodes.append(node)
            continue

        pos = 0
        for anchor, url in matches:
            md_link = f"[{anchor}]({url})"
            idx = text.find(md_link, pos)
            if idx == -1:
                continue  # Shouldn't happen but safety

            before = text[pos:idx]
            if before:
                new_nodes.append(TextNode(before, TextType.NORMAL))
            new_nodes.append(TextNode(anchor, TextType.LINK, url))
            pos = idx + len(md_link)
        after = text[pos:]
        if after:
            new_nodes.append(TextNode(after, TextType.NORMAL))
    return new_nodes

def text_to_textnodes(text):
    """
    Converts markdown text to a list of TextNode objects,
    appropriately splitting by images, links, code, bold, and italics.
    """
    # Start with one node containing all text as NORMAL
    nodes = [TextNode(text, TextType.NORMAL)]
    # Images first (so they aren't processed by link/bold/italic)
    nodes = split_nodes_image(nodes)
    # Links next
    nodes = split_nodes_link(nodes)
    # Code (using backticks)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    # Bold (**)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    # Italic (_)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    return [node for node in nodes if node.text or node.text_type in [TextType.IMAGE, TextType.LINK]]

def markdown_to_blocks(markdown: str) -> list:
    """
    Splits a markdown string into blocks, using double newlines as separators.
    Strips whitespace from each block and removes any empty blocks.
    """
    # Split by two or more newlines, preserving blocks separated by blank lines
    blocks = markdown.split('\n\n')
    # Strip whitespace from each block, and filter out any that become empty
    return [block.strip() for block in blocks if block.strip()]

def block_to_block_type(block: str) -> BlockType:
    # Heading: 1-6 '#' at start
    if re.match(r"^#{1,6} ", block):
        return BlockType.HEADING
    # Code block: starts and ends with ```
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    # Quote: every line starts with '>'
    lines = block.splitlines()
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    # Unordered list: every line starts with '- '
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    # Ordered list: each line starts with incrementing '1. ', '2. ', ...
    if all(re.match(rf"{i+1}\. ", lines[i]) for i in range(len(lines))):
        return BlockType.ORDERED_LIST
    # Else: paragraph
    return BlockType.PARAGRAPH


def text_to_children(text):
    """
    Converts a text string with inline markdown to a list of HTMLNode children.
    """
    textnodes = text_to_textnodes(text)
    return [text_node_to_html_node(node) for node in textnodes]

def markdown_to_html_node(markdown):
    """
    Converts a Markdown document into a single Parent HTMLNode containing all child HTMLNodes.
    """
    blocks = markdown_to_blocks(markdown)
    children = []
    # Determine outer parent: if only one child and it's a list, don't wrap it in a div
    # Otherwise, always wrap in <div> (per test expectations)
    for block in blocks:
        btype = block_to_block_type(block)
        if btype == BlockType.PARAGRAPH:
            paragraph_text = ' '.join(line.strip() for line in block.splitlines())
            node = ParentNode("p", text_to_children(paragraph_text))
            children.append(node)
        elif btype == BlockType.HEADING:
            # Support multiple headings per block (split lines)
            for line in block.splitlines():
                line = line.strip()
                if not line:
                    continue
                level = 0
                while level < len(line) and line[level] == "#":
                    level += 1
                content = line[level:].strip()
                node = ParentNode(f"h{level}", text_to_children(content))
                children.append(node)
        elif btype == BlockType.CODE:
            # Remove the starting and ending ```
            stripped = block.strip()
            lines = stripped.splitlines()
            # Remove first and last line if they only contain ```
            # (don't remove code lines actually containing ```)
            if lines and lines[0].strip("`") == "":
                lines = lines[1:]
            if lines and lines[-1].strip("`") == "":
                lines = lines[:-1]
            content = "\n".join(lines)
            code_leaf = LeafNode("code", content)
            pre = ParentNode("pre", [code_leaf])
            children.append(pre)
        elif btype == BlockType.QUOTE:
            content = " ".join([line[1:].lstrip() if line.startswith(">") else line for line in block.splitlines()])
            # No <p> wrapping, as per expectations
            node = ParentNode("blockquote", text_to_children(content))
            children.append(node)
        elif btype == BlockType.UNORDERED_LIST:
            lines = [line for line in block.splitlines() if line.strip()]
            items = [ParentNode("li", text_to_children(line.lstrip("-* ").strip())) for line in lines]
            node = ParentNode("ul", items)
            children.append(node)
        elif btype == BlockType.ORDERED_LIST:
            lines = [line for line in block.splitlines() if line.strip()]
            items = []
            for line in lines:
                # Match ^\d+\.\s+
                after_dot = line
                if "." in line:
                    after_dot = line[line.find('.')+1:]
                items.append(ParentNode("li", text_to_children(after_dot.strip())))
            node = ParentNode("ol", items)
            children.append(node)
        else:
            # fallback to paragraph
            node = ParentNode("p", text_to_children(block))
            children.append(node)
    # For document root: if there is exactly 1 list and nothing else, return the list node raw, otherwise wrap in div.
    if len(children) == 1 and children[0].tag in ("ol", "ul"):
        return children[0]
    return ParentNode("div", children)