import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Load credentials from environment variables (recommended) or fallback to defaults
EMAIL = os.getenv("SUBSTACK_EMAIL", "your-email@domain.com")
PASSWORD = os.getenv("SUBSTACK_PASSWORD", "your-password")

# Load author information from environment variables
AUTHOR_NAME = os.getenv("SUBSTACK_AUTHOR_NAME", "Author Name")
BLOG_TITLE = os.getenv("SUBSTACK_BLOG_TITLE", "Technical Articles")
