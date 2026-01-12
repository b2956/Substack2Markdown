#!/usr/bin/env python3
"""
Remove duplicate entries from blog.json, keeping the best version of each article
"""
import json
from collections import defaultdict

def score_entry(entry):
    """Score an entry based on data completeness (higher is better)"""
    score = 0

    # Prefer entries with proper dates
    if entry.get('date') and entry['date'] != 'Date not found':
        score += 10
        # Penalize today's date (Jan 11, 2026) as it's likely from file metadata
        if 'Jan 11, 2026' not in entry['date']:
            score += 5

    # Prefer entries with proper titles
    if entry.get('title') and entry['title'] != 'Untitled':
        score += 10

    # Prefer entries with tags
    if entry.get('tags') and len(entry['tags']) > 0:
        score += 5

    # Prefer entries with like counts
    if entry.get('like_count') and entry['like_count'] != '0':
        score += 2

    # Prefer entries with subtitles
    if entry.get('subtitle'):
        score += 1

    # Check if sponsored/course_ad fields exist
    if 'is_sponsored' in entry:
        score += 1
    if 'is_course_ad' in entry:
        score += 1

    return score

def remove_duplicates():
    """Remove duplicate entries, keeping the best version"""

    # Load JSON
    with open('data/blog.json', 'r') as f:
        essays = json.load(f)

    print(f"Total entries before deduplication: {len(essays)}\n")

    # Group by file_link
    grouped = defaultdict(list)
    for essay in essays:
        file_link = essay.get('file_link', '')
        if file_link:
            grouped[file_link].append(essay)

    # Keep best version of each
    deduplicated = []
    duplicates_removed = 0

    for file_link, entries in grouped.items():
        if len(entries) > 1:
            # Multiple entries - keep the best one
            best_entry = max(entries, key=score_entry)
            duplicates_removed += len(entries) - 1

            print(f"Duplicate found: {file_link}")
            print(f"  Keeping: {best_entry.get('title', 'Untitled')[:60]} | {best_entry.get('date', 'No date')}")
            for entry in entries:
                if entry != best_entry:
                    print(f"  Removing: {entry.get('title', 'Untitled')[:60]} | {entry.get('date', 'No date')}")
            print()

            deduplicated.append(best_entry)
        else:
            # Single entry - keep it
            deduplicated.append(entries[0])

    # Write back
    with open('data/blog.json', 'w') as f:
        json.dump(deduplicated, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Deduplication complete!")
    print(f"   - Removed: {duplicates_removed} duplicate entries")
    print(f"   - Total entries after: {len(deduplicated)}")
    print(f"   - Unique articles: {len(grouped)}")

if __name__ == "__main__":
    remove_duplicates()
