// PSY0 Training App V3 — Premium Edition
const app = {
    // State
    questions: [], qIdx: 0, score: 0, wrong: [], answered: false,
    timer: null, timerVal: 0, timerMax: 0,
    fcCards: [], fcIdx: 0, fcKnown: 0,
    examMode: false,
    touchStartX: 0,

    // DOM
    $: id => document.getElementById(id),

    init() {
        // Theme
        const saved = localStorage.getItem('psy0_theme');
        if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.setAttribute('data-theme', 'dark');
            this.$('theme-toggle').textContent = '☀️';
        }
        this.$('theme-toggle').addEventListener('click', () => this.toggleDark());

        // Tabs
        document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => this.switchTab(t.dataset.tab)));
        // QCM
        this.$('start-btn').addEventListener('click', () => this.startQCM());
        this.$('next-btn').addEventListener('click', () => this.nextQ());
        this.$('restart-btn').addEventListener('click', () => this.showScreen('qcm-home'));
        // Flashcards
        this.$('fc-start-btn').addEventListener('click', () => this.startFC());
        // Mode hint + exam mode logic
        this.$('mode-select').addEventListener('change', e => {
            const hints = {
                all: 'Toutes les 3022 questions',
                random20: '20 questions aléatoires',
                random50: '50 questions aléatoires',
                random100: '100 questions aléatoires',
                weak: 'Questions les plus souvent ratées',
                exam: '80 questions, 20s imposé, sans feedback'
            };
            this.$('mode-hint').textContent = hints[e.target.value] || '';
            // Hide timer select in exam mode
            this.$('timer-setting').style.display = e.target.value === 'exam' ? 'none' : '';
        });
        // Search
        this.$('search-input').addEventListener('input', e => this.searchQuestions(e.target.value));
        // Keyboard
        document.addEventListener('keydown', e => this.handleKeyboard(e));
        // Touch events for flashcards
        const fc = this.$('flashcard');
        if (fc) {
            fc.addEventListener('touchstart', e => { this.touchStartX = e.touches[0].clientX; }, { passive: true });
            fc.addEventListener('touchend', e => {
                const diff = e.changedTouches[0].clientX - this.touchStartX;
                if (Math.abs(diff) > 60) {
                    this.fcMark(diff > 0); // swipe right = known, left = review
                }
            }, { passive: true });
        }
        // Populate category selects
        const cats = [...new Set(qcmData.map(q => q.category).filter(Boolean))];
        [this.$('cat-select')].forEach(sel => {
            cats.forEach(c => { const o = document.createElement('option'); o.value = c; o.textContent = c; sel.appendChild(o); });
        });
        const fcCats = [...new Set(flashcardData.map(f => f.category))];
        fcCats.forEach(c => { const o = document.createElement('option'); o.value = c; o.textContent = c; this.$('fc-cat-select').appendChild(o); });
        // Show stats + mastery
        this.renderStats();
        this.renderMastery();
    },

    // === THEME ===
    toggleDark() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        document.documentElement.setAttribute('data-theme', isDark ? '' : 'dark');
        this.$('theme-toggle').textContent = isDark ? '🌙' : '☀️';
        localStorage.setItem('psy0_theme', isDark ? 'light' : 'dark');
    },

    // === KEYBOARD ===
    handleKeyboard(e) {
        const active = document.querySelector('.screen.active');
        if (!active) return;

        // QCM screen
        if (active.id === 'question-screen') {
            const keys = { 'a': 0, 'b': 1, 'c': 2, 'd': 3 };
            const lower = e.key.toLowerCase();
            if (lower in keys && !this.answered) {
                const btns = this.$('options-container').querySelectorAll('.option-btn');
                if (btns[keys[lower]]) btns[keys[lower]].click();
                e.preventDefault();
            }
            if ((e.key === 'Enter' || e.key === 'ArrowRight') && this.answered) {
                this.nextQ();
                e.preventDefault();
            }
        }
        // Flashcard screen
        if (active.id === 'flashcard-screen') {
            if (e.key === ' ' || e.code === 'Space') { this.flipCard(); e.preventDefault(); }
            if (e.key === '1') { this.fcMark(false); e.preventDefault(); }
            if (e.key === '2') { this.fcMark(true); e.preventDefault(); }
        }
    },

    // === NAVIGATION ===
    switchTab(tab) {
        document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        if (tab === 'qcm') { this.$('qcm-home').classList.add('active'); this.renderMastery(); }
        else if (tab === 'flashcards') this.$('flashcards-home').classList.add('active');
        else if (tab === 'stats') { this.renderStats(); this.$('stats-screen').classList.add('active'); }
    },
    showScreen(id) {
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        this.$(id).classList.add('active');
        if (id === 'qcm-home') this.renderMastery();
    },

    // === SEARCH ===
    searchQuestions(query) {
        const container = this.$('search-results');
        const settings = this.$('qcm-settings');
        const startBtn = this.$('start-btn');
        if (!query || query.length < 2) {
            container.style.display = 'none';
            settings.style.display = '';
            startBtn.style.display = '';
            return;
        }
        const lower = query.toLowerCase();
        const results = qcmData.filter(q =>
            q.question.toLowerCase().includes(lower) ||
            q.options.some(o => o.text.toLowerCase().includes(lower)) ||
            (q.explanation && q.explanation.toLowerCase().includes(lower))
        ).slice(0, 15);

        if (results.length === 0) {
            container.innerHTML = '<p style="text-align:center;color:var(--text-muted);padding:1rem;">Aucun résultat</p>';
        } else {
            container.innerHTML = results.map(q => {
                const correct = q.options.find(o => o.id === q.answer);
                return `<div class="search-result-item">
                    <div class="sr-question">${q.id}. ${q.question}</div>
                    <div class="sr-answer">✅ ${correct ? correct.text : q.answer.toUpperCase()}</div>
                    ${q.explanation ? `<div class="sr-explanation">${q.explanation}</div>` : ''}
                    <div class="sr-cat">${q.category || 'Général'}</div>
                </div>`;
            }).join('');
        }
        container.style.display = 'flex';
        settings.style.display = 'none';
        startBtn.style.display = 'none';
    },

    // === QCM ===
    startQCM() {
        const mode = this.$('mode-select').value;
        const cat = this.$('cat-select').value;
        let pool = [...qcmData];
        if (cat !== 'all') pool = pool.filter(q => q.category === cat);

        this.examMode = mode === 'exam';

        if (mode === 'random20') { this.shuffle(pool); pool = pool.slice(0, 20); }
        else if (mode === 'random50') { this.shuffle(pool); pool = pool.slice(0, 50); }
        else if (mode === 'random100') { this.shuffle(pool); pool = pool.slice(0, 100); }
        else if (mode === 'weak') { pool = this.getWeakQuestions(pool); }
        else if (mode === 'exam') { this.shuffle(pool); pool = pool.slice(0, 80); }

        if (pool.length === 0) { alert('Aucune question disponible pour cette sélection.'); return; }
        this.questions = pool; this.qIdx = 0; this.score = 0; this.wrong = [];

        if (this.examMode) {
            this.timerMax = 20;
            this.$('exam-indicator').style.display = '';
        } else {
            this.timerMax = parseInt(this.$('timer-select').value);
            this.$('exam-indicator').style.display = 'none';
        }

        this.showScreen('question-screen');
        this.renderQ();
    },

    renderQ() {
        const q = this.questions[this.qIdx];
        this.answered = false;
        this.$('next-btn').classList.remove('show');
        this.$('explanation-box').style.display = 'none';
        // Question image
        const imgContainer = this.$('question-image');
        if (q.image) {
            imgContainer.style.display = 'block';
            imgContainer.innerHTML = '<div class="img-loading">📷 Chargement...</div>';
            const img = new Image();
            img.onload = () => { imgContainer.innerHTML = ''; imgContainer.appendChild(img); };
            img.onerror = () => { imgContainer.innerHTML = '<div class="img-error">⚠️ Image non disponible</div>'; };
            img.src = q.image;
            img.alt = q.question;
            img.className = 'question-img';
        } else {
            imgContainer.style.display = 'none';
            imgContainer.innerHTML = '';
        }
        this.$('question-text').innerHTML = `${this.qIdx + 1}. ${q.question}`;
        this.$('progress-text').textContent = `Question ${this.qIdx + 1} sur ${this.questions.length}`;
        this.$('score-text').textContent = this.examMode ? '' : `Score: ${this.score}`;
        this.$('progress-fill').style.width = `${(this.qIdx / this.questions.length) * 100}%`;
        this.$('q-category').textContent = q.category || 'Général';
        // Options
        const c = this.$('options-container'); c.innerHTML = '';
        const letters = ['a', 'b', 'c', 'd'];
        q.options.forEach((opt, idx) => {
            const b = document.createElement('button'); b.className = 'option-btn';
            b.innerHTML = `<span class="option-letter">${opt.id.toUpperCase()}</span><span>${opt.text}</span><span class="key-hint">${letters[idx].toUpperCase()}</span>`;
            b.addEventListener('click', () => this.answer(opt.id, b, q));
            c.appendChild(b);
        });
        // Slide animation
        c.classList.remove('slide-in');
        void c.offsetWidth; // force reflow
        c.classList.add('slide-in');
        // Timer
        if (this.timerMax > 0) {
            this.$('timer-bar-container').style.display = 'block';
            this.startTimer();
        } else {
            this.$('timer-bar-container').style.display = 'none';
        }
    },

    answer(sel, btn, q) {
        if (this.answered) return;
        this.answered = true;
        this.stopTimer();
        const correct = q.answer;
        const isCorrect = sel === correct;

        if (this.examMode) {
            // Exam mode: no feedback, just record answer
            if (isCorrect) this.score += 3;
            else { this.score -= 1; this.wrong.push({ q, selected: sel }); }
            // Auto-advance after short delay
            setTimeout(() => this.nextQ(), 300);
            return;
        }

        // Normal mode: show feedback
        this.$('options-container').querySelectorAll('.option-btn').forEach(b => {
            b.disabled = true;
            const letter = b.querySelector('.option-letter').textContent.toLowerCase();
            if (letter === correct) {
                b.classList.add('correct');
                b.classList.add('pulse-correct');
            }
            else if (letter === sel && !isCorrect) {
                b.classList.add('wrong');
                b.classList.add('shake');
            }
        });
        if (isCorrect) this.score += 3;
        else { this.score -= 1; this.wrong.push({ q, selected: sel }); }
        // Show explanation
        if (q.explanation) {
            this.$('explanation-box').innerHTML = `<strong>💡 Explication :</strong> ${q.explanation}`;
            this.$('explanation-box').style.display = 'block';
        }
        this.$('score-text').textContent = `Score: ${this.score}`;
        this.$('next-btn').innerHTML = this.qIdx === this.questions.length - 1 ? 'Terminer ➔' : 'Suivant ➔';
        this.$('next-btn').classList.add('show');
    },

    timeoutAnswer(q) {
        if (this.answered) return;
        this.answered = true;
        this.score -= 1;
        this.wrong.push({ q, selected: 'timeout' });

        if (this.examMode) {
            setTimeout(() => this.nextQ(), 300);
            return;
        }

        this.$('options-container').querySelectorAll('.option-btn').forEach(b => {
            b.disabled = true;
            const letter = b.querySelector('.option-letter').textContent.toLowerCase();
            if (letter === q.answer) {
                b.classList.add('correct');
                b.classList.add('pulse-correct');
            }
        });
        if (q.explanation) {
            this.$('explanation-box').innerHTML = `<strong>⏰ Temps écoulé !</strong> ${q.explanation}`;
            this.$('explanation-box').style.display = 'block';
        } else {
            this.$('explanation-box').innerHTML = `<strong>⏰ Temps écoulé !</strong> La bonne réponse était : <strong>${q.answer.toUpperCase()}</strong>`;
            this.$('explanation-box').style.display = 'block';
        }
        this.$('score-text').textContent = `Score: ${this.score}`;
        this.$('next-btn').innerHTML = this.qIdx === this.questions.length - 1 ? 'Terminer ➔' : 'Suivant ➔';
        this.$('next-btn').classList.add('show');
    },

    nextQ() {
        if (this.qIdx < this.questions.length - 1) { this.qIdx++; this.renderQ(); }
        else this.showSummary();
    },

    // Timer
    startTimer() {
        this.timerVal = this.timerMax;
        const fill = this.$('timer-bar-fill');
        fill.style.width = '100%'; fill.classList.remove('danger');
        this.$('timer-label').textContent = this.timerVal + 's';
        this.timer = setInterval(() => {
            this.timerVal--;
            const pct = (this.timerVal / this.timerMax) * 100;
            fill.style.width = pct + '%';
            this.$('timer-label').textContent = this.timerVal + 's';
            if (this.timerVal <= 5) fill.classList.add('danger');
            if (this.timerVal <= 0) { this.stopTimer(); this.timeoutAnswer(this.questions[this.qIdx]); }
        }, 1000);
    },
    stopTimer() { if (this.timer) { clearInterval(this.timer); this.timer = null; } },

    // Summary
    showSummary() {
        this.stopTimer();
        const max = this.questions.length * 3;
        const pct = Math.max(0, Math.round((this.score / max) * 100));
        const correctCount = this.questions.length - this.wrong.length;
        this.$('final-score').textContent = pct + '%';
        this.$('final-score').style.color = pct >= 80 ? 'var(--success)' : pct < 50 ? 'var(--error)' : 'var(--af-blue)';
        this.$('final-stats').textContent = `${this.score} pts sur ${max} possibles (${correctCount}/${this.questions.length} bonnes réponses)`;
        // Category breakdown
        const catStats = {};
        this.questions.forEach(q => {
            const c = q.category || 'Autre';
            if (!catStats[c]) catStats[c] = { total: 0, correct: 0 };
            catStats[c].total++;
        });
        this.questions.forEach(q => {
            const c = q.category || 'Autre';
            if (!this.wrong.find(w => w.q.id === q.id)) catStats[c].correct++;
        });
        const bd = this.$('cat-breakdown'); bd.innerHTML = '';
        Object.entries(catStats).forEach(([cat, s]) => {
            const p = Math.round((s.correct / s.total) * 100);
            const color = p >= 80 ? 'var(--success)' : p < 50 ? 'var(--error)' : 'var(--warning)';
            bd.innerHTML += `<div class="cat-card"><div class="cat-name">${cat}</div><div class="cat-score" style="color:${color}">${p}%</div><div class="cat-detail">${s.correct}/${s.total} bonnes réponses</div></div>`;
        });
        // Review
        if (this.wrong.length > 0 && !this.examMode) {
            this.$('review-container').style.display = 'block';
            const rl = this.$('review-list'); rl.innerHTML = '';
            this.wrong.forEach(item => {
                const selOpt = item.selected === 'timeout' ? { text: '⏰ Temps écoulé' } : item.q.options.find(o => o.id === item.selected);
                const corOpt = item.q.options.find(o => o.id === item.q.answer);
                rl.innerHTML += `<div class="review-item"><div class="review-q">${item.q.id}. ${item.q.question}</div><div class="review-a"><span class="review-wrong">❌ ${selOpt ? selOpt.text : ''}</span><span class="review-correct">✅ ${corOpt.text}</span></div></div>`;
            });
        } else if (this.examMode && this.wrong.length > 0) {
            // Exam: show review after finishing
            this.$('review-container').style.display = 'block';
            const rl = this.$('review-list'); rl.innerHTML = '';
            this.wrong.forEach(item => {
                const selOpt = item.selected === 'timeout' ? { text: '⏰ Temps écoulé' } : item.q.options.find(o => o.id === item.selected);
                const corOpt = item.q.options.find(o => o.id === item.q.answer);
                rl.innerHTML += `<div class="review-item"><div class="review-q">${item.q.id}. ${item.q.question}</div><div class="review-a"><span class="review-wrong">❌ ${selOpt ? selOpt.text : ''}</span><span class="review-correct">✅ ${corOpt.text}</span>${item.q.explanation ? `<span class="review-correct" style="color:var(--text-secondary);font-style:italic;margin-top:0.3rem;">💡 ${item.q.explanation}</span>` : ''}</div></div>`;
            });
        } else {
            this.$('review-container').style.display = 'none';
        }
        // Save + track mastery
        this.saveSession(pct, correctCount, catStats);
        this.saveMastery();
        this.showScreen('summary-screen');
        // Confetti if great score
        if (pct >= 80) this.showConfetti();
    },

    // === FLASHCARDS ===
    startFC() {
        const cat = this.$('fc-cat-select').value;
        const countSel = this.$('fc-count-select');
        const maxCards = countSel ? parseInt(countSel.value) : 0;
        let pool = [...flashcardData];
        if (cat !== 'all') pool = pool.filter(f => f.category === cat);
        this.shuffle(pool);
        if (maxCards > 0) pool = pool.slice(0, maxCards);
        if (pool.length === 0) { alert('Aucune flashcard disponible pour cette sélection.'); return; }
        this.fcCards = pool; this.fcIdx = 0; this.fcKnown = 0;
        this.showScreen('flashcard-screen');
        this.renderFC();
    },
    renderFC() {
        if (this.fcIdx >= this.fcCards.length) { this.endFC(); return; }
        const card = this.fcCards[this.fcIdx];
        this.$('fc-front').textContent = card.front;
        this.$('fc-back').textContent = card.back;
        this.$('fc-progress').textContent = `Carte ${this.fcIdx + 1} sur ${this.fcCards.length}`;
        this.$('fc-count').textContent = `✅ ${this.fcKnown} connues`;
        this.$('fc-progress-fill').style.width = `${(this.fcIdx / this.fcCards.length) * 100}%`;
        // Category badge
        const badge = this.$('fc-cat-badge');
        if (badge) badge.querySelector('span').textContent = card.category || 'Général';
        document.getElementById('flashcard').classList.remove('flipped');
    },
    flipCard() { document.getElementById('flashcard').classList.toggle('flipped'); },
    fcMark(known) {
        if (known) this.fcKnown++;
        this.fcIdx++;
        this.renderFC();
    },
    endFC() {
        const pct = Math.round((this.fcKnown / this.fcCards.length) * 100);
        const color = pct >= 80 ? 'var(--success)' : pct < 50 ? 'var(--error)' : 'var(--warning)';
        this.$('fc-final-score').textContent = pct + '%';
        this.$('fc-final-score').style.color = color;
        this.$('fc-final-detail').textContent = `Vous connaissiez ${this.fcKnown} cartes sur ${this.fcCards.length}`;
        const barFill = this.$('fc-summary-bar-fill');
        barFill.style.background = pct >= 80 ? 'var(--success)' : pct < 50 ? 'var(--error)' : 'var(--warning)';
        this.showScreen('fc-summary-screen');
        // Animate bar after screen transition
        setTimeout(() => { barFill.style.width = pct + '%'; }, 100);
        if (pct >= 80) this.showConfetti();
    },

    // === CONFETTI ===
    showConfetti() {
        const canvas = document.createElement('canvas');
        canvas.className = 'confetti-canvas';
        document.body.appendChild(canvas);
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        const colors = ['#003087', '#C8102E', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'];
        const particles = Array.from({ length: 80 }, () => ({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height - canvas.height,
            w: Math.random() * 8 + 4,
            h: Math.random() * 6 + 3,
            color: colors[Math.floor(Math.random() * colors.length)],
            speed: Math.random() * 3 + 2,
            angle: Math.random() * 360,
            spin: (Math.random() - 0.5) * 8,
            drift: (Math.random() - 0.5) * 2
        }));
        let frame = 0;
        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate((p.angle * Math.PI) / 180);
                ctx.fillStyle = p.color;
                ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
                ctx.restore();
                p.y += p.speed;
                p.x += p.drift;
                p.angle += p.spin;
            });
            frame++;
            if (frame < 180) requestAnimationFrame(animate);
            else canvas.remove();
        };
        animate();
    },

    // === MASTERY ===
    renderMastery() {
        const mastered = JSON.parse(localStorage.getItem('psy0_mastered') || '{}');
        const total = qcmData.length;
        const count = Object.keys(mastered).length;
        const pct = Math.round((count / total) * 100);
        const circumference = 2 * Math.PI * 18; // r=18
        const offset = circumference - (pct / 100) * circumference;

        const container = this.$('mastery-container');
        if (count > 0) {
            container.style.display = '';
            this.$('mastery-pct').textContent = pct + '%';
            this.$('mastery-detail').textContent = `${count} / ${total} questions maîtrisées`;
            this.$('mastery-ring-fill').setAttribute('stroke-dashoffset', offset);
        } else {
            container.style.display = 'none';
        }
    },
    saveMastery() {
        const mastered = JSON.parse(localStorage.getItem('psy0_mastered') || '{}');
        this.questions.forEach(q => {
            if (!this.wrong.find(w => w.q.id === q.id)) {
                mastered[q.id] = true;
            }
        });
        localStorage.setItem('psy0_mastered', JSON.stringify(mastered));
    },

    // === STATS (localStorage) ===
    saveSession(pct, correct, catStats) {
        const history = JSON.parse(localStorage.getItem('psy0_history') || '[]');
        history.push({
            date: new Date().toLocaleDateString('fr-FR'),
            score: pct,
            correct,
            total: this.questions.length,
            wrong: this.wrong.map(w => w.q.id),
            mode: this.examMode ? 'exam' : 'normal'
        });
        if (history.length > 50) history.shift();
        localStorage.setItem('psy0_history', JSON.stringify(history));
        // Track weak questions
        const weakMap = JSON.parse(localStorage.getItem('psy0_weak') || '{}');
        this.wrong.forEach(w => { weakMap[w.q.id] = (weakMap[w.q.id] || 0) + 1; });
        localStorage.setItem('psy0_weak', JSON.stringify(weakMap));
    },

    getWeakQuestions(pool) {
        const weakMap = JSON.parse(localStorage.getItem('psy0_weak') || '{}');
        const sorted = Object.entries(weakMap).sort((a, b) => b[1] - a[1]).slice(0, 30);
        const weakIds = sorted.map(([id]) => parseInt(id));
        let result = pool.filter(q => weakIds.includes(q.id));
        if (result.length < 10) { this.shuffle(pool); result = pool.slice(0, 20); }
        this.shuffle(result);
        return result;
    },

    renderStats() {
        const history = JSON.parse(localStorage.getItem('psy0_history') || '[]');
        const weakMap = JSON.parse(localStorage.getItem('psy0_weak') || '{}');
        const mastered = JSON.parse(localStorage.getItem('psy0_mastered') || '{}');
        const c = this.$('stats-content');
        if (history.length === 0) {
            c.innerHTML = '<p style="text-align:center;color:var(--text-muted);padding:2rem 0;">Aucune session enregistrée.<br>Lancez un QCM pour voir vos statistiques !</p>';
            return;
        }
        const avg = Math.round(history.reduce((s, h) => s + h.score, 0) / history.length);
        const best = Math.max(...history.map(h => h.score));
        const totalQ = history.reduce((s, h) => s + h.total, 0);
        const masteredCount = Object.keys(mastered).length;

        let html = `<div class="stat-row"><span class="stat-label">Sessions effectuées</span><span class="stat-value">${history.length}</span></div>`;
        html += `<div class="stat-row"><span class="stat-label">Score moyen</span><span class="stat-value">${avg}%</span></div>`;
        html += `<div class="stat-row"><span class="stat-label">Meilleur score</span><span class="stat-value" style="color:var(--success)">${best}%</span></div>`;
        html += `<div class="stat-row"><span class="stat-label">Questions répondues</span><span class="stat-value">${totalQ}</span></div>`;
        html += `<div class="stat-row"><span class="stat-label">Questions maîtrisées</span><span class="stat-value">${masteredCount} / ${qcmData.length}</span></div>`;

        // Sparkline
        if (history.length >= 2) {
            html += this.renderSparkline(history.map(h => h.score));
        }

        // Weak questions
        const sorted = Object.entries(weakMap).sort((a, b) => b[1] - a[1]).slice(0, 5);
        if (sorted.length > 0) {
            html += `<div class="stat-section"><h3>🔴 Questions les plus ratées</h3>`;
            sorted.forEach(([id, count]) => {
                const q = qcmData.find(q => q.id === parseInt(id));
                if (q) html += `<div class="history-item"><span>${q.question}</span><span style="color:var(--error);font-weight:700">${count}×</span></div>`;
            });
            html += '</div>';
        }
        // History
        html += `<div class="stat-section"><h3>📋 Historique récent</h3>`;
        [...history].reverse().slice(0, 10).forEach(h => {
            const color = h.score >= 80 ? 'var(--success)' : h.score < 50 ? 'var(--error)' : 'var(--warning)';
            const badge = h.mode === 'exam' ? ' 🔒' : '';
            html += `<div class="history-item"><span>${h.date} · ${h.total} questions${badge}</span><span style="color:${color};font-weight:700">${h.score}%</span></div>`;
        });
        html += '</div>';
        c.innerHTML = html;
    },

    // === SPARKLINE ===
    renderSparkline(scores) {
        const w = 600, h = 80, pad = 10;
        const n = scores.length;
        const maxScore = 100;
        const points = scores.map((s, i) => {
            const x = pad + (i / (n - 1)) * (w - 2 * pad);
            const y = h - pad - (s / maxScore) * (h - 2 * pad);
            return { x, y };
        });
        const lineD = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ');
        const areaD = lineD + ` L${points[n - 1].x},${h - pad} L${points[0].x},${h - pad} Z`;
        const dots = points.map((p, i) => `<circle class="sparkline-dot" cx="${p.x}" cy="${p.y}" r="${i === n - 1 ? 4 : 2.5}" />`).join('');
        // Reference lines
        const y80 = h - pad - (80 / maxScore) * (h - 2 * pad);
        const y50 = h - pad - (50 / maxScore) * (h - 2 * pad);

        return `<div class="sparkline-container"><h4>📈 Évolution des scores</h4>
            <svg class="sparkline-svg" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
                <defs><linearGradient id="sparkGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="var(--af-blue)" stop-opacity="0.3"/>
                    <stop offset="100%" stop-color="var(--af-blue)" stop-opacity="0"/>
                </linearGradient></defs>
                <line x1="${pad}" y1="${y80}" x2="${w - pad}" y2="${y80}" stroke="var(--success)" stroke-width="0.5" stroke-dasharray="4,4" opacity="0.5"/>
                <line x1="${pad}" y1="${y50}" x2="${w - pad}" y2="${y50}" stroke="var(--error)" stroke-width="0.5" stroke-dasharray="4,4" opacity="0.5"/>
                <text x="${w - pad + 2}" y="${y80 + 3}" fill="var(--success)" font-size="8" opacity="0.6">80%</text>
                <text x="${w - pad + 2}" y="${y50 + 3}" fill="var(--error)" font-size="8" opacity="0.6">50%</text>
                <path class="sparkline-area" d="${areaD}" />
                <path class="sparkline-line" d="${lineD}" />
                ${dots}
            </svg></div>`;
    },

    // === EXPORT / IMPORT ===
    exportStats() {
        const data = {
            history: JSON.parse(localStorage.getItem('psy0_history') || '[]'),
            weak: JSON.parse(localStorage.getItem('psy0_weak') || '{}'),
            mastered: JSON.parse(localStorage.getItem('psy0_mastered') || '{}'),
            exportDate: new Date().toISOString()
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `psy0_stats_${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
    },
    importStats(event) {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = e => {
            try {
                const data = JSON.parse(e.target.result);
                if (data.history) localStorage.setItem('psy0_history', JSON.stringify(data.history));
                if (data.weak) localStorage.setItem('psy0_weak', JSON.stringify(data.weak));
                if (data.mastered) localStorage.setItem('psy0_mastered', JSON.stringify(data.mastered));
                this.renderStats();
                alert('✅ Statistiques importées avec succès !');
            } catch {
                alert('❌ Fichier invalide.');
            }
        };
        reader.readAsText(file);
        event.target.value = '';
    },

    clearStats() {
        if (confirm('Êtes-vous sûr de vouloir supprimer toutes vos statistiques ?')) {
            localStorage.removeItem('psy0_history');
            localStorage.removeItem('psy0_weak');
            localStorage.removeItem('psy0_mastered');
            this.renderStats();
            this.renderMastery();
        }
    },

    // Helpers
    shuffle(arr) { for (let i = arr.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1));[arr[i], arr[j]] = [arr[j], arr[i]]; } },
};

document.addEventListener('DOMContentLoaded', () => app.init());
