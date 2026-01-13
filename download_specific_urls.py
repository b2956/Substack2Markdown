#!/usr/bin/env python3
"""
Download specific URLs from a file
"""
import sys
from substack_scraper import PremiumSubstackScraper, SubstackScraper, generate_html_file
from tqdm import tqdm
import os

def download_urls_from_file(url_file, use_premium=True, browser='chrome'):
    """Download articles from a list of URLs"""

    # Read URLs
    with open(url_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("No URLs found in file!")
        return

    print(f"Downloading {len(urls)} articles...")

    # Use first URL to determine base URL
    base_url = '/'.join(urls[0].split('/')[:3]) + '/'
    print(f"Base URL: {base_url}")

    # Create scraper
    if use_premium:
        scraper = PremiumSubstackScraper(
            base_url,
            md_save_dir="substack_md_files",
            html_save_dir="substack_html_pages",
            browser=browser,
            headless=False
        )
    else:
        scraper = SubstackScraper(
            base_url,
            md_save_dir="substack_md_files",
            html_save_dir="substack_html_pages"
        )

    # Override post_urls with our specific URLs
    scraper.post_urls = urls

    # Download
    scraper.scrape_posts(num_posts_to_scrape=0)  # 0 means all

    print(f"\n✓ Downloaded {len(urls)} new articles!")
    print(f"✓ Updated blog.html interface")

if __name__ == "__main__":
    url_file = 'new_articles_urls.txt'

    if not os.path.exists(url_file):
        print(f"Error: {url_file} not found!")
        print("Run download_new_articles.py first to generate the URL list.")
        sys.exit(1)

    # You can toggle premium/browser here
    download_urls_from_file(url_file, use_premium=True, browser='chrome')
