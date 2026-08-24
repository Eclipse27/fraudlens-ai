import pandas as pd
import numpy as np
import os

import glob

def load_data(base_path):
    print("Loading datasets...")
    train_file = glob.glob(os.path.join(base_path, "Train-*.csv"))[0] if glob.glob(os.path.join(base_path, "Train-*.csv")) else os.path.join(base_path, "Train.csv")
    train_bene_file = glob.glob(os.path.join(base_path, "Train_Beneficiarydata*.csv"))[0]
    train_inpatient_file = glob.glob(os.path.join(base_path, "Train_Inpatientdata*.csv"))[0]
    train_outpatient_file = glob.glob(os.path.join(base_path, "Train_Outpatientdata*.csv"))[0]
    
    train = pd.read_csv(train_file)
    train_bene = pd.read_csv(train_bene_file)
    train_inpatient = pd.read_csv(train_inpatient_file)
    train_outpatient = pd.read_csv(train_outpatient_file)
    return train, train_bene, train_inpatient, train_outpatient

def preprocess():
    base_path = os.path.join('data', 'archive (2)')
    
    train, train_bene, train_inpatient, train_outpatient = load_data(base_path)
    
    # 1. Combine Inpatient and Outpatient claims
    print("Combining Inpatient and Outpatient claims...")
    train_inpatient['Is_Inpatient'] = 1
    train_outpatient['Is_Inpatient'] = 0
    
    claims = pd.concat([train_inpatient, train_outpatient], axis=0, ignore_index=True)
    
    # 2. Merge with Beneficiary Data
    print("Merging with Beneficiary Data...")
    claims = pd.merge(claims, train_bene, on='BeneID', how='left')
    
    # 3. Feature Engineering at Claim Level
    print("Engineering features...")
    # Convert dates to datetime
    claims['ClaimStartDt'] = pd.to_datetime(claims['ClaimStartDt'])
    claims['ClaimEndDt'] = pd.to_datetime(claims['ClaimEndDt'])
    claims['DOB'] = pd.to_datetime(claims['DOB'])
    
    # Claim duration
    claims['Claim_Duration'] = (claims['ClaimEndDt'] - claims['ClaimStartDt']).dt.days
    
    # Patient age at claim start
    claims['Age'] = (claims['ClaimStartDt'] - claims['DOB']).dt.days // 365
    
    # Number of diagnosis and procedure codes
    diag_cols = [c for c in claims.columns if 'ClmDiagnosisCode' in c]
    proc_cols = [c for c in claims.columns if 'ClmProcedureCode' in c]
    
    claims['Num_Diagnosis'] = claims[diag_cols].notnull().sum(axis=1)
    claims['Num_Procedures'] = claims[proc_cols].notnull().sum(axis=1)
    
    # Replace RenalDiseaseIndicator 'Y' with 1, '0' with 0 (it's object type)
    claims['RenalDiseaseIndicator'] = claims['RenalDiseaseIndicator'].replace({'Y': 1, '0': 0}).astype(float)
    
    # Chronic conditions: they are often coded as 1 (Yes), 2 (No). Let's standardise to 0/1.
    chronic_cols = [c for c in claims.columns if 'ChronicCond' in c]
    for col in chronic_cols:
        claims[col] = claims[col].replace({2: 0})
        
    # Gender: standardise to 0/1 if it's 1/2
    claims['Gender'] = claims['Gender'].replace({2: 0})
    
    # Fill NA for financial columns
    claims['DeductibleAmtPaid'] = claims['DeductibleAmtPaid'].fillna(0)
    
    # 4. Aggregate to Provider Level
    print("Aggregating to Provider Level...")
    agg_funcs = {
        'BeneID': 'nunique', # Number of unique beneficiaries
        'ClaimID': 'count', # Total number of claims
        'InscClaimAmtReimbursed': ['sum', 'mean', 'max'],
        'DeductibleAmtPaid': ['sum', 'mean', 'max'],
        'Is_Inpatient': 'sum', # Total inpatient claims
        'Claim_Duration': 'mean',
        'Age': 'mean',
        'Num_Diagnosis': 'mean',
        'Num_Procedures': 'mean',
        'RenalDiseaseIndicator': 'mean',
        'Gender': 'mean',
        'IPAnnualReimbursementAmt': 'mean',
        'IPAnnualDeductibleAmt': 'mean',
        'OPAnnualReimbursementAmt': 'mean',
        'OPAnnualDeductibleAmt': 'mean'
    }
    
    # Add chronic conditions to aggregation
    for col in chronic_cols:
        agg_funcs[col] = 'mean' # Proportion of claims with this chronic condition
        
    provider_features = claims.groupby('Provider').agg(agg_funcs).reset_index()
    
    # Flatten hierarchical columns
    provider_features.columns = ['_'.join(col).strip('_') for col in provider_features.columns.values]
    
    # Rename some columns for clarity
    provider_features.rename(columns={
        'BeneID_nunique': 'Num_Unique_Beneficiaries',
        'ClaimID_count': 'Total_Claims',
        'Is_Inpatient_sum': 'Total_Inpatient_Claims'
    }, inplace=True)
    
    # Add Outpatient claim count
    provider_features['Total_Outpatient_Claims'] = provider_features['Total_Claims'] - provider_features['Total_Inpatient_Claims']
    
    # 5. Merge with Labels
    print("Merging with Fraud Labels...")
    final_data = pd.merge(provider_features, train, on='Provider', how='left')
    
    # Convert label to binary
    final_data['PotentialFraud'] = final_data['PotentialFraud'].replace({'Yes': 1, 'No': 0})
    
    # Fill remaining NaNs if any
    final_data = final_data.fillna(0)
    
    # 6. Save Final Dataset
    output_path = os.path.join('data', 'processed_claims.csv')
    print(f"Saving final dataset to {output_path}...")
    final_data.to_csv(output_path, index=False)
    
    print("\n================ PREPROCESSING COMPLETE ================")
    print(f"Final Dataset Shape: {final_data.shape}")
    fraud_count = final_data['PotentialFraud'].sum()
    non_fraud_count = len(final_data) - fraud_count
    print(f"Fraudulent Records (Providers): {fraud_count}")
    print(f"Non-Fraudulent Records (Providers): {non_fraud_count}")
    print(f"Fraud Percentage: {(fraud_count / len(final_data)) * 100:.2f}%")
    if (fraud_count / len(final_data)) < 0.2:
        print("WARNING: Class Imbalance Detected. Consider SMOTE or class weights during model training.")
        
    print("\nFinal Feature List:")
    for col in final_data.columns:
        print(f" - {col}")
        
    print(f"\nSaved to: {output_path}")

