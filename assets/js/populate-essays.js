// State management
let sortLikesAscending = false;
let sortDatesAscending = false;
let showHTML = true;
let hideSponsored = false;
let hideCourseAds = false;
let searchQuery = '';
let selectedTags = [];
let originalData = [];
let currentSort = null;

// Check if essay is sponsored
function isSponsored(essay) {
    // Use the is_sponsored flag if available, otherwise check title/subtitle
    if (essay.hasOwnProperty('is_sponsored')) {
        return essay.is_sponsored;
    }
    return essay.title.toLowerCase().includes('sponsored') ||
           essay.subtitle.toLowerCase().includes('sponsored');
}

// Check if essay is a course ad
function isCourseAd(essay) {
    if (essay.hasOwnProperty('is_course_ad')) {
        return essay.is_course_ad;
    }
    return false;
}

// Filter and search essays
function filterEssays(data) {
    let filtered = [...data];

    // Apply sponsored filter
    if (hideSponsored) {
        filtered = filtered.filter(essay => !isSponsored(essay));
    }

    // Apply course ads filter
    if (hideCourseAds) {
        filtered = filtered.filter(essay => !isCourseAd(essay));
    }

    // Apply tag filter (must have ALL selected tags)
    if (selectedTags.length > 0) {
        filtered = filtered.filter(essay => {
            const essayTags = essay.tags || [];
            return selectedTags.every(tag => essayTags.includes(tag));
        });
    }

    // Apply search filter
    if (searchQuery) {
        const query = searchQuery.toLowerCase();
        filtered = filtered.filter(essay =>
            essay.title.toLowerCase().includes(query) ||
            essay.subtitle.toLowerCase().includes(query)
        );
    }

    return filtered;
}

// Sort essays by date
function sortEssaysByDate(data) {
    sortDatesAscending = !sortDatesAscending;
    currentSort = 'date';
    return data.sort((a, b) => sortDatesAscending
        ? new Date(a.date) - new Date(b.date)
        : new Date(b.date) - new Date(a.date));
}

// Sort essays by likes
function sortEssaysByLikes(data) {
    sortLikesAscending = !sortLikesAscending;
    currentSort = 'likes';
    return data.sort((a, b) => sortLikesAscending
        ? a.like_count - b.like_count
        : b.like_count - a.like_count);
}

// Get all unique tags with counts
function getAllTagsWithCounts() {
    const tagCounts = {};
    originalData.forEach(essay => {
        const tags = essay.tags || [];
        tags.forEach(tag => {
            tagCounts[tag] = (tagCounts[tag] || 0) + 1;
        });
    });
    return tagCounts;
}

// Create tag filter buttons
function createTagButtons() {
    const tagCounts = getAllTagsWithCounts();
    const tagButtonsContainer = document.getElementById('tag-buttons');

    // Sort tags by count (descending)
    const sortedTags = Object.entries(tagCounts).sort((a, b) => b[1] - a[1]);

    // Create buttons
    sortedTags.forEach(([tag, count]) => {
        const button = document.createElement('button');
        button.textContent = `${tag} (${count})`;
        button.dataset.tag = tag;
        button.addEventListener('click', () => toggleTag(tag, button));
        tagButtonsContainer.appendChild(button);
    });
}

// Toggle tag selection
function toggleTag(tag, button) {
    const index = selectedTags.indexOf(tag);
    if (index > -1) {
        selectedTags.splice(index, 1);
        button.classList.remove('active');
    } else {
        selectedTags.push(tag);
        button.classList.add('active');
    }
    refreshDisplay();
}

