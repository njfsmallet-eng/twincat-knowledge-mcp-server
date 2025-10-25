#!/usr/bin/env python3
import json
import gzip
import numpy as np
from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from chunking import process_document
import sys
import io
import os

# Configure output encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Fix PyTorch compatibility issues
os.environ['TORCH_DISTRIBUTED_BACKEND'] = 'gloo'
# Patch torch.distributed for development builds
import torch
if not hasattr(torch.distributed, 'is_initialized'):
    torch.distributed.is_initialized = lambda: False

def main():
    print("Génération des embeddings avec GPU ROCm...")
    
    # 1. Charger modèle (compatible Transformers.js)
    # Use Xenova equivalent for compatibility
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'  # 384 dims, ~90 MB
    print(f"[INFO] Chargement du modèle {model_name}...")
    
    try:
        model = SentenceTransformer(model_name)
        print("[OK] Modèle chargé")
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement du modèle: {e}")
        print("[INFO] Tentative avec modèle alternatif...")
        try:
            model_name = 'all-MiniLM-L6-v2'
            model = SentenceTransformer(model_name)
            print("[OK] Modèle alternatif chargé")
        except Exception as e2:
            print(f"[ERROR] Impossible de charger le modèle: {e2}")
            return
    
    # Vérifier si GPU disponible
    try:
        import torch
        if torch.cuda.is_available():
            model = model.to('cuda')
            print("[OK] GPU détecté - utilisation du GPU")
        else:
            print("[INFO] Pas de GPU disponible - utilisation CPU (plus lent)")
    except Exception as e:
        print(f"[WARNING] Impossible de vérifier GPU: {e}")
        print("[INFO] Utilisation CPU")
    
    # 2. Traiter tous les documents
    print("[INFO] Traitement des documents...")
    docs_dir = Path('docs')
    all_chunks = []
    
    for md_file in tqdm(list(docs_dir.glob('*.md'))):
        if md_file.name == 'INDEX.md':
            continue
        chunks = process_document(md_file)
        all_chunks.extend(chunks)
    
    print(f"[OK] {len(all_chunks)} chunks générés")
    
    # 3. Générer embeddings
    print("[INFO] Génération des embeddings (batch 128)...")
    texts = [chunk['text'] for chunk in all_chunks]
    embeddings = model.encode(
        texts,
        batch_size=128,
        show_progress_bar=True,
        normalize_embeddings=True  # Important pour cosine similarity
    )
    
    # 4. Sauvegarder
    output_dir = Path('embeddings')
    output_dir.mkdir(exist_ok=True)
    
    # 4a. Chunks JSON (métadonnées + texte)
    print("[INFO] Sauvegarde chunks.json...")
    with open(output_dir / 'chunks.json', 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    
    # 4b. Embeddings en Float32 compressé
    print("[INFO] Sauvegarde embeddings.npy.gz...")
    embeddings_f32 = embeddings.astype(np.float32)
    with gzip.open(output_dir / 'embeddings.npy.gz', 'wb') as f:
        np.save(f, embeddings_f32)
    
    # 4c. Métadonnées
    metadata = {
        'model': model_name,
        'dimensions': embeddings.shape[1],
        'num_chunks': len(all_chunks),
        'chunk_size': 512,
        'overlap': 50,
        'generated_at': datetime.now().isoformat()
    }
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # 5. Statistiques
    print("\n[STATS] Statistiques:")
    print(f"  Chunks: {len(all_chunks)}")
    print(f"  Dimensions: {embeddings.shape[1]}")
    print(f"  Taille chunks.json: {(output_dir / 'chunks.json').stat().st_size / 1024 / 1024:.1f} MB")
    print(f"  Taille embeddings.npy.gz: {(output_dir / 'embeddings.npy.gz').stat().st_size / 1024 / 1024:.1f} MB")
    
    print("\n[OK] Génération terminée!")
    print("[NEXT] Prochaine étape: git add embeddings/ && git commit && git push")


if __name__ == '__main__':
    main()
