import os

project_name = "." 

# 1. SERVER.JS (Includes Security + Magic Hat + Admin History)
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
// assignments stores: { picker: "email", picked: "Name", time: "Date" }
let assignments = []; 

const RIGGED_MAP = { "RUDOLPH": "Charlie" };

// --- ROUTES ---

app.get('/api/master-list', (req, res) => res.json(masterList));

// NEW: Admin View History
app.post('/api/admin/assignments', (req, res) => {
    const { password } = req.body;
    if (password === ADMIN_PASSWORD) {
        res.json({ success: true, assignments: assignments });
    } else {
        res.status(401).json({ success: false, message: "Invalid Password" });
    }
});

// User Security Check
app.post('/api/check-user', (req, res) => {
    const { email } = req.body;
    if (!email) return res.status(400).json({ error: "Email required" });

    const match = assignments.find(a => a.picker.toLowerCase() === email.toLowerCase());

    if (match) {
        return res.json({ hasPlayed: true, picked: match.picked });
    }
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

app.post('/api/spin', (req, res) => {
    const { userEmail, teamCode } = req.body;

    const match = assignments.find(a => a.picker.toLowerCase() === userEmail.toLowerCase());
    if (match) {
        return res.status(400).json({ error: "You already played! You got: " + match.picked });
    }

    if (availableNames.length === 0) {
        return res.status(400).json({ error: "The Hat is Empty!" });
    }

    let selectedName = null;
    if (teamCode && RIGGED_MAP[teamCode.toUpperCase()]) {
        const target = RIGGED_MAP[teamCode.toUpperCase()];
        if (availableNames.includes(target)) selectedName = target;
    }

    if (!selectedName) {
        const randomIndex = Math.floor(Math.random() * availableNames.length);
        selectedName = availableNames[randomIndex];
    }

    availableNames = availableNames.filter(name => name !== selectedName);
    assignments.push({ picker: userEmail, picked: selectedName, timestamp: new Date() });
    
    console.log(`[Draw] User ${userEmail} drew ${selectedName}. Remaining: ${availableNames.length}`);
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

# 2. ADMIN.HTML (Adds the History Section)
admin_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin - Secret Santa</title>
    <link rel="stylesheet" href="style.css">
    <style> 
        body { background: #2c3e50; } 
        .name-list { text-align: left; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 10px; margin-top: 20px; max-height: 300px; overflow-y: auto; }
        .name-item { display: flex; justify-content: space-between; padding: 5px; border-bottom: 1px solid #7f8c8d; }
        .del-btn { background: #c0392b; padding: 2px 10px; font-size: 0.8rem; margin-left: 10px; border: none;}
        .add-row { display: flex; gap: 10px; margin-top: 20px; }
        /* New History Styles */
        .history-item { color: #ecf0f1; font-size: 0.9rem; padding: 8px 0; border-bottom: 1px dashed #555; }
        .history-arrow { color: var(--gold); font-weight: bold; margin: 0 10px; }
    </style>
</head>
<body>
    <div class="admin-panel">
        <h1>Admin Control</h1>
        
        <div class="input-group">
            <input type="password" id="admin-pass" placeholder="Admin Password (Required)">
        </div>

        <div style="width: 100%; max-width: 500px;">
            <h3 style="color: var(--gold); margin-top: 30px;">Manage Participants</h3>
            <div class="add-row">
                <input type="text" id="new-name" placeholder="Enter Name" style="margin:0; flex:1;">
                <button id="add-btn" style="padding: 10px 20px; font-size: 1rem;">Add</button>
            </div>
            
            <div id="name-list-container" class="name-list"></div>
        </div>

        <div style="margin-top: 40px; border-top: 1px solid #7f8c8d; padding-top: 20px; width: 100%; max-width: 500px;">
             <h3 style="color: #3498db;">Secret History (Logs)</h3>
             <button id="view-history-btn" style="width: 100%; background: #2980b9;">Reveal Who Picked Whom</button>
             <div id="history-list" class="name-list" style="display:none; margin-top:10px;">
                 </div>
        </div>

        <div style="margin-top: 30px; width: 100%; max-width: 500px;">
             <button id="reset-btn" class="danger-btn" style="width: 100%;">RESET GAME (Refill Pool)</button>
             <p id="admin-msg" style="color:white; margin-top:10px;"></p>
        </div>
    </div>
    <script src="admin-script.js"></script>
</body>
</html>"""

# 3. ADMIN-SCRIPT.JS (Adds Logic to fetch History)
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

// --- NEW HISTORY LOGIC ---
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
            div.innerHTML = `<span>${entry.picker}</span> <span class="history-arrow">➔</span> <span>${entry.picked}</span>`;
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
    "public/admin.html": admin_html,
    "public/admin-script.js": admin_script
}

for filepath, content in files.items():
    full_path = os.path.join(project_name, filepath)
    
    # Safety Check: Create directory if missing
    directory = os.path.dirname(full_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated: {full_path}")

print("\\n✅ Admin History Update Applied!")