import { SearchResult, SearchFilters, ChunkMetadata } from './types.js';
import { pipeline } from '@xenova/transformers';

interface EmbeddingsUrls {
  chunks: string;
  embeddings: string;
  metadata: string;
}

export class GitHubPagesClient {
  private baseUrl: string;
  private embedder: any = null;
  
  constructor(githubUser: string, repo: string) {
    this.baseUrl = `https://${githubUser}.github.io/${repo}`;
  }
  
  private async initializeEmbedder() {
    if (this.embedder !== null) {
      return this.embedder;
    }
    
    console.error('[MCP] Initializing Xenova embedding model...');
    this.embedder = await pipeline(
      'feature-extraction',
      'Xenova/all-MiniLM-L6-v2',
      {
        quantized: true
      }
    );
    console.error('[MCP] Embedding model initialized');
    
    return this.embedder;
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
      
      // Charger et utiliser le modèle d'embedding Xenova
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
    // Initialize the embedder if not already done
    const embedder = await this.initializeEmbedder();
    
    // Generate embedding using the Xenova model (same as search.js)
    const output = await embedder(query, { pooling: 'mean', normalize: true });
    const embedding = Array.from(output.data) as number[];
    
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
