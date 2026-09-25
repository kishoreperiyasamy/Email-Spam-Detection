// Email Analysis Frontend Logic (AJAX / Fetch)

const SAMPLE_EMAILS = {
    phishing: {
        subject: "URGENT: Your PayPal Account Has Been Suspended",
        body: "Dear customer, We detected unauthorized login attempts from an unknown IP address. Your account is temporarily locked. Please verify your credentials and update your credit card immediately at http://192.168.1.55/paypal-verify to restore full access. Failure to do so within 24 hours will result in permanent account termination."
    },
    lottery: {
        subject: "CONGRATULATIONS! You have won $2,500,000 in the International Mega Lottery",
        body: "Official Notification: Your email address was selected in the category 'A' draws of the Euro Million Lottery. You have won a cash lump sum of $2,500,000.00 USD! Send your full name, passport copy, telephone number, and bank details to claim-dept@lottery-winner.biz to receive funds."
    },
    crypto: {
        subject: "GUARANTEED 500% RETURN: Next 100x Crypto Gem Revealed",
        body: "Don't miss the biggest crypto boom in history! Our secret AI automated trading bot guarantees 500% weekly returns. Deposit 0.05 BTC or $250 USDT today and watch your wallet grow automatically. Sign up: http://crypto-wealth-bot.io/invest"
    },
    work: {
        subject: "Project Status Update: Q3 Sprint Review Agenda and Deliverables",
        body: "Hi Team, Here is the agenda for tomorrow's Q3 sprint review at 10:00 AM in Conference Room B. We will review completed frontend components, database migration milestones, and test coverage. Please update your Jira tickets before the meeting. The slides are attached to the team drive. Best regards, Sarah."
    },
    photo_ad: {
        subject: "MEGA FLASH SALE: 70% Off Luxury Watches & Free Shipping",
        body: "FLASH SALE FLYER ATTACHED!\n[Photo Ad OCR Extraction]: Summer Clearance Event! Claim your 70% off promo voucher code 'MEGA70' today only. Limited stock available. Click here to buy now: http://watches-superdeal-promo.online/claim. Don't miss out - discount expires at midnight!",
        attachment: {
            filename: "flash_sale_flyer.jpg",
            file_type: "Photo / Image Ad",
            file_size_kb: 342.5
        }
    },
    pdf_brochure: {
        subject: "PRODUCT BROCHURE & INVOICE: Corporate Q3 Marketing Catalog",
        body: "Attached is our corporate sales brochure and billing prospectus.\n[Extracted from PDF Brochure]: Exclusive B2B catalog and discount schedule. Please remit invoice balance via direct wire transfer to lock in wholesale rates. Access billing portal here: http://portal-invoice-billing-verify.net/brochure-download.pdf",
        attachment: {
            filename: "Q3_Corporate_Brochure.pdf",
            file_type: "PDF Brochure / Document",
            file_size_kb: 1248.0
        }
    },
    receipt: {
        subject: "Your Amazon.com Order #112-984716 has been delivered",
        body: "Your package containing 'Data Science from Scratch by Joel Grus' was handed directly to a resident at your front door. If you did not receive this delivery, check your mailbox or contact customer service."
    }
};

let currentAttachmentInfo = null;

let currentDetectionId = null;

