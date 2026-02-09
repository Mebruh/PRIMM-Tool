/**
 * PRIMM3 Exercise JavaScript
 * Handles all interactions for PRIMM Question Set 3 (JOIN Queries)
 */

// ============================================================================
// Section 1: Predict and Run
// ============================================================================

/**
 * Run the predefined JOIN query and check user's prediction.
 * @param {string} runQueryUrl - URL endpoint to execute the query
 */
function runPredictQueryJoin(runQueryUrl) {
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
                displayFeedback(
                    'answer-feedback',
                    '❌ Incorrect. Think about what INNER JOIN does. It combines rows from two tables where there is a match.',
                    'error'
                );
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
    showNextSection('section-2');
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
    showNextSection('section-3');
}


// ============================================================================
// Section 3: Modify
// ============================================================================

/**
 * Run user's modified JOIN query and validate the result.
 * @param {string} modifyQueryUrl - URL endpoint to submit modified query
 */
function runModifiedQueryJoin(modifyQueryUrl) {
    const userQuery = getTextareaValue('modify-query');
    
    submitQuery(modifyQueryUrl, userQuery)
        .then(data => {
            const resultContainer = document.getElementById('modify-result-display');
            
            if (data.error) {
                resultContainer.innerHTML = `<p class='text-danger'>${data.error}</p>`;
            } else {
                const resultHtml = formatQueryResultsAsTable(data.result);
                resultContainer.innerHTML = resultHtml;
            }
            
            showElement('modify-query-output');
            
            if (data.correct) {
                displayFeedback('modify-feedback', '✅ Correct! Well done.', 'success');
                showElement('next-section-btn-3', 'inline-block');
            } else {
                displayFeedback(
                    'modify-feedback',
                    "❌ Incorrect. Make sure you're filtering projects that started after 2023-01-01.",
                    'error'
                );
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
    showNextSection('section-4');
}


// ============================================================================
// Section 4: Make
// ============================================================================

/**
 * Run user's custom JOIN query (LEFT JOIN for employees without projects).
 * @param {string} makeQueryUrl - URL endpoint to submit custom query
 * @param {string} homeUrl - URL to redirect to on success
 */
function runMakeQueryJoin(makeQueryUrl, homeUrl) {
    const userQuery = getTextareaValue('make-query');
    
    submitQuery(makeQueryUrl, userQuery)
        .then(data => {
            showElement('make-query-output');
            
            if (data.error) {
                displayFeedback('make-feedback', `❌ Error: ${data.error}`, 'error');
            } else if (data.correct) {
                showSuccessAndRedirect(
                    '✅ Well done! You wrote the correct SQL query.',
                    homeUrl
                );
            } else {
                const hint = data.hint || "Try using LEFT JOIN and check for NULL values in the projects table.";
                displayFeedback('make-feedback', `⚠️ Hint: ${hint}`, 'warning');
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
