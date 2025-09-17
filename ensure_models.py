#!/usr/bin/env python3
"""
Simple Model Download Script
Downloads the required PII detection models from their correct repositories
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path

def ensure_package_installed(pkg: str) -> bool:
    """Ensure a package is installed"""
    try:
        __import__(pkg)
        return True
    except ImportError:
        print(f"Installing {pkg}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '--quiet'])
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to install {pkg}")
            return False

def file_exists_in(path: str) -> bool:
    """Check if required model files exist in the given path"""
    candidates = [
        'tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json', 
        'added_tokens.json', 'merges.txt', 'vocab.json', 'spm.model',
        'config.json', 'pytorch_model.bin', 'model.safetensors', 'checkpoint_0.ckpt',
        'pytorch_model-00001-of-00001.bin', 'model-00001-of-00001.safetensors'
    ]
    return any(os.path.exists(os.path.join(path, f)) for f in candidates)

def dir_file_count(path: str) -> int:
    """Count files in directory"""
    try:
        return len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
    except:
        return 0

def download_model(repo: str, target_dir: str, base_path: str) -> bool:
    """Download a single model from HuggingFace repository"""
    print(f"🌐 Downloading {target_dir} from {repo}...")
    
    try:
        from huggingface_hub import snapshot_download
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Download snapshot
            local_path = snapshot_download(
                repo_id=repo, 
                local_dir=tmp_dir, 
                local_dir_use_symlinks=False
            )
            print(f"📦 Downloaded to: {local_path}")
            
            # Create target directory
            target_path = os.path.join(base_path, target_dir)
            os.makedirs(target_path, exist_ok=True)
            
            # Copy all files from the downloaded repository
            for root, dirs, files in os.walk(local_path):
                for file in files:
                    if file.startswith('.') or file.startswith('last'):
                        continue  # Skip hidden files
                    
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, local_path)
                    dest_file = os.path.join(target_path, rel_path)
                    
                    # Create subdirectories if needed
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    shutil.copy2(src_file, dest_file)
            
            # Fix the misspelled checkpoint filename
            misspelled_file = os.path.join(target_path, 'ckeckpoint_0.ckpt')
            correct_file = os.path.join(target_path, 'checkpoint_0.ckpt')
            if os.path.exists(misspelled_file):
                os.rename(misspelled_file, correct_file)
                print(f"🔧 Renamed ckeckpoint_0.ckpt to checkpoint_0.ckpt")
            
            print(f"📁 Copied all files to {target_dir}")
            return True
            
    except Exception as e:
        print(f"❌ Failed to download {target_dir} from {repo}: {e}")
        return False

def main():
    """Main function"""
    print("🚀 PII Model Manager")
    print("=" * 50)
    
    # Ensure huggingface_hub is installed
    if not ensure_package_installed('huggingface_hub'):
        print("❌ Failed to install huggingface_hub")
        return 1
    
    # Set up paths
    base_path = "pii-mask/pii-masker/output model"
    os.makedirs(base_path, exist_ok=True)
    
    # Define model repositories and their target directories
    models = [
        ('hydroxai/pii_model_weight', 'deberta3base_1024'),
        ('hydroxai/pii_model_longtransfomer_version', 'longtransformer_pii')
    ]
    
    # Check if models already exist
    missing_models = []
    for repo, target_dir in models:
        target_path = os.path.join(base_path, target_dir)
        if not os.path.isdir(target_path) or not file_exists_in(target_path):
            missing_models.append((repo, target_dir))
        else:
            count = dir_file_count(target_path)
            print(f"✅ {target_dir}: {count} files (already present)")
    
    if not missing_models:
        print("✅ All models are ready!")
        return 0
    
    print(f"📥 Downloading {len(missing_models)} missing models...")
    
    # Download missing models
    success_count = 0
    for repo, target_dir in missing_models:
        if download_model(repo, target_dir, base_path):
            success_count += 1
            count = dir_file_count(os.path.join(base_path, target_dir))
            print(f"✅ {target_dir}: {count} files")
        else:
            print(f"❌ Failed to download {target_dir}")
    
    if success_count == len(missing_models):
        print("✅ All models downloaded successfully!")
        return 0
    else:
        print(f"⚠️ Downloaded {success_count}/{len(missing_models)} models")
        return 1

if __name__ == '__main__':
    sys.exit(main())