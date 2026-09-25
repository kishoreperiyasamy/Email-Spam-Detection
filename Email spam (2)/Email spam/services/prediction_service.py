import os
import json
import joblib
from config import Config
from preprocessing.text_cleaner import clean_email_text, extract_text_statistics
from services.url_analyzer import analyze_urls_in_text
from services.spam_reason_service import analyze_spam_indicators
from database.connection import get_db_cursor

class PredictionService:
    _instance = None
    model = None
    vectorizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PredictionService, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance

    def _load_models(self):
        print(f"[PredictionService] Loading models into memory from {Config.MODEL_DIR}...")
        if not os.path.exists(Config.MODEL_PATH) or not os.path.exists(Config.VECTORIZER_PATH):
            raise FileNotFoundError(
                f"Model or vectorizer file missing. Please ensure train_model.py has executed."
            )
        self.model = joblib.load(Config.MODEL_PATH)
        self.vectorizer = joblib.load(Config.VECTORIZER_PATH)
        print("[PredictionService] Model and TF-IDF Vectorizer successfully initialized.")

    def predict_email(self, subject: str, body: str, user_id: int = None, attachment_info: dict = None) -> dict:
        subject = subject or ""
        body = body or ""
        combined_text = f"{subject} {body}".strip()

        if not combined_text:
            raise ValueError("Email subject or body must contain text to analyze.")

        # 1. Surface Text Statistics
        text_stats = extract_text_statistics(combined_text)

        # 2. Safe URL Analysis
        url_stats = analyze_urls_in_text(combined_text)

        # 3. Clean Text for TF-IDF Vectorization
        cleaned_text = clean_email_text(combined_text)

        # Handle edge case if cleaned text is empty
        if not cleaned_text:
            cleaned_text = combined_text.lower()

        # 4. TF-IDF Transformation
        tfidf_vec = self.vectorizer.transform([cleaned_text])

        # 5. Logistic Regression Prediction & Probability
        probabilities = self.model.predict_proba(tfidf_vec)[0]
        # Class 0: Not Spam (Ham), Class 1: Spam
        not_spam_prob = round(float(probabilities[0]), 4)
        spam_prob = round(float(probabilities[1]), 4)

        prediction_label = "Spam" if spam_prob >= 0.50 else "Not Spam"

        # 6. Risk Level Categorization
        if spam_prob >= 0.70:
            risk_level = "High Risk"
        elif spam_prob >= 0.35:
            risk_level = "Suspicious"
        else:
            risk_level = "Safe"

        # 7. Supporting Indicators Analysis
        reasons = analyze_spam_indicators(subject, body, text_stats, url_stats, attachment_info=attachment_info)

        # 8. Persist Prediction in PostgreSQL
        detection_id = None
        try:
            with get_db_cursor() as cur:
                cur.execute("""
                    INSERT INTO email_detections 
                    (user_id, subject, body, prediction, spam_probability, not_spam_probability, risk_level, reasons, url_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, created_at;
                """, (
                    user_id,
                    subject,
                    body,
                    prediction_label,
                    spam_prob,
                    not_spam_prob,
                    risk_level,
                    json.dumps(reasons),
                    url_stats["url_count"]
                ))
                row = cur.fetchone()
                if row:
                    detection_id = row['id']
                    created_at = row['created_at'].isoformat()
        except Exception as e:
            print(f"[PredictionService Warning] Could not persist detection to PostgreSQL: {e}")
            from datetime import datetime
            created_at = datetime.utcnow().isoformat()

        return {
            "detection_id": detection_id,
            "prediction": prediction_label,
            "spam_probability": spam_prob,
            "not_spam_probability": not_spam_prob,
            "spam_percentage": round(spam_prob * 100, 1),
            "not_spam_percentage": round(not_spam_prob * 100, 1),
            "risk_level": risk_level,
            "reasons": reasons,
            "url_count": url_stats["url_count"],
            "urls_detected": url_stats["urls_detected"],
            "text_statistics": text_stats,
            "attachment_info": attachment_info,
            "timestamp": created_at
        }

# Global singleton accessor
prediction_service = PredictionService()
