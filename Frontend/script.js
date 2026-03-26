const API_BASE = 'http://localhost:8000';
let currentStore = null;
let tempLoginPhone = "";
let selectedFile = null;

window.onload = () => {
    const stored = localStorage.getItem('shelfscan_store');
    if (stored) {
        try {
            currentStore = JSON.parse(stored);
            showScreen('dashboard');
            loadDashboard();
        } catch (e) {
            showScreen('login');
        }
    } else {
        showScreen('login');
    }
    setupDragDrop();
};

function showScreen(name) {
    document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
    const el = document.getElementById(name + 'Screen');
    if(el) el.classList.remove('hidden');
}

function showToast(msg, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerText = msg;
    container.appendChild(toast);
    
    void toast.offsetWidth; // Force reflow
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function formatDate(str) {
    if (!str) return 'N/A';
    const d = new Date(str);
    if (isNaN(d.getTime())) return str;
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: 'numeric' });
}

function getHealthColor(score) {
    if (score >= 70) return 'var(--success)';
    if (score >= 50) return 'var(--warning)';
    return 'var(--danger)';
}

async function handleLogin(e) {
    e.preventDefault();
    const phone = document.getElementById('loginPhone').value.trim();
    if (phone.length !== 10) return;
    
    tempLoginPhone = phone;
    const btn = document.getElementById('loginBtn');
    btn.disabled = true;
    btn.innerText = 'Checking...';

    try {
        const res = await fetch(`${API_BASE}/api/stores/login/${phone}`);
        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('shelfscan_store', JSON.stringify(data.store));
            currentStore = data.store;
            showScreen('dashboard');
            loadDashboard();
        } else if (res.status === 404) {
            showScreen('register');
        } else {
            showToast('Server error', 'error');
        }
    } catch (err) {
        showToast('Failed to connect to server', 'error');
                showToast('Failed to connect to the server.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Login / Register &rarr;';
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const btn = document.getElementById('regBtn');
    const errDiv = document.getElementById('regError');
    errDiv.classList.add('hidden');
    
    const payload = {
        owner_name: document.getElementById('regOwnerName').value.trim(),
        store_name: document.getElementById('regStoreName').value.trim(),
        city: document.getElementById('regCity').value.trim(),
        pincode: document.getElementById('regPincode').value.trim(),
        store_type: document.getElementById('regStoreType').value,
        whatsapp_number: tempLoginPhone
    };

    btn.disabled = true;
    btn.innerText = 'Registering...';

    try {
        const res = await fetch(`${API_BASE}/api/stores/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('shelfscan_store', JSON.stringify(data.store));
            currentStore = data.store;
            showScreen('dashboard');
            loadDashboard();
        } else {
            errDiv.innerText = data.detail || 'Registration failed';
            errDiv.classList.remove('hidden');
        }
    } catch (err) {
        errDiv.innerText = 'Failed to connect to server';
                errDiv.innerText = 'Failed to connect to the server.';
        errDiv.classList.remove('hidden');
    } finally {
        btn.disabled = false;
    btn.innerHTML = 'Register &rarr;';
        btn.innerHTML = 'Register Karo &rarr;';
    }
}

function logout() {
    localStorage.removeItem('shelfscan_store');
    currentStore = null;
    showScreen('login');
}

async function loadDashboard() {
    if (!currentStore) return;
    document.getElementById('navOwnerName').innerText = currentStore.owner_name;

    try {
        const res = await fetch(`${API_BASE}/api/dashboard/${currentStore.id}`);
        if (res.ok) {
            const data = await res.json();
            document.getElementById('statTotalScans').innerText = data.stats.total_scans;
            const hScore = data.stats.shelf_health_score || 0;
            const hEl = document.getElementById('statHealthScore');
            hEl.innerText = hScore + '%';
            hEl.style.color = getHealthColor(hScore);
            document.getElementById('statCritical').innerText = data.stats.critical_items;
            document.getElementById('statLastScan').innerText = formatDate(data.store.last_scan_at);
        }
        fetchRecentScans();
    } catch (err) {
        console.error("Dashboard error", err);
    }
}

async function fetchRecentScans() {
    try {
        const res = await fetch(`${API_BASE}/api/scans/${currentStore.id}`);
        if (res.ok) {
            const data = await res.json();
            const container = document.getElementById('recentScansList');
            container.innerHTML = '';
            if (!data.scans || data.scans.length === 0) {
                container.innerHTML = '<div class="text-muted text-center italic py-4">No scans yet</div>';
                container.innerHTML = '<div class="text-muted text-center italic py-4">Abhi tak koi scan nahi hua</div>';
                return;
            }
            data.scans.forEach(scan => {
                const score = scan.shelf_health_score || 0;
                const div = document.createElement('div');
                div.className = 'scan-row';
                div.innerHTML = `
                    <div>
                        <div class="font-bold">${formatDate(scan.created_at)}</div>
                        <div class="text-sm text-muted">${scan.products_detected || 0} items detected</div>
                    </div>
                    <div class="badge" style="background: ${getHealthColor(score)}33; color: ${getHealthColor(score)}">Score: ${score}%</div>
                `;
                container.appendChild(div);
            });
        }
    } catch (err) {
        console.error(err);
    }
}

function setupDragDrop() {
    const dropZone = document.getElementById('dropZone');
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) processFile(e.dataTransfer.files[0]);
    });
}

function handleImageSelect(e) {
    if (e.target.files && e.target.files[0]) processFile(e.target.files[0]);
}

function processFile(file) {
    if (!file.type.startsWith('image/')) {
        showToast('Please select an image file', 'error');
        return;
    }
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('imagePreview').src = e.target.result;
        document.getElementById('imagePreview').classList.remove('hidden');
        document.getElementById('dropText').classList.add('hidden');
                document.getElementById('dropText').innerText = 'Image selected.';
        document.getElementById('scanBtn').disabled = false;
    };
    reader.readAsDataURL(file);
}

async function handleScan() {
    if (!selectedFile || !currentStore) return;
    const btn = document.getElementById('scanBtn');
    const progress = document.getElementById('scanProgress');
    const fill = progress.querySelector('.progress-fill');
    
    btn.disabled = true;
    btn.innerText = 'Analyzing...';
    progress.style.display = 'block';
    fill.style.width = '50%';

    const formData = new FormData();
    formData.append('store_id', currentStore.id);
    formData.append('image', selectedFile);

    try {
        const res = await fetch(`${API_BASE}/api/scan`, { method: 'POST', body: formData });
        fill.style.width = '100%';
        if (res.ok) {
            const data = await res.json();
            showScanResult(data);
            loadDashboard();
        } else {
            const err = await res.json();
            showToast(err.detail || 'Scan failed', 'error');
            resetScanInput();
        }
    } catch (err) {
        showToast('Network error during scan', 'error');
        resetScanInput();
    }
}

function resetScanInput() {
    const btn = document.getElementById('scanBtn');
    const progress = document.getElementById('scanProgress');
    btn.disabled = false;
    btn.innerText = '🔍 Analyse Karo';
            btn.innerText = '🔍 Analyze Shelf';
    progress.style.display = 'none';
}

function resetScan() {
    selectedFile = null;
    document.getElementById('scanImage').value = '';
    document.getElementById('imagePreview').classList.add('hidden');
    document.getElementById('dropText').classList.remove('hidden');
            document.getElementById('dropText').innerText = '📸 Drop your photo here or click to upload.';
    document.getElementById('scanBtn').disabled = true;
    document.getElementById('scanProgress').style.display = 'none';
    document.getElementById('scanProgress').querySelector('.progress-fill').style.width = '0%';
    document.getElementById('scanResultSection').classList.add('hidden');
    document.getElementById('scanInputSection').classList.remove('hidden');
}

function showScanResult(data) {
    document.getElementById('scanInputSection').classList.add('hidden');
    document.getElementById('scanResultSection').classList.remove('hidden');

    const hScore = data.shelf_health_score || 0;
    const hCircle = document.getElementById('healthCircle');
    hCircle.innerText = hScore;
    hCircle.style.borderColor = getHealthColor(hScore);
    hCircle.style.color = getHealthColor(hScore);

    const voiceContainer = document.getElementById('voiceContainer');
    const voicePlayer = document.getElementById('voicePlayer');
    if (data.voice_note_url) {
        voicePlayer.src = data.voice_note_url;
        voiceContainer.classList.remove('hidden');
    } else {
        voiceContainer.classList.add('hidden');
    }

    const grid = document.getElementById('productsGrid');
    grid.innerHTML = '';
    const products = data.vision_analysis?.products || [];
    if (products.length === 0) {
        grid.innerHTML = '<div class="text-muted text-sm">No products detected</div>';
    } else {
        products.forEach(p => {
            const stock = p.stock_level || 'ok';
            let badgeClass = 'badge-ok';
            if (stock === 'critical') badgeClass = 'badge-critical';
            else if (stock === 'low') badgeClass = 'badge-low';
            else if (stock === 'overstocked') badgeClass = 'badge-overstocked';
            grid.innerHTML += `
                <div class="product-card">
                    <div class="font-bold">${p.name || p.product_name || 'Unknown'}</div>
                    <div class="text-muted text-sm">${p.brand || 'No brand'}</div>
                    <div class="badge ${badgeClass}">${stock.toUpperCase()}</div>
                </div>
            `;
        });
    }

    const debateCont = document.getElementById('debateContainer');
    debateCont.innerHTML = '';
    const rounds = data.debate_rounds || [];
    rounds.forEach(r => {
        let agentClass = '';
        if (r.type === 'presenter') agentClass = 'agent-presenter';
        if (r.type === 'critic') agentClass = 'agent-critic';
        if (r.type === 'decider') agentClass = 'agent-decider';

        let rawContent = typeof r.recommendation === 'string' ? r.recommendation : JSON.stringify(r.recommendation, null, 2);
        const div = document.createElement('div');
        div.className = `debate-card ${agentClass}`;
        div.innerHTML = `
            <div class="debate-header" onclick="this.parentElement.classList.toggle('open')">
                <div class="font-bold">${r.agent_name.toUpperCase()}</div>
                <div class="text-xs text-muted">Model: ${r.agent_type || 'AI'} ▼</div>
            </div>
            <div class="debate-body">${rawContent}</div>
        `;
        debateCont.appendChild(div);
    });
}