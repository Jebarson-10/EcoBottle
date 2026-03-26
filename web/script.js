// ═══════════════════════════════════════════════════════════════
// EcoBottle - Frontend JavaScript (Firebase Version)
// ═══════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    initFormEffects();
    initFirebaseApp();
});

let db;

function initFirebaseApp() {
    // Initialize Firebase
    if (typeof firebaseConfig !== 'undefined' && firebaseConfig.apiKey !== 'YOUR_API_KEY') {
        firebase.initializeApp(firebaseConfig);
        db = firebase.firestore();
        console.log("Firebase initialized");
    } else {
        console.warn("Firebase configuration not found or not configured. Use firebase-config.js to set up your project.");
    }
}

// ─── Search Functionality ─────────────────────────────────────
async function lookupPoints(registerNumber) {
    if (!db) {
        alert("Please configure Firebase in firebase-config.js first!");
        return;
    }

    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsContainer = document.getElementById('resultsContainer');
    const successTemplate = document.getElementById('successTemplate');
    const errorTemplate = document.getElementById('errorTemplate');

    loadingIndicator.style.display = 'block';
    resultsContainer.innerHTML = '';

    try {
        // Query user document
        const userRef = db.collection('users').doc(registerNumber);
        const userDoc = await userRef.get();

        loadingIndicator.style.display = 'none';

        if (userDoc.exists) {
            const userData = userDoc.data();
            
            // Clone success template
            const resultNode = successTemplate.content.cloneNode(true);
            
            // Set user info
            resultNode.querySelector('#displayRegNum').textContent = userData.register_number;
            
            const date = userData.created_at ? userData.created_at.toDate() : new Date();
            resultNode.querySelector('#memberSince').textContent = `Member since ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
            
            // Set points with counter animation
            const pointsCounter = resultNode.querySelector('#pointsCounter');
            animateNumber(pointsCounter, 0, userData.total_points || 0, 1500);

            // Fetch transactions
            const transactionsRef = userRef.collection('transactions').orderBy('timestamp', 'desc').limit(20);
            const transactionsSnapshot = await transactionsRef.get();
            
            if (!transactionsSnapshot.empty) {
                const transSection = resultNode.querySelector('#transactionsSection');
                const transList = resultNode.querySelector('#transactionsList');
                transSection.style.display = 'block';
                
                transactionsSnapshot.forEach((doc, index) => {
                    const t = doc.data();
                    const transItem = document.createElement('div');
                    transItem.className = 'transaction-item';
                    transItem.style.animationDelay = `${index * 100}ms`;
                    
                    const tDate = t.timestamp ? t.timestamp.toDate() : new Date();
                    const formattedDate = tDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                    const formattedTime = tDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

                    transItem.innerHTML = `
                        <div class="transaction-left">
                            <div class="transaction-icon">🍶</div>
                            <div class="transaction-details">
                                <span class="transaction-weight">${t.weight_grams}g bottle</span>
                                <span class="transaction-time">${formattedDate} · ${formattedTime}</span>
                            </div>
                        </div>
                        <div class="transaction-points">+${t.points_earned} pts</div>
                    `;
                    transList.appendChild(transItem);
                });
            }

            resultsContainer.appendChild(resultNode);
            
            // Scroll to results
            setTimeout(() => {
                const section = document.getElementById('resultsSection');
                if (section) section.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);

        } else {
            // Document does not exist
            const resultNode = errorTemplate.content.cloneNode(true);
            resultNode.querySelector('#errorRegNum').textContent = `"${registerNumber}"`;
            resultsContainer.appendChild(resultNode);
        }
    } catch (error) {
        loadingIndicator.style.display = 'none';
        console.error("Error fetching data:", error);
        alert("Error connecting to database. Check console for details.");
    }
}

function animateNumber(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const current = Math.floor(progress * (end - start) + start);
        element.textContent = current;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            element.textContent = end;
        }
    };
    window.requestAnimationFrame(step);
}

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
    const form = document.getElementById('searchForm');
    const input = document.getElementById('registerInput');
    const btn = document.getElementById('submitBtn');

    if (input) {
        input.focus();
    }

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const regNum = input.value.trim();
            if (regNum) {
                lookupPoints(regNum);
            }
        });
    }

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

    // Add ripple animation style
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to { transform: scale(4); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}
