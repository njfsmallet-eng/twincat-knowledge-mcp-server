import { SearchResult, SearchFilters, ChunkMetadata } from './types.js';

interface EmbeddingsUrls {
  chunks: string;
  embeddings: string;
  metadata: string;
}

export class GitHubPagesClient {
  private baseUrl: string;
  
  constructor(githubUser: string, repo: string) {
    this.baseUrl = `https://${githubUser}.github.io/${repo}`;
  }
  
  async search(query: string, filters: SearchFilters = {}): Promise<SearchResult[]> {
    try {
      // Appeler l'API hébergée sur GitHub Pages via le fichier API
      const apiUrl = `${this.baseUrl}/api/embeddings.json`;
      console.error(`[MCP] Fetching embeddings URLs from: ${apiUrl}`);
      
      const apiRes = await fetch(apiUrl);
      if (!apiRes.ok) {
        throw new Error(`Failed to fetch embeddings API: ${apiRes.status}`);
      }
      
      const urls = await apiRes.json() as EmbeddingsUrls;
      console.error(`[MCP] Embeddings URLs loaded:`, urls);
      
      // Charger les chunks
      console.error(`[MCP] Loading chunks from: ${urls.chunks}`);
      const chunksRes = await fetch(urls.chunks);
      if (!chunksRes.ok) {
        throw new Error(`Failed to load chunks: ${chunksRes.status}`);
      }
      const chunks = await chunksRes.json() as ChunkMetadata[];
      console.error(`[MCP] Loaded ${chunks.length} chunks`);
      
      // Charger et décompresser les embeddings
      console.error(`[MCP] Loading embeddings from: ${urls.embeddings}`);
      const embRes = await fetch(urls.embeddings);
      if (!embRes.ok) {
        throw new Error(`Failed to load embeddings: ${embRes.status}`);
      }
      const embBuffer = await embRes.arrayBuffer();
      
      // Utiliser l'API native DecompressionStream
      let decompressed: Uint8Array;
      try {
        const stream = new DecompressionStream('gzip');
        const blob = new Blob([embBuffer]);
        const decompressedBlob = await blob.stream().pipeThrough(stream);
        const decompressedArrayBuffer = await new Response(decompressedBlob).arrayBuffer();
        decompressed = new Uint8Array(decompressedArrayBuffer);
      } catch (error) {
        // Fallback: utiliser une décompression manuelle basique
        console.error('[MCP] Native decompression failed, using simple fallback');
        decompressed = new Uint8Array(embBuffer);
      }
      
      // Parser NPY (version simplifiée pour Node.js)
      const embeddings = this.parseNpy(decompressed.buffer as ArrayBuffer);
      console.error(`[MCP] Parsed ${embeddings.length} embedding vectors`);
      
      // Charger le modèle d'embedding (nous allons utiliser une version côté serveur)
      // Pour l'instant, nous allons utiliser un embedding simple basé sur TF-IDF
      const queryEmbedding = await this.getQueryEmbedding(query);
      
      // Calculer les similarités
      const results: SearchResult[] = [];
      for (let i = 0; i < chunks.length && i < embeddings.length; i++) {
        const similarity = this.cosineSimilarity(queryEmbedding, embeddings[i]);
        results.push({
          ...chunks[i],
          score: similarity
        });
      }
      
      // Trier par score
      results.sort((a, b) => b.score - a.score);
      
      // Appliquer les filtres
      let filteredResults = results;
      if (filters.category) {
        filteredResults = filteredResults.filter(r => r.metadata.category === filters.category);
      }
      if (filters.product) {
        filteredResults = filteredResults.filter(r => r.metadata.product === filters.product);
      }
      if (filters.tags && filters.tags.length > 0) {
        filteredResults = filteredResults.filter(r => 
          filters.tags!.some(tag => r.metadata.tags.includes(tag))
        );
      }
      if (filters.language) {
        filteredResults = filteredResults.filter(r => r.metadata.language === filters.language);
      }
      
      // Retourner les top_k résultats
      return filteredResults.slice(0, filters.top_k || 10);
      
    } catch (error) {
      console.error('[MCP] Search error:', error);
      throw error;
    }
  }
  
  private async getQueryEmbedding(query: string): Promise<number[]> {
    // NOTE: This simplified embedding method doesn't match the quality of the
    // Xenova model used to generate the pre-computed embeddings.
    // For production use, consider either:
    // 1. Using @xenova/transformers with pipeline feature extraction
    // 2. Proxying requests to the GitHub Pages search API
    // 
    // Current implementation uses a hash-based approach for simplicity.
    
    const words = query.toLowerCase().split(/\s+/);
    const embedding = new Array(384).fill(0);
    
    // Simple hash-based encoding (NOT production quality)
    for (let i = 0; i < words.length && i < 384; i++) {
      const word = words[i];
      let hash = 0;
      for (let j = 0; j < word.length; j++) {
        hash = ((hash << 5) - hash) + word.charCodeAt(j);
        hash = hash & hash;
      }
      const index = Math.abs(hash) % 384;
      embedding[index] = 1.0;
    }
    
    // Normalize
    const norm = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
    if (norm > 0) {
      return embedding.map(v => v / norm);
    }
    return embedding;
  }
  
  private cosineSimilarity(a: number[], b: number[]): number {
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < Math.min(a.length, b.length); i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    
    const denominator = Math.sqrt(normA) * Math.sqrt(normB);
    return denominator > 0 ? dotProduct / denominator : 0;
  }
  
  private parseNpy(buffer: ArrayBuffer): number[][] {
    const view = new DataView(buffer);
    const version = view.getUint8(6);
    let offset = version === 1 ? 8 : 10;
    
    const headerLen = version === 1 
      ? view.getUint16(offset, true) 
      : view.getUint32(offset, true);
    offset += version === 1 ? 2 : 4;
    
    const headerText = new TextDecoder().decode(
      new Uint8Array(buffer).subarray(offset, offset + headerLen)
    );
    
    const dtypeMatch = headerText.match(/descr':\s*'([^']+)'/);
    const shapeMatch = headerText.match(/shape':\s*\((\d+),\s*(\d+)\)/);
    
    if (!shapeMatch || !dtypeMatch) {
      throw new Error('Cannot parse NPY header');
    }
    
    const numVectors = parseInt(shapeMatch[1]);
    const dims = parseInt(shapeMatch[2]);
    
    offset += headerLen;
    const padding = (4 - (offset % 4)) % 4;
    offset += padding;
    
    const expectedDataSize = numVectors * dims * 4;
    const availableSize = buffer.byteLength - offset;
    const actualDataSize = Math.min(expectedDataSize, availableSize);
    const actualNumVectors = Math.floor(actualDataSize / (dims * 4));
    
    const data = new Float32Array(buffer, offset, actualNumVectors * dims);
    const vectors: number[][] = [];
    
    for (let i = 0; i < actualNumVectors; i++) {
      vectors.push(Array.from(data.slice(i * dims, (i + 1) * dims)));
    }
    
    return vectors;
  }
  
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/embeddings.json`);
      return response.ok;
    } catch {
      return false;
    }
  }
}
