from typing import List


class HtmlNode:
    def __init__(self, tag: str = None, value: str = None, children: list = None, props: dict = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        props_html = ""
        if self.props:
            for key, value in self.props.items():
                props_html += f' {key}="{value}"'
        return props_html

    def __eq__(self, other):
        return self.tag == other.tag and self.value == other.value and self.children == other.children and self.props == other.props

    def __repr__(self):
        return f"HtmlNode({self.tag}, {self.value}, {self.children}, {self.props})"


class ParentNode(HtmlNode):
    def __init__(self, tag: str, children: List[HtmlNode], value: str = None, props: dict = None):
        if tag is None:
            raise ValueError("Tag cannot be None")
        if children is None or len(children) == 0:
            raise ValueError("Children cannot be None or an empty list")
        super().__init__(tag, value, children, props)

    def to_html(self):
        value_html = self.value if self.value is not None else ""
        return f"<{self.tag}{self.props_to_html()}>{value_html}{''.join([child.to_html() for child in self.children])}</{self.tag}>"


class LeafNode(HtmlNode):
    SELF_CLOSING_TAGS = {"img", "br", "hr", "input", "meta", "link", "area", "base", "col", "embed", "source", "track", "wbr"}

    def __init__(self, tag: str, value: str, props: dict = None):
        if tag in LeafNode.SELF_CLOSING_TAGS:
            value = None
        elif value is None:
            raise ValueError("Value cannot be None")
        super().__init__(tag, value, [], props)

    def to_html(self):
        if self.tag is None:
            return self.value
        if self.tag in LeafNode.SELF_CLOSING_TAGS:
            return f"<{self.tag}{self.props_to_html()}/>"
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"