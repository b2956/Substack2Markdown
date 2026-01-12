#!/usr/bin/env python3
"""
Download only new articles that aren't in our library yet
"""
import requests
from xml.etree import ElementTree as ET
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_existing_slugs():
    """Get slugs of articles we already have"""
    with open('data/blog.json', 'r') as f:
        essays = json.load(f)

    existing_slugs = set()
    for essay in essays:
        file_path = essay['file_link']
        slug = file_path.split('/')[-1].replace('.md', '')
        existing_slugs.add(slug)

    return existing_slugs

def get_new_article_urls():
    """Fetch sitemap and find new articles"""
    blog_url = os.getenv('SUBSTACK_BLOG_URL')
    if not blog_url:
        print("❌ Error: SUBSTACK_BLOG_URL not set in .env file")
        print("Please add SUBSTACK_BLOG_URL=https://your-blog.substack.com to your .env file")
        sys.exit(1)

    sitemap_url = f"{blog_url}/sitemap.xml"
    response = requests.get(sitemap_url)
    root = ET.fromstring(response.content)

    # Get all URLs
    urls = [element.text for element in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]

    # Filter to post URLs only
    post_urls = [url for url in urls if '/p/' in url and not any(kw in url for kw in ['about', 'archive', 'podcast'])]

    # Find new URLs
    existing_slugs = get_existing_slugs()
    new_urls = []
    for url in post_urls:
        slug = url.split('/p/')[-1]
        if slug not in existing_slugs:
            new_urls.append(url)

    return new_urls

def write_new_urls_file(urls):
    """Write new URLs to a temporary file for the scraper"""
    with open('new_articles_urls.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
    print(f"✓ Wrote {len(urls)} URLs to new_articles_urls.txt")

if __name__ == "__main__":
    new_urls = get_new_article_urls()

    if not new_urls:
        print("No new articles found!")
        sys.exit(0)

    print(f"Found {len(new_urls)} new articles:")
    for url in new_urls:
        print(f"  - {url}")

    write_new_urls_file(new_urls)

    print(f"\nTo download these, run:")
    print(f"  python download_specific_urls.py")
