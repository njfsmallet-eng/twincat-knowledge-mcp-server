#!/bin/bash

# PDF to Markdown Converter Setup and Execution Script

echo "Setting up PDF to Markdown converter..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Install dependencies
echo "Installing required Python packages..."
pip3 install -r requirements.txt

# Make the converter script executable
chmod +x convert_pdfs.py

echo "Setup complete!"
echo ""
echo "To run the converter:"
echo "  python3 convert_pdfs.py"
echo ""
echo "The script will:"
echo "  - Read URLs from index.txt"
echo "  - Download and convert 290 PDFs to Markdown"
echo "  - Save files to docs/ directory"
echo "  - Use 4 worker threads for parallel processing"
echo "  - Show progress bar and logging"
echo "  - Create docs/INDEX.md with links to all converted files"
echo ""
echo "Logs will be saved to conversion.log"
