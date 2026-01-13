#!/usr/bin/env python3
"""
Fix articles with Jan 11, 2026 dates by extracting from markdown content
"""
import json
import re

def extract_date_from_markdown(md_filepath):
    """Extract date from markdown file"""
    try:
        with open(md_filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

            # Look for date in first 10 lines
            for line in lines[:10]:
                line = line.strip()

                # Pattern: **Month DD, YYYY**
                if line.startswith('**') and any(month in line for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                    date = line.strip('*').strip()
                    return date

    except Exception as e:
        print(f"Error reading {md_filepath}: {e}")
        return None

def fix_jan_11_dates():
    """Fix articles with Jan 11, 2026 dates"""

    # Load JSON
    with open('data/blog.json', 'r') as f:
        essays = json.load(f)

    fixed_count = 0

    print(f"Checking {len(essays)} articles...\n")

    for essay in essays:
        if essay['date'] == 'Jan 11, 2026':
            md_filepath = essay['file_link']
            extracted_date = extract_date_from_markdown(md_filepath)

            if extracted_date and extracted_date != 'Jan 11, 2026':
                old_date = essay['date']
                essay['date'] = extracted_date
                fixed_count += 1
                print(f"✓ Fixed: {essay['title'][:60]}")
                print(f"  Changed: {old_date} → {extracted_date}\n")

    # Write back
    with open('data/blog.json', 'w') as f:
        json.dump(essays, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Fixed {fixed_count} articles with Jan 11, 2026 dates")

    # Check remaining
    remaining = sum(1 for e in essays if e['date'] == 'Jan 11, 2026')
    if remaining > 0:
        print(f"⚠️  {remaining} articles still have Jan 11, 2026")
    else:
        print(f"✓ All dates are now correct!")

if __name__ == "__main__":
    fix_jan_11_dates()
