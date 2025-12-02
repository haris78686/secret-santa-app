const intakeView = document.getElementById('intake-view');
const gameView = document.getElementById('game-view');
const resultView = document.getElementById('result-view');
const wheel = document.getElementById('wheel');
const resultNameDisplay = document.getElementById('result-name');
const enterBtn = document.getElementById('enter-btn');
const spinBtn = document.getElementById('spin-btn');

let userData = { name: '', email: '', code: '' };
let masterList = [];
let segmentAngle = 0;

async function init() {
    try {
        const response = await fetch('/api/master-list');
        masterList = await response.json();
        drawWheel();
    } catch (err) { console.error("Failed to load names", err); }
}

function drawWheel() {
    wheel.innerHTML = '';
    const colors = ['#e74c3c', '#2ecc71', '#f1c40f', '#ecf0f1', '#3498db', '#9b59b6'];
    segmentAngle = 360 / masterList.length;

    masterList.forEach((name, i) => {
        const rotation = i * segmentAngle;
        const textWrapper = document.createElement('div');
        textWrapper.style.position = 'absolute';
        textWrapper.style.height = '50%';
        textWrapper.style.width = '20px';
        textWrapper.style.left = 'calc(50% - 10px)';
        textWrapper.style.top = '0';
        textWrapper.style.transformOrigin = 'bottom center';
        textWrapper.style.transform = `rotate(${rotation}deg)`;
        
        const span = document.createElement('span');
        span.innerText = name;
        span.style.display = 'block';
        span.style.transform = 'translateY(20px)';
        span.style.fontWeight = 'bold';
        span.style.writingMode = 'vertical-rl';
        span.style.color = '#333';
        
        textWrapper.appendChild(span);
        wheel.appendChild(textWrapper);
    });

    let gradientStr = 'conic-gradient(';
    masterList.forEach((_, i) => {
        const color = colors[i % colors.length];
        const start = i * segmentAngle;
        const end = (i + 1) * segmentAngle;
        gradientStr += `${color} ${start}deg ${end}deg,`;
    });
    gradientStr = gradientStr.slice(0, -1) + ')';
    wheel.style.background = gradientStr;
}

enterBtn.addEventListener('click', () => {
    const name = document.getElementById('user-name').value;
    const email = document.getElementById('user-email').value;
    const code = document.getElementById('team-code').value;

    if (!name || !email) { alert("Please enter Name and Email!"); return; }
    userData = { name, email, code };
    intakeView.classList.add('hidden');
    gameView.classList.remove('hidden');
});

spinBtn.addEventListener('click', async () => {
    spinBtn.disabled = true;
    try {
        const response = await fetch('/api/spin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userEmail: userData.email, teamCode: userData.code })
        });
        const data = await response.json();
        if (data.error) { alert(data.error); spinBtn.disabled = false; return; }

        const winnerIndex = masterList.indexOf(data.result);
        const stopAngle = 360 - (winnerIndex * segmentAngle) - (segmentAngle / 2);
        const totalRotation = 1800 + stopAngle;

        wheel.style.transform = `rotate(${totalRotation}deg)`;
        setTimeout(() => {
            gameView.classList.add('hidden');
            resultView.classList.remove('hidden');
            resultNameDisplay.innerText = data.result;
        }, 4000);
    } catch (e) { console.error(e); spinBtn.disabled = false; }
});
init();
