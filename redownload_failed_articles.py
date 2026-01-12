#!/usr/bin/env python3
"""
Re-download articles that failed to scrape properly
"""
import os
import glob
from substack_scraper import PremiumSubstackScraper, generate_html_file

def find_failed_articles():
    """Find articles with 'Date not found' in their markdown content"""
    failed_files = []

    # Find all markdown files
    md_files = glob.glob('substack_md_files/blog/*.md')

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check if the actual content has "Date not found"
                if '**Date not found**' in content and content.count('\n') < 20:
                    failed_files.append(md_file)
        except:
            continue

    return failed_files

def get_urls_from_files(failed_files):
    """Convert file paths to URLs"""
    urls = []
    base_url = "https://blog.bytebytego.com/p/"

    for filepath in failed_files:
        # Extract slug from filename
        slug = os.path.basename(filepath).replace('.md', '')
        url = base_url + slug
        urls.append(url)

    return urls

def main():
    print("🔍 Finding articles that failed to scrape...\n")

    failed_files = find_failed_articles()

    if not failed_files:
        print("✓ No failed articles found!")
        return

    print(f"Found {len(failed_files)} articles that need re-downloading:\n")

    urls = get_urls_from_files(failed_files)

    for url in urls:
        print(f"  - {url}")

    print(f"\n⚙️  Re-downloading with premium scraper (Chrome)...\n")

    # Create scraper
    scraper = PremiumSubstackScraper(
        "https://blog.bytebytego.com/",
        md_save_dir="substack_md_files",
        html_save_dir="substack_html_pages",
        browser='chrome',
        headless=False
    )

    # Override URLs to only download failed ones
    scraper.post_urls = urls

    # Download
    scraper.scrape_posts(num_posts_to_scrape=0)

    print(f"\n🎨 Regenerating HTML interface...\n")
    generate_html_file('blog')

    print(f"\n✅ Re-download complete!")
    print(f"   - Fixed {len(urls)} articles")
    print(f"\n💡 Run fix_dates.py again to update the JSON with correct dates")

if __name__ == "__main__":
    main()