document.addEventListener('DOMContentLoaded', () => {
    const subjectInput = document.getElementById('subject');
    const bodyInput = document.getElementById('body');
    const analyzeBtn = document.getElementById('analyze-btn');
    const analyzeForm = document.getElementById('analyze-form');

    // Live word & character counters
    function updateCounters() {
        const text = `${subjectInput.value} ${bodyInput.value}`.trim();
        const charCount = text.length;
        const wordCount = text ? text.split(/\s+/).length : 0;
        
        const counterEl = document.getElementById('text-counters');
        if (counterEl) {
            counterEl.textContent = `${wordCount} words | ${charCount} characters`;
        }
    }

    if (subjectInput) subjectInput.addEventListener('input', updateCounters);
    if (bodyInput) bodyInput.addEventListener('input', updateCounters);

    // Attachment dropzone and file input handlers
    const dropzone = document.getElementById('dropzone');
    const attachmentFileInput = document.getElementById('attachment-file');

    if (dropzone && attachmentFileInput) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('drag-active');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('drag-active');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length) {
                handleUploadedFile(files[0]);
            }
        });

        attachmentFileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length) {
                handleUploadedFile(e.target.files[0]);
            }
        });
    }

    // Form submission via AJAX
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const subject = subjectInput.value.trim();
            const body = bodyInput.value.trim();

            if (!subject && !body) {
                showToast('Please enter an email subject, body, or upload an attachment.', 'warning');
                return;
            }

            // UI Loading state
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = `
                <span style="display:inline-block; animation: spin 1s linear infinite;">↻</span> Analyzing with TF-IDF &amp; Logistic Model...
            `;

            const resultCard = document.getElementById('result-card');
            const analyzingCard = document.getElementById('analyzing-card');
            const progressBarFill = document.getElementById('scan-progress-bar-fill');
            const progressLabel = document.getElementById('scan-progress-label');
            const progressTime = document.getElementById('scan-progress-time');

            if (resultCard) resultCard.style.display = 'none';
            if (analyzingCard) {
                analyzingCard.style.display = 'block';
                analyzingCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }

            // Reset steps to pending
            for (let i = 1; i <= 4; i++) {
                const stepEl = document.getElementById(`scan-step-${i}`);
                if (stepEl) {
                    stepEl.className = 'pipeline-step-item pending';
                    const tag = stepEl.querySelector('.step-status-tag');
                    if (tag) {
                        tag.textContent = 'WAITING';
                        tag.style.color = 'var(--text-muted)';
                    }
                }
            }

            if (progressBarFill) progressBarFill.style.width = '0%';
            if (progressTime) progressTime.textContent = '3.0s remaining';

            // 3-Second Active Scanning Sequence
            const totalDuration = 3000;
            const startTime = Date.now();

            function setStep(stepNum, state) {
                const stepEl = document.getElementById(`scan-step-${stepNum}`);
                if (!stepEl) return;
                const tag = stepEl.querySelector('.step-status-tag');
                if (state === 'active') {
                    stepEl.className = 'pipeline-step-item active';
                    if (tag) { tag.textContent = 'SCANNING...'; tag.style.color = 'var(--primary)'; }
                } else if (state === 'completed') {
                    stepEl.className = 'pipeline-step-item completed';
                    if (tag) { tag.textContent = 'VERIFIED ✓'; tag.style.color = 'var(--safe-green)'; }
                }
            }

            setStep(1, 'active');
            if (progressLabel) progressLabel.textContent = 'Step 1/4: Normalizing text tokens & regex parsing...';

            // 3-second Animation Sequence Promise
            const animationPromise = new Promise((resolve) => {
                const interval = setInterval(() => {
                    const elapsed = Date.now() - startTime;
                    const progress = Math.min(100, Math.round((elapsed / totalDuration) * 100));
                    const remainingSec = Math.max(0, ((totalDuration - elapsed) / 1000)).toFixed(1);

                    if (progressBarFill) progressBarFill.style.width = `${progress}%`;
                    if (progressTime) progressTime.textContent = `${remainingSec}s remaining`;

                    if (elapsed >= 750 && elapsed < 1500) {
                        setStep(1, 'completed');
                        setStep(2, 'active');
                        if (progressLabel) progressLabel.textContent = 'Step 2/4: Computing TF-IDF n-gram vectors...';
                    } else if (elapsed >= 1500 && elapsed < 2250) {
                        setStep(2, 'completed');
                        setStep(3, 'active');
                        if (progressLabel) progressLabel.textContent = 'Step 3/4: Evaluating Logistic Regression probability...';
                    } else if (elapsed >= 2250 && elapsed < 3000) {
                        setStep(3, 'completed');
                        setStep(4, 'active');
                        if (progressLabel) progressLabel.textContent = 'Step 4/4: Sandboxing links & threat heuristics...';
                    }

                    if (elapsed >= totalDuration) {
                        clearInterval(interval);
                        setStep(4, 'completed');
                        if (progressBarFill) progressBarFill.style.width = '100%';
                        if (progressLabel) progressLabel.textContent = 'Analysis complete!';
                        if (progressTime) progressTime.textContent = '0.0s';
                        resolve();
                    }
                }, 50);
            });

            try {
                // Fetch API and run 3-second animation concurrently
                const apiPromise = fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        subject, 
                        body, 
                        attachment_info: currentAttachmentInfo 
                    })
                }).then(res => res.json());

                const [result] = await Promise.all([apiPromise, animationPromise]);

                if (!result || !result.success) {
                    showToast(result?.error || 'Prediction failed. Please try again.', 'danger');
                    if (analyzingCard) analyzingCard.style.display = 'none';
                    return;
                }

                // Smoothly switch from analyzing card to result card
                if (analyzingCard) analyzingCard.style.display = 'none';
                renderPredictionResult(result.data);
                showToast('Email analysis completed in 3 seconds!', 'success');

                // Smooth scroll to results
                if (resultCard) {
                    resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }

            } catch (err) {
                console.error(err);
                showToast('Network error during prediction.', 'danger');
                if (analyzingCard) analyzingCard.style.display = 'none';
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = `
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    Analyze Email
                `;
            }
        });
    }
});