def preprocess_dataset1():
    print("\n--- PREPROCESSING DATASET 1 (SYNTHETIC HEALTH CLAIMS) ---")
    base_path = os.path.join('data', 'archive (1)')
    file_path = os.path.join(base_path, 'synthetic_health_claims.csv')
    
    df = pd.read_csv(file_path)
    print(f"Original shape: {df.shape}")
    
    # 1. Drop duplicates
    df = df.drop_duplicates()
    
    # 2. Convert booleans to int
    df['Claim_Submitted_Late'] = df['Claim_Submitted_Late'].astype(int)
    df['Is_Fraudulent'] = df['Is_Fraudulent'].astype(int)
    
    # 3. Handle Dates
    df['Claim_Date'] = pd.to_datetime(df['Claim_Date'])
    df['Service_Date'] = pd.to_datetime(df['Service_Date'])
    df['Policy_Expiration_Date'] = pd.to_datetime(df['Policy_Expiration_Date'])
    
    df['Service_to_Claim_Days'] = (df['Claim_Date'] - df['Service_Date']).dt.days
    df['Policy_Days_Left'] = (df['Policy_Expiration_Date'] - df['Claim_Date']).dt.days
    
    # 4. Drop IDs, highly cardinal features, and raw dates
    cols_to_drop = [
        'Patient_ID', 'Policy_Number', 'Claim_ID', 'Hospital_ID', 
        'Diagnosis_Code', 'Procedure_Code', 'Patient_City', 'Patient_State', 
        'Provider_City', 'Provider_State', 'Claim_Date', 'Service_Date', 
        'Policy_Expiration_Date'
    ]
    df = df.drop(columns=cols_to_drop, errors='ignore')
    
    # 5. One-hot encoding for categoricals
    categorical_cols = ['Patient_Gender', 'Provider_Type', 'Provider_Specialty', 
                        'Admission_Type', 'Discharge_Type', 'Service_Type']
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
    
    # 6. Save final dataset
    output_path = os.path.join('data', 'processed_claims_synthetic.csv')
    df.to_csv(output_path, index=False)
    
    print(f"Final Dataset Shape: {df.shape}")
    fraud_count = df['Is_Fraudulent'].sum()
    print(f"Fraudulent Records (Claims): {fraud_count}")
    print(f"Non-Fraudulent Records (Claims): {len(df) - fraud_count}")
    print(f"Fraud Percentage: {(fraud_count / len(df)) * 100:.2f}%")
    print(f"Saved to: {output_path}")

def preprocess_cms():
    print("\n--- PREPROCESSING CMS UTILIZATION (UNLABELED) ---")
    file_path = os.path.join('data', 'Utilization_3.csv')
    
    df = pd.read_csv(file_path, low_memory=False)
    print(f"Original shape: {df.shape}")
    
    # 1. Drop highly missing or redundant columns
    cols_to_drop = ['Ind_PAC_ID', 'Provider Middle Name', 'suff', 'Percentile']
    df = df.drop(columns=cols_to_drop, errors='ignore')
    
    # 2. Convert 'Count' to numeric (remove commas, handle non-numeric)
    if 'Count' in df.columns and df['Count'].dtype == object:
        df['Count'] = pd.to_numeric(df['Count'].astype(str).str.replace(',', ''), errors='coerce')
        df['Count'] = df['Count'].fillna(0)
    
    # 3. Drop rows missing critical identifiers (NPI) if any
    df = df.dropna(subset=['NPI'])
    
    # 4. Fill missing names
    df['Provider Last Name'] = df['Provider Last Name'].fillna('UNKNOWN')
    df['Provider First Name'] = df['Provider First Name'].fillna('UNKNOWN')
    
    output_path = os.path.join('data', 'processed_cms_unlabeled.csv')
    df.to_csv(output_path, index=False)
    print(f"Final Dataset Shape: {df.shape}")
    print(f"Saved to: {output_path}")
    print("NOTE: This dataset remains unlabeled and separate from the supervised fraud datasets.")

if __name__ == "__main__":
    preprocess()
    preprocess_dataset1()
    preprocess_cms()
