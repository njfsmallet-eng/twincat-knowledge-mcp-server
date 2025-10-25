import { pipeline } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.10.0';

let embedder = null;
let chunks = null;
let embeddings = null;

// Configuration - à mettre à jour avec votre repo GitHub
const GITHUB_USER = 'njfsmallet-eng';
const REPO_NAME = 'twincat-knowledge-mcp-server';

// Initialisation au chargement
async function init() {
    console.log('[DEBUG] Initializing search...');
    const statusEl = document.getElementById('status');
    
    try {
        console.log('[DEBUG] Starting model load...');
        statusEl.textContent = 'Loading model (first time: ~90 MB, then cached)...';
        
        // 1. Charger modèle ONNX (cache automatique IndexedDB)
        console.log('[DEBUG] Loading model pipeline...');
        embedder = await pipeline(
            'feature-extraction',
            'Xenova/all-MiniLM-L6-v2',
            {
                quantized: true, // Use quantized model for faster loading
                cache_dir: 'indexeddb://transformers-cache' // Cache in IndexedDB
            }
        );
        console.log('[DEBUG] Model loaded successfully');
        
        statusEl.textContent = 'Loading embeddings URLs...';
        
        // 2. Charger URLs depuis l'API
        console.log('[DEBUG] Fetching /api/embeddings.json...');
        const apiRes = await fetch('./api/embeddings.json');
        console.log('[DEBUG] API response status:', apiRes.status, apiRes.statusText);
        
        if (!apiRes.ok) {
            const errorText = await apiRes.text();
            console.error('[DEBUG] API response error:', errorText);
            throw new Error(`Failed to load API: ${apiRes.status} ${apiRes.statusText}`);
        }
        
        const urls = await apiRes.json();
        console.log('[DEBUG] URLs loaded:', urls);
        
        statusEl.textContent = 'Loading chunks...';
        
        // Charger chunks depuis LFS media URL
        console.log('[DEBUG] Fetching chunks from:', urls.chunks);
        const chunksRes = await fetch(urls.chunks);
        console.log('[DEBUG] Chunks response status:', chunksRes.status);
        
        if (!chunksRes.ok) {
            throw new Error(`Failed to load chunks: ${chunksRes.status}`);
        }
        chunks = await chunksRes.json();
        console.log('[DEBUG] Chunks loaded:', chunks.length, 'chunks');
        
        statusEl.textContent = 'Loading embeddings...';
        
        // Charger embeddings compressés depuis LFS media URL
        console.log('[DEBUG] Fetching embeddings from:', urls.embeddings);
        const embRes = await fetch(urls.embeddings);
        console.log('[DEBUG] Embeddings response status:', embRes.status);
        
        if (!embRes.ok) {
            throw new Error(`Failed to load embeddings: ${embRes.status}`);
        }
        const embBuffer = await embRes.arrayBuffer();
        console.log('[DEBUG] Embeddings buffer size:', embBuffer.byteLength);
        
        // Décompresser avec l'API native du navigateur (comme le client MCP)
        let decompressed;
        try {
            const stream = new DecompressionStream('gzip');
            const blob = new Blob([embBuffer]);
            const decompressedBlob = await blob.stream().pipeThrough(stream);
            const decompressedArrayBuffer = await new Response(decompressedBlob).arrayBuffer();
            decompressed = new Uint8Array(decompressedArrayBuffer);
        } catch (error) {
            console.log('[DEBUG] Native decompression failed, loading Pako...');
            // Fallback: charger Pako dynamiquement
            const pakoScript = document.createElement('script');
            pakoScript.src = 'https://cdn.jsdelivr.net/npm/pako@2.1.0/dist/pako.min.js';
            await new Promise((resolve, reject) => {
                pakoScript.onload = resolve;
                pakoScript.onerror = reject;
                document.head.appendChild(pakoScript);
            });
            
            decompressed = pako.inflate(new Uint8Array(embBuffer));
        }
        embeddings = parseNpy(decompressed.buffer);
        
        statusEl.className = 'status ready';
        statusEl.textContent = `Ready! ${chunks.length} chunks loaded`;
        document.getElementById('search-ui').style.display = 'block';
        
    } catch (error) {
        statusEl.className = 'status error';
        statusEl.textContent = `Error: ${error.message}`;
        console.error(error);
    }
}

// Recherche
async function search(query, topK = 10) {
    if (!embedder || !chunks || !embeddings) {
        throw new Error('Not initialized');
    }
    
    // 1. Générer embedding de la query
    const output = await embedder(query, { pooling: 'mean', normalize: true });
    const queryEmb = Array.from(output.data);
    
    // 2. Cosine similarity avec tous les embeddings (comme le client MCP)
    const results = [];
    for (let i = 0; i < chunks.length && i < embeddings.length; i++) {
        const similarity = cosineSimilarity(queryEmb, embeddings[i]);
        results.push({
            ...chunks[i],
            score: similarity
        });
    }
    
    // 3. Trier et prendre top-K
    results.sort((a, b) => b.score - a.score);
    return results.slice(0, topK);
}

