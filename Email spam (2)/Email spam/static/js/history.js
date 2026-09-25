// Detection History Logic

let activeHistoryId = null;

document.addEventListener('DOMContentLoaded', () => {
    loadHistory();

    const searchInput = document.getElementById('history-search');
    const predSelect = document.getElementById('filter-prediction');
    const riskSelect = document.getElementById('filter-risk');
    const dateFrom = document.getElementById('filter-date-from');
    const dateTo = document.getElementById('filter-date-to');

    // Debounced search
    let debounceTimer;
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => loadHistory(), 300);
        });
    }

    if (predSelect) predSelect.addEventListener('change', loadHistory);
    if (riskSelect) riskSelect.addEventListener('change', loadHistory);
    if (dateFrom) dateFrom.addEventListener('change', loadHistory);
    if (dateTo) dateTo.addEventListener('change', loadHistory);
});

async function loadHistory() {
    const tableBody = document.getElementById('history-table-body');
    const emptyState = document.getElementById('history-empty');
    if (!tableBody) return;

    const search = document.getElementById('history-search')?.value || '';
    const prediction = document.getElementById('filter-prediction')?.value || '';
    const risk = document.getElementById('filter-risk')?.value || '';
    const dateFrom = document.getElementById('filter-date-from')?.value || '';
    const dateTo = document.getElementById('filter-date-to')?.value || '';

    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (prediction) params.append('prediction', prediction);
    if (risk) params.append('risk_level', risk);
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);

    tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">Loading history...</td></tr>`;

    try {
        const res = await fetch(`/api/history?${params.toString()}`);
        const result = await res.json();

        if (!res.ok || !result.success) {
            tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--spam-red); padding: 1.5rem;">Failed to load records.</td></tr>`;
            return;
        }

        const items = result.data;
        if (items.length === 0) {
            tableBody.innerHTML = '';
            if (emptyState) emptyState.style.display = 'block';
            return;
        }

        if (emptyState) emptyState.style.display = 'none';

        let html = '';
        items.forEach(item => {
            const isSpam = item.prediction === 'Spam';
            const riskClass = item.risk_level === 'High Risk' ? 'badge-risk-high' : (item.risk_level === 'Suspicious' ? 'badge-risk-suspicious' : 'badge-risk-safe');
            const feedbackBadge = item.user_feedback 
                ? `<span style="font-size: 0.75rem; color: ${item.user_feedback === 'Correct' ? 'var(--safe-green)' : 'var(--spam-red)'}; font-weight:600;">✓ ${item.user_feedback}</span>`
                : `<span style="color: var(--text-muted); font-size: 0.75rem;">None</span>`;

            html += `
                <tr>
                    <td class="font-mono" style="font-size: 0.8rem; color: var(--text-muted);">#${item.id}</td>
                    <td style="font-weight: 600; max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${item.subject || '<em style="color:var(--text-muted)">[No Subject]</em>'}
                    </td>
                    <td>
                        <span class="badge ${isSpam ? 'badge-spam' : 'badge-safe'}">${item.prediction}</span>
                    </td>
                    <td>
                        <div style="font-weight: 700; font-size: 0.88rem; color: ${isSpam ? 'var(--spam-red)' : 'var(--safe-green)'}">
                            ${item.spam_percentage}%
                        </div>
                    </td>
                    <td>
                        <span class="badge ${riskClass}">${item.risk_level}</span>
                    </td>
                    <td style="font-size: 0.82rem; color: var(--text-muted);">${item.created_at}</td>
                    <td>
                        <button class="btn btn-secondary btn-sm" onclick="viewHistoryDetails(${item.id})">
                            View Details
                        </button>
                    </td>
                </tr>
            `;
        });

        tableBody.innerHTML = html;

    } catch (err) {
        console.error(err);
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--spam-red); padding: 1.5rem;">Network error fetching history.</td></tr>`;
    }
}

async function viewHistoryDetails(id) {
    activeHistoryId = id;
    const modal = document.getElementById('details-modal');
    if (!modal) return;

    try {
        const res = await fetch(`/api/history/${id}`);
        const result = await res.json();
        if (!res.ok || !result.success) {
            showToast('Unable to fetch detection details.', 'danger');
            return;
        }

        const d = result.data;
        document.getElementById('modal-id').textContent = `#${d.id}`;
        document.getElementById('modal-subject').textContent = d.subject || '[No Subject]';
        document.getElementById('modal-body').textContent = d.body;
        document.getElementById('modal-date').textContent = d.created_at;

        const isSpam = d.prediction === 'Spam';
        const modalPred = document.getElementById('modal-prediction');
        modalPred.className = `badge ${isSpam ? 'badge-spam' : 'badge-safe'}`;
        modalPred.textContent = d.prediction;

        const modalRisk = document.getElementById('modal-risk');
        const riskClass = d.risk_level === 'High Risk' ? 'badge-risk-high' : (d.risk_level === 'Suspicious' ? 'badge-risk-suspicious' : 'badge-risk-safe');
        modalRisk.className = `badge ${riskClass}`;
        modalRisk.textContent = d.risk_level;

        document.getElementById('modal-spam-pct').textContent = `${d.spam_percentage}%`;
        document.getElementById('modal-safe-pct').textContent = `${d.not_spam_percentage}%`;
        document.getElementById('modal-url-count').textContent = d.url_count;

        // Render reasons
        const reasonsBox = document.getElementById('modal-reasons');
        if (reasonsBox) {
            if (!d.reasons || d.reasons.length === 0) {
                reasonsBox.innerHTML = `<span style="color: var(--text-muted); font-size: 0.88rem;">No suspicious signals detected.</span>`;
            } else {
                let rHtml = '';
                d.reasons.forEach(r => {
                    const sev = r.severity ? r.severity.toLowerCase() : 'low';
                    rHtml += `
                        <div class="indicator-pill ${sev}" style="padding: 8px 12px; margin-bottom: 6px;">
                            <div>
                                <strong style="color: var(--text-primary); font-size: 0.88rem;">${r.indicator}</strong>
                                <p style="margin: 2px 0 0; font-size: 0.82rem; color: var(--text-secondary);">${r.description}</p>
                            </div>
                        </div>
                    `;
                });
                reasonsBox.innerHTML = rHtml;
            }
        }

        // Render feedback status
        const fbStatus = document.getElementById('modal-feedback-status');
        if (fbStatus) {
            fbStatus.innerHTML = d.user_feedback 
                ? `Current Rating: <strong style="color: var(--cyan);">${d.user_feedback}</strong>`
                : `No feedback submitted yet.`;
        }

        modal.classList.add('active');
    } catch (err) {
        showToast('Error displaying details modal.', 'danger');
    }
}

function closeDetailsModal() {
    const modal = document.getElementById('details-modal');
    if (modal) modal.classList.remove('active');
}

async function submitModalFeedback(choice) {
    if (!activeHistoryId) return;

    try {
        const res = await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                detection_id: activeHistoryId,
                feedback: choice
            })
        });
        const data = await res.json();
        if (res.ok && data.success) {
            showToast(data.message, 'success');
            const fbStatus = document.getElementById('modal-feedback-status');
            if (fbStatus) fbStatus.innerHTML = `Updated Rating: <strong style="color: var(--safe-green);">${choice}</strong>`;
            loadHistory();
        } else {
            showToast(data.error || 'Failed to submit feedback.', 'danger');
        }
    } catch (err) {
        showToast('Network error while saving feedback.', 'danger');
    }
}
