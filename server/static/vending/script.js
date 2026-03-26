// ═══════════════════════════════════════════════════════════════
// EcoBottle - Frontend JavaScript
// ═══════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    initFormEffects();
});

// ─── Animated Background Particles ──────────────────────────
function createParticles() {
    const container = document.getElementById('bgParticles');
    if (!container) return;

    const colors = ['#34d399', '#06b6d4', '#10b981', '#22d3ee'];
    const count = 25;

    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');

        const size = Math.random() * 6 + 2;
        const color = colors[Math.floor(Math.random() * colors.length)];
        const left = Math.random() * 100;
        const duration = Math.random() * 20 + 15;
        const delay = Math.random() * 15;

        particle.style.cssText = `
            width: ${size}px;
            height: ${size}px;
            background: ${color};
            left: ${left}%;
            animation-duration: ${duration}s;
            animation-delay: ${delay}s;
            box-shadow: 0 0 ${size * 2}px ${color};
        `;

        container.appendChild(particle);
    }
}

// ─── Form Effects ───────────────────────────────────────────
function initFormEffects() {
    const input = document.getElementById('registerInput');
    const btn = document.getElementById('submitBtn');

    if (input) {
        // Auto-focus the input
        input.focus();

        // Add ripple effect to button
        if (btn) {
            btn.addEventListener('click', function (e) {
                const ripple = document.createElement('span');
                ripple.style.cssText = `
                    position: absolute;
                    border-radius: 50%;
                    background: rgba(255,255,255,0.3);
                    transform: scale(0);
                    animation: ripple 0.6s linear;
                    pointer-events: none;
                `;

                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
                ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';

                this.appendChild(ripple);
                setTimeout(() => ripple.remove(), 600);
            });
        }
    }

    // Add ripple animation style
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to { transform: scale(4); opacity: 0; }
        }
    `;
    document.head.appendChild(style);

    // Apply staggered animation delay to transaction items
    document.querySelectorAll('.transaction-item[data-index]').forEach(item => {
        item.style.animationDelay = (item.dataset.index * 100) + 'ms';
    });

    // Smooth scroll to results if present
    const results = document.getElementById('resultsSection');
    if (results) {
        setTimeout(() => {
            results.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    }
}
