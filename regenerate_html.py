#!/usr/bin/env python3
"""
Regenerate blog.html from existing JSON data and updated template
"""
import json
import os
from config import AUTHOR_NAME as DISPLAY_AUTHOR_NAME, BLOG_TITLE

BASE_HTML_DIR = "substack_html_pages"
HTML_TEMPLATE = "author_template.html"
JSON_DATA_DIR = "data"
AUTHOR_NAME = "blog"


def generate_html_file(author_name: str) -> None:
    """
    Generates a HTML file for the given author.
    """
    if not os.path.exists(BASE_HTML_DIR):
        os.makedirs(BASE_HTML_DIR)

    # Read JSON data
    json_path = os.path.join(JSON_DATA_DIR, f'{author_name}.json')
    with open(json_path, 'r', encoding='utf-8') as file:
        essays_data = json.load(file)

    # Convert JSON data to a JSON string for embedding
    embedded_json_data = json.dumps(essays_data, ensure_ascii=False, indent=4)

    with open(HTML_TEMPLATE, 'r', encoding='utf-8') as file:
        html_template = file.read()

    # Replace template placeholders with actual values from config
    html_with_data = html_template.replace('{{AUTHOR_NAME}}', DISPLAY_AUTHOR_NAME).replace(
        '{{BLOG_TITLE}}', BLOG_TITLE
    ).replace(
        '<script type="application/json" id="essaysData"></script>',
        f'<script type="application/json" id="essaysData">{embedded_json_data}</script>'
    )

    # Write the modified HTML to a new file
    html_output_path = os.path.join(BASE_HTML_DIR, f'{author_name}.html')
    with open(html_output_path, 'w', encoding='utf-8') as file:
        file.write(html_with_data)

    print(f"✅ Regenerated {html_output_path}")


if __name__ == "__main__":
    generate_html_file(AUTHOR_NAME)
