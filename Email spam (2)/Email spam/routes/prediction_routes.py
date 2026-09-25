import json
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from routes.auth_routes import login_required
from services.prediction_service import prediction_service
from database.connection import get_db_cursor

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('predict.dashboard'))
    return render_template('index.html')

@predict_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    stats = {
        "total_analyzed": 0,
        "spam_count": 0,
        "safe_count": 0,
        "spam_percentage": 0.0,
        "suspicious_count": 0,
        "high_risk_count": 0
    }
    recent_detections = []

    try:
        with get_db_cursor(commit=False) as cur:
            # 1. Aggregated statistics for current user
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN prediction = 'Spam' THEN 1 END) as spam,
                    COUNT(CASE WHEN prediction = 'Not Spam' THEN 1 END) as safe,
                    COUNT(CASE WHEN risk_level = 'Suspicious' THEN 1 END) as suspicious,
                    COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) as high_risk
                FROM email_detections 
                WHERE user_id = %s;
            """, (user_id,))
            row = cur.fetchone()
            if row and row['total'] > 0:
                stats["total_analyzed"] = row['total']
                stats["spam_count"] = row['spam']
                stats["safe_count"] = row['safe']
                stats["suspicious_count"] = row['suspicious']
                stats["high_risk_count"] = row['high_risk']
                stats["spam_percentage"] = round((row['spam'] / row['total']) * 100, 1)

            # 2. Recent detections (last 5)
            cur.execute("""
                SELECT id, subject, prediction, spam_probability, risk_level, url_count, created_at 
                FROM email_detections 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 5;
            """, (user_id,))
            recent_detections = cur.fetchall()

    except Exception as e:
        print(f"[Dashboard Error] Failed to load user metrics: {e}")

    return render_template('dashboard.html', stats=stats, recent_detections=recent_detections)

from services.document_extractor import extract_text_from_file

@predict_bp.route('/analyze')
@login_required
def analyze():
    return render_template('analyze.html')

@predict_bp.route('/api/extract-document', methods=['POST'])
def api_extract_document():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded."}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({"success": False, "error": "Empty filename."}), 400

    try:
        extraction_result = extract_text_from_file(file)
        return jsonify({
            "success": extraction_result.get("success", True),
            "data": extraction_result
        })
    except Exception as e:
        print(f"[Document Extraction Error] {e}")
        return jsonify({"success": False, "error": f"Extraction failed: {str(e)}"}), 500

@predict_bp.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    data = request.get_json() or {}
    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()
    attachment_info = data.get('attachment_info')

    if not subject and not body:
        return jsonify({
            "success": False,
            "error": "Please enter an email subject or body to analyze."
        }), 400

    try:
        user_id = session.get('user_id')
        result = prediction_service.predict_email(subject, body, user_id=user_id, attachment_info=attachment_info)
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        print(f"[API Predict Error] {e}")
        return jsonify({
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }), 500
