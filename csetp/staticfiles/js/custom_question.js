// ============================================================================
// Section 1: Predict and Run
// ============================================================================

// Each function takes apiBase, the URL prefix for the question set's
// endpoints, e.g. "/api/custom-question/5/" or "/api/question-set/primm4/".

function runCustomPredictQuery(apiBase, correctAnswer) {
    const selectedValue = getSelectedRadioValue('prediction');
    
    if (!selectedValue) {
        alert("Please select an answer first!");
        return;
    }
    
    fetch(`${apiBase}run-predict/`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showElement('query-output');
                document.getElementById('result-display').innerHTML = '';
                displayFeedback('answer-feedback', data.error, 'error');
                return;
            }

            const resultHtml = formatQueryResultsAsTable(data.result);
            document.getElementById('result-display').innerHTML = resultHtml;
            
            showElement('query-output');
            
            if (selectedValue === String(correctAnswer)) {
                displayFeedback('answer-feedback', '✅ Correct! Well done.', 'success');
                showElement('next-section-btn', 'inline-block');
            } else {
                displayFeedback('answer-feedback', '❌ Incorrect. Have a look at the result again.', 'error');
            }
        })
        .catch(error => {
            displayFeedback('answer-feedback', `Error: ${error.message}`, 'error');
        });
}


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

document.addEventListener('input', function(event) {
    if (event.target.closest('#investigate-form')) {
        const allFilled = areAllInputsFilled('investigate-form');
        setButtonEnabled('submit-investigate', allFilled);
    }
});


function submitInvestigateAnswers() {
    document.getElementById('user-answer1').textContent = 
        document.getElementById('question1').value;
    document.getElementById('user-answer2').textContent = 
        document.getElementById('question2').value;
    document.getElementById('user-answer3').textContent = 
        document.getElementById('question3').value;
    
    hideElement('investigate-form');
    showElement('investigate-results');
    showElement('next-section-btn-2', 'inline-block');
}


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

function runCustomModifyQuery(apiBase) {
    const userQuery = getTextareaValue('modify-query');
    
    submitQuery(`${apiBase}run-modify/`, userQuery)
        .then(data => {
            showElement('modify-query-output');
            
            if (data.error) {
                document.getElementById('modify-result-display').innerHTML = '';
                displayFeedback('modify-feedback', data.error, 'error');
            } else {
                const resultHtml = formatQueryResultsAsTable(data.result);
                document.getElementById('modify-result-display').innerHTML = resultHtml;
                
                if (data.correct) {
                    displayFeedback('modify-feedback', '✅ Correct! Well done.', 'success');
                    showElement('next-section-btn-3', 'inline-block');
                } else {
                    displayFeedback('modify-feedback', '❌ Incorrect. Try modifying the query again.', 'error');
                }
            }
        })
        .catch(error => {
            showElement('modify-query-output');
            displayFeedback('modify-feedback', `Error: ${error.message}`, 'error');
        });
}


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

function runCustomMakeQuery(apiBase) {
    const userQuery = getTextareaValue('make-query');
    
    submitQuery(`${apiBase}run-make/`, userQuery)
        .then(data => {
            showElement('make-query-output');
            
            if (data.error) {
                displayFeedback('make-feedback', data.error, 'error');
            } else if (data.correct) {
                hideElement('make-query-output');
                showSuccessModal();
            } else {
                const message = data.hint
                    ? `⚠️ Incorrect. Hint: ${data.hint}`
                    : '⚠️ Incorrect. Try again!';
                displayFeedback('make-feedback', message, 'warning');
            }
        })
        .catch(error => {
            showElement('make-query-output');
            displayFeedback('make-feedback', `Error: ${error.message}`, 'error');
        });
}