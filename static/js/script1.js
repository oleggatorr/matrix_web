// static/js/matrix.js
const canvas = document.getElementById('matrixCanvas');
const ctx = canvas.getContext('2d');

// Настройка размера canvas
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Символы из фильма (латиница + цифры + спецсимволы)
const chars = "アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ$#@%&*()";
const charArray = chars.split("");

const fontSize = 14;
const columns = canvas.width / fontSize;

// Каждый столбец: y-позиция падения
const drops = [];
for (let i = 0; i < columns; i++) {
    drops[i] = Math.random() * -100;
}

function draw() {
    // Полупрозрачный чёрный — создаёт эффект "хвоста"
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#0F0';
    ctx.font = `${fontSize}px monospace`;

    for (let i = 0; i < drops.length; i++) {
        const text = charArray[Math.floor(Math.random() * charArray.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);

        // Если капля дошла до низа или рандомно — сброс
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }
        drops[i]++;
    }
}
function confirmLogout() {
    // Первое подтверждение
    if (confirm("Текст?")) {
        // Второе подтверждение
        if (confirm("Текст?")) {
            // Перенаправляем на роут /logout
            window.location.href = "/logout";
        }
    }
}
setInterval(draw, 35);