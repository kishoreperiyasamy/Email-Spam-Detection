from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re
from database.connection import get_db_cursor

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({"error": "Authentication required. Please log in."}), 401
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({"error": "Admin authentication required."}), 401
            flash("Please log in with administrative privileges.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        if session.get('user_role') != 'ADMIN':
            if request.is_json:
                return jsonify({"error": "Forbidden. Admin privileges required."}), 403
            flash("Access denied. Admin role required.", "danger")
            return redirect(url_for('predict.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' not in session:
        return None
    try:
        with get_db_cursor(commit=False) as cur:
            cur.execute("SELECT id, name, email, role, is_active, created_at FROM users WHERE id = %s;", (session['user_id'],))
            return cur.fetchone()
    except Exception:
        return None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('predict.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('register.html', name=name, email=email)

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please enter a valid email address.", "danger")
            return render_template('register.html', name=name, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html', name=name, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', name=name, email=email)

        password_hash = generate_password_hash(password)

        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT id FROM users WHERE email = %s;", (email,))
                if cur.fetchone():
                    flash("An account with this email already exists. Please login.", "warning")
                    return redirect(url_for('auth.login'))

                cur.execute("""
                    INSERT INTO users (name, email, password_hash, role, is_active)
                    VALUES (%s, %s, %s, 'USER', TRUE)
                    RETURNING id;
                """, (name, email, password_hash))
                new_user = cur.fetchone()

            flash("Registration successful! Please log in to your account.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f"An error occurred during registration: {str(e)}", "danger")
            return render_template('register.html', name=name, email=email)

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('predict.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html', email=email)

        try:
            with get_db_cursor(commit=False) as cur:
                cur.execute("""
                    SELECT id, name, email, password_hash, role, is_active 
                    FROM users 
                    WHERE email = %s;
                """, (email,))
                user = cur.fetchone()

            if not user or not check_password_hash(user['password_hash'], password):
                flash("Invalid email or password.", "danger")
                return render_template('login.html', email=email)

            if not user['is_active']:
                flash("Your account has been deactivated. Please contact an administrator.", "danger")
                return render_template('login.html', email=email)

            # Store in session
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']

            flash(f"Welcome back, {user['name']}!", "success")
            
            # Redirect based on user role
            if user['role'] == 'ADMIN':
                next_page = request.args.get('next')
                if next_page and not next_page.startswith('/auth/login') and '/admin' in next_page:
                    return redirect(next_page)
                return redirect(url_for('admin.dashboard'))

            # Regular user always redirects to user dashboard
            return redirect(url_for('predict.dashboard'))

        except Exception as e:
            flash(f"Login failed: {str(e)}", "danger")
            return render_template('login.html', email=email)

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('predict.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_current_user()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_new_password = request.form.get('confirm_new_password', '')

        if not name:
            flash("Name cannot be empty.", "danger")
            return render_template('profile.html', user=user)

        try:
            with get_db_cursor() as cur:
                # If user wants to change password
                if new_password:
                    if not current_password:
                        flash("Please enter your current password to set a new password.", "danger")
                        return render_template('profile.html', user=user)

                    cur.execute("SELECT password_hash FROM users WHERE id = %s;", (user['id'],))
                    stored_pwd = cur.fetchone()['password_hash']
                    if not check_password_hash(stored_pwd, current_password):
                        flash("Incorrect current password.", "danger")
                        return render_template('profile.html', user=user)

                    if len(new_password) < 6:
                        flash("New password must be at least 6 characters.", "danger")
                        return render_template('profile.html', user=user)

                    if new_password != confirm_new_password:
                        flash("New passwords do not match.", "danger")
                        return render_template('profile.html', user=user)

                    new_hash = generate_password_hash(new_password)
                    cur.execute("""
                        UPDATE users 
                        SET name = %s, password_hash = %s 
                        WHERE id = %s;
                    """, (name, new_hash, user['id']))
                    flash("Profile and password updated successfully!", "success")
                else:
                    cur.execute("UPDATE users SET name = %s WHERE id = %s;", (name, user['id']))
                    flash("Profile updated successfully!", "success")

            session['user_name'] = name
            user['name'] = name
        except Exception as e:
            flash(f"Update failed: {str(e)}", "danger")

    # Get user quick stats
    user_stats = {"total": 0, "spam": 0, "safe": 0}
    try:
        with get_db_cursor(commit=False) as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN prediction = 'Spam' THEN 1 END) as spam,
                    COUNT(CASE WHEN prediction = 'Not Spam' THEN 1 END) as safe
                FROM email_detections 
                WHERE user_id = %s;
            """, (user['id'],))
            res = cur.fetchone()
            if res:
                user_stats = res
    except Exception:
        pass

    return render_template('profile.html', user=user, user_stats=user_stats)
