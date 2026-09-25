// User Dashboard Interactive Analytics & Chart.js Visualizer

document.addEventListener('DOMContentLoaded', () => {
    initUserThreatChart();
});

function initUserThreatChart() {
    const chartCanvas = document.getElementById('userThreatChart');
    if (!chartCanvas || !window.Chart) return;

    const safeCount = parseInt(chartCanvas.getAttribute('data-safe') || '0', 10);
    const suspiciousCount = parseInt(chartCanvas.getAttribute('data-suspicious') || '0', 10);
    const highRiskCount = parseInt(chartCanvas.getAttribute('data-high-risk') || '0', 10);
    const totalCount = safeCount + suspiciousCount + highRiskCount;

    // Center text plugin for doughnut chart
    const centerTextPlugin = {
        id: 'centerTextPlugin',
        afterDraw(chart) {
            const { ctx, chartArea: { top, bottom, left, right } } = chart;
            ctx.save();
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            const centerX = (left + right) / 2;
            const centerY = (top + bottom) / 2;

            ctx.font = '800 1.6rem Inter, sans-serif';
            ctx.fillStyle = '#0f172a';
            ctx.fillText(totalCount > 0 ? `${totalCount}` : '0', centerX, centerY - 8);

            ctx.font = '600 0.75rem Inter, sans-serif';
            ctx.fillStyle = '#64748b';
            ctx.fillText(totalCount === 1 ? 'EMAIL' : 'EMAILS', centerX, centerY + 14);

            ctx.restore();
        }
    };

    const dataValues = totalCount > 0 ? [safeCount, suspiciousCount, highRiskCount] : [1, 0, 0];
    const bgColors = totalCount > 0 
        ? ['#10b981', '#f59e0b', '#ef4444'] 
        : ['#e2e8f0', '#e2e8f0', '#e2e8f0'];

    new Chart(chartCanvas, {
        type: 'doughnut',
        data: {
            labels: ['Safe', 'Suspicious', 'High Risk'],
            datasets: [{
                data: dataValues,
                backgroundColor: bgColors,
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '72%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: totalCount > 0,
                    backgroundColor: 'rgba(15, 23, 42, 0.92)',
                    titleFont: { size: 13, family: 'Inter', weight: '700' },
                    bodyFont: { size: 12, family: 'Inter' },
                    padding: 10,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const count = context.raw || 0;
                            const pct = totalCount > 0 ? Math.round((count / totalCount) * 100) : 0;
                            return ` ${context.label}: ${count} (${pct}%)`;
                        }
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 1000,
                easing: 'easeOutQuart'
            }
        },
        plugins: [centerTextPlugin]
    });
}
