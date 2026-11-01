import zipfile
import os

def create_eb_zip():
    zip_name = 'FraudLens-Backend-v7.zip'
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add backend files
        backend_dir = 'backend'
        for root, dirs, files in os.walk(backend_dir):
            # Exclude venv and pycache
            if 'venv' in root or '__pycache__' in root:
                continue
            for file in files:
                if file.endswith('.pyc') or file == 'patch_main.py':
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, backend_dir).replace('\\', '/')
                zf.write(file_path, arcname)
        
        # Add model files
        model_dir = 'model'
        for root, dirs, files in os.walk(model_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = 'model/' + os.path.relpath(file_path, model_dir).replace('\\', '/')
                zf.write(file_path, arcname)

        # Add data files
        data_file = os.path.join('data', 'synthetic_database.json')
        if os.path.exists(data_file):
            zf.write(data_file, 'data/synthetic_database.json')

if __name__ == '__main__':
    create_eb_zip()
    print("Created FraudLens-Backend-v7.zip successfully.")
