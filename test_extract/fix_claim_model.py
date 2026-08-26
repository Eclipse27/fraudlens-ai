import pandas as pd
import numpy as np
import json
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def fix_claim_model():
    print("Loading claim dataset...")
    df = pd.read_csv('data/processed_claims_synthetic.csv')
    target = 'Is_Fraudulent'
    
    # Check for constants or ID-like cols
    drop_cols = [target]
    for col in df.columns:
        if df[col].nunique() <= 1:
            drop_cols.append(col)
            
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    y = df[target]
    
    scale_pos = len(y[y==0]) / len(y[y==1])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    models = {
        'Regularized Random Forest': RandomForestClassifier(
            random_state=42, 
            class_weight='balanced', 
            n_estimators=150, 
            max_depth=6, 
            min_samples_leaf=10,
            max_features='sqrt'
        ),
        'Regularized XGBoost': XGBClassifier(
            random_state=42, 
            scale_pos_weight=scale_pos, 
            max_depth=4, 
            learning_rate=0.05, 
            subsample=0.8, 
            colsample_bytree=0.8,
            reg_alpha=1.0,
            reg_lambda=10.0,
            use_label_encoder=False,
            eval_metric='logloss'
        ),
        'Logistic Regression': LogisticRegression(
            random_state=42, 
            class_weight='balanced', 
            C=0.1, 
            max_iter=1000
        )
    }
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = {'f1': 'f1', 'pr_auc': 'average_precision'}
    
    best_model_name = None
    best_pipeline = None
    best_score = -1 # we will score based on PR-AUC mostly, but considering gap
    
    results = {}
    
    for name, model in models.items():
        print(f"\nEvaluating {name}...")
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', model)
        ])
        
        cv_res = cross_validate(pipeline, X, y, cv=skf, scoring=scoring, return_train_score=True)
        cv_f1 = np.mean(cv_res['test_f1'])
        cv_f1_std = np.std(cv_res['test_f1'])
        
        pipeline.fit(X_train, y_train)
        y_train_pred = pipeline.predict(X_train)
        y_test_pred = pipeline.predict(X_test)
        
        if hasattr(model, 'predict_proba'):
            y_test_prob = pipeline.predict_proba(X_test)[:, 1]
        else:
            y_test_prob = y_test_pred
            
        train_f1 = f1_score(y_train, y_train_pred)
        test_f1 = f1_score(y_test, y_test_pred)
        gap = train_f1 - test_f1
        test_prauc = average_precision_score(y_test, y_test_prob)
        test_recall = recall_score(y_test, y_test_pred)
        
        print(f"Train F1: {train_f1:.4f}, Test F1: {test_f1:.4f}, Gap: {gap:.4f}")
        print(f"Test PR-AUC: {test_prauc:.4f}, CV Mean F1: {cv_f1:.4f}")
        
        overfitting = 'NONE'
        if gap > 0.15: overfitting = 'SEVERE'
        elif gap > 0.05: overfitting = 'MODERATE'
        elif gap > 0.02: overfitting = 'MILD'
        
        # Penalize severe overfitting in selection
        score = test_prauc
        if gap > 0.15: score -= 0.1 
        
        results[name] = {
            'Train_F1': float(train_f1),
            'Test_F1': float(test_f1),
            'Test_Recall': float(test_recall),
            'Test_PR_AUC': float(test_prauc),
            'CV_Mean_F1': float(cv_f1),
            'CV_Std_F1': float(cv_f1_std),
            'Gap': float(gap),
            'Overfitting': overfitting,
            'model': model
        }
        
        if score > best_score:
            best_score = score
            best_model_name = name
            best_pipeline = pipeline

    print(f"\nBest Model Selected: {best_model_name}")
    best_stats = results[best_model_name]
    
    # Feature importance
    final_model = results[best_model_name]['model']
    top_features = []
    
    if hasattr(final_model, 'feature_importances_'):
        imp = final_model.feature_importances_
        indices = np.argsort(imp)[::-1]
        for i in range(10):
            top_features.append({"feature": X.columns[indices[i]], "importance": float(imp[indices[i]])})
    elif hasattr(final_model, 'coef_'):
        imp = np.abs(final_model.coef_[0])
        indices = np.argsort(imp)[::-1]
        for i in range(10):
            top_features.append({"feature": X.columns[indices[i]], "importance": float(imp[indices[i]])})
            
    # Save the model
    joblib.dump(best_pipeline, 'model/best_claim_model.pkl')
    
    # Update JSON files safely
    try:
        with open('model/model_results.json', 'r') as f:
            model_res = json.load(f)
        model_res['Claim Dataset']['Best Model'] = best_model_name
        model_res['Claim Dataset']['Top 10 Features'] = top_features
        with open('model/model_results.json', 'w') as f:
            json.dump(model_res, f, indent=4)
    except: pass
    
    try:
        with open('model/validation_results.json', 'r') as f:
            val_res = json.load(f)
        val_res['Claim']['Overfitting'] = best_stats['Overfitting']
        val_res['Claim']['Test_PR_AUC'] = best_stats['Test_PR_AUC']
        val_res['Claim']['Test_F1'] = best_stats['Test_F1']
        val_res['Claim']['Test_Recall'] = best_stats['Test_Recall']
        val_res['Claim']['Train_F1'] = best_stats['Train_F1']
        val_res['Claim']['CV_Mean_F1'] = best_stats['CV_Mean_F1']
        val_res['Claim']['CV_Std_F1'] = best_stats['CV_Std_F1']
        val_res['Claim']['Top_10_Features'] = top_features
        with open('model/validation_results.json', 'w') as f:
            json.dump(val_res, f, indent=4)
    except: pass

    # Print report values
    print("--- REPORT DATA ---")
    print(f"New Best Model: {best_model_name}")
    print(f"Training F1: {best_stats['Train_F1']:.4f}")
    print(f"Test F1: {best_stats['Test_F1']:.4f}")
    print(f"Test Recall: {best_stats['Test_Recall']:.4f}")
    print(f"Test PR-AUC: {best_stats['Test_PR_AUC']:.4f}")
    print(f"5-Fold CV Mean F1: {best_stats['CV_Mean_F1']:.4f}")
    print(f"5-Fold CV Std F1: {best_stats['CV_Std_F1']:.4f}")
    print(f"Generalization Gap: {best_stats['Gap']:.4f}")
    print(f"Overfitting: {best_stats['Overfitting']}")
    print("Top 5 Features:")
    for f in top_features[:5]: print(f" - {f['feature']} ({f['importance']:.4f})")

if __name__ == "__main__":
    fix_claim_model()
