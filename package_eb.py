import zipfile
import os

def create_eb_zip():
    zip_name = 'FraudLens-Backend-v6.zip'
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add backend files
        backend_dir = 'backend'
        for root, _, files in os.walk(backend_dir):
            if '__pycache__' in root:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                # Ensure forward slashes in archive name
                arcname = os.path.relpath(file_path, backend_dir).replace('\\', '/')
                zf.write(file_path, arcname)
        
        # Add model files
        model_dir = 'model'
        for root, _, files in os.walk(model_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Model files go into a 'model/' folder in the zip
                arcname = 'model/' + os.path.relpath(file_path, model_dir).replace('\\', '/')
                zf.write(file_path, arcname)

if __name__ == '__main__':
    create_eb_zip()
    print("Created FraudLens-Backend-v5.zip successfully with forward slashes.")
