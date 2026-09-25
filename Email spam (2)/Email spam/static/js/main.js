// Main Global JavaScript Utilities

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.4s ease';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });
    // Scroll reveal observer
    const reveals = document.querySelectorAll('.reveal');
    if ('IntersectionObserver' in window && reveals.length > 0) {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        reveals.forEach(r => observer.observe(r));
    } else {
        reveals.forEach(r => r.classList.add('active'));
    }

    // Initialize Theme Switcher UI
    initTheme();

    // Initialize Cyber Defense Background Animation
    initCyberBackground();
});

// ==========================================================================
// Theme Switcher (Dark / Light Theme)
// ==========================================================================
function initTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    updateThemeToggleUI(isDark ? 'dark' : 'light');
}

function toggleTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';

    if (newTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        try { localStorage.setItem('spamshield_theme', 'dark'); } catch (e) {}
    } else {
        document.documentElement.removeAttribute('data-theme');
        try { localStorage.setItem('spamshield_theme', 'light'); } catch (e) {}
    }

    updateThemeToggleUI(newTheme);
    showToast(`Switched to ${newTheme === 'dark' ? 'Dark' : 'Light'} Mode`, 'info');
}

function updateThemeToggleUI(theme) {
    const isDark = theme === 'dark';
    const homeBtn = document.getElementById('home-theme-btn');
    const homeIcon = document.getElementById('home-theme-icon');
    const homeLabel = document.getElementById('home-theme-label');
    const navBtn = document.getElementById('nav-theme-btn');

    if (homeIcon) homeIcon.textContent = isDark ? '☀️' : '🌙';
    if (homeLabel) homeLabel.textContent = isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme';
    if (homeBtn) homeBtn.setAttribute('title', isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme');

    if (navBtn) {
        navBtn.textContent = isDark ? '☀️' : '🌙';
        navBtn.setAttribute('title', isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme');
    }
}

// Toast notification helper
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 380px;
        `;
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const bgColors = {
        success: 'rgba(16, 185, 129, 0.95)',
        danger: 'rgba(239, 68, 68, 0.95)',
        warning: 'rgba(245, 158, 11, 0.95)',
        info: 'rgba(6, 182, 212, 0.95)'
    };

    toast.style.cssText = `
        background: ${bgColors[type] || bgColors.info};
        color: #ffffff;
        padding: 12px 18px;
        border-radius: 10px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        font-size: 0.9rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        backdrop-filter: blur(8px);
        animation: fadeInDown 0.3s ease;
    `;

    toast.innerHTML = `
        <span>${message}</span>
        <span style="cursor:pointer; opacity:0.8;" onclick="this.parentElement.remove()">&times;</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4500);
}

