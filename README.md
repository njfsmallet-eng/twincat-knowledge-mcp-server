# TwinCAT Knowledge MCP Server

A Model Context Protocol (MCP) server providing semantic search access to TwinCAT 3 documentation. This project includes tools for converting PDFs to Markdown, generating embeddings with GPU acceleration, and hosting a searchable API on GitHub Pages.

## Overview

This project provides a complete semantic search solution for TwinCAT 3 documentation:

1. **PDF Conversion**: Converts 290 TwinCAT 3 documentation PDFs from Beckhoff to Markdown format
2. **Embedding Generation**: Generates semantic embeddings using GPU-accelerated models
3. **Search API**: Hosts a search API on GitHub Pages using Transformers.js
4. **MCP Server**: Provides an MCP-compatible interface for Claude Desktop
5. **GitHub Packages**: Published package for easy installation via `npx`

## Architecture

```
[Local GPU ROCm] → Generate Embeddings → Push to GitHub
                                              ↓
[GitHub Pages] → Transformers.js API
                                              ↓
[GitHub Packages] → MCP Server → Returns to Claude
```

## Features

- **Semantic Search**: Natural language search using transformer-based embeddings
- **GPU Acceleration**: Fast embedding generation with ROCm (AMD GPU) support
- **Zero-Config Clients**: Users only need `npx` to use the MCP server
- **GitHub Pages API**: Free, unlimited hosting with Transformers.js
- **GitHub Packages**: Easy distribution without npm account requirements
- **Rich Metadata**: Structured YAML frontmatter for advanced filtering
- **Category Support**: Search by product, category, version, and more

## Quick Start (For Users)

### Option 1: npm Registry (Recommended)

**No authentication required - package is public!**

1. **Add to your Claude Desktop `mcp.json`**:
```json
{
  "mcpServers": {
    "twincat-knowledge": {
      "command": "npx",
      "args": ["@njfsmallet-eng/twincat-knowledge-mcp"],
      "env": {}
    }
  }
}
```

### Option 2: Direct Git Installation

```json
{
  "mcpServers": {
    "twincat-knowledge": {
      "command": "npx",
      "args": ["https://github.com/njfsmallet-eng/twincat-knowledge-mcp-server.git"],
      "env": {}
    }
  }
}
```

That's it! No npm account or authentication required.

## Installation (For Developers)

### 1. Clone the repository:
```bash
git clone https://github.com/njfsmallet-eng/twincat-knowledge-mcp-server.git
cd twincat-knowledge-mcp-server
```

### 2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Install Node.js dependencies:
```bash
npm install
```

### 4. Build the project:
```bash
npm run build
```

## Usage

### Generating Embeddings (Local GPU Required)

1. Ensure you have a GPU with ROCm support

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

GitHub Actions will automatically deploy to GitHub Pages and publish to GitHub Packages.

### Publishing New Versions

#### Method 1: Automatic via Git Tags (Recommended)
```bash
# Update version in package.json if needed
npm version patch  # or minor, major

# Create and push tag
git tag v1.0.1
git push origin main
git push origin v1.0.1

# GitHub Actions will automatically publish to GitHub Packages
```

#### Method 2: Manual via GitHub Actions
1. Go to **Actions** → **Publish Package to GitHub Packages**
2. Click **Run workflow**
3. Enter version (e.g., `1.0.1`)
4. Click **Run workflow**

### Using the MCP Server

Once configured in Claude Desktop, use the `search_knowledge` tool:

```
"Search for information about OPC UA configuration"
```

**Available filters:**
- `category`: Communication, PLC, Motion_Control, etc.
- `product`: TF6100, TC3, TE1000, etc.
- `top_k`: Number of results (default: 5)

## File Structure

```
twincat-knowledge-mcp-server/
├── src/                         # TypeScript source
│   ├── index.ts                # MCP server
│   ├── types.ts                # Type definitions
│   └── github-pages-client.ts  # API client
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
├── .github/workflows/           # CI/CD
│   ├── deploy-pages.yml        # GitHub Pages deployment
│   └── publish-package.yml     # GitHub Packages publishing
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
- **Model**: `Alibaba-NLP/gte-small-en-v1.5` (384 dimensions)
- **GPU**: ROCm (AMD) or CUDA (NVIDIA)
- **Format**: Float32 NumPy arrays compressed with gzip
- **Size**: ~13 MB compressed for all documents

### Search API
- **Frontend**: Transformers.js in browser
- **Model**: Xenova/gte-small-en-v1.5 ONNX
- **Latency**: ~500ms-1s per query
- **Cache**: IndexedDB for model caching

### MCP Server
- **Transport**: stdio
- **Compatibility**: Claude Desktop
- **Zero Config**: Works with just `npx`

## Distribution

### npm Registry
- **Registry**: `https://registry.npmjs.org/`
- **Package**: `@njfsmallet-eng/twincat-knowledge-mcp`
- **Auto-publish**: On git tags via GitHub Actions
- **Public**: No authentication required
- **Free**: No npm account required

### Package Information
- **Size**: ~85 MB (includes embeddings)
- **Files**: 338 files
- **Dependencies**: Minimal (only MCP SDK)
- **Compatibility**: Node.js >=18.0.0

## Contributing

Contributions welcome! Areas for improvement:
- Support for additional TwinCAT products
- Multi-language support
- Improved chunking strategies
- Vector database integration
- Better embedding model integration

## License

MIT License
