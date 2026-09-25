import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from config import Config
from preprocessing.text_cleaner import clean_email_text
from database.connection import get_db_cursor, init_db

def train_and_evaluate():
    print("[ML Pipeline] Starting model training pipeline...")
    
    # 1. Ensure Model directory exists
    os.makedirs(Config.MODEL_DIR, exist_ok=True)

    # 2. Load dataset
    if not os.path.exists(Config.DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {Config.DATASET_PATH}")

    df = pd.read_csv(Config.DATASET_PATH)
    print(f"[ML Pipeline] Loaded dataset with {len(df)} samples.")
    print(f"[ML Pipeline] Label distribution:\n{df['label'].value_counts()}")

    # 3. Combine Subject and Body for rich text representation
    df['combined_text'] = df['subject'].fillna('') + " " + df['body'].fillna('')
    
    # 4. Apply text preprocessing
    print("[ML Pipeline] Applying text cleaning and normalization...")
    df['cleaned_text'] = df['combined_text'].apply(clean_email_text)
    
    # Map label to binary: spam = 1, ham = 0
    df['target'] = df['label'].map({'spam': 1, 'ham': 0})

    X = df['cleaned_text']
    y = df['target']

    # 5. Stratified train-test split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"[ML Pipeline] Split: {len(X_train)} training samples, {len(X_test)} testing samples.")

    # 6. Fit TF-IDF Vectorizer ONLY on training set
    print("[ML Pipeline] Fitting TF-IDF Vectorizer on training data...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        sublinear_tf=True
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # 7. Train Logistic Regression
    print("[ML Pipeline] Training Logistic Regression classifier...")
    model = LogisticRegression(
        C=1.0,
        solver='liblinear',
        random_state=42,
        max_iter=1000
    )
    model.fit(X_train_tfidf, y_train)

    # 8. Evaluate on test set
    y_pred = model.predict(X_test_tfidf)
    y_pred_proba = model.predict_proba(X_test_tfidf)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_test, y_pred).tolist()

    print("\n================ ML EVALUATION METRICS ================")
    print(f"Accuracy:        {acc * 100:.2f}%")
    print(f"Precision:       {prec * 100:.2f}%")
    print(f"Recall:          {rec * 100:.2f}%")
    print(f"F1-Score:        {f1 * 100:.2f}%")
    print(f"Confusion Matrix:\n{cm}")
    print("=======================================================\n")

    # Extract top spam and ham predictive words
    feature_names = vectorizer.get_feature_names_out()
    coefs = model.coef_[0]
    top_spam_indices = np.argsort(coefs)[-15:][::-1]
    top_ham_indices = np.argsort(coefs)[:15]

    top_spam_words = [{"word": feature_names[i], "weight": round(float(coefs[i]), 4)} for i in top_spam_indices]
    top_ham_words = [{"word": feature_names[i], "weight": round(float(coefs[i]), 4)} for i in top_ham_indices]

    metrics_payload = {
        "model_name": "Logistic Regression + TF-IDF",
        "accuracy": round(acc, 4),
        "precision_score": round(prec, 4),
        "recall_score": round(rec, 4),
        "f1_score": round(f1, 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "confusion_matrix": cm,
        "top_spam_words": top_spam_words,
        "top_ham_words": top_ham_words
    }

    # 9. Save artifacts
    print(f"[ML Pipeline] Saving model to {Config.MODEL_PATH}...")
    joblib.dump(model, Config.MODEL_PATH)

    print(f"[ML Pipeline] Saving TF-IDF vectorizer to {Config.VECTORIZER_PATH}...")
    joblib.dump(vectorizer, Config.VECTORIZER_PATH)

    print(f"[ML Pipeline] Saving evaluation metrics to {Config.METRICS_PATH}...")
    with open(Config.METRICS_PATH, 'w', encoding='utf-8') as f:
        json.dump(metrics_payload, f, indent=4)

    # 10. Persist metrics in PostgreSQL
    try:
        init_db()
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO model_metrics 
                (model_name, accuracy, precision_score, recall_score, f1_score, train_samples, test_samples, confusion_matrix)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                metrics_payload["model_name"],
                metrics_payload["accuracy"],
                metrics_payload["precision_score"],
                metrics_payload["recall_score"],
                metrics_payload["f1_score"],
                metrics_payload["train_samples"],
                metrics_payload["test_samples"],
                json.dumps(metrics_payload["confusion_matrix"])
            ))
        print("[ML Pipeline] Metrics successfully inserted into PostgreSQL database.")
    except Exception as e:
        print(f"[ML Pipeline Warning] Could not persist metrics to PostgreSQL: {e}")

    print("[ML Pipeline] Training and artifact generation completed successfully!")
    return metrics_payload

if __name__ == '__main__':
    train_and_evaluate()
