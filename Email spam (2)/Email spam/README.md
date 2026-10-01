# SpamShield AI - Email Spam Detection Web Application

> An end-to-end, production-grade Machine Learning web application built with **Python Flask, PostgreSQL 18, Scikit-learn (TF-IDF + Logistic Regression), HTML5, CSS3, and JavaScript (AJAX & Chart.js)**.

---

## 🌟 Key Features

- **Machine Learning Core**: Classifies emails as **Spam** or **Not Spam** using **TF-IDF Vectorization** (n-grams 1-2, sublinear scaling) and **Logistic Regression** calibrated with `predict_proba()`.
- **Pre-warmed Singleton Service**: Saved Joblib model artifacts (`spam_model.pkl` and `tfidf_vectorizer.pkl`) are loaded into memory once on application startup — zero retraining per request.
- **Explainable Supporting Indicators**: Identifies urgent pressure tactics, promotional keywords, lottery/prize claims, credential/banking harvesting triggers, excessive capitalization, and unusual punctuation.
- **Sandboxed URL Analyzer**: Statically detects embedded links, IP-based hostnames, URL shorteners, and deceptive path patterns without ever opening or visiting them.
- **PostgreSQL 18 Relational Storage**: Full audit logs with foreign key constraints, indexes, and session management (`users`, `email_detections`, `feedback`, `model_metrics`).
- **Role-Based Access Control (RBAC)**:
  - **USER**: Dashboard, AJAX Email Analyzer, Personal Detection History with filters, Profile Management, and Accuracy Feedback.
  - **ADMIN**: Executive Telemetry Dashboard with Chart.js analytics, User Management (Activation/Deactivation toggles), System-wide Detection Auditing, and Real ML Model Performance Metrics.
- **Mathematical Transparency**: Real-time Confusion Matrix visual heatmap, Precision, Recall, Accuracy, and F1-Score directly from the trained model (no fake/mock values).

---

## 📁 Project Structure

```text
email-spam-detector/
├── app.py                     # Flask application entry point & blueprint registration
├── config.py                  # Environment-driven configuration
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (DB URI, SECRET_KEY)
├── .gitignore                 # Git ignore rules
├── train_model.py             # ML model training, evaluation & PostgreSQL metrics insertion
├── evaluate_model.py          # Standalone model test & classification report script
├── dataset/
│   ├── generate_dataset.py    # Balanced dataset generator
│   └── spam_emails.csv        # 600 labeled email samples (300 spam, 300 ham)
├── model/
│   ├── spam_model.pkl         # Serialized Logistic Regression model
│   ├── tfidf_vectorizer.pkl   # Serialized TF-IDF vectorizer
│   └── metrics.json           # Actual performance metrics & top feature weights
├── preprocessing/
│   └── text_cleaner.py        # Text cleaning, tokenization & surface statistics
├── services/
│   ├── prediction_service.py  # In-memory singleton loader, predict_proba & risk scoring
│   ├── url_analyzer.py        # Static, sandboxed URL inspection
│   └── spam_reason_service.py # Supporting indicators rule engine
├── routes/
│   ├── auth_routes.py         # Login, Register, Logout, Profile
│   ├── prediction_routes.py   # Landing, Dashboard, Analyze & /api/predict
│   ├── history_routes.py      # Detection History & /api/feedback
│   └── admin_routes.py        # Admin Telemetry, User Management, Detections, Metrics
├── database/
│   ├── connection.py          # Threaded PostgreSQL connection pool & helpers
│   └── schema.sql             # SQL DDL & default seed users
├── templates/
│   ├── base.html              # Layout, navbar, flash messages, footer
│   ├── index.html             # High-converting Landing Page
│   ├── login.html             # Login with fast demo credential buttons
│   ├── register.html          # User registration form
│   ├── dashboard.html         # User statistics & threat breakdown
│   ├── analyze.html           # AJAX analyzer with sample loaders & gauge meter
│   ├── history.html           # User history with date/risk/prediction filters & modal
│   ├── profile.html           # User profile & password reset
│   ├── admin_dashboard.html   # Admin analytics with Chart.js
│   ├── admin_users.html       # User activation/deactivation portal
│   └── admin_detections.html  # System-wide email audit log
└── static/
    ├── css/
    │   └── style.css          # Modern cybersecurity dark theme & design tokens
    └── js/
        ├── main.js            # Global alerts & toast notifications
        ├── auth.js            # One-click demo credential autofill
        ├── analyze.js         # AJAX Fetch prediction, dynamic badge rendering, feedback
        ├── history.js         # History search, filters, details modal
        └── admin.js           # Admin Chart.js charts & user status toggles
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 14+ (PostgreSQL 18 is running locally)

### 2. Environment Configuration (`.env`)
Configure your database credentials in `.env`. You can use **Supabase** or **local PostgreSQL**:

**Option A: Supabase (Recommended for Cloud)**
```ini
# Copy the URI from Supabase: Project Settings -> Database -> Connection string -> URI
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
SECRET_KEY=spamshield_ultra_secure_secret_key_2026_jwt_session_prod
FLASK_ENV=development
PORT=5000
```

**Option B: Local PostgreSQL**
```ini
DATABASE_URL=
DB_HOST=localhost
DB_PORT=5432
DB_NAME=email_spam_db
DB_USER=postgres
DB_PASSWORD=password
DB_SSLMODE=prefer
SECRET_KEY=spamshield_ultra_secure_secret_key_2026_jwt_session_prod
FLASK_ENV=development
PORT=5000
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Train the ML Model
Trains the TF-IDF vectorizer and Logistic Regression model on `dataset/spam_emails.csv`, calculates real evaluation metrics, creates `model/spam_model.pkl`, and seeds PostgreSQL `model_metrics`:
```bash
python train_model.py
```

