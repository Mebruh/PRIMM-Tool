/**
 * PRIMM1 Exercise JavaScript
 * Handles all interactions for PRIMM Question Set 1 (Basic SELECT queries)
 */

// ============================================================================
// Section 1: Predict and Run
// ============================================================================

/**
 * Run the predefined SQL query and check user's prediction.
 * @param {string} runQueryUrl - URL endpoint to execute the query
 */
function runPredictQuery(runQueryUrl) {
    const CORRECT_ANSWER = "2";
    const selectedValue = getSelectedRadioValue('prediction');
    
    if (!selectedValue) {
        alert("Please select an answer first!");
        return;
    }
    
    fetchQueryResults(runQueryUrl)
        .then(data => {
            // Display query results
            const resultHtml = formatQueryResultsAsTable(data.result);
            document.getElementById('result-display').innerHTML = resultHtml;
            
            showElement('query-output');
            
            // Check if prediction was correct
            if (selectedValue === CORRECT_ANSWER) {
                displayFeedback('answer-feedback', '✅ Correct! Well done.', 'success');
                showElement('next-section-btn', 'inline-block');
            } else {
                displayFeedback('answer-feedback', '❌ Incorrect. Have a look at the condition again', 'error');
            }
        })
        .catch(error => {
            displayFeedback('answer-feedback', `Error: ${error.message}`, 'error');
        });
}


/**
 * Navigate to the Investigate section.
 */
function showInvestigateSection() {
    showElement('section-2');
    const section = document.getElementById('section-2');
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}


// ============================================================================
// Section 2: Investigate
// ============================================================================

/**
 * Enable submit button when all investigation questions are answered.
 */
function enableInvestigateSubmit() {
    document.addEventListener('input', function(event) {
        if (event.target.closest('#investigate-form')) {
            const allFilled = areAllInputsFilled('investigate-form');
            setButtonEnabled('submit-investigate', allFilled);
        }
    });
}


/**
 * Submit investigation answers and show correct answers.
 */
function submitInvestigateAnswers() {
    // Display user's answers
    document.getElementById('user-answer1').textContent = 
        document.getElementById('question1').value;
    document.getElementById('user-answer2').textContent = 
        document.getElementById('question2').value;
    document.getElementById('user-answer3').textContent = 
        document.getElementById('question3').value;
    
    // Hide form and show results
    hideElement('investigate-form');
    showElement('investigate-results');
    showElement('next-section-btn-2', 'inline-block');
}


/**
 * Navigate to the Modify section.
 */
function showModifySection() {
    showElement('section-3');
    const section = document.getElementById('section-3');
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}


// ============================================================================
// Section 3: Modify
// ============================================================================

/**
 * Run user's modified query and validate the result.
 * @param {string} modifyQueryUrl - URL endpoint to submit modified query
 */
function runModifiedQuery(modifyQueryUrl) {
    const userQuery = getTextareaValue('modify-query');
    
    submitQuery(modifyQueryUrl, userQuery)
        .then(data => {
            const resultContainer = document.getElementById('modify-result-display');
            
            if (data.error) {
                resultContainer.innerHTML = `<p class='text-danger'>${data.error}</p>`;
            } else {
                // Exclude job_title column from display
                const resultHtml = formatQueryResultsAsTable(data.result, ['job_title']);
                resultContainer.innerHTML = resultHtml;
            }
            
            showElement('modify-query-output');
            
            if (data.correct) {
                displayFeedback('modify-feedback', '✅ Correct! Well done.', 'success');
                showElement('next-section-btn-3', 'inline-block');
            } else {
                displayFeedback('modify-feedback', '❌ Incorrect. Try modifying the query again.', 'error');
            }
        })
        .catch(error => {
            displayFeedback('modify-feedback', `Error: ${error.message}`, 'error');
        });
}


/**
 * Navigate to the Make section.
 */
function showMakeSection() {
    showElement('section-4');
    const section = document.getElementById('section-4');
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}


// ============================================================================
// Section 4: Make
// ============================================================================

/**
 * Run user's custom query and provide feedback.
 * @param {string} makeQueryUrl - URL endpoint to submit custom query
 * @param {string} homeUrl - URL to redirect to on success
 */
function runMakeQuery(makeQueryUrl, homeUrl) {
    const userQuery = getTextareaValue('make-query');
    
    submitQuery(makeQueryUrl, userQuery)
        .then(data => {
            showElement('make-query-output');
            
            if (data.error) {
                displayFeedback('make-feedback', `❌ Error: ${data.error}`, 'error');
            } else if (data.correct) {
                showSuccessModal();
            } else {
                displayFeedback('make-feedback', `⚠️ Hint: ${data.hint}`, 'warning');
            }
        })
        .catch(error => {
            displayFeedback('make-feedback', `Error: ${error.message}`, 'error');
        });
}


// ============================================================================
// Initialization
// ============================================================================

/**
 * Initialize event listeners when DOM is loaded.
 */
document.addEventListener('DOMContentLoaded', function() {
    enableInvestigateSubmit();
});
