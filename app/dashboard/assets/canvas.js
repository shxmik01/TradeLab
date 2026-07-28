const canvas = document.getElementById("bg-canvas");
const ctx = canvas.getContext("2d");

let width, height;
let particles = [];

function resize() {
    width = window.innerWidth;
    height = window.innerHeight;

    canvas.width = width;
    canvas.height = height;

    // Responsive node count
    const nodeCount =
        width < 600 ? 25 :
        width < 1024 ? 50 : 90;

    particles = [];

    for (let i = 0; i < nodeCount; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4
        });
    }
}

window.addEventListener("resize", resize);
resize();

function animate() {

    ctx.clearRect(0, 0, width, height);

    // Draw connection lines
    for (let i = 0; i < particles.length; i++) {

        for (let j = i + 1; j < particles.length; j++) {

            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;

            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < 140) {

                ctx.strokeStyle = `rgba(0,180,255,${1 - dist / 140})`;
                ctx.lineWidth = 1;

                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.stroke();
            }

        }

    }

    // Draw nodes
    particles.forEach(p => {

        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = "#00C8FF";
        ctx.shadowBlur = 12;
        ctx.shadowColor = "#00C8FF";
        ctx.fill();

    });

    requestAnimationFrame(animate);

}

animate();