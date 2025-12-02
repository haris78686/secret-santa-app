import os

# Ensure we are working in the current directory
project_name = "." 

# 1. SERVER.JS (Now with Email Protection)
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
// assignments stores: { picker: "email@test.com", picked: "Alice" }
let assignments = []; 

const RIGGED_MAP = { "RUDOLPH": "Charlie" };

// --- ROUTES ---

app.get('/api/master-list', (req, res) => res.json(masterList));

// NEW: Check if user already played
app.post('/api/check-user', (req, res) => {
    const { email } = req.body;
    if (!email) return res.status(400).json({ error: "Email required" });

    // Case-insensitive check
    const match = assignments.find(a => a.picker.toLowerCase() === email.toLowerCase());

    if (match) {
        // User already played! Return their result so they don't lose it.
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

    // Double Check: Did they already play?
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

# 2. SCRIPT.JS (Frontend Security Check)
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

// Check LocalStorage on load
window.addEventListener('load', async () => {
    const savedEmail = localStorage.getItem('santa_email');
    if(savedEmail) {
        // Automatically check status if they refresh
        checkUserStatus(savedEmail);
    }
});

enterBtn.addEventListener('click', () => {
    const name = document.getElementById('user-name').value;
    const email = document.getElementById('user-email').value;
    const code = document.getElementById('team-code').value;

    if (!name || !email) { alert("Please enter Name and Email!"); return; }
    
    // Save locally
    userData = { name, email, code };
    localStorage.setItem('santa_email', email);
    
    // Check server before letting them in
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
            // User already played! Show result screen immediately.
            alert("Welcome back! You have already drawn a name.");
            showFinalResult(data.picked);
        } else {
            // New user, let them in
            userData.email = email; // Ensure email is set
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
        const response = await fetch('/api/spin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userEmail: userData.email, teamCode: userData.code })
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
    
    # Create directory if missing
    directory = os.path.dirname(full_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated: {full_path}")

print("\\n✅ Security Update Applied!")