#!/usr/bin/env python3
"""
Script to fix untitled articles and mark course advertisements.
"""
import json
import os
import re

def extract_title_from_markdown(md_filepath):
    """Extract the first H1 title from a markdown file"""
    try:
        with open(md_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Look for markdown H1 header
                if line.startswith('# ') and len(line) > 2:
                    title = line[2:].strip()
                    # Skip if it looks like just metadata
                    if title and title.lower() not in ['untitled', 'title']:
                        return title
    except:
        pass
    return None

def extract_title_from_filename(filepath):
    """Extract title from filename as fallback"""
    filename = os.path.basename(filepath)
    # Remove .md extension
    name = filename.replace('.md', '')
    # Replace hyphens with spaces
    name = name.replace('-', ' ')
    # Capitalize words
    words = name.split()
    # Capitalize first letter of each word, except small words
    small_words = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
    title_words = []
    for i, word in enumerate(words):
        if i == 0 or word.lower() not in small_words:
            title_words.append(word.capitalize())
        else:
            title_words.append(word.lower())
    return ' '.join(title_words)

def is_course_ad(essay):
    """Check if an article is a course advertisement"""
    title_lower = essay['title'].lower()
    patterns = [
        'become an ai engineer',
        'last chance to enroll',
        'last call: enrollment',
        'cohort-based course',
        'cohort 2',
        'cohort 3',
    ]

    # Check if title contains promotional language + cohort
    has_promotion = any(p in title_lower for p in ['last chance', 'last call', 'new launch', '🚀'])
    has_cohort = 'cohort' in title_lower or 'enroll' in title_lower

    # It's an ad if it has both promotional language and cohort mentions
    # OR if it exactly matches known patterns
    if has_promotion and has_cohort:
        return True

    for pattern in patterns:
        if pattern in title_lower:
            return True

    return False

def fix_json_data(json_path):
    """Fix untitled articles and mark course ads"""
    print(f"Reading {json_path}...")

    with open(json_path, 'r', encoding='utf-8') as f:
        essays = json.load(f)

    print(f"Found {len(essays)} essays")

    untitled_count = 0
    fixed_count = 0
    course_ad_count = 0

    for essay in essays:
        # Fix untitled articles
        if essay['title'] == 'Untitled':
            untitled_count += 1
            md_file = essay['file_link']

            # Try to extract from markdown first
            new_title = extract_title_from_markdown(md_file)

            # Fallback to filename
            if not new_title:
                new_title = extract_title_from_filename(md_file)

            if new_title:
                essay['title'] = new_title
                fixed_count += 1
                print(f"  Fixed: {new_title}")

        # Mark course advertisements
        if is_course_ad(essay):
            essay['is_course_ad'] = True
            course_ad_count += 1
            if not essay.get('is_sponsored'):  # Don't double-count
                print(f"  Course ad: {essay['title']}")
        else:
            essay['is_course_ad'] = False

    # Write back to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(essays, f, ensure_ascii=False, indent=4)

    print(f"\n✓ Updated {json_path}")
    print(f"\nSummary:")
    print(f"  - Untitled articles found: {untitled_count}")
    print(f"  - Titles fixed: {fixed_count}")
    print(f"  - Course ads marked: {course_ad_count}")

    return fixed_count, course_ad_count

if __name__ == "__main__":
    json_path = "data/blog.json"
    fix_json_data(json_path)