// Update stats display
function updateStats(filtered, total) {
    // Update main counts
    document.getElementById('showing-count').textContent = filtered;
    document.getElementById('total-count').textContent = total;

    // Count different types in original dataset
    const totalSponsored = originalData.filter(essay => isSponsored(essay)).length;
    const totalCourseAds = originalData.filter(essay => isCourseAd(essay)).length;
    const totalRegular = total - totalSponsored - totalCourseAds;

    // Update type breakdown
    const sponsoredCountEl = document.getElementById('sponsored-count');
    sponsoredCountEl.textContent = `${totalSponsored} sponsored • ${totalCourseAds} course ads • ${totalRegular} regular`;

    // Update filter status
    const filterStatusEl = document.getElementById('filter-status');
    const statusParts = [];

    if (hideSponsored) {
        statusParts.push('Sponsored hidden');
    }
    if (hideCourseAds) {
        statusParts.push('Course ads hidden');
    }
    if (selectedTags.length > 0) {
        statusParts.push(`Tags: ${selectedTags.join(', ')}`);
    }
    if (searchQuery) {
        statusParts.push(`Searching: "${searchQuery}"`);
    }

    if (statusParts.length > 0) {
        filterStatusEl.textContent = statusParts.join(' • ');
        filterStatusEl.style.display = 'inline';
    } else {
        filterStatusEl.style.display = 'none';
    }
}

// Populate essays list
function populateEssays(data) {
    const essaysContainer = document.getElementById('essays-container');
    const filtered = filterEssays(data);

    if (filtered.length === 0) {
        essaysContainer.innerHTML = '<div style="text-align: center; padding: 40px; color: #888;">No articles found matching your filters.</div>';
        updateStats(0, originalData.length);
        return;
    }

    const list = filtered.map(essay => {
        let badges = '';
        if (isSponsored(essay)) {
            badges += '<span style="background: #ff6b6b; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 10px;">SPONSORED</span>';
        }
        if (isCourseAd(essay)) {
            badges += '<span style="background: #ffa500; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 10px;">COURSE AD</span>';
        }

        // Add topic tags
        const tags = essay.tags || [];
        const tagBadges = tags.map(tag =>
            `<span style="background: #e9ecef; color: #495057; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 4px;">${tag}</span>`
        ).join('');

        return `
            <li>
                <a href="#" class="article-link" data-html-link="${essay.html_link}" data-md-link="${essay.file_link}">
                    ${essay.title}${badges}
                </a>
                <div class="subtitle">${essay.subtitle}</div>
                <div class="metadata">
                    ${essay.like_count} Likes - ${essay.date}
                    ${tagBadges ? '<br><div style="margin-top: 8px;">' + tagBadges + '</div>' : ''}
                </div>
            </li>
        `;
    }).join('');

    essaysContainer.innerHTML = `<ul>${list}</ul>`;
    updateStats(filtered.length, originalData.length);

    // Add click handlers to article links
    document.querySelectorAll('.article-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const articlePath = showHTML ? link.dataset.htmlLink : link.dataset.mdLink;
            loadArticle(articlePath);
        });
    });
}

// Refresh display with current filters and sort
function refreshDisplay() {
    let data = [...originalData];

    // Reapply current sort if any
    if (currentSort === 'date') {
        data.sort((a, b) => sortDatesAscending
            ? new Date(a.date) - new Date(b.date)
            : new Date(b.date) - new Date(a.date));
    } else if (currentSort === 'likes') {
        data.sort((a, b) => sortLikesAscending
            ? a.like_count - b.like_count
            : b.like_count - a.like_count);
    }

    populateEssays(data);
}

// Navigation functions
function showListView() {
    document.getElementById('list-view').style.display = 'block';
    document.getElementById('article-view').style.display = 'none';
    document.getElementById('controls').style.display = 'block';
    window.scrollTo(0, 0);
}

function showArticleView() {
    document.getElementById('list-view').style.display = 'none';
    document.getElementById('article-view').style.display = 'block';
    document.getElementById('controls').style.display = 'none';
    window.scrollTo(0, 0);
}

