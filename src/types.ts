export interface ChunkMetadata {
  id: string;
  doc_id: string;
  chunk_index: number;
  text: string;
  metadata: {
    title: string;
    product: string;
    category: string;
    tags: string[];
    language: string;
    document_type: string;
    version?: string;
    source_pdf?: string;
    release_date?: string;
  };
}

export interface SearchResult extends ChunkMetadata {
  score: number;
}

export interface SearchFilters {
  category?: string;
  product?: string;
  tags?: string[];
  language?: string;
  top_k?: number;
}
