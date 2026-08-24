import pandas as pd
import numpy as np
import os
import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

def evaluate_models(X_train, y_train, X_test, y_test, dataset_name):
    print(f"--- Training models for {dataset_name} ---")
    
    models = {
        'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000),
        'Random Forest': RandomForestClassifier(random_state=42, class_weight='balanced', n_estimators=100),
        'XGBoost': XGBClassifier(random_state=42, scale_pos_weight=len(y_train[y_train==0])/len(y_train[y_train==1]), use_label_encoder=False, eval_metric='logloss')
    }
    
    results = {}
    best_model_name = None
    best_model = None
    best_pr_auc = -1
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
        
        pr_auc = average_precision_score(y_test, y_prob)
        f1 = f1_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        
        results[name] = {
            'Precision': float(precision_score(y_test, y_pred)),
            'Recall': float(recall),
            'F1-score': float(f1),
            'ROC-AUC': float(roc_auc_score(y_test, y_prob)),
            'PR-AUC': float(pr_auc),
            'Confusion Matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        print(f"  {name} - PR-AUC: {pr_auc:.4f}, F1: {f1:.4f}, Recall: {recall:.4f}")
        
        if pr_auc > best_pr_auc:
            best_pr_auc = pr_auc
            best_model_name = name
            best_model = model
            
    print(f"Best model for {dataset_name}: {best_model_name}\n")
    return best_model_name, best_model, results

def get_feature_importance(model, feature_names):
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        top_features = []
        for i in range(min(10, len(feature_names))):
            top_features.append({"feature": feature_names[indices[i]], "importance": float(importances[indices[i]])})
        return top_features
    return []

def main():
    os.makedirs('model', exist_ok=True)
    all_results = {}
    
    # =================================================================
    # 1. Provider Dataset (processed_claims.csv)
    # =================================================================
    print("Processing Provider Dataset...")
    provider_df = pd.read_csv('data/processed_claims.csv')
    
    target_col = 'PotentialFraud'
    drop_cols = ['Provider', target_col]
    X_prov = provider_df.drop(columns=[c for c in drop_cols if c in provider_df.columns])
    y_prov = provider_df[target_col]
    
    # All features are numeric here based on preprocessing
    X_prov_train, X_prov_test, y_prov_train, y_prov_test = train_test_split(X_prov, y_prov, test_size=0.2, stratify=y_prov, random_state=42)
    
    best_name_prov, best_model_prov, res_prov = evaluate_models(X_prov_train, y_prov_train, X_prov_test, y_prov_test, "Provider Dataset")
    
    top_features_prov = get_feature_importance(best_model_prov, X_prov.columns)
    
    all_results["Provider Dataset"] = {
        "Records": len(provider_df),
        "Features": X_prov.shape[1],
        "Target": target_col,
        "Class Distribution": {"0": int((y_prov==0).sum()), "1": int((y_prov==1).sum())},
        "Models": res_prov,
        "Best Model": best_name_prov,
        "Top 10 Features": top_features_prov
    }
    
    joblib.dump(best_model_prov, 'model/best_provider_model.pkl')
    
    # =================================================================
    # 2. Claim Dataset (processed_claims_synthetic.csv)
    # =================================================================
    print("Processing Claim Dataset...")
    claim_df = pd.read_csv('data/processed_claims_synthetic.csv')
    
    target_col = 'Is_Fraudulent'
    drop_cols = [target_col]
    X_claim = claim_df.drop(columns=[c for c in drop_cols if c in claim_df.columns])
    y_claim = claim_df[target_col]
    
    X_claim_train, X_claim_test, y_claim_train, y_claim_test = train_test_split(X_claim, y_claim, test_size=0.2, stratify=y_claim, random_state=42)
    
    best_name_claim, best_model_claim, res_claim = evaluate_models(X_claim_train, y_claim_train, X_claim_test, y_claim_test, "Claim Dataset")
    
    top_features_claim = get_feature_importance(best_model_claim, X_claim.columns)
    
    all_results["Claim Dataset"] = {
        "Records": len(claim_df),
        "Features": X_claim.shape[1],
        "Target": target_col,
        "Class Distribution": {"0": int((y_claim==0).sum()), "1": int((y_claim==1).sum())},
        "Models": res_claim,
        "Best Model": best_name_claim,
        "Top 10 Features": top_features_claim
    }
    
    joblib.dump(best_model_claim, 'model/best_claim_model.pkl')
    
    # =================================================================
    # 3. CMS Unlabeled Dataset (processed_cms_unlabeled.csv)
    # =================================================================
    print("Processing CMS Unlabeled Dataset...")
    cms_df = pd.read_csv('data/processed_cms_unlabeled.csv')
    
    # Identifiers to drop for modeling
    cms_drop = ['NPI', 'Provider Last Name', 'Provider First Name']
    X_cms = cms_df.drop(columns=[c for c in cms_drop if c in cms_df.columns])
    
    # Preprocessing pipeline
    numeric_features = ['Count']
    categorical_features = ['Procedure_Category', 'Profile_Display_Indicator']
    
    # Handle missing/invalid just in case
    for col in categorical_features:
        if col in X_cms.columns:
            X_cms[col] = X_cms[col].fillna('UNKNOWN').astype(str)
            
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), [c for c in numeric_features if c in X_cms.columns]),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), [c for c in categorical_features if c in X_cms.columns])
        ])
    
    print("Training Isolation Forest...")
    contamination_val = 0.01 # Assume 1% anomalies
    iso_forest = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', IsolationForest(contamination=contamination_val, random_state=42, n_jobs=-1))
    ])
    
    # Train and predict
    iso_forest.fit(X_cms)
    anomaly_preds = iso_forest.predict(X_cms)
    
    # Convert predictions: -1 (anomaly) -> 1, 1 (normal) -> 0
    anomaly_flags = (anomaly_preds == -1).astype(int)
    num_anomalies = int(anomaly_flags.sum())
    
    all_results["CMS Dataset"] = {
        "Records": len(cms_df),
        "Features": X_cms.shape[1],
        "Configuration": {"Model": "Isolation Forest", "Contamination": contamination_val},
        "Anomalies Detected": num_anomalies,
        "Anomaly Percentage": float((num_anomalies / len(cms_df)) * 100)
    }
    
    joblib.dump(iso_forest, 'model/cms_anomaly_model.pkl')
    
    # Save all results
    with open('model/model_results.json', 'w') as f:
        json.dump(all_results, f, indent=4)
        
    print("All training complete. Results saved to model/model_results.json")

if __name__ == "__main__":
    main()
