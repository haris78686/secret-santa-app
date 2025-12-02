const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// --- CONFIGURATION ---

const ADMIN_PASSWORD = "HoHoHo123";

// The Master List of all participants
const MASTER_LIST = [
    "Alice", "Bob", "Charlie", "Diana", 
    "Evan", "Fiona", "George", "Hannah"
];

// The "Rigging" Configuration (Code -> Target Name)
const RIGGED_MAP = {
    "RUDOLPH": "Charlie",
    "FROSTY": "Alice"
};

// --- STATE MANAGEMENT ---

let availableNames = [...MASTER_LIST];
let assignments = []; 

// --- ROUTES ---

app.get('/api/master-list', (req, res) => {
    res.json(MASTER_LIST);
});

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

app.post('/api/reset', (req, res) => {
    const { password } = req.body;

    if (password === ADMIN_PASSWORD) {
        availableNames = [...MASTER_LIST];
        assignments = [];
        console.log('[Admin] Game has been RESET.');
        res.json({ success: true, message: "Game reset successfully!" });
    } else {
        res.status(401).json({ success: false, message: "Invalid Password" });
    }
});

app.listen(PORT, () => {
    console.log(`Secret Santa Server running on http://localhost:${PORT}`);
});
