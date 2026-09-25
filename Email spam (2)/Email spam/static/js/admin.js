// Admin Dashboard & Management Logic

document.addEventListener('DOMContentLoaded', () => {
    initAdminCharts();
});

async function initAdminCharts() {
    const trendsCanvas = document.getElementById('chart-daily-trends');
    const riskCanvas = document.getElementById('chart-risk-dist');

    if (!trendsCanvas && !riskCanvas) return;

    try {
        const res = await fetch('/admin/api/stats');
        const data = await res.json();

        if (!res.ok || !data.success) return;

        // 1. Daily Trends Chart
        if (trendsCanvas && window.Chart) {
            const daily = data.daily_trends;
            const labels = daily.map(d => d.day);
            const spamCounts = daily.map(d => parseInt(d.spam_count));
            const safeCounts = daily.map(d => parseInt(d.safe_count));

            new Chart(trendsCanvas, {
                type: 'bar',
                data: {
                    labels: labels.length ? labels : ['No Data'],
                    datasets: [
                        {
                            label: 'Spam Detected',
                            data: spamCounts.length ? spamCounts : [0],
                            backgroundColor: 'rgba(239, 68, 68, 0.75)',
                            borderColor: '#ef4444',
                            borderWidth: 1,
                            borderRadius: 6
                        },
                        {
                            label: 'Legitimate (Safe)',
                            data: safeCounts.length ? safeCounts : [0],
                            backgroundColor: 'rgba(16, 185, 129, 0.75)',
                            borderColor: '#10b981',
                            borderWidth: 1,
                            borderRadius: 6
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#334155', font: { weight: '600' } }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(0, 0, 0, 0.05)' },
                            ticks: { color: '#64748b' }
                        },
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(0, 0, 0, 0.05)' },
                            ticks: { color: '#64748b', stepSize: 1 }
                        }
                    }
                }
            });
        }

        // 2. Risk Distribution Chart
        if (riskCanvas && window.Chart) {
            const r = data.risk_distribution;
            new Chart(riskCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['Safe', 'Suspicious', 'High Risk'],
                    datasets: [{
                        data: [r.safe || 0, r.suspicious || 0, r.high_risk || 0],
                        backgroundColor: [
                            'rgba(16, 185, 129, 0.85)',
                            'rgba(245, 158, 11, 0.85)',
                            'rgba(239, 68, 68, 0.85)'
                        ],
                        borderColor: '#ffffff',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#334155', boxWidth: 14, font: { weight: '500' } }
                        }
                    }
                }
            });
        }

    } catch (err) {
        console.error("Admin stats chart error:", err);
    }
}

async function toggleUserStatus(userId, currentStatus) {
    const actionText = currentStatus ? "deactivate" : "activate";
    if (!confirm(`Are you sure you want to ${actionText} this user?`)) return;

    try {
        const res = await fetch(`/admin/api/users/${userId}/toggle-status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await res.json();
        if (res.ok && data.success) {
            showToast(data.message, 'success');
            setTimeout(() => window.location.reload(), 600);
        } else {
            showToast(data.error || 'Operation failed.', 'danger');
        }
    } catch (err) {
        showToast('Network error while updating user status.', 'danger');
    }
}
