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
let currentArticle = null;

// Pagination state
let currentPage = 1;
let itemsPerPage = 50;
let totalPages = 1;

// Theme management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Initialize theme on page load
initTheme();

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

// Update visual state of tags in article list
function updateArticleTagsVisualState() {
    document.querySelectorAll('.tag-clickable').forEach(tagElement => {
        const tag = tagElement.dataset.tag;
        if (selectedTags.includes(tag)) {
            tagElement.classList.add('active');
        } else {
            tagElement.classList.remove('active');
        }
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
    currentPage = 1; // Reset to first page when filtering changes
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

// Update pagination controls
function updatePaginationControls(totalItems) {
    totalPages = Math.ceil(totalItems / itemsPerPage);

    // Update page info
    const start = totalItems === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1;
    const end = Math.min(currentPage * itemsPerPage, totalItems);
    document.getElementById('page-info').textContent = `Showing ${start}-${end} of ${totalItems}`;

    // Update current page display
    document.getElementById('current-page-display').textContent = `Page ${currentPage} of ${totalPages}`;

    // Update button states
    document.getElementById('first-page').disabled = currentPage === 1;
    document.getElementById('prev-page').disabled = currentPage === 1;
    document.getElementById('next-page').disabled = currentPage === totalPages || totalPages === 0;
    document.getElementById('last-page').disabled = currentPage === totalPages || totalPages === 0;
}

// Go to specific page
function goToPage(page) {
    currentPage = Math.max(1, Math.min(page, totalPages));
    refreshDisplay();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Populate essays list
function populateEssays(data) {
    const essaysContainer = document.getElementById('essays-container');
    const filtered = filterEssays(data);

    if (filtered.length === 0) {
        essaysContainer.innerHTML = '<div style="text-align: center; padding: 40px; color: #888;">No articles found matching your filters.</div>';
        updateStats(0, originalData.length);
        updatePaginationControls(0);
        return;
    }

    // Calculate pagination
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedData = filtered.slice(startIndex, endIndex);

    const list = paginatedData.map(essay => {
        let badges = '';
        if (isSponsored(essay)) {
            badges += '<span class="badge badge-sponsored">SPONSORED</span>';
        }
        if (isCourseAd(essay)) {
            badges += '<span class="badge badge-course">COURSE AD</span>';
        }

        // Add topic tags
        const tags = essay.tags || [];
        const tagBadges = tags.map(tag =>
            `<span class="badge badge-tag tag-clickable" data-tag="${tag}">${tag}</span>`
        ).join('');

        return `
            <li class="article-item" data-html-link="${essay.html_link}" data-md-link="${essay.file_link}">
                <div class="article-title-wrapper">
                    <span class="article-link">${essay.title}</span>
                    ${badges}
                </div>
                <div class="subtitle">${essay.subtitle}</div>
                <div class="metadata">
                    <div>${essay.like_count} Likes - ${essay.date}</div>
                    ${tagBadges ? '<div style="margin-top: 8px;">' + tagBadges + '</div>' : ''}
                </div>
            </li>
        `;
    }).join('');

    essaysContainer.innerHTML = `<ul>${list}</ul>`;
    updateStats(filtered.length, originalData.length);
    updatePaginationControls(filtered.length);

    // Add click handlers to tags for filtering (must be done first)
    document.querySelectorAll('.tag-clickable').forEach(tagElement => {
        tagElement.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent article click
            e.preventDefault();
            const tag = tagElement.dataset.tag;

            // Find the corresponding tag button in the filter section
            const tagButton = Array.from(document.querySelectorAll('#tag-buttons button'))
                .find(btn => btn.dataset.tag === tag);

            if (tagButton) {
                // Toggle tag selection
                toggleTag(tag, tagButton);
            }
        });
    });

    // Add click handlers to article items (entire row clickable except tags)
    document.querySelectorAll('.article-item').forEach(item => {
        // Click on title wrapper
        const titleWrapper = item.querySelector('.article-title-wrapper');
        if (titleWrapper) {
            titleWrapper.addEventListener('click', (e) => {
                if (e.target.classList.contains('tag-clickable') ||
                    e.target.classList.contains('badge-sponsored') ||
                    e.target.classList.contains('badge-course')) {
                    return;
                }
                const articlePath = showHTML ? item.dataset.htmlLink : item.dataset.mdLink;
                loadArticle(articlePath);
            });
        }

        // Click on subtitle
        const subtitle = item.querySelector('.subtitle');
        if (subtitle) {
            subtitle.addEventListener('click', (e) => {
                const articlePath = showHTML ? item.dataset.htmlLink : item.dataset.mdLink;
                loadArticle(articlePath);
            });
        }

        // Click on metadata (likes/date)
        const metadataFirst = item.querySelector('.metadata > div:first-child');
        if (metadataFirst) {
            metadataFirst.addEventListener('click', (e) => {
                const articlePath = showHTML ? item.dataset.htmlLink : item.dataset.mdLink;
                loadArticle(articlePath);
            });
        }
    });

    // Update visual state of tags based on current selection
    updateArticleTagsVisualState();
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

// Find related articles based on shared tags
function findRelatedArticles(currentArticle, maxResults = 5) {
    const currentTags = currentArticle.tags || [];
    if (currentTags.length === 0) {
        return [];
    }

    // Score each article by number of shared tags
    const scoredArticles = originalData
        .filter(essay => essay.file_link !== currentArticle.file_link) // Exclude current article
        .map(essay => {
            const essayTags = essay.tags || [];
            const sharedTags = currentTags.filter(tag => essayTags.includes(tag));
            return {
                essay,
                sharedTags: sharedTags,
                score: sharedTags.length
            };
        })
        .filter(item => item.score > 0) // Only include articles with at least one shared tag
        .sort((a, b) => {
            // Sort by score (descending), then by likes (descending)
            if (b.score !== a.score) {
                return b.score - a.score;
            }
            return b.essay.like_count - a.essay.like_count;
        });

    return scoredArticles.slice(0, maxResults);
}

// Display related articles
function displayRelatedArticles(currentArticle) {
    const relatedSection = document.getElementById('related-articles-section');
    const relatedList = document.getElementById('related-articles-list');

    const related = findRelatedArticles(currentArticle);

    if (related.length === 0) {
        relatedSection.style.display = 'none';
        return;
    }

    const relatedHTML = related.map(item => {
        const { essay, sharedTags } = item;
        const tagBadges = sharedTags.map(tag =>
            `<span class="badge badge-tag" style="background: var(--accent-primary); color: white; border-color: var(--accent-primary);">${tag}</span>`
        ).join('');

        return `
            <div class="related-article-item">
                <a href="#" class="related-article-link" data-html-link="${essay.html_link}" data-md-link="${essay.file_link}">
                    <strong>${essay.title}</strong>
                </a>
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: var(--space-xs);">
                    ${essay.subtitle}
                </div>
                <div style="margin-top: var(--space-sm);">
                    ${tagBadges}
                </div>
            </div>
        `;
    }).join('');

    relatedList.innerHTML = relatedHTML;
    relatedSection.style.display = 'block';

    // Add click handlers to related article links
    document.querySelectorAll('.related-article-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const articlePath = showHTML ? link.dataset.htmlLink : link.dataset.mdLink;
            loadArticle(articlePath);
        });
    });
}

