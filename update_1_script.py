import os

# Use current directory
project_name = "." 

# 1. SERVER.JS
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
        res.json({ success: true, message: "Hat refilled!" });
    } else {
        res.status(401).json({ success: false, message: "Invalid Password" });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
"""

# 2. STYLE.CSS
style_css = """:root {
    --red: #c0392b;
    --green: #27ae60;
    --gold: #f1c40f;
    --white: #ecf0f1;
    --dark: #2c3e50;
}

body {
    font-family: 'Georgia', serif;
    background-color: var(--red);
    color: var(--white);
    text-align: center;
    margin: 0;
    padding: 0;
    overflow-x: hidden;
    background-image: radial-gradient(circle, #d63031 10%, #630808 90%);
    min-height: 100vh;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

h1 {
    font-size: 3rem;
    text-shadow: 2px 2px 4px #000;
    margin-bottom: 10px;
    color: var(--gold);
}

.hidden { display: none !important; }

.input-group {
    background: rgba(0, 0, 0, 0.3);
    padding: 30px;
    border-radius: 15px;
    border: 2px solid var(--gold);
    display: inline-block;
    margin-top: 20px;
}

input {
    display: block;
    width: 250px;
    padding: 12px;
    margin: 10px auto;
    border-radius: 5px;
    border: none;
    font-size: 16px;
}

button {
    background-color: var(--green);
    color: white;
    padding: 15px 30px;
    border: 2px solid var(--white);
    border-radius: 50px;
    font-size: 1.2rem;
    cursor: pointer;
    transition: transform 0.2s, background 0.2s;
    font-weight: bold;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

button:hover {
    background-color: #2ecc71;
    transform: scale(1.05);
}

button:disabled {
    background-color: #7f8c8d;
    cursor: not-allowed;
}

/* Hat Styles */
.hat-stage {
    position: relative;
    height: 400px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 20px;
}

.hat {
    font-size: 150px;
    cursor: pointer;
    filter: drop-shadow(0 10px 10px rgba(0,0,0,0.5));
    transition: transform 0.3s;
    z-index: 10;
}

.hat:hover { transform: scale(1.1); }

.shake { animation: shake-animation 0.5s infinite; }

@keyframes shake-animation {
    0% { transform: translate(1px, 1px) rotate(0deg); }
    10% { transform: translate(-1px, -2px) rotate(-1deg); }
    20% { transform: translate(-3px, 0px) rotate(1deg); }
    30% { transform: translate(3px, 2px) rotate(0deg); }
    40% { transform: translate(1px, -1px) rotate(1deg); }
    50% { transform: translate(-1px, 2px) rotate(-1deg); }
    60% { transform: translate(-3px, 1px) rotate(0deg); }
    70% { transform: translate(3px, 1px) rotate(-1deg); }
    80% { transform: translate(-1px, -1px) rotate(1deg); }
    90% { transform: translate(1px, 2px) rotate(0deg); }
    100% { transform: translate(1px, -2px) rotate(-1deg); }
}

.magic-name-card {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) scale(0);
    background: white;
    color: var(--red);
    padding: 20px 40px;
    border: 3px solid var(--gold);
    border-radius: 10px;
    font-weight: bold;
    font-size: 2rem;
    z-index: 5;
    opacity: 0;
    transition: all 1s ease-out;
}

.popped-out {
    top: 10%;
    transform: translate(-50%, -50%) scale(1.2) rotate(-5deg);
    opacity: 1;
    z-index: 20;
    box-shadow: 0 10px 20px rgba(0,0,0,0.5);
}

.sparkles {
    font-size: 2rem;
    position: absolute;
    animation: fadeOut 1s forwards;
}

@keyframes fadeOut {
    0% { opacity: 1; transform: scale(0.5); }
    100% { opacity: 0; transform: scale(2); }
}

/* Admin Styles */
.name-list { text-align: left; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 10px; margin-top: 20px; max-height: 300px; overflow-y: auto; }
.name-item { display: flex; justify-content: space-between; padding: 5px; border-bottom: 1px solid #7f8c8d; }
.del-btn { background: #c0392b; padding: 2px 10px; font-size: 0.8rem; margin-left: 10px; border: none;}
.admin-panel { background: #34495e; min-height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; }
.danger-btn { background-color: var(--red); border: 2px solid var(--gold); }
"""

# 3. INDEX.HTML
index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secret Santa Hat</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>🎩 Secret Santa 🎩</h1>
        
        <div id="intake-view" class="input-group">
            <h3>Who are you?</h3>
            <input type="text" id="user-name" placeholder="Your Name" required>
            <input type="email" id="user-email" placeholder="Your Email" required>
            <input type="text" id="team-code" placeholder="Team Code (Optional)">
            <button id="enter-btn">Enter Room</button>
        </div>

        <div id="game-view" class="hidden">
            <h2>Tap the Hat to Draw a Name!</h2>
            <div class="hat-stage">
                <div class="hat" id="magic-hat">🎩</div>
                <div id="name-card" class="magic-name-card">
                    <span id="drawn-name">???</span>
                </div>
            </div>
            <button id="draw-btn">Reach into the Hat</button>
        </div>

        <div id="result-view" class="hidden">
            <h3 style="margin-top: 50px;">You drew:</h3>
            <h1 id="final-result-name" style="font-size: 4rem; color: var(--gold);">...</h1>
            <p>(Take a screenshot or write it down!)</p>
            <button onclick="location.reload()" style="margin-top:20px;">Done / Next Person</button>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>"""

# 4. SCRIPT.JS
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

enterBtn.addEventListener('click', () => {
    const name = document.getElementById('user-name').value;
    const email = document.getElementById('user-email').value;
    const code = document.getElementById('team-code').value;

    if (!name || !email) { alert("Please enter Name and Email!"); return; }
    userData = { name, email, code };
    intakeView.classList.add('hidden');
    gameView.classList.remove('hidden');
});

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
                gameView.classList.add('hidden');
                resultView.classList.remove('hidden');
                finalResultName.innerText = data.result;
            }, 3000);
        }, 2000);

    } catch (e) {
        console.error(e);
        alert("Connection Error");
        magicHat.classList.remove('shake');
        drawBtn.disabled = false;
    }
});

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
    "public/style.css": style_css,
    "public/index.html": index_html,
    "public/script.js": script_js
}

for filepath, content in files.items():
    full_path = os.path.join(project_name, filepath)
    
    # --- THIS WAS THE MISSING FIX ---
    # Create the directory if it doesn't exist (e.g., 'public')
    directory = os.path.dirname(full_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    # --------------------------------
        
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated: {full_path}")

print("\\n✅ Magic Hat Update Applied Successfully!")