#!/usr/bin/env python3
"""
Add topic tags to articles based on their titles and content.
"""
import json
import sys
import os

# Common technology tags to look for
TAG_PATTERNS = {
    'system-design': ['system design', 'architecture', 'scalability', 'distributed', 'microservices'],
    'databases': ['database', 'sql', 'nosql', 'mongodb', 'postgres', 'redis', 'cassandra', 'mysql', 'oracle', 'sharding', 'transaction'],
    'backend': ['backend', 'api', 'rest', 'graphql', 'server', 'endpoint'],
    'cloud': ['aws', 'azure', 'gcp', 'cloud', 's3', 'lambda', 'kubernetes', 'docker', 'container'],
    'ai-ml': ['ai', 'machine learning', 'ml', 'llm', 'gpt', 'neural', 'model', 'claude', 'openai', 'anthropic', 'gemini', 'agent'],
    'devops': ['devops', 'ci/cd', 'deployment', 'jenkins', 'github actions', 'terraform', 'ansible'],
    'networking': ['network', 'http', 'tcp', 'cdn', 'dns', 'load balancer', 'proxy', 'websocket'],
    'security': ['security', 'authentication', 'oauth', 'jwt', 'encryption', 'ssl', 'tls', 'auth'],
    'performance': ['performance', 'optimization', 'caching', 'cache', 'scaling', 'latency', 'throughput'],
    'frontend': ['frontend', 'react', 'vue', 'angular', 'ui', 'ux', 'javascript', 'css'],
    'data': ['data', 'analytics', 'etl', 'pipeline', 'kafka', 'spark', 'stream'],
    'mobile': ['mobile', 'ios', 'android', 'app'],
    'interview': ['interview', 'interview question', 'coding pattern'],
    'case-study': ['how', 'migration', 'built', 'scaled', 'netflix', 'uber', 'google', 'amazon', 'meta', 'twitter'],
}

def extract_tags(title, subtitle, content_preview):
    """Extract relevant tags from article metadata"""
    text = f"{title} {subtitle} {content_preview}".lower()
    tags = []

    for tag, patterns in TAG_PATTERNS.items():
        if any(pattern in text for pattern in patterns):
            tags.append(tag)

    # Limit to top 5 most relevant tags
    return tags[:5] if tags else ['general']

def read_content_preview(md_filepath, max_chars=500):
    """Read first 500 chars of markdown file"""
    try:
        with open(md_filepath, 'r', encoding='utf-8') as f:
            content = f.read(max_chars)
            return content
    except:
        return ""

def process_batch(start_idx, end_idx, json_path):
    """Process a batch of articles and add tags"""
    print(f"Processing articles {start_idx} to {end_idx}...")

    with open(json_path, 'r', encoding='utf-8') as f:
        essays = json.load(f)

    processed = 0
    for i in range(start_idx, min(end_idx, len(essays))):
        essay = essays[i]

        # Skip if already has tags
        if 'tags' in essay and essay['tags']:
            continue

        # Read content preview
        content_preview = read_content_preview(essay['file_link'])

        # Extract tags
        tags = extract_tags(essay['title'], essay.get('subtitle', ''), content_preview)
        essay['tags'] = tags
        processed += 1

    # Write back
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(essays, f, ensure_ascii=False, indent=4)

    print(f"✓ Processed {processed} articles (batch {start_idx}-{end_idx})")
    return processed

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python add_tags_batch.py <start_idx> <end_idx>")
        sys.exit(1)

    start = int(sys.argv[1])
    end = int(sys.argv[2])
    json_path = "data/blog.json"

    processed = process_batch(start, end, json_path)
    print(f"Done! Tagged {processed} articles.")
