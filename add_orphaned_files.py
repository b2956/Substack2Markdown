#!/usr/bin/env python3
"""
Add markdown files that exist on disk but aren't in the JSON database
"""
import json
import os
import glob
import re
from datetime import datetime

def read_markdown_metadata(md_filepath):
    """Extract metadata from markdown file"""
    try:
        with open(md_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

            # Extract title (first H1)
            title = "Untitled"
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break

            # Extract date
            date = "Date not found"
            for line in lines[:20]:
                if line.startswith('**') and any(month in line for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                    date = line.strip('*').strip()
                    break

            # Extract likes
            like_count = "0"
            for line in lines[:30]:
                if 'Likes:' in line:
                    match = re.search(r'Likes:\s*(\d+)', line)
                    if match:
                        like_count = match.group(1)
                    break

            # Check if sponsored
            is_sponsored = "sponsored)" in content.lower() or "(sponsored)" in content.lower()

            # Check if course ad
            is_course_ad_check = any(p in title.lower() for p in [
                'become an ai engineer',
                'last chance to enroll',
                'cohort-based course',
                'cohort 2',
                'cohort 3'
            ])

            return {
                'title': title,
                'subtitle': '',
                'date': date,
                'like_count': like_count,
                'is_sponsored': is_sponsored,
                'is_course_ad': is_course_ad_check,
                'content_preview': content[:500]
            }
    except Exception as e:
        print(f"Error reading {md_filepath}: {e}")
        return None

def extract_tags_from_content(title, content_preview):
    """Extract tags based on title and content"""
    TAG_PATTERNS = {
        'system-design': ['system design', 'architecture', 'scalability', 'distributed', 'microservices', 'pattern', 'architectural'],
        'databases': ['database', 'sql', 'nosql', 'mongodb', 'postgres', 'redis', 'debugging'],
        'backend': ['backend', 'api', 'rest', 'graphql', 'server'],
        'cloud': ['aws', 'azure', 'gcp', 'cloud', 's3', 'lambda', 'kubernetes', 'docker', 'load balancer'],
        'ai-ml': ['ai', 'machine learning', 'ml', 'llm', 'gpt', 'neural', 'model', 'evals', 'clip', 'tensor', 'tpu'],
        'devops': ['devops', 'ci/cd', 'deployment'],
        'networking': ['network', 'http', 'tcp', 'cdn', 'dns', 'protocol'],
        'security': ['security', 'authentication', 'oauth', 'jwt'],
        'performance': ['performance', 'optimization', 'caching'],
        'frontend': ['frontend', 'react', 'vue', 'ui'],
        'data': ['data', 'analytics', 'pipeline', 'kafka', 'message broker', 'replication', 'storage'],
        'mobile': ['mobile', 'ios', 'android'],
        'interview': ['interview', 'cheat sheet'],
        'case-study': [],
    }

    text = f"{title} {content_preview}".lower()
    tags = []

    # Case study detection
    case_study_patterns = [
        r'\bhow\s+\w+\s+(built|scaled|handles|transformed|uses)',
        r'\b(google|openai|anthropic)\b'
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

def add_orphaned_files():
    """Add files that exist on disk but not in JSON"""

    # Load existing JSON
    with open('data/blog.json', 'r') as f:
        essays = json.load(f)

    # Get existing file paths
    existing_paths = {essay['file_link'] for essay in essays}

    # Find all markdown files
    all_md_files = glob.glob('substack_md_files/blog/*.md')

    orphaned = []
    for md_file in all_md_files:
        if md_file not in existing_paths:
            orphaned.append(md_file)

    if not orphaned:
        print("✓ No orphaned files found!")
        return

    print(f"Found {len(orphaned)} orphaned files:\n")

    added = []
    for md_file in orphaned:
        print(f"Processing: {md_file}")

        # Extract metadata
        metadata = read_markdown_metadata(md_file)
        if not metadata:
            continue

        # Extract tags
        tags = extract_tags_from_content(metadata['title'], metadata['content_preview'])

        # Create HTML path
        html_file = md_file.replace('substack_md_files', 'substack_html_pages').replace('.md', '.html')

        # Create entry
        entry = {
            'title': metadata['title'],
            'subtitle': metadata['subtitle'],
            'like_count': metadata['like_count'],
            'date': metadata['date'],
            'file_link': md_file,
            'html_link': html_file,
            'is_sponsored': metadata['is_sponsored'],
            'is_course_ad': metadata['is_course_ad'],
            'tags': tags
        }

        essays.append(entry)
        added.append(entry)

        print(f"  ✓ Added: {metadata['title']}")
        print(f"    Tags: {', '.join(tags)}")
        print(f"    Sponsored: {metadata['is_sponsored']}")
        print()

    # Write back
    with open('data/blog.json', 'w') as f:
        json.dump(essays, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Added {len(added)} orphaned files to database")
    print(f"Total articles now: {len(essays)}")

    return added

if __name__ == "__main__":
    add_orphaned_files()
