import os

project_name = "." 

# 1. SERVER.JS (Now saves 'pickerName' in the history log)
server_js = """const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

const ADMIN_PASSWORD = "HoHoHo123";

let masterList = ["Alice", "Bob", "Charlie", "Diana", "Evan"];
let availableNames = [...masterList];
// assignments stores: { picker: email, pickerName: "Alice", picked: "Bob" }
let assignments = []; 

const RIGGED_MAP = { "RUDOLPH": "Charlie" };

// --- ROUTES ---

app.get('/api/master-list', (req, res) => res.json(masterList));

app.post('/api/admin/assignments', (req, res) => {
    const { password } = req.body;
    if (password === ADMIN_PASSWORD) {
        res.json({ success: true, assignments: assignments });
    } else {
        res.status(401).json({ success: false, message: "Invalid Password" });
    }
});

app.post('/api/check-user', (req, res) => {
    const { email } = req.body;
    if (!email) return res.status(400).json({ error: "Email required" });
    const match = assignments.find(a => a.picker.toLowerCase() === email.toLowerCase());
    if (match) return res.json({ hasPlayed: true, picked: match.picked });
    res.json({ hasPlayed: false });
});

app.post('/api/add-name', (req, res) => {
    const { name, password } = req.body;
    if (password !== ADMIN_PASSWORD) return res.status(401).json({error: "Wrong Password"});
    if (!name) return res.status(400).json({error: "Name required"});

    if (!masterList.includes(name)) {
        masterList.push(name);
        if (!availableNames.includes(name)) availableNames.push(name);
        return res.json({success: true, list: masterList});
    }
    res.json({success: false, message: "Name already exists"});
});

app.post('/api/remove-name', (req, res) => {
    const { name, password } = req.body;
    if (password !== ADMIN_PASSWORD) return res.status(401).json({error: "Wrong Password"});
    masterList = masterList.filter(n => n !== name);
    availableNames = availableNames.filter(n => n !== name);
    res.json({success: true, list: masterList});
});

// --- SPIN LOGIC ---
app.post('/api/spin', (req, res) => {
    const { userEmail, userName, teamCode } = req.body; 

    // 1. Security Check
    const match = assignments.find(a => a.picker.toLowerCase() === userEmail.toLowerCase());
    if (match) {
        return res.status(400).json({ error: "You already played! You got: " + match.picked });
    }

    if (availableNames.length === 0) {
        return res.status(400).json({ error: "The Hat is Empty!" });
    }

    let selectedName = null;

    // 2. Rigging Logic
    if (teamCode && RIGGED_MAP[teamCode.toUpperCase()]) {
        const target = RIGGED_MAP[teamCode.toUpperCase()];
        if (availableNames.includes(target)) selectedName = target;
    }

    // 3. Smart Random Logic (Self-Exclusion)
    if (!selectedName) {
        let candidates = availableNames.filter(n => n.toLowerCase() !== userName.toLowerCase());

        if (candidates.length === 0) {
            if (availableNames.length === 1 && availableNames[0].toLowerCase() === userName.toLowerCase()) {
                 return res.status(400).json({ 
                     error: "Game Deadlock! You are the last one and only your name is left. Ask Admin to RESET." 
                 });
            }
        }

        const randomIndex = Math.floor(Math.random() * candidates.length);
        selectedName = candidates[randomIndex];
    }

    // 4. Commit (NOW SAVING PICKER NAME)
    availableNames = availableNames.filter(name => name !== selectedName);
    
    assignments.push({ 
        picker: userEmail, 
        pickerName: userName, // <--- SAVED HERE
        picked: selectedName, 
        timestamp: new Date() 
    });
    
    console.log(`[Draw] ${userName} (${userEmail}) drew ${selectedName}.`);
    res.json({ result: selectedName });
});

app.post('/api/reset', (req, res) => {
    const { password } = req.body;
    if (password === ADMIN_PASSWORD) {
        availableNames = [...masterList]; 
        assignments = [];
        res.json({ success: true, message: "Hat refilled! History cleared." });
    } else {
        res.status(401).json({ success: false, message: "Invalid Password" });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
"""

# 2. ADMIN-SCRIPT.JS (Displays Name instead of Email)
admin_script = """
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
"""

files = {
    "server.js": server_js,
    "public/admin-script.js": admin_script
}

for filepath, content in files.items():
    full_path = os.path.join(project_name, filepath)
    directory = os.path.dirname(full_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated: {full_path}")

print("\\n✅ Admin History Names Update Applied!")