#!/usr/bin/env python3
import json
import re
import subprocess
from pathlib import Path

def extract_lfs_oid(filepath):
    """Extract OID (sha256) from Git LFS pointer file"""
    try:
        # Read from git repository (pointer) not working directory (actual file)
        content = subprocess.check_output(['git', 'show', f'HEAD:{filepath}'], universal_newlines=True)
        
        # Look for oid sha256:xxxxxxxx...
        match = re.search(r'oid sha256:([a-f0-9]{64})', content)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"[DEBUG] Error reading LFS pointer for {filepath}: {e}")
    
    return None

def generate_media_url(user, repo, filepath, oid):
    """Generate GitHub media URL for Git LFS file"""
    # GitHub media URL format for LFS files
    # Use media.githubusercontent.com CDN which serves LFS files without auth
    return f"https://media.githubusercontent.com/media/{user}/{repo}/refs/heads/main/{filepath}"

def main():
    """Generate LFS URLs for embedding files"""
    GITHUB_USER = 'njfsmallet-eng'
    REPO_NAME = 'twincat-knowledge-mcp-server'
    BRANCH = 'main'
    
    # Get current commit SHA
    try:
        commit_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], universal_newlines=True).strip()
    except:
        # Fallback to 'main' if git not available
        commit_sha = 'main'
    
    # Define embedding files
    embedding_files = {
        'chunks': 'embeddings/chunks.json',
        'embeddings': 'embeddings/embeddings.npy.gz',
        'metadata': 'embeddings/metadata.json'
    }
    
    urls = {}
    
    # Generate URLs - extract OIDs from LFS pointers
    for key, filepath in embedding_files.items():
        # Try to read the LFS pointer file
        try:
            oid = extract_lfs_oid(filepath)
            if oid:
                # Generate media URL using OID
                url = generate_media_url(GITHUB_USER, REPO_NAME, filepath, oid)
                print(f"[INFO] Extracted OID for {key}: {oid[:16]}...")
            else:
                # Fallback to raw.githubusercontent.com
                url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{commit_sha}/{filepath}"
                print(f"[WARNING] No OID found for {key}, using raw URL")
        except Exception as e:
            # Fallback to raw.githubusercontent.com
            url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{commit_sha}/{filepath}"
            print(f"[WARNING] Error processing {key}: {e}, using raw URL")
        
        urls[key] = url
        print(f"[INFO] Generated URL for {key}: {url}")
    
    # Save to API directory
    output_dir = Path('gh-pages/api')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'embeddings.json'
    with open(output_file, 'w') as f:
        json.dump(urls, f, indent=2)
    
    print(f"[OK] Saved URLs to {output_file}")
    print(f"[INFO] Generated {len(urls)} URLs")

if __name__ == '__main__':
    main()
