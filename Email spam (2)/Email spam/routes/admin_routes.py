import json
import os
from flask import Blueprint, render_template, request, jsonify, session
from routes.auth_routes import admin_required
from database.connection import get_db_cursor
from config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = {
        "total_users": 0,
        "total_emails": 0,
        "total_spam": 0,
        "total_safe": 0,
        "spam_percentage": 0.0,
        "feedback_total": 0,
        "feedback_correct": 0,
        "feedback_incorrect": 0,
        "feedback_accuracy": 0.0,
        "risk_safe": 0,
        "risk_suspicious": 0,
        "risk_high": 0
    }

    try:
        with get_db_cursor(commit=False) as cur:
            # 1. User count
            cur.execute("SELECT COUNT(*) as count FROM users;")
            stats["total_users"] = cur.fetchone()['count']

            # 2. Email detection stats
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN prediction = 'Spam' THEN 1 END) as spam,
                    COUNT(CASE WHEN prediction = 'Not Spam' THEN 1 END) as safe,
                    COUNT(CASE WHEN risk_level = 'Safe' THEN 1 END) as risk_safe,
                    COUNT(CASE WHEN risk_level = 'Suspicious' THEN 1 END) as risk_suspicious,
                    COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) as risk_high
                FROM email_detections;
            """)
            d_row = cur.fetchone()
            if d_row and d_row['total'] > 0:
                stats["total_emails"] = d_row['total']
                stats["total_spam"] = d_row['spam']
                stats["total_safe"] = d_row['safe']
                stats["risk_safe"] = d_row['risk_safe']
                stats["risk_suspicious"] = d_row['risk_suspicious']
                stats["risk_high"] = d_row['risk_high']
                stats["spam_percentage"] = round((d_row['spam'] / d_row['total']) * 100, 1)

            # 3. Feedback stats
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN feedback = 'Correct' THEN 1 END) as correct,
                    COUNT(CASE WHEN feedback = 'Incorrect' THEN 1 END) as incorrect
                FROM feedback;
            """)
            f_row = cur.fetchone()
            if f_row and f_row['total'] > 0:
                stats["feedback_total"] = f_row['total']
                stats["feedback_correct"] = f_row['correct']
                stats["feedback_incorrect"] = f_row['incorrect']
                stats["feedback_accuracy"] = round((f_row['correct'] / f_row['total']) * 100, 1)

            # 4. Recent Detections (last 5)
            cur.execute("""
                SELECT d.id, d.subject, d.prediction, d.spam_probability, d.risk_level, d.created_at,
                       u.name as user_name, u.email as user_email
                FROM email_detections d
                LEFT JOIN users u ON d.user_id = u.id
                ORDER BY d.created_at DESC
                LIMIT 5;
            """)
            recent_detections = cur.fetchall()

    except Exception as e:
        print(f"[Admin Dashboard Error] {e}")
        recent_detections = []

    return render_template('admin_dashboard.html', stats=stats, recent_detections=recent_detections)

