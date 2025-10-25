# TwinCAT Knowledge MCP Server

A Model Context Protocol (MCP) server providing semantic search access to TwinCAT 3 documentation. This project includes tools for converting PDFs to Markdown, generating embeddings with GPU acceleration, and hosting a searchable API on GitHub Pages.

## Overview

This project provides a complete semantic search solution for TwinCAT 3 documentation:

1. **PDF Conversion**: Converts 290 TwinCAT 3 documentation PDFs from Beckhoff to Markdown format
2. **Embedding Generation**: Generates semantic embeddings using GPU-accelerated models
3. **Search API**: Hosts a search API on GitHub Pages using Transformers.js
4. **MCP Server**: Provides an MCP-compatible interface for Claude Desktop/Cursor

## Architecture

```
[Local GPU ROCm] → Generate Embeddings → Push to GitHub
                                              ↓
[GitHub Pages] → Transformers.js API
                                              ↓
[Local MCP Server] → Returns to Claude
```

## Features

- **Semantic Search**: Natural language search using transformer-based embeddings
- **Persistent Cache**: Intelligent caching system for 90% faster subsequent searches
- **GPU Acceleration**: Fast embedding generation with ROCm (AMD) or CUDA (NVIDIA) support (CPU fallback available)
- **GitHub Pages API**: Free, unlimited hosting with Transformers.js
- **Rich Metadata**: Structured YAML frontmatter for advanced filtering
- **Category Support**: Search by product, category, version, and more

## Quick Start

### Local Installation

1. **Clone the repository**:
```bash
git clone https://github.com/njfsmallet-eng/twincat-knowledge-mcp-server.git
cd twincat-knowledge-mcp-server
```

2. **Install dependencies**:
```bash
npm install
```

3. **Add to your Claude Desktop `mcp.json`**:
```json
{
  "mcpServers": {
    "twincat-knowledge": {
      "command": "npx",
      "args": ["-y", "tsx", "C:\\path\\to\\twincat-knowledge-mcp-server\\src\\index.ts"],
      "env": {}
    }
  }
}
```

**Note**: Replace `C:\\path\\to\\twincat-knowledge-mcp-server` with your actual path to the cloned repository.

## Usage

### Generating Embeddings

1. **GPU recommended** (ROCm for AMD or CUDA for NVIDIA) for faster processing, but CPU works too

2. Generate embeddings:
```bash
cd scripts
python generate_embeddings.py
```

3. Push to GitHub:
```bash
git add embeddings/
git commit -m "Update embeddings"
git push
```

GitHub Actions will automatically deploy to GitHub Pages.

### Using the MCP Server

Once configured in Claude Desktop, use the `search_knowledge` tool:

```
"Search for information about OPC UA configuration"
```

**Available filters:**
- `category`: Communication, PLC, Motion_Control, etc.
- `product`: TF6100, TC3, TE1000, etc.
- `top_k`: Number of results (default: 5)

### Cache System

The MCP server includes an intelligent caching system that dramatically improves performance:

- **First call**: Downloads and caches all data (~16 seconds)
- **Subsequent calls**: Loads from cache (~1.6 seconds)
- **Performance improvement**: 90% faster after initial cache population
- **Cache location**: `.cache/` directory in project root
- **Persistent**: Cache survives between MCP server sessions
- **Automatic**: No manual configuration required

**Cache contents:**
- Xenova embedding model (~50 MB)
- Documentation chunks (42,314 chunks)
- Pre-computed embeddings (~57 MB compressed)

### Testing the Search API

You can test the search functionality directly in your browser at:
**https://njfsmallet-eng.github.io/twincat-knowledge-mcp-server/**

This web interface allows you to:
- Test semantic search queries
- See real-time results from the TwinCAT documentation
- Verify that the API is working correctly before configuring Claude Desktop

## File Structure

```
twincat-knowledge-mcp-server/
├── src/                         # TypeScript source
│   ├── index.ts                # MCP server
│   ├── types.ts                # Type definitions
│   ├── github-pages-client.ts  # API client
│   └── cache-manager.ts        # Cache management
├── scripts/                     # Python scripts
│   ├── chunking.py             # Text chunking
│   ├── generate_embeddings.py  # Embedding generation
│   └── README.md               # Scripts documentation
├── gh-pages/                    # GitHub Pages files
│   ├── index.html              # API interface
│   └── search.js               # Transformers.js search
├── embeddings/                  # Generated embeddings
│   ├── chunks.json             # Chunks with metadata
│   ├── embeddings.npy.gz       # Compressed vectors
│   └── metadata.json           # Generation stats
├── docs/                        # Converted markdown docs
├── .cache/                      # Persistent cache (auto-created)
│   ├── chunks.json             # Cached documentation chunks
│   ├── embeddings.npy.gz       # Cached embeddings
│   └── model/                  # Xenova model cache
│       └── Xenova/
│           └── all-MiniLM-L6-v2/
├── .github/workflows/           # CI/CD
│   └── deploy-pages.yml        # GitHub Pages deployment
├── package.json                 # Node.js config
├── tsconfig.json               # TypeScript config
└── requirements.txt            # Python dependencies
```

## Dependencies

**Python:**
- `sentence-transformers` - Transformer models for embeddings
- `torch` - PyTorch with ROCm support
- `numpy` - Numerical operations
- `pyyaml` - YAML parsing
- `tqdm` - Progress bars

**Node.js:**
- `@modelcontextprotocol/sdk` - MCP protocol
- `typescript` - TypeScript compiler

## Architecture Details

### Embedding Generation
- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **GPU**: ROCm (AMD) or CUDA (NVIDIA) - CPU fallback available
- **Format**: Float32 NumPy arrays compressed with gzip
- **Size**: ~57 MB compressed for all documents

### Search API
- **Frontend**: Transformers.js in browser
- **Model**: `Xenova/all-MiniLM-L6-v2` ONNX (quantized)
- **Latency**: ~500ms-1s per query
- **Cache**: IndexedDB for model caching

### MCP Server
- **Transport**: stdio
- **Compatibility**: Claude Desktop
- **Local Installation**: Clone and configure directly
- **Cache System**: Persistent disk-based caching for optimal performance
- **Performance**: 90% faster after initial cache population

## Local Usage

### Requirements
- **Node.js**: >=18.0.0
- **Dependencies**: Only MCP SDK and Transformers.js required
- **Size**: ~160 MB (includes embeddings and documentation)
- **Cache**: Additional ~110 MB for persistent cache (auto-created)
- **Files**: 338 files total

## License

MIT License
