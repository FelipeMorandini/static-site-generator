from enum import Enum

from src.htmlnode import LeafNode


class TextType(Enum):
    NORMAL = "Normal Text"
    BOLD = "Bold Text"
    ITALIC = "Italic Text"
    CODE = "Code Text"
    LINK = "Link"
    IMAGE = "Image"

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
        return LeafNode('img', None, {'src': text_node.link})
    else:
        raise ValueError(f"Invalid text type: {text_node.text_type}")