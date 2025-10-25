import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple


def extract_frontmatter(filepath: Path) -> Dict:
    """Parse YAML frontmatter d'un fichier markdown"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.startswith('---'):
        return {}
    
    match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
    if match:
        return yaml.safe_load(match.group(1))
    return {}


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Chunking intelligent:
    - 512 tokens par chunk (approximation: 4 chars = 1 token)
    - Overlap de 50 tokens
    - Coupe aux limites de phrases
    - Supprime les headers "## Page X"
    """
    # Supprimer headers "## Page X"
    text = re.sub(r'^##\s*Page\s*\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)  # Normaliser espaces
    
    chunk_chars = chunk_size * 4
    overlap_chars = overlap * 4
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_chars
        chunk = text[start:end]
        
        # Couper à la dernière phrase complète
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n\n')
            cut_point = max(last_period, last_newline)
            
            if cut_point > chunk_chars * 0.5:
                end = start + cut_point + 1
                chunk = text[start:end]
        
        if chunk.strip():
            chunks.append(chunk.strip())
        
        start = end - overlap_chars
    
    return chunks


def process_document(filepath: Path) -> List[Dict]:
    """
    Traite un document markdown:
    - Extrait frontmatter
    - Chunke le contenu
    - Retourne chunks avec métadonnées
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire frontmatter
    metadata = extract_frontmatter(filepath)
    
    # Retirer frontmatter du contenu
    if content.startswith('---'):
        content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    
    # Chunker
    text_chunks = chunk_text(content)
    
    # Enrichir avec métadonnées
    chunks = []
    for i, text in enumerate(text_chunks):
        chunk = {
            'id': f"{filepath.stem}_chunk_{i:04d}",
            'doc_id': str(filepath),
            'chunk_index': i,
            'text': text,
            'metadata': metadata
        }
        chunks.append(chunk)
    
    return chunks
