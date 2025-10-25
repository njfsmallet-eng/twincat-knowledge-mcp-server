// Script pour précharger le modèle Xenova sur GitHub Pages
// À exécuter une fois pour mettre le modèle en cache

import { pipeline } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.10.0';

console.log('Preloading Xenova model for GitHub Pages...');

try {
    const embedder = await pipeline(
        'feature-extraction',
        'Xenova/all-MiniLM-L6-v2',
        {
            quantized: true,
            cache_dir: 'indexeddb://transformers-cache'
        }
    );
    
    console.log('✅ Model preloaded successfully!');
    console.log('The model is now cached and will load faster on the GitHub Pages site.');
    
    // Test simple
    const testOutput = await embedder('test query', { pooling: 'mean', normalize: true });
    console.log('✅ Test embedding generated:', testOutput.data.length, 'dimensions');
    
} catch (error) {
    console.error('❌ Failed to preload model:', error);
}