// Cosine similarity
function cosineSimilarity(a, b) {
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < a.length; i++) {
        dotProduct += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }
    
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

// Parser NPY format simplifié (Float32 seulement)
function parseNpy(buffer) {
    const view = new DataView(buffer);
    
    // Parser NPY header magique (simplifié)
    if (view.getUint8(0) !== 0x93 || view.getUint8(1) !== 0x4e ||
        view.getUint8(2) !== 0x55 && view.getUint8(3) !== 0x4d &&
        view.getUint8(4) !== 0x50 && view.getUint8(5) !== 0x59) {
        throw new Error('Invalid NPY file');
    }
    
    // Lire version et header
    const version = view.getUint8(6);
    let offset = version === 1 ? 8 : 10;
    
    // Lire header length (2 bytes pour v1, 4 bytes pour v2)
    let headerLen;
    if (version === 1) {
        headerLen = view.getUint16(offset, true);
        offset += 2;
    } else {
        headerLen = view.getUint32(offset, true);
        offset += 4;
    }
    
    // Parser header string pour shape et dtype
    const headerText = new TextDecoder().decode(buffer.slice(offset, offset + headerLen));
    console.log('[DEBUG] NPY header text:', headerText);
    
    // Extraire le dtype avec une regex plus robuste
    const dtypeMatch = headerText.match(/descr':\s*'([^']+)'/);
    const shapeMatch = headerText.match(/shape':\s*\((\d+),\s*(\d+)\)/);
    
    if (!shapeMatch || !dtypeMatch) {
        console.error('[DEBUG] Cannot parse NPY header. Shape match:', shapeMatch, 'Dtype match:', dtypeMatch);
        throw new Error('Cannot parse NPY header');
    }
    
    const numVectors = parseInt(shapeMatch[1]);
    const dims = parseInt(shapeMatch[2]);
    const dtype = dtypeMatch[1];
    
    console.log('[DEBUG] NPY parsed - vectors:', numVectors, 'dims:', dims, 'dtype:', dtype);
    
    if (dtype !== '<f4') {
        throw new Error(`Unsupported dtype: ${dtype}`);
    }
    
    offset += headerLen;
    
    // Aligner l'offset sur 4 octets pour Float32Array
    const padding = (4 - (offset % 4)) % 4;
    offset += padding;
    
    console.log('[DEBUG] NPY data offset:', offset, 'padding:', padding);
    
    // Calculer la taille des données et vérifier les limites
    const expectedDataSize = numVectors * dims * 4; // 4 bytes par float32
    const availableSize = buffer.byteLength - offset;
    const actualDataSize = Math.min(expectedDataSize, availableSize);
    const actualNumVectors = Math.floor(actualDataSize / (dims * 4));
    
    console.log('[DEBUG] Expected data size:', expectedDataSize, 'Available size:', availableSize);
    console.log('[DEBUG] Using actual data size:', actualDataSize, 'Actual vectors:', actualNumVectors);
    
    if (actualNumVectors === 0) {
        throw new Error(`No data available: actual vectors = ${actualNumVectors}`);
    }
    
    // Lire données float32 avec la taille disponible
    const data = new Float32Array(buffer, offset, actualNumVectors * dims);
    
    // Convertir en array de vecteurs
    const vectors = [];
    for (let i = 0; i < actualNumVectors; i++) {
        vectors.push(Array.from(data.slice(i * dims, (i + 1) * dims)));
    }
    
    return vectors;
}

// API endpoint pour MCP
window.searchAPI = async function(query, filters = {}) {
    const results = await search(query, filters.top_k || 10);
    
    // Filtrage par métadonnées si demandé
    if (filters.category) {
        return results.filter(r => r.metadata.category === filters.category);
    }
    if (filters.product) {
        return results.filter(r => r.metadata.product === filters.product);
    }
    
    return results;
};

// UI test
window.search = async function() {
    const query = document.getElementById('query').value;
    const resultsEl = document.getElementById('results');
    resultsEl.innerHTML = 'Searching...';
    
    const results = await searchAPI(query, { top_k: 5 });
    
    resultsEl.innerHTML = results.map(r => `
        <div class="result">
            <strong>${r.metadata.title}</strong> (${r.metadata.product})
            <br>Score: ${r.score.toFixed(3)}
            <br><small>${r.text.substring(0, 200)}...</small>
        </div>
    `).join('');
};

// Initialiser au chargement
init();
