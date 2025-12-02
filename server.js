const express = require('express');
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
