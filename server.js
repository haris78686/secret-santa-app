const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// --- CONFIGURATION ---
const ADMIN_PASSWORD = "HoHoHo123";

// --- STATE MANAGEMENT ---
// We start with a default list, but now it is editable.
let masterList = ["Alice", "Bob", "Charlie", "Diana", "Evan"];
let availableNames = [...masterList];
let assignments = []; 

// Rigging (Optional - Hardcoded for now)
const RIGGED_MAP = { "RUDOLPH": "Charlie" };

// --- ROUTES ---

// 1. Get the current list of names
app.get('/api/master-list', (req, res) => {
    res.json(masterList);
});

// 2. Add a Name (Admin)
app.post('/api/add-name', (req, res) => {
    const { name, password } = req.body;
    if (password !== ADMIN_PASSWORD) return res.status(401).json({error: "Wrong Password"});
    if (!name) return res.status(400).json({error: "Name required"});

    if (!masterList.includes(name)) {
        masterList.push(name);
        // Only add to available if the game hasn't fully ended or if we want to include them immediately
        if (!availableNames.includes(name)) {
            availableNames.push(name);
        }
        return res.json({success: true, list: masterList});
    }
    res.json({success: false, message: "Name already exists"});
});

// 3. Remove a Name (Admin)
app.post('/api/remove-name', (req, res) => {
    const { name, password } = req.body;
    if (password !== ADMIN_PASSWORD) return res.status(401).json({error: "Wrong Password"});

    masterList = masterList.filter(n => n !== name);
    availableNames = availableNames.filter(n => n !== name);
    
    res.json({success: true, list: masterList});
});

// 4. Spin Logic
app.post('/api/spin', (req, res) => {
    const { userEmail, teamCode } = req.body;

    if (availableNames.length === 0) {
        return res.status(400).json({ error: "All names have been drawn!" });
    }

    let selectedName = null;

    if (teamCode && RIGGED_MAP[teamCode.toUpperCase()]) {
        const target = RIGGED_MAP[teamCode.toUpperCase()];
        if (availableNames.includes(target)) {
            selectedName = target;
        }
    }

    if (!selectedName) {
        const randomIndex = Math.floor(Math.random() * availableNames.length);
        selectedName = availableNames[randomIndex];
    }

    availableNames = availableNames.filter(name => name !== selectedName);
    assignments.push({ picker: userEmail, picked: selectedName, timestamp: new Date() });

    console.log(`[Spin] User ${userEmail} got ${selectedName}. Remaining: ${availableNames.length}`);
    res.json({ result: selectedName });
});

// 5. Reset Game (Keep names, clear assignments)
app.post('/api/reset', (req, res) => {
    const { password } = req.body;
    if (password === ADMIN_PASSWORD) {
        availableNames = [...masterList]; // Refill from the CURRENT master list
        assignments = [];
        console.log('[Admin] Game has been RESET.');
        res.json({ success: true, message: "Game reset! Name pool refreshed." });
    } else {
        res.status(401).json({ success: false, message: "Invalid Password" });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
