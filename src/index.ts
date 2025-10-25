import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { GitHubPagesClient } from './github-pages-client.js';
import { promises as fs } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const GITHUB_USER = 'njfsmallet-eng';
const REPO_NAME = 'twincat-knowledge-mcp-server';

// Get the project root directory (where package.json is located)
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PROJECT_ROOT = dirname(__dirname);
const CACHE_DIR = join(PROJECT_ROOT, '.cache');

// Set up Xenova cache directory
process.env.TRANSFORMERS_CACHE = join(CACHE_DIR, 'model');

// Ensure cache directory exists
async function ensureCacheDirectory() {
  try {
    await fs.access(CACHE_DIR);
  } catch {
    await fs.mkdir(CACHE_DIR, { recursive: true });
    console.error(`[MCP] Created cache directory: ${CACHE_DIR}`);
  }
}

const searchClient = new GitHubPagesClient(GITHUB_USER, REPO_NAME, CACHE_DIR);

const server = new Server(
  {
    name: 'twincat-knowledge-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'search_knowledge',
      description: 'Search TwinCAT documentation using semantic search. Returns relevant documentation chunks with metadata.',
      inputSchema: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Search query (e.g., "How to configure OPC UA server?")'
          },
          category: {
            type: 'string',
            description: 'Filter by category (Communication, PLC, Motion_Control, etc.)',
            enum: ['Communication', 'PLC', 'Motion_Control', 'HMI', 'IoT', 'Engineering_Tools', 'Vision', 'Analytics', 'Building_Automation', 'Fundamentals']
          },
          product: {
            type: 'string',
            description: 'Filter by product code (e.g., TF6100, TC3, TE1000)'
          },
          top_k: {
            type: 'number',
            description: 'Number of results to return (default: 5)',
            default: 5
          }
        },
        required: ['query']
      }
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'search_knowledge') {
    const { query, category, product, top_k = 5 } = request.params.arguments as any;
    
    try {
      const results = await searchClient.search(query, {
        category,
        product,
        top_k
      });
      
      // Formater pour Claude
      const formattedResults = results.map((result, idx) => ({
        rank: idx + 1,
        title: result.metadata.title,
        product: result.metadata.product,
        category: result.metadata.category,
        version: result.metadata.version,
        relevance_score: result.score.toFixed(3),
        content: result.text,
        source: result.metadata.source_pdf
      }));
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(formattedResults, null, 2)
          }
        ]
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: `Error searching knowledge base: ${error.message}`
          }
        ],
        isError: true
      };
    }
  }
  
  throw new Error('Unknown tool');
});

async function main() {
  // Ensure cache directory exists before starting
  await ensureCacheDirectory();
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('TwinCAT Knowledge MCP Server running on stdio');
}

main();
