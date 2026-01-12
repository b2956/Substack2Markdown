#!/usr/bin/env python3
"""
Script to update existing JSON data with is_sponsored flags by scanning markdown files.
"""
import json
import os

def check_if_sponsored(md_filepath):
    """Check if a markdown file contains sponsored content"""
    try:
        with open(md_filepath, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            return "sponsored)" in content or "(sponsored)" in content
    except:
        return False

def update_json_with_sponsored_flags(json_path):
    """Update JSON file with is_sponsored flags"""
    print(f"Reading {json_path}...")

    with open(json_path, 'r', encoding='utf-8') as f:
        essays = json.load(f)

    print(f"Found {len(essays)} essays")
    sponsored_count = 0

    for essay in essays:
        md_file = essay['file_link']
        is_sponsored = check_if_sponsored(md_file)
        essay['is_sponsored'] = is_sponsored
        if is_sponsored:
            sponsored_count += 1

    print(f"Detected {sponsored_count} sponsored posts")

    # Write back to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(essays, f, ensure_ascii=False, indent=4)

    print(f"✓ Updated {json_path}")
    return sponsored_count

if __name__ == "__main__":
    json_path = "data/blog.json"
    sponsored_count = update_json_with_sponsored_flags(json_path)
    print(f"\nSummary: {sponsored_count} sponsored posts out of total")
