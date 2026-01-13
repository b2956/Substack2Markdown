# Substack2Markdown

Substack2Markdown is a Python tool for downloading free and premium Substack posts and saving them as both Markdown and 
HTML files, and includes a simple HTML interface to browse and sort through the posts. It will save paid for content as 
long as you're subscribed to that substack. 

🆕 @Firevvork has built a web version of this tool at [Substack Reader](https://www.substacktools.com/reader) - no 
installation required! (Works for free Substacks only.)


![Substack2Markdown Interface](./assets/images/screenshot.png)

Once you run the script, it will create a folder named after the substack in `/substack_md_files`,
and then begin to scrape the substack URL, converting the blog posts into markdown files. Once all the posts have been
saved, it will generate an HTML file in `/substack_html_pages` directory that allows you to browse the posts.

You can either hardcode the substack URL and the number of posts you'd like to save into the top of the file, or 
specify them as command line arguments.

## Features

### Core Features
- Converts Substack posts into Markdown and HTML files
- Supports free and premium content (with subscription)
- Multi-browser support: Chrome, Firefox, and Edge
- Environment variable support for secure credential storage

### Enhanced HTML Interface
- **Smart Filtering**: Hide sponsored content, course advertisements, or filter by topic tags
- **Topic Tags**: 15 categories including system-design, databases, cloud, ai-ml, and more
- **Real-time Search**: Find articles by title or subtitle instantly
- **Advanced Stats**: See exactly how many articles match your filters
- **Sort Options**: Sort by date or likes (ascending/descending)
- **Format Toggle**: Switch between Markdown and HTML views
- **Responsive Design**: Modern, mobile-friendly interface with smooth animations

## Installation

Clone the repo and install the dependencies:

```bash
git clone https://github.com/yourusername/substack_scraper.git
cd substack_scraper

# # Optinally create a virtual environment
# python -m venv venv
# # Activate the virtual environment
# .\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux

pip install -r requirements.txt
```

For the premium scraper, set your Substack credentials as environment variables (recommended for security).

**Option 1: Using a .env file (easiest)**

Copy the example file and edit it:
```bash
cp .env.example .env
# Edit .env with your credentials (this file is gitignored)
```

Required variables in `.env`:
- `SUBSTACK_EMAIL` - Your Substack account email
- `SUBSTACK_PASSWORD` - Your Substack account password
- `SUBSTACK_BLOG_URL` - Your Substack blog URL (e.g., https://your-blog.substack.com)
- `SUBSTACK_AUTHOR_NAME` - Author name to display in the HTML interface
- `SUBSTACK_BLOG_TITLE` - Blog title/subtitle to display in the HTML interface

The `.env` file is automatically loaded when you run the scraper.

**Option 2: Set environment variables directly**

```bash
# Linux/Mac
export SUBSTACK_EMAIL="your-email@domain.com"
export SUBSTACK_PASSWORD="your-password"
export SUBSTACK_AUTHOR_NAME="Your Name"
export SUBSTACK_BLOG_TITLE="Your Blog Title"

# Windows (PowerShell)
$env:SUBSTACK_EMAIL="your-email@domain.com"
$env:SUBSTACK_PASSWORD="your-password"
$env:SUBSTACK_AUTHOR_NAME="Your Name"
$env:SUBSTACK_BLOG_TITLE="Your Blog Title"

# Windows (Command Prompt)
set SUBSTACK_EMAIL=your-email@domain.com
set SUBSTACK_PASSWORD=your-password
set SUBSTACK_AUTHOR_NAME=Your Name
set SUBSTACK_BLOG_TITLE=Your Blog Title
```

**Option 3: Edit config.py directly (not recommended)**

Alternatively, you can edit `config.py` in the root directory (not recommended as it may expose credentials):

```python
EMAIL = "your-email@domain.com"
PASSWORD = "your-password"
```

You'll need a browser installed for Selenium automation:
- **Edge** (default) - Microsoft Edge
- **Chrome** - Google Chrome
- **Firefox** - Mozilla Firefox

## Usage

Specify the Substack URL and the directory to save the posts to:

You can hardcode your desired Substack URL and the number of posts you'd like to save into the top of the file and run:
```bash
python substack_scraper.py
```

For free Substack sites:

```bash
python substack_scraper.py --url https://example.substack.com --directory /path/to/save/posts
```

For premium Substack sites:

```bash
python substack_scraper.py --url https://example.substack.com --directory /path/to/save/posts --premium
```

To use a specific browser (Chrome, Firefox, or Edge):

```bash
# Using Chrome
python substack_scraper.py --url https://example.substack.com --premium --browser chrome

# Using Firefox
python substack_scraper.py --url https://example.substack.com --premium --browser firefox

# Using Edge (default)
python substack_scraper.py --url https://example.substack.com --premium --browser edge
```

To run in headless mode (no browser window):

```bash
python substack_scraper.py --url https://example.substack.com --premium --headless
```

To scrape a specific number of posts:

```bash
python substack_scraper.py --url https://example.substack.com --directory /path/to/save/posts --number 5
```

### Online Version

For a hassle-free experience without any local setup:

1. Visit [Substack Reader](https://www.substacktools.com/reader)
2. Enter the Substack URL you want to read or export
3. Click "Go" to instantly view the content or "Export" to download Markdown files

This online version provides a user-friendly web interface for reading and exporting free Substack articles, with no installation required. However, please note that the online version currently does not support exporting premium content. For full functionality, including premium content export, please use the local script as described above. Built by @Firevvork. 

## Using the Enhanced HTML Interface

After scraping, you need to run a local web server to view the interface with full functionality (including single-page article navigation):

```bash
# Start the local web server
python3 serve.py
```

This will:
- Start a web server on `http://localhost:8000`
- Automatically open the interface in your browser
- Enable all features including in-page article viewing

**Why use a server?** Modern browsers block local file access for security (CORS policy), which prevents article navigation from working when opening HTML files directly.

**Tip**: Press `Ctrl+C` to stop the server when done.

### Interface Features

#### 🔄 Single-Page Navigation
- **Click to read**: Click any article to view it in the same page
- **Back button**: Instantly return to your filtered article list
- **Preserved state**: Your search, filters, and scroll position are maintained
- **Smooth transitions**: Seamless navigation between list and article views

#### 📊 Smart Statistics
- **Live counters**: Shows "X / Y articles" with real-time updates as you filter
- **Content breakdown**: See counts for sponsored, course ads, and regular articles
- **Active filters display**: Know exactly which filters are applied

#### 🔍 Search & Filter
- **Text Search**: Type in the search box to find articles by title/subtitle
- **Content Filters**:
  - Hide Sponsored: Remove sponsored articles (351 articles)
  - Hide Course Ads: Remove promotional course content (7 articles)
- **Topic Tags**: Filter by 15 categories with article counts:
  ```
  system-design (264)    case-study (236)     networking (215)
  backend (178)          databases (170)      ai-ml (143)
  cloud (135)            frontend (129)       performance (127)
  data (126)             mobile (91)          security (77)
  interview (66)         devops (59)          general (81)
  ```
- **Multi-tag filtering**: Select multiple tags to find articles with ALL selected topics

#### 🎯 Use Cases
```bash
# Find all Kubernetes articles
→ Click "cloud" tag

# System design case studies only
→ Click "system-design" + "case-study"

# Pure technical content (no ads)
→ Click "Hide Sponsored" + "Hide Course Ads"

# AI/ML backend articles
→ Click "ai-ml" + "backend"

# Search for specific topics
→ Type "load balancer" in search box
```

#### 📱 Additional Features
- **Sort Options**: By date or likes (click again to reverse)
- **Format Toggle**: Switch between viewing HTML and Markdown files
- **Tag Badges**: Each article shows its topic tags
- **Clear Buttons**: Quick reset for search, tags, and sort options

### Alternative Viewing Methods

To read the Markdown files directly in your browser, install the [Markdown Viewer](https://chromewebstore.google.com/detail/markdown-viewer/ckkdlimhmcjmikdlpkmbgfkaikojcbjk) browser extension.

Or use the [Substack Reader](https://www.substacktools.com/reader) online tool for free Substack articles (premium content requires the local script).
