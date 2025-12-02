document.getElementById('reset-btn').addEventListener('click', async () => {
    const password = document.getElementById('admin-pass').value;
    const msg = document.getElementById('admin-msg');
    if(!password) return;
    try {
        const res = await fetch('/api/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });
        const data = await res.json();
        msg.innerText = data.message;
        msg.style.color = data.success ? '#2ecc71' : '#e74c3c';
    } catch(e) { msg.innerText = "Error connecting to server."; }
});