async function loadArticle(articlePath) {
    try {
        // Find the current article in originalData
        currentArticle = originalData.find(essay =>
            (showHTML && essay.html_link === articlePath) ||
            (!showHTML && essay.file_link === articlePath)
        );

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

        // Display related articles
        if (currentArticle) {
            displayRelatedArticles(currentArticle);
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

    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }

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
        currentPage = 1;
        refreshDisplay();
    });

    // Toggle course ads filter
    document.getElementById('toggle-course-ads').addEventListener('click', (e) => {
        hideCourseAds = !hideCourseAds;
        e.target.textContent = hideCourseAds ? 'Show Course Ads' : 'Hide Course Ads';
        e.target.classList.toggle('active');
        currentPage = 1;
        refreshDisplay();
    });

    // Search functionality
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        currentPage = 1;
        refreshDisplay();
    });

    document.getElementById('clear-search').addEventListener('click', () => {
        searchInput.value = '';
        searchQuery = '';
        currentPage = 1;
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
        currentPage = 1;
        refreshDisplay();
    });

    // Back button
    document.getElementById('back-button').addEventListener('click', () => {
        showListView();
    });

    // Pagination controls
    document.getElementById('first-page').addEventListener('click', () => goToPage(1));
    document.getElementById('prev-page').addEventListener('click', () => goToPage(currentPage - 1));
    document.getElementById('next-page').addEventListener('click', () => goToPage(currentPage + 1));
    document.getElementById('last-page').addEventListener('click', () => goToPage(totalPages));

    // Items per page selector
    document.getElementById('items-per-page-select').addEventListener('change', (e) => {
        itemsPerPage = parseInt(e.target.value);
        currentPage = 1; // Reset to first page when changing items per page
        refreshDisplay();
    });

    // Create tag buttons and initial population
    createTagButtons();

    // Sort by date (newest first) by default
    currentSort = 'date';
    sortDatesAscending = false;
    const sortedData = [...originalData].sort((a, b) => new Date(b.date) - new Date(a.date));
    populateEssays(sortedData);
});
