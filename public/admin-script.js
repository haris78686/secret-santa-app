
const passInput = document.getElementById('admin-pass');
const msg = document.getElementById('admin-msg');
const listContainer = document.getElementById('name-list-container');

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

// Add Name
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

// Remove Name
window.removeName = async (name) => {
    const password = passInput.value;
    if(!password) return alert("Please enter password at the top first.");
    
    if(!confirm(`Delete ${name}?`)) return;

    const res = await fetch('/api/remove-name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, password })
    });
    const data = await res.json();
    if(data.success) {
        renderList(data.list);
    } else {
        alert(data.error);
    }
};

// Reset Game
document.getElementById('reset-btn').addEventListener('click', async () => {
    const password = passInput.value;
    if(!password) return alert("Password required");

    const res = await fetch('/api/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
    });
    const data = await res.json();
    msg.innerText = data.message;
    msg.style.color = data.success ? '#2ecc71' : '#e74c3c';
});
