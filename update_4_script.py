import os

project_name = "." 

# 1. SERVER.JS (Now with Self-Exclusion Logic)
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
let assignments = []; 

const RIGGED_MAP = { "RUDOLPH": "Charlie" };

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

// --- THE UPDATED SPIN LOGIC ---
app.post('/api/spin', (req, res) => {
    const { userEmail, userName, teamCode } = req.body; // NOW READING USERNAME

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
        // Filter out the user's own name from the pool of candidates
        // We use lowercase comparison to be safe
        let candidates = availableNames.filter(n => n.toLowerCase() !== userName.toLowerCase());

        if (candidates.length === 0) {
            // CRITICAL EDGE CASE: 
            // If the user is the LAST person and the only name left is their own.
            // (This happens if everyone else picked someone else and left 'Bob' for 'Bob')
            if (availableNames.length === 1 && availableNames[0].toLowerCase() === userName.toLowerCase()) {
                 return res.status(400).json({ 
                     error: "Game Deadlock! You are the last one and only your name is left. Please ask Admin to RESET." 
                 });
            }
        }

        // Pick from the safe candidates
        const randomIndex = Math.floor(Math.random() * candidates.length);
        selectedName = candidates[randomIndex];
    }

    // 4. Commit the draw
    availableNames = availableNames.filter(name => name !== selectedName);
    assignments.push({ picker: userEmail, picked: selectedName, timestamp: new Date() });
    
    console.log(`[Draw] User ${userEmail} (${userName}) drew ${selectedName}.`);
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

# 2. SCRIPT.JS (Sends the Name to Backend)
script_js = """const intakeView = document.getElementById('intake-view');
const gameView = document.getElementById('game-view');
const resultView = document.getElementById('result-view');
const magicHat = document.getElementById('magic-hat');
const nameCard = document.getElementById('name-card');
const drawnNameSpan = document.getElementById('drawn-name');
const finalResultName = document.getElementById('final-result-name');

const enterBtn = document.getElementById('enter-btn');
const drawBtn = document.getElementById('draw-btn');

let userData = { name: '', email: '', code: '' };

window.addEventListener('load', async () => {
    const savedEmail = localStorage.getItem('santa_email');
    if(savedEmail) {
        checkUserStatus(savedEmail);
    }
});

enterBtn.addEventListener('click', () => {
    const name = document.getElementById('user-name').value.trim(); // Trim whitespace
    const email = document.getElementById('user-email').value.trim();
    const code = document.getElementById('team-code').value;

    if (!name || !email) { alert("Please enter Name and Email!"); return; }
    
    userData = { name, email, code };
    localStorage.setItem('santa_email', email);
    
    checkUserStatus(email);
});

async function checkUserStatus(email) {
    try {
        const res = await fetch('/api/check-user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();

        if (data.hasPlayed) {
            alert("Welcome back! You have already drawn a name.");
            showFinalResult(data.picked);
        } else {
            userData.email = email; 
            intakeView.classList.add('hidden');
            resultView.classList.add('hidden');
            gameView.classList.remove('hidden');
        }
    } catch(e) {
        console.error(e);
        alert("Server connection error");
    }
}

drawBtn.addEventListener('click', async () => {
    drawBtn.disabled = true;
    drawBtn.innerText = "Rummaging around...";
    magicHat.classList.add('shake');

    try {
        // NOW SENDING USERNAME
        const response = await fetch('/api/spin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                userEmail: userData.email, 
                userName: userData.name, 
                teamCode: userData.code 
            })
        });
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            magicHat.classList.remove('shake');
            drawBtn.disabled = false;
            drawBtn.innerText = "Reach into the Hat";
            return;
        }

        setTimeout(() => {
            magicHat.classList.remove('shake');
            drawnNameSpan.innerText = data.result;
            nameCard.classList.add('popped-out');
            createSparkles();

            setTimeout(() => {
                showFinalResult(data.result);
            }, 3000);
        }, 2000);

    } catch (e) {
        console.error(e);
        alert("Connection Error");
        magicHat.classList.remove('shake');
        drawBtn.disabled = false;
    }
});

function showFinalResult(name) {
    intakeView.classList.add('hidden');
    gameView.classList.add('hidden');
    resultView.classList.remove('hidden');
    finalResultName.innerText = name;
}

function createSparkles() {
    const hatStage = document.querySelector('.hat-stage');
    for(let i=0; i<10; i++) {
        const spark = document.createElement('div');
        spark.innerText = '✨';
        spark.className = 'sparkles';
        spark.style.left = (50 + (Math.random() * 40 - 20)) + '%';
        spark.style.top = (50 + (Math.random() * 40 - 20)) + '%';
        hatStage.appendChild(spark);
        setTimeout(() => spark.remove(), 1000);
    }
}
"""

files = {
    "server.js": server_js,
    "public/script.js": script_js
}

for filepath, content in files.items():
    full_path = os.path.join(project_name, filepath)
    directory = os.path.dirname(full_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated: {full_path}")

print("\\n✅ Self-Exclusion Logic Applied!")