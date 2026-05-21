"""
ThreatSense AI — Model Training and Evaluation Pipeline
This script:
1. Unzips and loads the URL dataset (urlmalicious_phish.csv.zip) and Message dataset (Message.zip).
2. Performs data analysis (class distributions, cleaning).
3. Preprocesses URLs and trains a high-accuracy Logistic Regression model (char TF-IDF).
4. Preprocesses Messages and trains a high-accuracy Naive Bayes model (word TF-IDF).
5. Evaluates both models and outputs classification metrics.
6. Saves the trained models and vectorizers to backend/saved_models/.
"""

import os
import zipfile
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "Dataset")
SAVED_MODELS_DIR = os.path.join(BASE_DIR, "backend", "saved_models")

def ensure_dirs():
    """Ensure that saved_models directory exists."""
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)

def analyze_and_train():
    print("=" * 60)
    print("STARTING THREATSENSE AI DATASET ANALYSIS & TRAINING PIPELINE")
    print("=" * 60)
    
    ensure_dirs()
    
    # ----------------------------------------------------
    # 1. URL DATASET ANALYSIS & TRAINING
    # ----------------------------------------------------
    print("\n--- 1. Analyzing URL Dataset ---")
    url_zip_path = os.path.join(DATASET_DIR, "urlmalicious_phish.csv.zip")
    
    if not os.path.exists(url_zip_path):
        print(f"Error: URL dataset zip not found at {url_zip_path}")
        return
        
    print("Extracting urlmalicious_phish.csv.zip...")
    with zipfile.ZipFile(url_zip_path, 'r') as zf:
        print("Zip contents:", zf.namelist())
        csv_filename = [name for name in zf.namelist() if name.endswith('.csv')][0]
        with zf.open(csv_filename) as f:
            url_df = pd.read_csv(f)
            
    print(f"URL Dataset Shape: {url_df.shape}")
    print("Class distribution:")
    dist = url_df['type'].value_counts()
    for k, v in dist.items():
        print(f" - {k}: {v} ({v/len(url_df)*100:.2f}%)")
        
    # Map classes to binary (benign -> 0, others -> 1)
    # 0 = SAFE, 1 = DANGEROUS
    url_df['label'] = url_df['type'].apply(lambda x: 0 if x == 'benign' else 1)
    
    # Sampling for efficient local training with extremely high quality
    # We take all defacement, malware, phishing and a balanced sample of benign URLs
    print("\nCreating balanced sub-sample for training...")
    benign_subset = url_df[url_df['label'] == 0].sample(n=40000, random_state=42)
    malicious_subset = url_df[url_df['label'] == 1].sample(n=40000, random_state=42)
    sampled_url_df = pd.concat([benign_subset, malicious_subset]).sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Sampled URL Dataset Shape: {sampled_url_df.shape}")
    print("Sampled Label Distribution:")
    print(sampled_url_df['label'].value_counts())
    
    # Train/Test Split
    X_url = sampled_url_df['url']
    y_url = sampled_url_df['label']
    X_train_url, X_test_url, y_train_url, y_test_url = train_test_split(
        X_url, y_url, test_size=0.2, random_state=42, stratify=y_url
    )
    
    print("\nTraining URL Vectorizer (Char-level TF-IDF)...")
    # Character level n-grams capture patterns like subdomains, specific paths, protocols
    url_vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 5), max_features=35000)
    X_train_url_feats = url_vectorizer.fit_transform(X_train_url)
    X_test_url_feats = url_vectorizer.transform(X_test_url)
    
    print("Training URL Classifier (Logistic Regression)...")
    url_classifier = LogisticRegression(max_iter=1000, C=10, random_state=42)
    url_classifier.fit(X_train_url_feats, y_train_url)
    
    # Evaluate
    y_pred_url = url_classifier.predict(X_test_url_feats)
    url_acc = accuracy_score(y_test_url, y_pred_url)
    print(f"\nURL Model Accuracy: {url_acc*100:.2f}%")
    print("Classification Report:")
    print(classification_report(y_test_url, y_pred_url, target_names=['SAFE', 'DANGEROUS']))
    
    # Save URL model
    url_model_path = os.path.join(SAVED_MODELS_DIR, "url_model.joblib")
    url_vect_path = os.path.join(SAVED_MODELS_DIR, "url_vectorizer.joblib")
    joblib.dump(url_classifier, url_model_path)
    joblib.dump(url_vectorizer, url_vect_path)
    print(f"Saved URL model to {url_model_path}")
    print(f"Saved URL vectorizer to {url_vect_path}")
    
    # ----------------------------------------------------
    # 2. MESSAGE/EMAIL DATASET ANALYSIS & TRAINING
    # ----------------------------------------------------
    print("\n" + "-" * 50)
    print("--- 2. Analyzing Message/Email Dataset ---")
    msg_zip_path = os.path.join(DATASET_DIR, "Message.zip")
    
    if not os.path.exists(msg_zip_path):
        print(f"Error: Message dataset zip not found at {msg_zip_path}")
        return
        
    print("Extracting Message.zip...")
    with zipfile.ZipFile(msg_zip_path, 'r') as zf:
        print("Zip contents:", zf.namelist())
        csv_filename = [name for name in zf.namelist() if name.endswith('.csv')][0]
        with zf.open(csv_filename) as f:
            # spam.csv is in latin-1 encoding
            msg_df = pd.read_csv(f, encoding='latin-1')
            
    # Drop unused columns and rename
    msg_df = msg_df[['v1', 'v2']].rename(columns={'v1': 'label_raw', 'v2': 'text'})
    msg_df['label'] = msg_df['label_raw'].apply(lambda x: 0 if x == 'ham' else 1)
    
    print(f"Message Dataset Shape: {msg_df.shape}")
    print("Class distribution:")
    dist_msg = msg_df['label_raw'].value_counts()
    for k, v in dist_msg.items():
        print(f" - {k}: {v} ({v/len(msg_df)*100:.2f}%)")
        
    # Clean up empty strings or nulls
    msg_df = msg_df.dropna(subset=['text'])
    
    # Train/Test Split
    X_msg = msg_df['text']
    y_msg = msg_df['label']
    X_train_msg, X_test_msg, y_train_msg, y_test_msg = train_test_split(
        X_msg, y_msg, test_size=0.2, random_state=42, stratify=y_msg
    )
    
    print("\nTraining Message Vectorizer (Word-level TF-IDF)...")
    msg_vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=10000, stop_words='english')
    X_train_msg_feats = msg_vectorizer.fit_transform(X_train_msg)
    X_test_msg_feats = msg_vectorizer.transform(X_test_msg)
    
    print("Training Message Classifier (Multinomial Naive Bayes)...")
    msg_classifier = MultinomialNB(alpha=0.1)
    msg_classifier.fit(X_train_msg_feats, y_train_msg)
    
    # Evaluate
    y_pred_msg = msg_classifier.predict(X_test_msg_feats)
    msg_acc = accuracy_score(y_test_msg, y_pred_msg)
    print(f"\nMessage Model Accuracy: {msg_acc*100:.2f}%")
    print("Classification Report:")
    print(classification_report(y_test_msg, y_pred_msg, target_names=['SAFE', 'DANGEROUS']))
    
    # Save Message model
    msg_model_path = os.path.join(SAVED_MODELS_DIR, "message_model.joblib")
    msg_vect_path = os.path.join(SAVED_MODELS_DIR, "message_vectorizer.joblib")
    joblib.dump(msg_classifier, msg_model_path)
    joblib.dump(msg_vectorizer, msg_vect_path)
    print(f"Saved Message model to {msg_model_path}")
    print(f"Saved Message vectorizer to {msg_vect_path}")
    
    print("\n" + "=" * 60)
    print("TRAINING PIPELINE COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    analyze_train_time = analyze_and_train()
