const intakeView = document.getElementById('intake-view');
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
