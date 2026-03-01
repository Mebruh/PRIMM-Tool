
// ============================================================================
// Section 1: Predict and Run
// ============================================================================

function runCustomPredictQuery(questionSetId, correctAnswer) {
    const selectedValue = getSelectedRadioValue('prediction');
    
    if (!selectedValue) {
        alert("Please select an answer first!");
        return;
    }
    
    fetch(`/api/custom-question/${questionSetId}/run-predict/`)
        .then(response => response.json())
        .then(data => {
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

function runCustomModifyQuery(questionSetId) {
    const userQuery = getTextareaValue('modify-query');
    
    submitQuery(`/api/custom-question/${questionSetId}/run-modify/`, userQuery)
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

function runCustomMakeQuery(questionSetId) {
    const userQuery = getTextareaValue('make-query');
    
    submitQuery(`/api/custom-question/${questionSetId}/run-make/`, userQuery)
        .then(data => {
            showElement('make-query-output');
            
            if (data.error) {
                displayFeedback('make-feedback', data.error, 'error');
            } else if (data.correct) {
                hideElement('make-query-output');
                showSuccessModal();
            } else {
                displayFeedback('make-feedback', `⚠️ Incorrect. Try again!`, 'warning');
            }
        })
        .catch(error => {
            showElement('make-query-output');
            displayFeedback('make-feedback', `Error: ${error.message}`, 'error');
        });
}