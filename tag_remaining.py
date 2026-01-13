#!/usr/bin/env python3
"""
Tag remaining untagged articles
"""
import json
import re

TAG_PATTERNS = {
    'system-design': ['system design', 'architecture', 'scalability', 'distributed', 'microservices', 'pattern'],
    'databases': ['database', 'sql', 'nosql', 'mongodb', 'postgres', 'redis', 'cassandra', 'mysql', 'dynamo', 'sharding', 'transaction'],
    'backend': ['backend', 'api', 'rest', 'graphql', 'server', 'endpoint'],
    'cloud': ['aws', 'azure', 'gcp', 'cloud', 's3', 'lambda', 'kubernetes', 'docker', 'container', 'k8s'],
    'ai-ml': ['ai', 'machine learning', 'ml', 'llm', 'gpt', 'neural', 'model', 'claude', 'openai', 'anthropic', 'gemini', 'agent', 'rag'],
    'devops': ['devops', 'ci/cd', 'deployment', 'jenkins', 'github actions', 'terraform', 'ansible'],
    'networking': ['network', 'http', 'tcp', 'cdn', 'dns', 'load balancer', 'proxy', 'websocket', 'protocol'],
    'security': ['security', 'authentication', 'oauth', 'jwt', 'encryption', 'ssl', 'tls', 'auth', 'sso'],
    'performance': ['performance', 'optimization', 'caching', 'cache', 'scaling', 'latency', 'throughput', 'speed'],
    'frontend': ['frontend', 'react', 'vue', 'angular', 'ui', 'ux', 'javascript', 'css', 'web'],
    'data': ['data', 'analytics', 'etl', 'pipeline', 'kafka', 'spark', 'stream', 'processing'],
    'mobile': ['mobile', 'ios', 'android', 'app'],
    'interview': ['interview', 'coding pattern', 'leetcode', 'algorithm'],
    'case-study': [],  # Special handling
}

def extract_tags(title, subtitle):
    """Extract tags from title and subtitle"""
    text = f"{title} {subtitle}".lower()
    tags = []

    # Check for case studies
    case_study_patterns = [
        r'\bhow\s+\w+\s+(built|scaled|handles|manages|migrated|uses)',
        r'\b(netflix|uber|google|amazon|meta|facebook|twitter|airbnb|spotify|linkedin|dropbox|instagram|discord|reddit|slack|zoom|figma|stripe|shopify|paypal|tinder|doordash|lyft|pinterest|snap|tiktok|bytedance|grab|nubank|halo)\b'
    ]
    if any(re.search(pattern, text) for pattern in case_study_patterns):
        tags.append('case-study')

    # Check other tags
    for tag, patterns in TAG_PATTERNS.items():
        if tag == 'case-study':
            continue
        if any(pattern in text for pattern in patterns):
            tags.append(tag)

    # Limit to 5 tags
    return tags[:5] if tags else ['general']

def tag_remaining_articles():
    """Tag all untagged articles"""
    with open('data/blog.json', 'r') as f:
        essays = json.load(f)

    tagged_count = 0
    for essay in essays:
        if 'tags' not in essay or not essay['tags']:
            tags = extract_tags(essay['title'], essay.get('subtitle', ''))
            essay['tags'] = tags
            tagged_count += 1

    with open('data/blog.json', 'w') as f:
        json.dump(essays, f, ensure_ascii=False, indent=4)

    print(f"✓ Tagged {tagged_count} remaining articles")

    # Show tag distribution
    all_tags = {}
    for e in essays:
        for tag in e.get('tags', []):
            all_tags[tag] = all_tags.get(tag, 0) + 1

    print(f"\nFinal tag distribution:")
    for tag, count in sorted(all_tags.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tag}: {count}")

if __name__ == "__main__":
    tag_remaining_articles()
