# Génération des Embeddings

## Prérequis

- Python 3.10+
- PyTorch avec ROCm (GPU AMD) recommandé
- ~10 GB RAM
- ~5 GB espace disque

## Installation

```bash
pip install -r requirements.txt
```

## Génération

```bash
cd scripts
python generate_embeddings.py
```

Temps estimé: 2-3 minutes avec GPU ROCm, 10-15 minutes sur CPU

## Sortie

Le script génère dans `embeddings/`:
- `chunks.json` (~15 MB) - Métadonnées et texte
- `embeddings.npy.gz` (~13 MB) - Vecteurs compressés
- `metadata.json` - Statistiques

## Après génération

```bash
git add embeddings/
git commit -m "Update embeddings"
git push
```

GitHub Actions déploiera automatiquement sur GitHub Pages.
