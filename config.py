import os

# Load credentials from environment variables (recommended) or fallback to defaults
EMAIL = os.getenv("SUBSTACK_EMAIL", "your-email@domain.com")
PASSWORD = os.getenv("SUBSTACK_PASSWORD", "your-password")
