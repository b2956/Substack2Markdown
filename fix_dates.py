#!/usr/bin/env python3
"""
Fix articles with 'Date not found' by extracting dates from their markdown files
"""
import json
import os
import re
from datetime import datetime

def extract_date_from_markdown(md_filepath):
    """Extract date from markdown file"""
    try:
        with open(md_filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

            # Look for date in first 20 lines
            for i, line in enumerate(lines[:20]):
                line = line.strip()

                # Pattern 1: **Month DD, YYYY**
                if line.startswith('**') and any(month in line for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                    date = line.strip('*').strip()
                    return date

                # Pattern 2: Month DD, YYYY (without asterisks)
                date_pattern = r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}\b'
                match = re.search(date_pattern, line)
                if match:
                    return match.group(0)

            # Fallback: Try to get modification time from file metadata
            mod_time = os.path.getmtime(md_filepath)
            date_obj = datetime.fromtimestamp(mod_time)
            return date_obj.strftime("%b %d, %Y")

    except Exception as e:
        print(f"Error reading {md_filepath}: {e}")
        return None

def fix_dates():
    """Update JSON with dates extracted from markdown files"""

    # Load JSON
    with open('data/blog.json', 'r') as f:
        essays = json.load(f)

    fixed_count = 0
    fallback_count = 0

    print(f"Checking {len(essays)} articles...\n")

    for essay in essays:
        if essay['date'] == 'Date not found':
            md_filepath = essay['file_link']

            if not os.path.exists(md_filepath):
                print(f"⚠️  File not found: {md_filepath}")
                continue

            extracted_date = extract_date_from_markdown(md_filepath)

            if extracted_date and extracted_date != 'Date not found':
                essay['date'] = extracted_date
                fixed_count += 1

                # Check if this was from file metadata (fallback)
                if ',' in extracted_date and any(month in extracted_date for month in ['Jan', 'Feb', 'Mar']):
                    print(f"✓ Fixed: {essay['title'][:60]}")
                    print(f"  Date: {extracted_date}")
                else:
                    fallback_count += 1
                    print(f"⚠️  Used file metadata: {essay['title'][:60]}")
                    print(f"  Date: {extracted_date}")

    # Write back
    with open('data/blog.json', 'w') as f:
        json.dump(essays, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Fixed {fixed_count} articles")
    print(f"   - Extracted from content: {fixed_count - fallback_count}")
    print(f"   - Used file metadata: {fallback_count}")

    # Check remaining
    remaining = sum(1 for e in essays if e['date'] == 'Date not found')
    if remaining > 0:
        print(f"\n⚠️  {remaining} articles still have 'Date not found'")

    return fixed_count

if __name__ == "__main__":
    fix_dates()
