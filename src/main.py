from copyutil import copy_static_to_public
from utils import generate_page
import shutil
import os
import sys

def main():
    # Get basepath from CLI, default to "/"
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    if not basepath.startswith("/"):
        basepath = "/" + basepath
    if not basepath.endswith("/"):
        basepath += "/"

    output_dir = "docs"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    copy_static_to_public(dest=output_dir)

    # Walk through all markdown files in content/
    for root, dirs, files in os.walk("content"):
        for file in files:
            if file.endswith(".md"):
                md_path = os.path.join(root, file)
                rel_path = os.path.relpath(md_path, "content")  # ex: blog/foo.md
                html_path = os.path.splitext(rel_path)[0] + ".html"
                dest_path = os.path.join(output_dir, html_path)
                generate_page(
                    from_path=md_path,
                    template_path="template.html",
                    dest_path=dest_path,
                    basepath=basepath,
                )

if __name__ == "__main__":
    main()