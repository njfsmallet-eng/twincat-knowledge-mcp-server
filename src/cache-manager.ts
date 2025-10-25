import { promises as fs } from 'fs';
import { join, dirname } from 'path';
import { ChunkMetadata } from './types.js';

interface EmbeddingsUrls {
  chunks: string;
  embeddings: string;
  metadata: string;
}

export class CacheManager {
  private cacheDir: string;
  private baseUrl: string;

  constructor(cacheDir: string, baseUrl: string) {
    this.cacheDir = cacheDir;
    this.baseUrl = baseUrl;
  }

  /**
   * Ensure the cache directory exists
   */
  async ensureCacheDirectory(): Promise<void> {
    try {
      await fs.access(this.cacheDir);
      console.error(`[CACHE] Cache directory exists: ${this.cacheDir}`);
    } catch {
      await fs.mkdir(this.cacheDir, { recursive: true });
      console.error(`[CACHE] Created cache directory: ${this.cacheDir}`);
    }
  }

  /**
   * Check if cache files exist and are valid
   */
  async isCacheValid(): Promise<boolean> {
    try {
      const chunksPath = join(this.cacheDir, 'chunks.json');
      const embeddingsPath = join(this.cacheDir, 'embeddings.npy.gz');
      
      await fs.access(chunksPath);
      await fs.access(embeddingsPath);
      
      console.error(`[CACHE] Cache files found at: ${this.cacheDir}`);
      console.error(`[CACHE] - chunks.json: ${chunksPath}`);
      console.error(`[CACHE] - embeddings.npy.gz: ${embeddingsPath}`);
      return true;
    } catch (error) {
      console.error(`[CACHE] Cache files not found in: ${this.cacheDir}`);
      console.error(`[CACHE] Error: ${error}`);
      return false;
    }
  }

  /**
   * Load chunks from cache or download from GitHub Pages
   */
  async loadOrDownloadChunks(): Promise<ChunkMetadata[]> {
    const chunksPath = join(this.cacheDir, 'chunks.json');
    
    try {
      // Try to load from cache first
      const cachedData = await fs.readFile(chunksPath, 'utf-8');
      const chunks = JSON.parse(cachedData) as ChunkMetadata[];
      console.error(`[CACHE] Loaded ${chunks.length} chunks from cache`);
      return chunks;
    } catch {
      // Cache miss, download from GitHub Pages
      console.error('[CACHE] Loading chunks from GitHub Pages...');
      
      const apiUrl = `${this.baseUrl}/api/embeddings.json`;
      const apiRes = await fetch(apiUrl);
      if (!apiRes.ok) {
        throw new Error(`Failed to fetch embeddings API: ${apiRes.status}`);
      }
      
      const urls = await apiRes.json() as EmbeddingsUrls;
      
      // Download chunks
      const chunksRes = await fetch(urls.chunks);
      if (!chunksRes.ok) {
        throw new Error(`Failed to load chunks: ${chunksRes.status}`);
      }
      const chunks = await chunksRes.json() as ChunkMetadata[];
      
      // Save to cache
      await fs.writeFile(chunksPath, JSON.stringify(chunks, null, 2));
      console.error(`[CACHE] Cached ${chunks.length} chunks to disk`);
      
      return chunks;
    }
  }

  /**
   * Load embeddings from cache or download from GitHub Pages
   */
  async loadOrDownloadEmbeddings(): Promise<ArrayBuffer> {
    const embeddingsPath = join(this.cacheDir, 'embeddings.npy.gz');
    
    try {
      // Try to load from cache first
      const cachedData = await fs.readFile(embeddingsPath);
      console.error('[CACHE] Loaded embeddings from cache');
      return cachedData.buffer;
    } catch {
      // Cache miss, download from GitHub Pages
      console.error('[CACHE] Loading embeddings from GitHub Pages...');
      
      const apiUrl = `${this.baseUrl}/api/embeddings.json`;
      const apiRes = await fetch(apiUrl);
      if (!apiRes.ok) {
        throw new Error(`Failed to fetch embeddings API: ${apiRes.status}`);
      }
      
      const urls = await apiRes.json() as EmbeddingsUrls;
      
      // Download embeddings
      const embRes = await fetch(urls.embeddings);
      if (!embRes.ok) {
        throw new Error(`Failed to load embeddings: ${embRes.status}`);
      }
      const embBuffer = await embRes.arrayBuffer();
      
      // Save to cache
      await fs.writeFile(embeddingsPath, Buffer.from(embBuffer));
      console.error('[CACHE] Cached embeddings to disk');
      
      return embBuffer;
    }
  }

  /**
   * Get the path to the Xenova model cache directory
   */
  getModelCachePath(): string {
    return join(this.cacheDir, 'model');
  }
}
