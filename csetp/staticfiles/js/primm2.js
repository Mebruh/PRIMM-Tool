/**
 * PRIMM2 Exercise JavaScript
 * Handles all interactions for PRIMM Question Set 2 (Aggregate Functions)
 */

// ============================================================================
// Section 1: Predict and Run
// ============================================================================

/**
 * Run the predefined aggregate query and check user's prediction.
 * @param {string} runQueryUrl - URL endpoint to execute the query
 */
function runPredictQueryAggregate(runQueryUrl) {
    const CORRECT_ANSWER = "2";
    const selectedValue = getSelectedRadioValue('prediction');
    
    if (!selectedValue) {
        alert("Please select an answer first!");
        return;
    }
    
    fetchQueryResults(runQueryUrl)
        .then(data => {
            // Display aggregate result
            const resultHtml = formatAggregateValue(data.result);
            document.getElementById('result-display').innerHTML = resultHtml;
            
            showElement('query-output');
            
            // Check if prediction was correct
            if (selectedValue === CORRECT_ANSWER) {
                displayFeedback('answer-feedback', '✅ Correct! Well done.', 'success');
                showElement('next-section-btn', 'inline-block');
            } else {
                displayFeedback(
                    'answer-feedback',
                    '❌ Incorrect. Think about what COUNT() does. Have a look at the number and then look at the database. Do you see a link?',
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
 * Run user's modified aggregate query and validate the result.
 * @param {string} modifyQueryUrl - URL endpoint to submit modified query
 */
function runModifiedQueryAggregate(modifyQueryUrl) {
    const userQuery = getTextareaValue('modify-query');
    
    submitQuery(modifyQueryUrl, userQuery)
        .then(data => {
            const resultContainer = document.getElementById('modify-result-display');
            
            if (data.error) {
                resultContainer.innerHTML = `<p class='text-danger'>❌ Error: ${data.error}</p>`;
            } else {
                resultContainer.innerHTML = formatAggregateValue(data.result);
            }
            
            showElement('modify-query-output');
            
            if (data.correct) {
                displayFeedback('modify-feedback', '✅ Correct! Well done.', 'success');
                showElement('next-section-btn-3', 'inline-block');
            } else {
                displayFeedback(
                    'modify-feedback',
                    "❌ Incorrect. Make sure you're filtering by job title 'Data Scientist'.",
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
 * Run user's custom aggregate query and provide feedback.
 * @param {string} makeQueryUrl - URL endpoint to submit custom query
 * @param {string} homeUrl - URL to redirect to on success
 */
function runMakeQueryAggregate(makeQueryUrl, homeUrl) {
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
