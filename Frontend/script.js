        const API_BASE = 'http://localhost:8000';

        let currentStore = JSON.parse(localStorage.getItem('shelfscan_store') || 'null');
        let currentScanId = null;
        let scanImageFile = null;

        // Page load
        window.addEventListener('load', () => {
            if (currentStore) {
                showScreen('dashboard');
                loadDashboard();
            } else {
                showScreen('login');
            }
            staggerAnimations();
        });

        // Screen transitions
        function showScreen(screenName) {
            document.querySelectorAll('.screen').forEach(s => {
                s.classList.add('hidden');
                s.style.animation = 'none';
            });
            const target = document.getElementById(screenName + 'Screen');
            target.classList.remove('hidden');
            setTimeout(() => {
                target.style.animation = 'fadeUp 0.6s ease forwards';
            }, 50);
        }

        // Stagger card animations
        function staggerAnimations() {
            document.querySelectorAll('.card, .stat-card').forEach((el, i) => {
                el.style.animationDelay = `${0.1 + i * 0.1}s`;
            });
        }

        // Toast notifications
        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.textContent = message;
            document.getElementById('toastContainer').appendChild(toast);
            setTimeout(() => {
                toast.classList.add('exit');
                setTimeout(() => toast.remove(), 400);
            }, 3500);
        }

        // Login handler
        async function handleLogin(event) {
            event.preventDefault();
            const phone = document.getElementById('loginPhone').value.replace(/\D/g, '');
            const btn = document.getElementById('loginBtn');
            const errorEl = document.getElementById('phoneError');

            if (phone.length !== 10) {
                errorEl.textContent = '⚠️ 10 digits ka WhatsApp number daaliye';
                errorEl.style.display = 'block';
                return;
            }

            btn.classList.add('btn-loading');
            btn.querySelector('.spinner').classList.remove('hidden');
            errorEl.style.display = 'none';

            try {
                const res = await fetch(`${API_BASE}/api/stores/login/${phone}`);
                if (res.ok) {
                    currentStore = await res.json();
                    localStorage.setItem('shelfscan_store', JSON.stringify(currentStore));
                    showScreen('dashboard');
                    loadDashboard();
                } else if (res.status === 404) {
                    showScreen('register');
                } else {
                    throw new Error('Server error');
                }
            } catch (e) {
                showToast('Server se connect nahi ho saka', 'error');
            } finally {
                btn.classList.remove('btn-loading');
                btn.querySelector('.spinner').classList.add('hidden');
            }
        }

        // Register handler
        async function handleRegister(event) {
            event.preventDefault();
            const formData = {
                owner_name: document.getElementById('regOwnerName').value,
                whatsapp_number: document.getElementById('loginPhone').value.replace(/\D/g, ''),
                store_name: document.getElementById('regStoreName').value,
                city: document.getElementById('regCity').value,
                pincode: document.getElementById('regPincode').value,
                store_type: document.getElementById('regStoreType').value
            };
            const btn = document.getElementById('regBtn');
            const errorEl = document.getElementById('regError');

            btn.classList.add('btn-loading');
            btn.querySelector('.spinner').classList.remove('hidden');

            try {
                const res = await fetch(`${API_BASE}/api/stores/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                if (res.ok) {
                    currentStore = await res.json();
                    localStorage.setItem('shelfscan_store', JSON.stringify(currentStore));
                    showScreen('dashboard');
                    loadDashboard();
                } else {
                    const err = await res.json();
                    errorEl.textContent = err.detail || 'Registration failed';
                    errorEl.style.display = 'block';
                }
            } catch (e) {
                showToast('Registration failed: ' + e.message, 'error');
            } finally {
                btn.classList.remove('btn-loading');
                btn.querySelector('.spinner').classList.add('hidden');
            }
        }

        // Load dashboard data
        async function loadDashboard() {
            if (!currentStore?.store_id) return;

            try {
                const res = await fetch(`${API_BASE}/api/dashboard/${currentStore.store_id}`);
                const data = await res.json();
                const stats = data.stats || {};

                document.getElementById('navStoreName').textContent = currentStore.store_name;
                document.getElementById('navOwnerName').textContent = currentStore.owner_name;

                animateCount('statTotalScans', stats.total_scans || 0);
                const health = stats.shelf_health_score || 0;
                document.getElementById('statHealthScore').style.color = getHealthColor(health);
                animateCount('statHealthScore', Math.round(health));
                animateCount('statCritical', stats.critical_items || 0);
                document.getElementById('statLastScan').textContent = stats.last_scan_at ? formatDate(stats.last_scan_at) : 'Never';

                // Recent scans
                const scans = data.recent_scans || [];
                document.getElementById('scansCount').textContent = `(${scans.length})`;
                const list = document.getElementById('recentScansList');
                if (scans.length === 0) {
                    list.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 3rem 1rem; font-style: italic;">Abhi tak koi scan nahi hua 📭<br><small>Upar wali photo upload karein</small></div>';
                } else {
                    list.innerHTML = scans.map(scan => `
                        <div class="scan-row" onclick="loadScanDetails('${scan.id}')">
                            <div class="health-badge" style="background: ${getHealthColor(scan.health_score || 0)}">${Math.round(scan.health_score || 0)}%</div>
                            <div style="flex: 1; margin-left: 1rem;">
                                <div>${formatDate(scan.created_at)}</div>
                                <div style="font-size: 0.9rem; color: var(--text-muted);">${scan.products_count || 0} products</div>
                            </div>
                            <div>→</div>
                        </div>
                    `).join('');
                }
            } catch (e) {
                showToast('Dashboard load failed', 'error');
            }
        }

        // Scan image select
        document.getElementById('scanImage').addEventListener('change', handleImageSelect);
        document.getElementById('dropZone').addEventListener('click', () => document.getElementById('scanImage').click());
        document.getElementById('dropZone').addEventListener('dragover', (e) => {
            e.preventDefault();
            document.getElementById('dropZone').classList.add('dragover');
        });
        document.getElementById('dropZone').addEventListener('dragleave', () => {
            document.getElementById('dropZone').classList.remove('dragover');
        });
        document.getElementById('dropZone').addEventListener('drop', (e) => {
            e.preventDefault();
            document.getElementById('dropZone').classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) handleImageSelect({ target: { files: [file] } });
        });

        function handleImageSelect(event) {
            const file = event.target.files[0];
            if (!file || !file.type.startsWith('image/')) return;
            scanImageFile = file;
            const preview = document.getElementById('imagePreview');
            const dropText = document.getElementById('dropText');
            const filenameEl = document.getElementById('filename');
            const btn = document.getElementById('scanBtn');
            preview.src = URL.createObjectURL(file);
            preview.classList.remove('hidden');
            dropText.style.display = 'none';
            filenameEl.textContent = file.name;
            filenameEl.style.display = 'block';
            btn.disabled = false;
        }

        // Scan handler
        async function handleScan() {
            if (!scanImageFile || !currentStore?.store_id) return;

            const btn = document.getElementById('scanBtn');
            const progress = document.getElementById('scanProgress');
            const steps = ['step1', 'step2', 'step3', 'step4'];

            btn.disabled = true;
            btn.textContent = 'Analysing...';
            progress.style.display = 'block';

            // Cycle steps
            let stepIdx = 0;
            const stepInterval = setInterval(() => {
                document.querySelectorAll('.progress-step').forEach(s => s.classList.remove('active'));
                document.getElementById(steps[stepIdx]).classList.add('active');
                stepIdx = (stepIdx + 1) % 4;
            }, 1000);

            try {
                const formData = new FormData();
                formData.append('store_id', currentStore.store_id);
                formData.append('image', scanImageFile);

                const res = await fetch(`${API_BASE}/api/scan`, {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();

                if (data.success) {
                    currentScanId = data.scan_id;
                    showScanResult(data);
                    document.getElementById('scanResultSection').scrollIntoView({ behavior: 'smooth' });
                } else {
                    throw new Error(data.error || 'Scan failed');
                }
            } catch (e) {
                showToast('Scan failed: ' + e.message, 'error');
            } finally {
                clearInterval(stepInterval);
                progress.style.display = 'none';
                btn.disabled = false;
                btn.textContent = '🔍 Analyse Karo';
            }
        }

        // Show scan result
        function showScanResult(data) {
            document.getElementById('scanResultSection').style.display = 'block';
            document.getElementById('recentScansCard').style.display = 'none';

            // Health circle
            const health = data.health_score || 0;
            const circle = document.getElementById('resultHealthCircle');
            circle.innerHTML = createCircularProgress(health, 140, 8);
            setTimeout(() => {
                circle.querySelector('.progress').style.strokeDashoffset = 283 - (283 * health / 100);
            }, 100);

            document.getElementById('visionSummary').textContent = data.vision_summary || 'No summary';

            // Counts
            const productsCount = data.products ? data.products.length : 0;
            const critical = data.products ? data.products.filter(p => p.stock_status === 'critical').length : 0;
            const low = data.products ? data.products.filter(p => p.stock_status === 'low').length : 0;
            document.getElementById('resultProductsCount').textContent = `${productsCount} Products`;
            document.getElementById('resultCriticalCount').textContent = `${critical} Critical`;
            document.getElementById('resultLowCount').textContent = `${low} Low`;

            // Voice
            if (data.voice_url) {
                const voiceCont = document.getElementById('resultVoiceContainer');
                const player = document.getElementById('voicePlayer');
                const download = document.getElementById('voiceDownload');
                player.src = data.voice_url;
                download.href = data.voice_url;
                voiceCont.style.display = 'block';
            }

            // Products grid
            const grid = document.getElementById('productsGrid');
            if (data.products) {
                grid.innerHTML = data.products.map(p => `
                    <div class="product-card">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">${p.product_name || 'Unknown'}</div>
                        <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.5rem;">${p.brand || ''}</div>
                        <div class="stock-badge stock-${p.stock_status || 'ok'}">${p.stock_status ? (p.stock_status === 'critical' ? '⚠️ Critical' : p.stock_status === 'low' ? '📉 Low Stock' : p.stock_status === 'ok' ? '✅ OK' : '📦 Overstocked') : 'Unknown'}</div>
                        <div style="font-size: 0.8rem; color: var(--text-dim); margin-top: 0.5rem;">Shelf ${p.shelf_position || '?'}</div>
                    </div>
                `).join('');
            }

            // Debates
            const debateCont = document.getElementById('debateContainer');
            if (data.debate_rounds) {
                const agents = {
                    presenter: '🎯 Presenter Agent',
                    critic: '🔥 Critic Agent',
                    decider: '⚡ Decider Agent'
                };
                const html = data.debate_rounds.map(round => {
                    const cls = round.agent_name.toLowerCase().replace(' ', '-');
                    return `
                        <div class="debate-section">
                            <button class="debate-header debate-${cls}" onclick="toggleDebate(this)">
                                ${agents[round.agent_name.toLowerCase()] || round.agent_name}
                            </button>
                            <div class="debate-body">
                                <div class="model-badge">${round.model_used || 'Unknown Model'}</div>
                                <div style="margin-top: 1rem; white-space: pre-wrap;">${round.recommendation || ''}</div>
                                ${round.reasoning ? `<details style="margin-top: 1rem;"><summary style="cursor: pointer; color: var(--text-muted);">Reasoning</summary><div style="margin-top: 0.5rem; padding: 1rem; background: var(--bg-card); border-radius: 8px; white-space: pre-wrap;">${round.reasoning}</div></details>` : ''}
                            </div>
                        </div>
                    `;
                }).join('');
                debateCont.innerHTML = html;
                // Default expand decider
                const decider = document.querySelector('.debate-decider');
                if (decider) toggleDebate(decider, true);
            }
        }

        function toggleDebate(header, forceOpen = false) {
            const body = header.nextElementSibling;
            const isOpen = body.classList.contains('active');
            if (forceOpen || !isOpen) {
                body.classList.add('active');
            } else {
                body.classList.remove('active');
            }
        }

        // Load scan details
        async function loadScanDetails(scanId) {
            try {
                const res = await fetch(`${API_BASE}/api/scan/${scanId}/details`);
                const data = await res.json();
                showScanResult(data);
                document.getElementById('scanResultSection').scrollIntoView({ behavior: 'smooth' });
            } catch (e) {
                showToast('Failed to load scan details', 'error');
            }
        }

        // Reset scan
        function resetScan() {
            document.getElementById('scanImage').value = '';
            document.getElementById('imagePreview').classList.add('hidden');
            document.getElementById('imagePreview').src = '';
            document.getElementById('dropText').style.display = 'block';
            document.getElementById('filename').style.display = 'none';
            document.getElementById('scanBtn').disabled = true;
            document.getElementById('scanResultSection').style.display = 'none';
            document.getElementById('recentScansCard').style.display = 'block';
            scanImageFile = null;
            currentScanId = null;
        }

        // Logout
        function logout() {
            localStorage.removeItem('shelfscan_store');
            currentStore = null;
            showScreen('login');
        }

        // Utilities
        function animateCount(id, target) {
            const el = document.getElementById(id);
            const start = parseInt(el.textContent) || 0;
            const duration = 800;
            const startTime = performance.now();
            function step(time) {
                const progress = Math.min((time - startTime) / duration, 1);
                el.textContent = Math.floor(progress * target + (1 - progress) * start);
                if (progress < 1) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        }

        function createCircularProgress(score, size, strokeWidth) {
            const r = (size - strokeWidth) / 2;
            const circ = 2 * Math.PI * r;
            const color = getHealthColor(score);
            return `
                <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
                    <defs>
                        <linearGradient id="healthGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="${color}"/>
                            <stop offset="100%" stop-color="${color}aa"/>
                        </linearGradient>
                    </defs>
                    <circle class="bg" cx="${size/2}" cy="${size/2}" r="${r}" stroke-dasharray="${circ}"/>
                    <circle class="progress" cx="${size/2}" cy="${size/2}" r="${r}" stroke-dashoffset="${circ}"/>
                    <text x="${size/2}" y="${size/2 + 6}" text-anchor="middle" fill="var(--text-primary)" font-family="'DM Mono', monospace" font-size="28" font-weight="500">${Math.round(score)}</text>
                    <text x="${size/2}" y="${size/2 + 28}" text-anchor="middle" fill="var(--text-muted)" font-size="14">%</text>
                </svg>
            `;
        }

        function getHealthColor(score) {
            if (score > 70) return 'var(--teal)';
            if (score > 50) return 'var(--orange)';
            return 'var(--red)';
        }

        function formatDate(isoStr) {
            const date = new Date(isoStr);
            const now = new Date();
            if (date.toDateString() === now.toDateString()) return 'Aaj';
            return date.toLocaleDateString('hi-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: 'numeric' });
        }
  