@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    """Returns dynamic time-series and chart distribution data for Admin Dashboard"""
    try:
        with get_db_cursor(commit=False) as cur:
            # Daily trends (last 7 days)
            cur.execute("""
                SELECT 
                    TO_CHAR(created_at, 'YYYY-MM-DD') as day,
                    COUNT(CASE WHEN prediction = 'Spam' THEN 1 END) as spam_count,
                    COUNT(CASE WHEN prediction = 'Not Spam' THEN 1 END) as safe_count
                FROM email_detections
                WHERE created_at >= CURRENT_DATE - INTERVAL '6 days'
                GROUP BY day
                ORDER BY day ASC;
            """)
            daily_rows = cur.fetchall()

            # Risk Distribution
            cur.execute("""
                SELECT 
                    COUNT(CASE WHEN risk_level = 'Safe' THEN 1 END) as safe,
                    COUNT(CASE WHEN risk_level = 'Suspicious' THEN 1 END) as suspicious,
                    COUNT(CASE WHEN risk_level = 'High Risk' THEN 1 END) as high_risk
                FROM email_detections;
            """)
            risk_row = cur.fetchone()

            return jsonify({
                "success": True,
                "daily_trends": daily_rows or [],
                "risk_distribution": risk_row or {"safe": 0, "suspicious": 0, "high_risk": 0}
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/users')
@admin_required
def users_page():
    search = request.args.get('search', '').strip()
    users_list = []
    try:
        with get_db_cursor(commit=False) as cur:
            sql = """
                SELECT 
                    u.id, u.name, u.email, u.role, u.is_active, u.created_at,
                    COUNT(d.id) as detection_count
                FROM users u
                LEFT JOIN email_detections d ON u.id = d.user_id
            """
            params = []
            if search:
                sql += " WHERE u.name ILIKE %s OR u.email ILIKE %s"
                p = f"%{search}%"
                params.extend([p, p])

            sql += " GROUP BY u.id ORDER BY u.id ASC;"
            cur.execute(sql, tuple(params))
            users_list = cur.fetchall()
    except Exception as e:
        print(f"[Admin Users Error] {e}")

    return render_template('admin_users.html', users=users_list, search=search)

@admin_bp.route('/api/users/<int:target_user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(target_user_id):
    current_admin_id = session.get('user_id')
    if target_user_id == current_admin_id:
        return jsonify({"success": False, "error": "You cannot deactivate your own administrative account."}), 400

    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT id, is_active, name FROM users WHERE id = %s;", (target_user_id,))
            target = cur.fetchone()
            if not target:
                return jsonify({"success": False, "error": "User not found."}), 404

            new_status = not target['is_active']
            cur.execute("UPDATE users SET is_active = %s WHERE id = %s;", (new_status, target_user_id))

        status_text = "activated" if new_status else "deactivated"
        return jsonify({
            "success": True,
            "new_status": new_status,
            "message": f"User {target['name']} has been {status_text}."
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/detections')
@admin_required
def detections_page():
    search = request.args.get('search', '').strip()
    prediction_filter = request.args.get('prediction', '').strip()
    risk_filter = request.args.get('risk_level', '').strip()

    sql = """
        SELECT 
            d.id, d.subject, d.prediction, d.spam_probability, d.risk_level, 
            d.url_count, d.created_at, d.reasons,
            u.name as user_name, u.email as user_email,
            f.feedback
        FROM email_detections d
        LEFT JOIN users u ON d.user_id = u.id
        LEFT JOIN feedback f ON d.id = f.detection_id
        WHERE 1=1
    """
    params = []

    if search:
        sql += " AND (d.subject ILIKE %s OR d.body ILIKE %s OR u.email ILIKE %s OR u.name ILIKE %s)"
        p = f"%{search}%"
        params.extend([p, p, p, p])

    if prediction_filter and prediction_filter in ['Spam', 'Not Spam']:
        sql += " AND d.prediction = %s"
        params.append(prediction_filter)

    if risk_filter and risk_filter in ['Safe', 'Suspicious', 'High Risk']:
        sql += " AND d.risk_level = %s"
        params.append(risk_filter)

    sql += " ORDER BY d.created_at DESC LIMIT 100;"

    detections_list = []
    try:
        with get_db_cursor(commit=False) as cur:
            cur.execute(sql, tuple(params))
            records = cur.fetchall()
            for r in records:
                reasons = r['reasons']
                if isinstance(reasons, str):
                    try:
                        reasons = json.loads(reasons)
                    except Exception:
                        reasons = []
                r['reasons_parsed'] = reasons or []
                detections_list.append(r)
    except Exception as e:
        print(f"[Admin Detections Error] {e}")

    return render_template(
        'admin_detections.html', 
        detections=detections_list, 
        search=search, 
        prediction_filter=prediction_filter, 
        risk_filter=risk_filter
    )