async function loadArticle(articlePath) {
    try {
        // Strip the 'substack_html_pages/' or 'substack_md_files/' prefix from path
        // Since blog.html is in substack_html_pages/, we need relative path from there
        const relativePath = articlePath.replace('substack_html_pages/', '').replace('substack_md_files/', '../substack_md_files/');

        const response = await fetch(relativePath);
        if (!response.ok) {
            throw new Error(`Failed to load article: ${response.status}`);
        }
        const htmlContent = await response.text();

        // Check if this is a markdown file
        if (articlePath.endsWith('.md')) {
            // For markdown files, display as preformatted text
            document.getElementById('article-content').innerHTML = `<pre style="white-space: pre-wrap; word-wrap: break-word;">${htmlContent}</pre>`;
        } else {
            // Extract the content from the fetched HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlContent, 'text/html');
            const content = doc.querySelector('.markdown-content') || doc.querySelector('main') || doc.body;

            document.getElementById('article-content').innerHTML = content.innerHTML;
        }
        showArticleView();
    } catch (error) {
        console.error('Error loading article:', error);
        document.getElementById('article-content').innerHTML = `
            <div style="padding: 20px; text-align: center;">
                <p style="color: red; font-size: 18px; margin-bottom: 10px;">⚠️ Error loading article</p>
                <p style="color: #666;">${error.message}</p>
                <p style="color: #999; margin-top: 10px;">Try refreshing the page or selecting a different article.</p>
            </div>
        `;
        showArticleView();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const embeddedDataElement = document.getElementById('essaysData');
    originalData = JSON.parse(embeddedDataElement.textContent);

    // Toggle format (HTML/Markdown)
    const toggleButton = document.getElementById('toggle-format');
    if (toggleButton) {
        toggleButton.addEventListener('click', () => {
            showHTML = !showHTML;
            toggleButton.textContent = showHTML ? 'Show Markdown' : 'Show HTML';
            refreshDisplay();
        });
    } else {
        showHTML = false;
    }

    // Toggle sponsored filter
    document.getElementById('toggle-sponsored').addEventListener('click', (e) => {
        hideSponsored = !hideSponsored;
        e.target.textContent = hideSponsored ? 'Show Sponsored' : 'Hide Sponsored';
        e.target.classList.toggle('active');
        refreshDisplay();
    });

    // Toggle course ads filter
    document.getElementById('toggle-course-ads').addEventListener('click', (e) => {
        hideCourseAds = !hideCourseAds;
        e.target.textContent = hideCourseAds ? 'Show Course Ads' : 'Hide Course Ads';
        e.target.classList.toggle('active');
        refreshDisplay();
    });

    // Search functionality
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        refreshDisplay();
    });

    document.getElementById('clear-search').addEventListener('click', () => {
        searchInput.value = '';
        searchQuery = '';
        refreshDisplay();
    });

    // Sort buttons
    document.getElementById('sort-by-date').addEventListener('click', () => {
        let data = sortEssaysByDate([...originalData]);
        populateEssays(data);
    });

    document.getElementById('sort-by-likes').addEventListener('click', () => {
        let data = sortEssaysByLikes([...originalData]);
        populateEssays(data);
    });

    document.getElementById('reset-sort').addEventListener('click', () => {
        currentSort = null;
        sortLikesAscending = false;
        sortDatesAscending = false;
        refreshDisplay();
    });

    // Clear all tag filters
    document.getElementById('clear-tags').addEventListener('click', () => {
        selectedTags = [];
        document.querySelectorAll('#tag-buttons button').forEach(btn => {
            btn.classList.remove('active');
        });
        refreshDisplay();
    });

    // Back button
    document.getElementById('back-button').addEventListener('click', () => {
        showListView();
    });

    // Create tag buttons and initial population
    createTagButtons();

    // Sort by date (newest first) by default
    currentSort = 'date';
    sortDatesAscending = false;
    const sortedData = [...originalData].sort((a, b) => new Date(b.date) - new Date(a.date));
    populateEssays(sortedData);
});
