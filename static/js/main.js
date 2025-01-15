function showLoading() {
    document.getElementById('loading').classList.remove('d-none');
}

function hideLoading() {
    document.getElementById('loading').classList.add('d-none');
}

function askQuestion() {
    const question = document.getElementById('question-input').value.trim();
    
    if (!question) return;
    
    showLoading();
    
    fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Display response
        document.getElementById('response-container').innerHTML = `
            <div class="response-text">${data.response}</div>
        `;
        
        // Display sources
        const sourcesHtml = data.sources.map((source, index) => `
            <div class="source-item">
                <strong>Source ${index + 1}:</strong><br>
                Content: ${source.content}<br>
                Source: ${source.source}<br>
                Page: ${source.page}
            </div>
        `).join('');
        
        document.getElementById('sources-container').innerHTML = sourcesHtml;
        
        // Display stats
        document.getElementById('stats-container').innerHTML = `
            <div class="stats-item">
                Prompt Tokens: ${data.tokens.prompt_tokens}<br>
                Completion Tokens: ${data.tokens.completion_tokens}<br>
                Total Tokens: ${data.tokens.total_tokens}<br>
                Cost: $${data.cost.toFixed(4)}
            </div>
        `;
    })
    .catch(error => {
        document.getElementById('response-container').innerHTML = `
            <div class="alert alert-danger">${error.message}</div>
        `;
    })
    .finally(() => {
        hideLoading();
    });
}

function switchMode(mode) {
    showLoading();
    
    fetch('/switch-mode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mode: mode })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        alert(`Error switching mode: ${error.message}`);
    })
    .finally(() => {
        hideLoading();
    });
}

// Add event listener for Enter key
document.getElementById('question-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        askQuestion();
    }
});