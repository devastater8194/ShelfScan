// Dummy Data (since Flask backend is removed)
let scans = [];

const chartLabels = [];
const chartData = [];

// Chart setup
const ctx = document.getElementById('scanChart').getContext('2d');

const scanChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: chartLabels,
        datasets: [{
            label: 'Scans',
            data: chartData
        }]
    }
});

// Handle Upload
document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const fileInput = document.getElementById('imageInput');
    const file = fileInput.files[0];

    if (!file) return;

    const newScan = {
        id: Date.now(),
        created_at: new Date().toLocaleString(),
        result: "Shelf analyzed successfully (demo result)"
    };

    scans.push(newScan);

    // Update chart
    chartLabels.push(newScan.created_at);
    chartData.push(Math.floor(Math.random() * 10) + 1);
    scanChart.update();

    renderHistory();
});

// Render History
function renderHistory() {
    const container = document.getElementById('historyContainer');
    container.innerHTML = "";

    scans.forEach(scan => {
        const div = document.createElement('div');
        div.className = "history-item";

        div.innerHTML = `
            <div>
                <strong>${scan.created_at}</strong>
                <p>${scan.result.substring(0,80)}...</p>
            </div>
            <button class="delete-btn" onclick="deleteScan(${scan.id})">Delete</button>
        `;

        container.appendChild(div);
    });
}

// Delete Scan
function deleteScan(id) {
    scans = scans.filter(scan => scan.id !== id);
    renderHistory();
}