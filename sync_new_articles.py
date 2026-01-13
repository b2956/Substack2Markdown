#!/usr/bin/env python3
"""
Complete workflow to sync new articles:
1. Find new articles from sitemap
2. Download them
3. Classify (tags, sponsored, course ads)
4. Regenerate HTML interface
"""
import requests
from xml.etree import ElementTree as ET
import json
import os
import sys
from substack_scraper import PremiumSubstackScraper, generate_html_file
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import classification functions
def is_sponsored_content(md_filepath):
    """Check if markdown file contains sponsored content"""
    try:
        with open(md_filepath, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            return "sponsored)" in content or "(sponsored)" in content
    except:
        return False

def is_course_ad_title(title):
    """Check if title indicates course advertisement"""
    title_lower = title.lower()
    patterns = [
        'become an ai engineer',
        'last chance to enroll',
        'last call: enrollment',
        'cohort-based course',
    ]
    has_promotion = any(p in title_lower for p in ['last chance', 'last call', 'new launch', '🚀'])
    has_cohort = 'cohort' in title_lower or 'enroll' in title_lower
    return (has_promotion and has_cohort) or any(p in title_lower for p in patterns)

def extract_tags_from_title(title):
    """Extract relevant tags from article title"""
    TAG_PATTERNS = {
        'system-design': ['system design', 'architecture', 'scalability', 'distributed', 'microservices', 'pattern'],
        'databases': ['database', 'sql', 'nosql', 'mongodb', 'postgres', 'redis', 'cassandra', 'mysql', 'dynamo', 'sharding', 'transaction'],
        'backend': ['backend', 'api', 'rest', 'graphql', 'server', 'endpoint'],
        'cloud': ['aws', 'azure', 'gcp', 'cloud', 's3', 'lambda', 'kubernetes', 'docker', 'container', 'k8s'],
        'ai-ml': ['ai', 'machine learning', 'ml', 'llm', 'gpt', 'neural', 'model', 'claude', 'openai', 'anthropic', 'gemini', 'agent', 'rag', 'clip', 'tensor'],
        'devops': ['devops', 'ci/cd', 'deployment', 'jenkins', 'github actions', 'terraform', 'ansible'],
        'networking': ['network', 'http', 'tcp', 'cdn', 'dns', 'load balancer', 'proxy', 'websocket', 'protocol'],
        'security': ['security', 'authentication', 'oauth', 'jwt', 'encryption', 'ssl', 'tls', 'auth', 'sso'],
        'performance': ['performance', 'optimization', 'caching', 'cache', 'scaling', 'latency', 'throughput', 'speed'],
        'frontend': ['frontend', 'react', 'vue', 'angular', 'ui', 'ux', 'javascript', 'css', 'web'],
        'data': ['data', 'analytics', 'etl', 'pipeline', 'kafka', 'spark', 'stream', 'processing', 'message broker', 'replication'],
        'mobile': ['mobile', 'ios', 'android', 'app'],
        'interview': ['interview', 'coding pattern', 'leetcode', 'algorithm', 'cheat sheet'],
        'case-study': [],
    }

    text = title.lower()
    tags = []

    # Case study detection
    case_study_patterns = [
        r'\bhow\s+\w+\s+(built|scaled|handles|manages|migrated|uses|transformed|debugging)',
        r'\b(netflix|uber|google|amazon|meta|facebook|twitter|airbnb|spotify|linkedin|dropbox|instagram|discord|reddit|slack|zoom|figma|stripe|shopify|tinder|openai|anthropic)\b'
    ]
    if any(re.search(pattern, text) for pattern in case_study_patterns):
        tags.append('case-study')

    # Check other tags
    for tag, patterns in TAG_PATTERNS.items():
        if tag == 'case-study':
            continue
        if any(pattern in text for pattern in patterns):
            tags.append(tag)

    return tags[:5] if tags else ['general']

def get_new_articles():
    """Find articles not in our library"""
    blog_url = os.getenv('SUBSTACK_BLOG_URL')
    if not blog_url:
        print("❌ Error: SUBSTACK_BLOG_URL not set in .env file")
        print("Please add SUBSTACK_BLOG_URL=https://your-blog.substack.com to your .env file")
        sys.exit(1)

    # Fetch sitemap
    sitemap_url = f"{blog_url}/sitemap.xml"
    response = requests.get(sitemap_url)
    root = ET.fromstring(response.content)

    urls = [element.text for element in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    post_urls = [url for url in urls if '/p/' in url and not any(kw in url for kw in ['about', 'archive', 'podcast'])]

    # Load existing articles
    with open('data/blog.json', 'r') as f:
        essays = json.load(f)

    existing_slugs = {essay['file_link'].split('/')[-1].replace('.md', '') for essay in essays}

    # Find new URLs
    new_urls = []
    for url in post_urls:
        slug = url.split('/p/')[-1]
        if slug not in existing_slugs:
            new_urls.append(url)

    return new_urls, len(essays)

def classify_new_articles():
    """Add classification to newly downloaded articles"""
    with open('data/blog.json', 'r') as f:
        essays = json.load(f)

    classified_count = 0
    for essay in essays:
        # Skip already classified
        if 'tags' in essay and essay['tags']:
            continue

        # Check sponsored
        if 'is_sponsored' not in essay:
            essay['is_sponsored'] = is_sponsored_content(essay['file_link'])

        # Check course ad
        if 'is_course_ad' not in essay:
            essay['is_course_ad'] = is_course_ad_title(essay['title'])

        # Add tags
        if 'tags' not in essay or not essay['tags']:
            essay['tags'] = extract_tags_from_title(essay['title'])
            classified_count += 1

    # Write back
    with open('data/blog.json', 'w') as f:
        json.dump(essays, f, ensure_ascii=False, indent=4)

    return classified_count

def main():
    blog_url = os.getenv('SUBSTACK_BLOG_URL')
    if not blog_url:
        print("❌ Error: SUBSTACK_BLOG_URL not set in .env file")
        print("Please add SUBSTACK_BLOG_URL=https://your-blog.substack.com to your .env file")
        sys.exit(1)

    print("🔍 Checking for new articles...")
    new_urls, current_count = get_new_articles()

    if not new_urls:
        print("✓ No new articles found. Library is up to date!")
        return

    print(f"\n📥 Found {len(new_urls)} new articles:")
    for url in new_urls:
        print(f"   {url}")

    print(f"\n⚙️  Downloading with premium scraper (Chrome)...")

    # Create scraper
    scraper = PremiumSubstackScraper(
        f"{blog_url}/",
        md_save_dir="substack_md_files",
        html_save_dir="substack_html_pages",
        browser='chrome',
        headless=False
    )

    # Override URLs to only download new ones
    scraper.post_urls = new_urls

    # Download
    scraper.scrape_posts(num_posts_to_scrape=0)

    print(f"\n🏷️  Classifying new articles...")
    classified = classify_new_articles()

    print(f"\n🎨 Regenerating HTML interface...")
    generate_html_file('blog')

    print(f"\n✅ Sync complete!")
    print(f"   - Downloaded: {len(new_urls)} new articles")
    print(f"   - Classified: {classified} articles")
    print(f"   - Total library: {current_count + len(new_urls)} articles")
    print(f"\n💡 Open substack_html_pages/blog.html to view!")

if __name__ == "__main__":
    main()