// ==========================================================================
// Animated Cyber Defense & Email Shield Background
// ==========================================================================
function initCyberBackground() {
    const canvas = document.getElementById('cyber-bg-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width = 0;
    let height = 0;
    let animationFrameId;

    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    resize();
    window.addEventListener('resize', resize);

    const mouse = { x: -1000, y: -1000, radius: 140 };
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });
    window.addEventListener('mouseleave', () => {
        mouse.x = -1000;
        mouse.y = -1000;
    });

    const PARTICLE_COUNT = Math.min(50, Math.max(25, Math.floor((window.innerWidth * window.innerHeight) / 28000)));
    const particles = [];
    const pulses = [];

    // Types: 'node', 'shield', 'email'
    for (let i = 0; i < PARTICLE_COUNT; i++) {
        const type = i % 7 === 0 ? 'shield' : (i % 5 === 0 ? 'email' : 'node');
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.45,
            vy: (Math.random() - 0.5) * 0.45,
            radius: type === 'node' ? (Math.random() * 2 + 1.2) : (type === 'shield' ? 6 : 5),
            type: type,
            pulse: Math.random() * Math.PI * 2
        });
    }

    function drawShield(cx, cy, size, alpha) {
        ctx.save();
        ctx.strokeStyle = `rgba(37, 99, 235, ${alpha})`;
        ctx.fillStyle = `rgba(37, 99, 235, ${alpha * 0.2})`;
        ctx.lineWidth = 1.3;
        ctx.beginPath();
        ctx.moveTo(cx, cy - size);
        ctx.lineTo(cx + size, cy - size * 0.45);
        ctx.lineTo(cx + size * 0.75, cy + size * 0.45);
        ctx.lineTo(cx, cy + size);
        ctx.lineTo(cx - size * 0.75, cy + size * 0.45);
        ctx.lineTo(cx - size, cy - size * 0.45);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        ctx.restore();
    }

    function drawEmail(cx, cy, size, alpha) {
        ctx.save();
        ctx.strokeStyle = `rgba(2, 132, 199, ${alpha})`;
        ctx.fillStyle = `rgba(2, 132, 199, ${alpha * 0.18})`;
        ctx.lineWidth = 1.2;
        const w = size * 1.7;
        const h = size * 1.15;
        ctx.strokeRect(cx - w / 2, cy - h / 2, w, h);
        ctx.beginPath();
        ctx.moveTo(cx - w / 2, cy - h / 2);
        ctx.lineTo(cx, cy + h * 0.15);
        ctx.lineTo(cx + w / 2, cy - h / 2);
        ctx.stroke();
        ctx.restore();
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        // Update & draw particles
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.pulse += 0.022;

            // Bounce on screen edges
            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;

            // Mouse interaction
            const dx = mouse.x - p.x;
            const dy = mouse.y - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < mouse.radius) {
                const angle = Math.atan2(dy, dx);
                const force = (mouse.radius - dist) / mouse.radius;
                p.x -= Math.cos(angle) * force * 1.1;
                p.y -= Math.sin(angle) * force * 1.1;

                // Connection line to cursor
                const mouseAlpha = (1 - dist / mouse.radius) * 0.35;
                ctx.strokeStyle = `rgba(37, 99, 235, ${mouseAlpha})`;
                ctx.lineWidth = 0.8;
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(mouse.x, mouse.y);
                ctx.stroke();
            }

            // Connection lines between nearby nodes
            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const pdx = p.x - p2.x;
                const pdy = p.y - p2.y;
                const pdist = Math.sqrt(pdx * pdx + pdy * pdy);
                const maxDist = 135;

                if (pdist < maxDist) {
                    const lineAlpha = (1 - pdist / maxDist) * 0.22;
                    ctx.strokeStyle = `rgba(56, 189, 248, ${lineAlpha})`;
                    ctx.lineWidth = 0.65;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }

            // Render symbol or node
            const baseAlpha = 0.45 + Math.sin(p.pulse) * 0.22;
            if (p.type === 'shield') {
                drawShield(p.x, p.y, p.radius, baseAlpha);
            } else if (p.type === 'email') {
                drawEmail(p.x, p.y, p.radius, baseAlpha);
            } else {
                ctx.fillStyle = `rgba(56, 189, 248, ${baseAlpha * 0.65})`;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Active neural data pulses traveling across network links
        if (Math.random() < 0.06 && pulses.length < 8) {
            const i = Math.floor(Math.random() * particles.length);
            for (let j = 0; j < particles.length; j++) {
                if (i === j) continue;
                const pdx = particles[i].x - particles[j].x;
                const pdy = particles[i].y - particles[j].y;
                if (Math.sqrt(pdx * pdx + pdy * pdy) < 135) {
                    pulses.push({
                        from: particles[i],
                        to: particles[j],
                        progress: 0,
                        speed: 0.018 + Math.random() * 0.015
                    });
                    break;
                }
            }
        }

        for (let k = pulses.length - 1; k >= 0; k--) {
            const pulse = pulses[k];
            pulse.progress += pulse.speed;
            if (pulse.progress >= 1) {
                pulses.splice(k, 1);
                continue;
            }
            const px = pulse.from.x + (pulse.to.x - pulse.from.x) * pulse.progress;
            const py = pulse.from.y + (pulse.to.y - pulse.from.y) * pulse.progress;
            ctx.save();
            ctx.fillStyle = '#00f2fe';
            ctx.shadowColor = '#38bdf8';
            ctx.shadowBlur = 8;
            ctx.beginPath();
            ctx.arc(px, py, 2.2, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }

        if (!document.hidden) {
            animationFrameId = requestAnimationFrame(animate);
        }
    }

    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) {
            cancelAnimationFrame(animationFrameId);
            animate();
        }
    });

    animate();
}

