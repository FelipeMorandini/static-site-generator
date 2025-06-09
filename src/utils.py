import os
from textnode import markdown_to_html_node

def extract_title(markdown):
    for line in markdown.splitlines():
        if line.strip().startswith("# "):
            return line.strip()[1:].strip()
    raise Exception("No h1 header found in markdown!")

def generate_page(from_path, template_path, dest_path, basepath="/"):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}, basepath={basepath}")

    with open(from_path, "r", encoding="utf-8") as f:
        markdown = f.read()

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    content_html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    out_html = template.replace("{{ Title }}", title).replace("{{ Content }}", content_html)

    # Adjust links for basepath
    out_html = out_html.replace('href="/', f'href="{basepath}')
    out_html = out_html.replace('src="/', f'src="{basepath}')

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(out_html)