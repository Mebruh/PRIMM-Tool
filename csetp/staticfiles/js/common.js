/**
 * Common Utilities for PRIMM SQL Learning Tool
 * Provides shared functionality across all PRIMM exercise pages.
 */

// ============================================================================
// CSRF Token Management
// ============================================================================

/**
 * Get CSRF token from cookies for Django POST requests.
 * @returns {string} CSRF token value
 */
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.substring('csrftoken='.length);
        }
    }
    return '';
}


// ============================================================================
// API Request Functions
// ============================================================================

/**
 * Make a GET request to fetch query results.
 * @param {string} url - API endpoint URL
 * @returns {Promise} Promise resolving to JSON response
 */
async function fetchQueryResults(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}


/**
 * Make a POST request with user's SQL query.
 * @param {string} url - API endpoint URL
 * @param {string} query - User's SQL query
 * @returns {Promise} Promise resolving to JSON response
 */
async function submitQuery(url, query) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ query: query })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Submit error:', error);
        throw error;
    }
}


// ============================================================================
// Result Formatting Functions
// ============================================================================

/**
 * Format query results as an HTML table.
 * @param {Array} results - Array of result objects
 * @param {Array} excludeColumns - Column names to exclude from display
 * @returns {string} HTML table string
 */
function formatQueryResultsAsTable(results, excludeColumns = []) {
    if (!results || results.length === 0) {
        return '<p class="text-muted">No results found.</p>';
    }
    
    const columns = Object.keys(results[0]).filter(col => !excludeColumns.includes(col));
    
    let table = '<table class="table table-bordered table-striped mt-3"><thead class="table-light"><tr>';
    
    // Generate column headers
    columns.forEach(col => {
        const headerName = col.replace(/_/g, ' ').toUpperCase();
        table += `<th>${headerName}</th>`;
    });
    
    table += '</tr></thead><tbody>';
    
    // Generate table rows
    results.forEach(row => {
        table += '<tr>';
        columns.forEach(col => {
            table += `<td>${row[col] !== null ? row[col] : ''}</td>`;
        });
        table += '</tr>';
    });
    
    table += '</tbody></table>';
    return table;
}


/**
 * Format a single aggregate value (COUNT, SUM, etc.).
 * @param {number} value - Aggregate value to display
 * @returns {string} Formatted HTML string
 */
function formatAggregateValue(value) {
    return `<div class="alert alert-info"><strong>Result:</strong> ${value}</div>`;
}


// ============================================================================
// UI Helper Functions
// ============================================================================

/**
 * Show an element by changing its display style.
 * @param {string} elementId - ID of element to show
 * @param {string} displayStyle - CSS display value (default: 'block')
 */
function showElement(elementId, displayStyle = 'block') {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = displayStyle;
    }
}


/**
 * Hide an element by setting display to 'none'.
 * @param {string} elementId - ID of element to hide
 */
function hideElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
}


/**
 * Enable or disable a button.
 * @param {string} buttonId - ID of button element
 * @param {boolean} enabled - Whether button should be enabled
 */
function setButtonEnabled(buttonId, enabled) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = !enabled;
    }
}


/**
 * Display feedback message with appropriate styling.
 * @param {string} elementId - ID of element to display feedback in
 * @param {string} message - Feedback message
 * @param {string} type - Type of feedback ('success', 'error', 'warning')
 */
function displayFeedback(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const classMap = {
        'success': 'text-success',
        'error': 'text-danger',
        'warning': 'text-warning',
        'info': 'text-info'
    };
    
    element.innerHTML = `<p class="${classMap[type] || 'text-info'}">${message}</p>`;
}


/**
 * Show a success alert modal and redirect after confirmation.
 * @param {string} message - Success message to display
 */
function showSuccessModal() {
    // Show Bootstrap modal
    const modalElement = document.getElementById('successModal');
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    }
}

/**
 * Legacy function - now just shows modal instead of redirecting.
 * @param {string} message - Success message (ignored)
 * @param {string} redirectUrl - Redirect URL (ignored - modal has links instead)
 */
function showSuccessAndRedirect(message, redirectUrl) {
    showSuccessModal();
}


// ============================================================================
// Form Validation
// ============================================================================

/**
 * Check if all inputs in a form are filled.
 * @param {string} formId - ID of form element
 * @returns {boolean} True if all inputs have values
 */
function areAllInputsFilled(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[type="text"], textarea');
    return Array.from(inputs).every(input => input.value.trim() !== '');
}


/**
 * Get selected radio button value.
 * @param {string} name - Name attribute of radio button group
 * @returns {string|null} Value of selected radio button or null
 */
function getSelectedRadioValue(name) {
    const selected = document.querySelector(`input[name="${name}"]:checked`);
    return selected ? selected.value : null;
}


/**
 * Get value from textarea element.
 * @param {string} elementId - ID of textarea element
 * @returns {string} Textarea value
 */
function getTextareaValue(elementId) {
    const element = document.getElementById(elementId);
    return element ? element.value : '';
}


// ============================================================================
// Section Navigation
// ============================================================================

/**
 * Show the next section in the PRIMM workflow.
 * @param {string} sectionId - ID of section to show
 */
/**
 * Show the next section in the PRIMM workflow.
 * @param {string} currentSectionId - ID of current section to hide
 * @param {string} nextSectionId - ID of next section to show
 */
function showNextSection(currentSectionId, nextSectionId) {
    showElement(nextSectionId);
    
    // Smooth scroll to the next section
    const section = document.getElementById(nextSectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}