function loadSample(key) {
    const sample = SAMPLE_EMAILS[key];
    if (!sample) return;

    // Highlight active chip
    document.querySelectorAll('.preset-chip-btn').forEach(btn => btn.classList.remove('active'));
    if (window.event && window.event.currentTarget) {
        window.event.currentTarget.classList.add('active');
    }

    const subjectInput = document.getElementById('subject');
    const bodyInput = document.getElementById('body');
    if (subjectInput && bodyInput) {
        subjectInput.value = sample.subject;
        bodyInput.value = sample.body;
        
        // Trigger counter update
        subjectInput.dispatchEvent(new Event('input'));
        showToast(`Loaded scenario: ${sample.subject.substring(0, 32)}...`, 'info');
    }

    if (sample.attachment) {
        showAttachmentPreview(sample.attachment);
    } else {
        removeAttachment(false);
    }
}

function showAttachmentPreview(info) {
    currentAttachmentInfo = info;
    const card = document.getElementById('file-preview-card');
    const dropzone = document.getElementById('dropzone');
    const nameEl = document.getElementById('file-name');
    const typeBadge = document.getElementById('file-type-badge');
    const sizeEl = document.getElementById('file-size');
    const thumbEl = document.getElementById('file-thumb');
    const iconEl = document.getElementById('file-icon');
    const ocrBox = document.getElementById('ocr-progress-box');

    if (dropzone) dropzone.style.display = 'none';
    if (card) card.style.display = 'flex';

    if (nameEl) nameEl.textContent = info.filename;
    if (typeBadge) typeBadge.textContent = info.file_type || 'Attachment';
    if (sizeEl) sizeEl.textContent = `${info.file_size_kb || 0} KB`;
    if (ocrBox) ocrBox.style.display = 'none';

    if (info.thumbnailUrl && thumbEl) {
        thumbEl.src = info.thumbnailUrl;
        thumbEl.style.display = 'block';
        if (iconEl) iconEl.style.display = 'none';
    } else {
        if (thumbEl) thumbEl.style.display = 'none';
        if (iconEl) {
            iconEl.style.display = 'flex';
            iconEl.textContent = info.filename.endsWith('.pdf') ? '📄' : '📸';
        }
    }
}

function removeAttachment(clearInputs = true) {
    currentAttachmentInfo = null;
    const fileInput = document.getElementById('attachment-file');
    if (fileInput) fileInput.value = '';
    const card = document.getElementById('file-preview-card');
    const dropzone = document.getElementById('dropzone');
    if (card) card.style.display = 'none';
    if (dropzone) dropzone.style.display = 'flex';
    const thumbEl = document.getElementById('file-thumb');
    if (thumbEl) { thumbEl.src = ''; thumbEl.style.display = 'none'; }
}

