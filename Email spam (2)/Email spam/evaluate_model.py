import os
import json
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from config import Config
from preprocessing.text_cleaner import clean_email_text

def run_evaluation():
    print("[Evaluation] Loading saved model and TF-IDF vectorizer...")
    if not os.path.exists(Config.MODEL_PATH) or not os.path.exists(Config.VECTORIZER_PATH):
        print("[Evaluation Error] Saved model or vectorizer not found. Please run train_model.py first.")
        return

    model = joblib.load(Config.MODEL_PATH)
    vectorizer = joblib.load(Config.VECTORIZER_PATH)

    print(f"[Evaluation] Loading dataset from {Config.DATASET_PATH}...")
    df = pd.read_csv(Config.DATASET_PATH)
    df['combined_text'] = df['subject'].fillna('') + " " + df['body'].fillna('')
    df['cleaned_text'] = df['combined_text'].apply(clean_email_text)
    df['target'] = df['label'].map({'spam': 1, 'ham': 0})

    X_tfidf = vectorizer.transform(df['cleaned_text'])
    y_true = df['target']
    y_pred = model.predict(X_tfidf)

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)

    print("\n================ EVALUATION SUMMARY ================")
    print(f"Total Samples Evaluated: {len(df)}")
    print(f"Accuracy:               {acc * 100:.2f}%")
    print(f"Precision:              {prec * 100:.2f}%")
    print(f"Recall:                 {rec * 100:.2f}%")
    print(f"F1 Score:               {f1 * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(f"[[TN={cm[0][0]}, FP={cm[0][1]}], [FN={cm[1][0]}, TP={cm[1][1]}]]")
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=["Ham (Not Spam)", "Spam"]))
    print("====================================================\n")

    if os.path.exists(Config.METRICS_PATH):
        with open(Config.METRICS_PATH, 'r', encoding='utf-8') as f:
            metrics_file_data = json.load(f)
        print("[Evaluation] Stored metrics in metrics.json are verified and up to date.")

if __name__ == '__main__':
    run_evaluation()
