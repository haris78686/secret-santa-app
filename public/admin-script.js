
const passInput = document.getElementById('admin-pass');
const msg = document.getElementById('admin-msg');
const listContainer = document.getElementById('name-list-container');
const historyList = document.getElementById('history-list');

// Load names on start
fetchNames();

async function fetchNames() {
    try {
        const res = await fetch('/api/master-list');
        const names = await res.json();
        renderList(names);
    } catch(e) { console.error(e); }
}

function renderList(names) {
    listContainer.innerHTML = '';
    names.forEach(name => {
        const div = document.createElement('div');
        div.className = 'name-item';
        div.innerHTML = `<span>${name}</span> <button class="del-btn" onclick="removeName('${name}')">X</button>`;
        listContainer.appendChild(div);
    });
}

document.getElementById('add-btn').addEventListener('click', async () => {
    const name = document.getElementById('new-name').value;
    const password = passInput.value;
    if(!name || !password) return alert("Password and Name required");

    const res = await fetch('/api/add-name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, password })
    });
    const data = await res.json();
    if(data.success) {
        document.getElementById('new-name').value = '';
        renderList(data.list);
    } else {
        alert(data.error || "Error");
    }
});

window.removeName = async (name) => {
    const password = passInput.value;
    if(!password) return alert("Please enter password first.");
    if(!confirm(`Delete ${name}?`)) return;

    const res = await fetch('/api/remove-name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, password })
    });
    const data = await res.json();
    if(data.success) renderList(data.list);
    else alert(data.error);
};

// --- UPDATED HISTORY LOGIC ---
document.getElementById('view-history-btn').addEventListener('click', async () => {
    const password = passInput.value;
    if(!password) return alert("Password required to see secrets!");

    const res = await fetch('/api/admin/assignments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
    });
    const data = await res.json();

    if(data.success) {
        historyList.style.display = 'block';
        historyList.innerHTML = '';
        
        if(data.assignments.length === 0) {
            historyList.innerHTML = '<div style="padding:10px; color:#bdc3c7;">No names drawn yet.</div>';
            return;
        }

        data.assignments.forEach(entry => {
            const div = document.createElement('div');
            div.className = 'history-item';
            
            // USE NAME IF AVAILABLE, OTHERWISE FALLBACK TO EMAIL
            const displayName = entry.pickerName || entry.picker;
            
            div.innerHTML = `<span>${displayName}</span> <span class="history-arrow">➔</span> <span>${entry.picked}</span>`;
            historyList.appendChild(div);
        });
    } else {
        alert(data.message);
    }
});

document.getElementById('reset-btn').addEventListener('click', async () => {
    const password = passInput.value;
    if(!password) return alert("Password required");
    if(!confirm("Are you sure? This deletes the history logs too!")) return;

    const res = await fetch('/api/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
    });
    const data = await res.json();
    msg.innerText = data.message;
    msg.style.color = data.success ? '#2ecc71' : '#e74c3c';
    
    // Clear history view if open
    historyList.innerHTML = '';
});