async function handleUploadedFile(file) {
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    const isImage = ['png', 'jpg', 'jpeg', 'webp', 'bmp'].includes(ext);
    const isPdf = ext === 'pdf';
    const fileSizeKb = Math.round(file.size / 1024);

    let info = {
        filename: file.name,
        file_type: isImage ? 'Photo / Image Ad' : (isPdf ? 'PDF Brochure / Document' : 'Attachment'),
        file_size_kb: fileSizeKb
    };

    if (isImage) {
        const reader = new FileReader();
        reader.onload = (e) => {
            info.thumbnailUrl = e.target.result;
            showAttachmentPreview(info);
        };
        reader.readAsDataURL(file);
    } else {
        showAttachmentPreview(info);
    }

    const ocrBox = document.getElementById('ocr-progress-box');
    const ocrStatus = document.getElementById('ocr-status-text');
    const ocrPercent = document.getElementById('ocr-percent-text');
    const ocrBarFill = document.getElementById('ocr-bar-fill');
    const bodyInput = document.getElementById('body');
    const subjectInput = document.getElementById('subject');

    if (isImage) {
        if (ocrBox) ocrBox.style.display = 'block';
        if (ocrStatus) ocrStatus.textContent = 'Scanning photo text via Tesseract OCR...';
        if (ocrPercent) ocrPercent.textContent = '10%';
        if (ocrBarFill) ocrBarFill.style.width = '10%';

        try {
            if (window.Tesseract) {
                const worker = await Tesseract.createWorker('eng', 1, {
                    logger: m => {
                        if (m.status === 'recognizing text') {
                            const p = Math.round((m.progress || 0) * 100);
                            if (ocrStatus) ocrStatus.textContent = `Scanning photo text: ${p}%`;
                            if (ocrPercent) ocrPercent.textContent = `${p}%`;
                            if (ocrBarFill) ocrBarFill.style.width = `${p}%`;
                        }
                    }
                });

                const ret = await worker.recognize(file);
                await worker.terminate();

                const text = (ret.data && ret.data.text) ? ret.data.text.trim() : '';
                if (text) {
                    if (!subjectInput.value.trim()) {
                        const firstLine = text.split('\n')[0].substring(0, 60);
                        subjectInput.value = `[Photo Ad]: ${firstLine}`;
                    }
                    const prefix = `[OCR Content from ${file.name}]:\n`;
                    bodyInput.value = (bodyInput.value ? bodyInput.value + '\n\n' : '') + prefix + text;
                    subjectInput.dispatchEvent(new Event('input'));
                    showToast('Extracted photo text via OCR successfully!', 'success');
                } else {
                    showToast('Photo attached. Ready for analysis.', 'info');
                }
            } else {
                showToast('Photo attached.', 'info');
            }
        } catch (err) {
            console.error(err);
            showToast('Photo attached.', 'info');
        } finally {
            if (ocrBox) ocrBox.style.display = 'none';
        }
    } else if (isPdf || ['txt', 'eml'].includes(ext)) {
        if (ocrBox) ocrBox.style.display = 'block';
        if (ocrStatus) ocrStatus.textContent = 'Extracting brochure pages & hyperlinks...';
        if (ocrPercent) ocrPercent.textContent = '50%';
        if (ocrBarFill) ocrBarFill.style.width = '50%';

        try {
            const formData = new FormData();
            formData.append('file', file);

            const res = await fetch('/api/extract-document', {
                method: 'POST',
                body: formData
            });
            const respData = await res.json();

            if (respData.success && respData.data.extracted_text) {
                const extractedText = respData.data.extracted_text;
                if (!subjectInput.value.trim()) {
                    subjectInput.value = `[Brochure]: ${file.name.replace(/\.[^/.]+$/, '')}`;
                }
                const prefix = `[Extracted from ${respData.data.file_type} "${file.name}"]:\n`;
                bodyInput.value = (bodyInput.value ? bodyInput.value + '\n\n' : '') + prefix + extractedText;
                subjectInput.dispatchEvent(new Event('input'));
                showToast(`Extracted ${respData.data.page_count} page(s) from brochure!`, 'success');
            } else {
                showToast(respData.data?.notes?.[0] || 'Document attached.', 'info');
            }
        } catch (err) {
            console.error(err);
            showToast('Document attached.', 'info');
        } finally {
            if (ocrBox) ocrBox.style.display = 'none';
        }
    }
}