Optional standalone verification:
```bash
python evaluate_model.py
```

### 5. Launch the Web Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔐 Default Demo Accounts

The application automatically seeds two verified test accounts:

| Role | Email | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@spamshield.com` | `Admin@12345` | Full access: Admin Dashboard, Users, All Detections, ML Performance |
| **Regular User** | `user@demo.com` | `User@12345` | User access: Dashboard, Email Analyzer, Personal History, Profile |

> **Tip:** You can click the **Demo User** or **Admin** quick-fill buttons on the login page for instant authentication during presentations or evaluations.

---

## 🔬 Machine Learning Pipeline

```mermaid
graph LR
    A[Subject + Body] --> B[Text Cleaner]
    B --> C[Stopwords & Tokenization]
    C --> D[TF-IDF Vectorizer]
    D --> E[Logistic Regression]
    E --> F[predict_proba]
    F --> G[Risk Level & Verdict]
    
    A --> H[Safe URL Analyzer]
    A --> I[Indicator Engine]
    H --> J[Explainable Signals]
    I --> J
    
    G --> K[PostgreSQL 18 Audit Log]
    J --> K
```

### Risk Level Calibration:
- **Safe**: Spam Probability $< 0.35$
- **Suspicious**: $0.35 \le \text{Spam Probability} < 0.70$
- **High Risk**: $\text{Spam Probability} \ge 0.70$

---

## 📡 REST API Reference

| Endpoint | Method | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `/api/predict` | `POST` | User / Admin | Accepts `{ "subject": "...", "body": "..." }`, returns prediction, probabilities, risk level, and indicators |
| `/api/feedback` | `POST` | User / Admin | Records `{ "detection_id": 1, "feedback": "Correct" \| "Incorrect" }` |
| `/api/history` | `GET` | User | Retrieves user's own detections with search and filtering params |
| `/api/history/<id>` | `GET` | User / Admin | Fetches full email body and details for modal drawer |
| `/admin/api/stats` | `GET` | Admin | Returns time-series daily trends and risk distribution for Chart.js |
| `/admin/api/users/<id>/toggle-status` | `POST` | Admin | Toggles account activation status |

---

## 🏆 Presentation & Viva Highlights

1. **Why Logistic Regression + TF-IDF?**
   - High computational efficiency with linear decision boundaries.
   - Interpretable coefficients where each word directly contributes a measurable weight towards spam or legitimate classification.
2. **Why Singleton Pattern for the ML Model?**
   - Retraining on every user request causes server latency spikes. By loading the fitted TF-IDF vocabulary and regression weights once into memory on Flask startup, prediction latency drops below 10 milliseconds.
3. **Safe URL Detection**:
   - Web crawlers in spam detectors can trigger honey-pots or malicious payloads. SpamShield analyzes URL structure completely offline with zero outbound network calls.
