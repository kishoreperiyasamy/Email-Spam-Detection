import json
from flask import Blueprint, render_template, request, jsonify, session
from routes.auth_routes import login_required
from database.connection import get_db_cursor

history_bp = Blueprint('history', __name__)

@history_bp.route('/history')
@login_required
def history_page():
    return render_template('history.html')

@history_bp.route('/api/history', methods=['GET'])
@login_required
def get_user_history():
    user_id = session.get('user_id')
    query_search = request.args.get('search', '').strip()
    filter_pred = request.args.get('prediction', '').strip()
    filter_risk = request.args.get('risk_level', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    sql = """
        SELECT 
            d.id, 
            d.subject, 
            d.prediction, 
            d.spam_probability, 
            d.not_spam_probability, 
            d.risk_level, 
            d.reasons, 
            d.url_count, 
            d.created_at,
            f.feedback as user_feedback
        FROM email_detections d
        LEFT JOIN feedback f ON d.id = f.detection_id AND f.user_id = %s
        WHERE d.user_id = %s
    """
    params = [user_id, user_id]

    if query_search:
        sql += " AND (d.subject ILIKE %s OR d.body ILIKE %s)"
        search_pattern = f"%{query_search}%"
        params.extend([search_pattern, search_pattern])

    if filter_pred and filter_pred in ['Spam', 'Not Spam']:
        sql += " AND d.prediction = %s"
        params.append(filter_pred)

    if filter_risk and filter_risk in ['Safe', 'Suspicious', 'High Risk']:
        sql += " AND d.risk_level = %s"
        params.append(filter_risk)

    if date_from:
        sql += " AND d.created_at >= %s"
        params.append(f"{date_from} 00:00:00")

    if date_to:
        sql += " AND d.created_at <= %s"
        params.append(f"{date_to} 23:59:59")

    sql += " ORDER BY d.created_at DESC LIMIT 100;"

    try:
        with get_db_cursor(commit=False) as cur:
            cur.execute(sql, tuple(params))
            records = cur.fetchall()

            formatted = []
            for r in records:
                reasons_data = r['reasons']
                if isinstance(reasons_data, str):
                    try:
                        reasons_data = json.loads(reasons_data)
                    except Exception:
                        reasons_data = []

                formatted.append({
                    "id": r['id'],
                    "subject": r['subject'],
                    "prediction": r['prediction'],
                    "spam_probability": r['spam_probability'],
                    "not_spam_probability": r['not_spam_probability'],
                    "spam_percentage": round(r['spam_probability'] * 100, 1),
                    "risk_level": r['risk_level'],
                    "reasons": reasons_data or [],
                    "url_count": r['url_count'],
                    "created_at": r['created_at'].strftime("%b %d, %Y %I:%M %p"),
                    "user_feedback": r['user_feedback']
                })

            return jsonify({
                "success": True,
                "count": len(formatted),
                "data": formatted
            })
    except Exception as e:
        print(f"[History API Error] {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@history_bp.route('/api/history/<int:detection_id>', methods=['GET'])
@login_required
def get_detection_details(detection_id):
    user_id = session.get('user_id')
    user_role = session.get('user_role')

    try:
        with get_db_cursor(commit=False) as cur:
            if user_role == 'ADMIN':
                cur.execute("""
                    SELECT d.*, u.name as user_name, u.email as user_email, f.feedback as user_feedback
                    FROM email_detections d
                    LEFT JOIN users u ON d.user_id = u.id
                    LEFT JOIN feedback f ON d.id = f.detection_id
                    WHERE d.id = %s;
                """, (detection_id,))
            else:
                cur.execute("""
                    SELECT d.*, f.feedback as user_feedback
                    FROM email_detections d
                    LEFT JOIN feedback f ON d.id = f.detection_id AND f.user_id = %s
                    WHERE d.id = %s AND d.user_id = %s;
                """, (user_id, detection_id, user_id))

            record = cur.fetchone()
            if not record:
                return jsonify({"success": False, "error": "Record not found."}), 404

            reasons_data = record['reasons']
            if isinstance(reasons_data, str):
                try:
                    reasons_data = json.loads(reasons_data)
                except Exception:
                    reasons_data = []

            return jsonify({
                "success": True,
                "data": {
                    "id": record['id'],
                    "subject": record['subject'],
                    "body": record['body'],
                    "prediction": record['prediction'],
                    "spam_probability": record['spam_probability'],
                    "not_spam_probability": record['not_spam_probability'],
                    "spam_percentage": round(record['spam_probability'] * 100, 1),
                    "not_spam_percentage": round(record['not_spam_probability'] * 100, 1),
                    "risk_level": record['risk_level'],
                    "reasons": reasons_data or [],
                    "url_count": record['url_count'],
                    "created_at": record['created_at'].strftime("%b %d, %Y %I:%M %p"),
                    "user_feedback": record['user_feedback'],
                    "user_name": record.get('user_name'),
                    "user_email": record.get('user_email')
                }
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@history_bp.route('/api/feedback', methods=['POST'])
@login_required
def submit_feedback():
    data = request.get_json() or {}
    detection_id = data.get('detection_id')
    feedback_choice = data.get('feedback')
    user_id = session.get('user_id')

    if not detection_id or feedback_choice not in ['Correct', 'Incorrect']:
        return jsonify({"success": False, "error": "Valid detection_id and feedback ('Correct' or 'Incorrect') required."}), 400

    try:
        with get_db_cursor() as cur:
            # Verify detection belongs to user or user is admin
            if session.get('user_role') != 'ADMIN':
                cur.execute("SELECT id FROM email_detections WHERE id = %s AND user_id = %s;", (detection_id, user_id))
                if not cur.fetchone():
                    return jsonify({"success": False, "error": "Detection not found or unauthorized."}), 403

            cur.execute("""
                INSERT INTO feedback (detection_id, user_id, feedback)
                VALUES (%s, %s, %s)
                ON CONFLICT (detection_id, user_id) 
                DO UPDATE SET feedback = EXCLUDED.feedback, created_at = CURRENT_TIMESTAMP;
            """, (detection_id, user_id, feedback_choice))

        return jsonify({
            "success": True,
            "message": f"Feedback '{feedback_choice}' recorded successfully. Thank you for helping improve model evaluation!"
        })
    except Exception as e:
        print(f"[Feedback API Error] {e}")
        return jsonify({"success": False, "error": str(e)}), 500
