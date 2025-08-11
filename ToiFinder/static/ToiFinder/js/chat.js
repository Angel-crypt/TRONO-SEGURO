function sendQuery() {
    const query = document.getElementById('query').value;
    fetch('/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `query=${query}`
    })
        .then(response => response.json())
        .then(data => {
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML += `<p><strong>Tú:</strong> ${query}</p>`;
            chatBox.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
        });
}