function renderPredictionResult(data) {
    currentDetectionId = data.detection_id;
    const resultCard = document.getElementById('result-card');
    if (!resultCard) return;

    resultCard.style.display = 'block';

    const isSpam = data.prediction === 'Spam';

    // 1. Verdict & Risk Badges
    const verdictBadge = document.getElementById('verdict-badge');
    if (verdictBadge) {
        verdictBadge.className = `badge ${isSpam ? 'badge-spam' : 'badge-safe'}`;
        verdictBadge.innerHTML = isSpam 
            ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"></polygon><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg> CLASSIFIED AS SPAM`
            : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg> CLASSIFIED AS NOT SPAM (SAFE)`;
    }

    const riskBadge = document.getElementById('risk-badge');
    if (riskBadge) {
        let riskClass = 'badge-risk-safe';
        if (data.risk_level === 'High Risk') riskClass = 'badge-risk-high';
        else if (data.risk_level === 'Suspicious') riskClass = 'badge-risk-suspicious';

        riskBadge.className = `badge ${riskClass}`;
        riskBadge.textContent = `Risk Level: ${data.risk_level}`;
    }

    // 2. Probabilities & Bars
    const spamPctEl = document.getElementById('spam-prob-pct');
    const safePctEl = document.getElementById('safe-prob-pct');
    const probBarEl = document.getElementById('prob-bar');

    if (spamPctEl) spamPctEl.textContent = `${data.spam_percentage}%`;
    if (safePctEl) safePctEl.textContent = `${data.not_spam_percentage}%`;

    if (probBarEl) {
        probBarEl.className = `prob-meter-bar ${isSpam ? 'spam' : 'safe'}`;
        probBarEl.style.width = '0%';
        setTimeout(() => {
            probBarEl.style.width = `${data.spam_percentage}%`;
        }, 50);
    }

    // 3. Supporting Indicators List
    const reasonsContainer = document.getElementById('reasons-container');
    if (reasonsContainer) {
        if (!data.reasons || data.reasons.length === 0) {
            reasonsContainer.innerHTML = `
                <div style="padding: 1rem; color: var(--text-secondary); background: #f8fafc; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
                    ✓ No suspicious spam indicators detected. The email appears authentic and normal in structure.
                </div>
            `;
        } else {
            let html = '';
            data.reasons.forEach(r => {
                const severityClass = r.severity ? r.severity.toLowerCase() : 'low';
                html += `
                    <div class="indicator-pill ${severityClass}">
                        <div style="flex-grow: 1;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                                <span style="font-weight: 700; font-size: 0.95rem; color: var(--text-primary);">${r.indicator}</span>
                                <span class="badge ${severityClass === 'high' ? 'badge-spam' : (severityClass === 'medium' ? 'badge-risk-suspicious' : 'badge-safe')}" style="font-size: 0.68rem;">${r.badge || r.category}</span>
                            </div>
                            <p style="font-size: 0.86rem; color: var(--text-secondary); margin: 0;">${r.description}</p>
                        </div>
                    </div>
                `;
            });
            reasonsContainer.innerHTML = html;
        }
    }

    // 4. URL Analysis Section
    const urlContainer = document.getElementById('url-analysis-container');
    if (urlContainer) {
        if (data.url_count === 0) {
            urlContainer.innerHTML = `<span style="color: var(--text-muted); font-size: 0.88rem;">No URLs detected in the email body.</span>`;
        } else {
            let urlsHtml = `<p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 8px;"><strong>${data.url_count} URL(s) detected:</strong></p><ul style="padding-left: 20px; font-size: 0.85rem; color: var(--text-muted);">`;
            data.urls_detected.forEach(u => {
                urlsHtml += `<li><code style="background: #f1f5f9; color: var(--text-primary); padding: 2px 6px; border-radius: 4px; border: 1px solid var(--border-color);">${u}</code> (Safe preview - not visited)</li>`;
            });
            urlsHtml += `</ul>`;
            urlContainer.innerHTML = urlsHtml;
        }
    }

    // Reset feedback buttons
    const feedbackStatus = document.getElementById('feedback-status');
    if (feedbackStatus) feedbackStatus.textContent = '';
}

async function sendFeedback(feedbackChoice) {
    if (!currentDetectionId) {
        showToast('No active detection to rate.', 'warning');
        return;
    }

    try {
        const res = await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                detection_id: currentDetectionId,
                feedback: feedbackChoice
            })
        });

        const data = await res.json();
        if (res.ok && data.success) {
            showToast(data.message, 'success');
            const statusEl = document.getElementById('feedback-status');
            if (statusEl) {
                statusEl.innerHTML = `<span style="color: var(--safe-green); font-weight:600;">✓ Marked as ${feedbackChoice}</span>`;
            }
        } else {
            showToast(data.error || 'Feedback submission failed', 'danger');
        }
    } catch (err) {
        showToast('Network error while saving feedback.', 'danger');
    }
}
