import os
from flask import Flask, render_template, session
from config import Config
from database.connection import init_db
from services.prediction_service import prediction_service
from routes.auth_routes import auth_bp
from routes.prediction_routes import predict_bp
from routes.history_routes import history_bp
from routes.admin_routes import admin_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 1. Initialize Database Schema & Default Accounts
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            print(f"[App Warning] Failed to initialize database: {e}")

    # 2. Pre-warm Prediction Service (Model and Vectorizer in memory)
    try:
        _ = prediction_service.model
        print("[App] ML Model and TF-IDF Vectorizer pre-warmed and ready.")
    except Exception as e:
        print(f"[App Warning] Could not pre-warm ML model: {e}")

    # 3. Context Processor for Global Template Context (User Session)
    @app.context_processor
    def inject_user():
        user = None
        if 'user_id' in session:
            user = {
                "id": session.get('user_id'),
                "name": session.get('user_name'),
                "email": session.get('user_email'),
                "role": session.get('user_role')
            }
        return dict(current_user=user)

    # 4. Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(predict_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(admin_bp)

    # 5. Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', not_found=True), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', server_error=True), 500

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    print("==================================================")
    print("  SpamShield AI - Email Spam Detection Engine     ")
    print(f"  Server running on http://127.0.0.1:{port}        ")
    print("==================================================")
    app.run(host='0.0.0.0', port=port, debug=debug)
