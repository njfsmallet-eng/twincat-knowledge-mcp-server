#!/usr/bin/env python3
"""
PDF to Markdown Batch Converter for TwinCAT Documentation

This script downloads PDFs from URLs in index.txt and converts them to Markdown format.
Uses multithreading (1 worker by default) for efficient processing with progress tracking.
"""

import os
import re
import sys
import time
import logging
import tempfile
import argparse
from pathlib import Path
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional

import requests
import pdfplumber
from tqdm import tqdm


class PDFToMarkdownConverter:
    def __init__(self, index_file: str = "index.txt", output_dir: str = "docs", max_workers: int = 1, force_reconvert: bool = False):
        self.index_file = index_file
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.force_reconvert = force_reconvert
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('conversion.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Statistics
        self.successful_conversions = []
        self.failed_conversions = []

    def read_urls(self) -> List[str]:
        """Read URLs from index.txt file."""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            self.logger.info(f"Loaded {len(urls)} URLs from {self.index_file}")
            return urls
        except FileNotFoundError:
            self.logger.error(f"Index file {self.index_file} not found")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Error reading index file: {e}")
            sys.exit(1)

    def extract_filename_from_url(self, url: str) -> str:
        """Extract filename from URL and convert to .md extension."""
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if filename.endswith('.pdf'):
            return filename.replace('.pdf', '.md')
        else:
            # Fallback: use URL path or generate name
            return f"document_{hash(url) % 10000}.md"

    def download_pdf(self, url: str, timeout: int = 30) -> Optional[bytes]:
        """Download PDF from URL."""
        try:
            response = self.session.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Check if it's actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                self.logger.warning(f"URL {url} may not be a PDF (content-type: {content_type})")
            
            return response.content
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return None

    def pdf_to_markdown_streaming(self, pdf_content: bytes, output_file) -> bool:
        """Convert PDF content to Markdown format and write directly to file."""
        temp_file_path = None
        pdf = None
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_content)
                temp_file.flush()
                temp_file_path = temp_file.name
                
                pdf = pdfplumber.open(temp_file_path)
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text from page
                    text = page.extract_text()
                    if text:
                        # Clean up the text
                        text = self.clean_text(text)
                        if text.strip():
                            # Write directly to file instead of accumulating in memory
                            output_file.write(f"## Page {page_num}\n\n{text}\n")
                    # Explicitly delete page object to free memory
                    del page
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error processing PDF: {e}")
            output_file.write(f"# Error\n\nFailed to process PDF: {e}")
            return False
        finally:
            # Explicitly close PDF object to free memory
            if pdf:
                try:
                    pdf.close()
                except Exception as e:
                    self.logger.warning(f"Error closing PDF: {e}")
            
            # Clean up temp file after pdfplumber has released all handles
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except OSError as e:
                    self.logger.warning(f"Could not delete temporary file {temp_file_path}: {e}")
            
            # Explicitly delete PDF content to free memory
            del pdf_content

    def clean_text(self, text: str) -> str:
        """Clean and format extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common PDF extraction issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)  # Add space after sentence endings
        
        # Remove page numbers and headers/footers (basic heuristics)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip likely page numbers
            if re.match(r'^\d+$', line) and len(line) <= 3:
                continue
                
            # Skip likely headers/footers (very short lines)
            if len(line) < 3:
                continue
                
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def process_single_pdf(self, url: str) -> Tuple[str, bool, str]:
        """Process a single PDF URL. Returns (filename, success, error_message)."""
        filename = self.extract_filename_from_url(url)
        output_path = self.output_dir / filename
        
        # Skip if file already exists (resume functionality)
        if output_path.exists() and not self.force_reconvert:
            self.logger.info(f"[SKIP] Already exists: {filename}")
            return filename, True, "Already converted"
        
        try:
            # Download PDF
            pdf_content = self.download_pdf(url)
            if pdf_content is None:
                return filename, False, "Failed to download PDF"
            
            # Convert to Markdown using streaming approach
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {filename.replace('.md', '')}\n\n")
                f.write(f"*Source: {url}*\n\n")
                f.write("---\n\n")
                
                # Use streaming conversion to avoid memory accumulation
                success = self.pdf_to_markdown_streaming(pdf_content, f)
                
                if not success:
                    return filename, False, "Failed to convert PDF content"
            
            return filename, True, ""
            
        except Exception as e:
            error_msg = f"Error processing {url}: {e}"
            self.logger.error(error_msg)
            return filename, False, error_msg

    def create_index(self):
        """Create an index file listing all converted documents."""
        index_path = self.output_dir / "INDEX.md"
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# TwinCAT Documentation Index\n\n")
            f.write(f"*Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write(f"Total documents processed: {len(self.successful_conversions)}\n")
            f.write(f"Failed conversions: {len(self.failed_conversions)}\n\n")
            
            if self.successful_conversions:
                f.write("## Successfully Converted Documents\n\n")
                for filename in sorted(self.successful_conversions):
                    f.write(f"- [{filename.replace('.md', '')}]({filename})\n")
                f.write("\n")
            
            if self.failed_conversions:
                f.write("## Failed Conversions\n\n")
                for filename, error in self.failed_conversions:
                    f.write(f"- {filename}: {error}\n")

    def run(self):
        """Main execution method."""
        self.logger.info("Starting PDF to Markdown conversion process")
        
        # Read URLs
        urls = self.read_urls()
        if not urls:
            self.logger.error("No URLs found to process")
            return
        
        # Process URLs with multithreading
        self.logger.info(f"Processing {len(urls)} URLs with {self.max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.process_single_pdf, url): url 
                for url in urls
            }
            
            # Process completed tasks with progress bar
            with tqdm(total=len(urls), desc="Converting PDFs", unit="file") as pbar:
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    filename, success, error = future.result()
                    
                    if success:
                        self.successful_conversions.append(filename)
                        self.logger.info(f"[OK] Converted: {filename}")
                    else:
                        self.failed_conversions.append((filename, error))
                        self.logger.warning(f"[FAIL] Failed: {filename} - {error}")
                    
                    pbar.update(1)
                    pbar.set_postfix({
                        'Success': len(self.successful_conversions),
                        'Failed': len(self.failed_conversions)
                    })
        
        # Create index file
        self.create_index()
        
        # Final summary
        self.logger.info(f"\nConversion completed!")
        self.logger.info(f"Successfully converted: {len(self.successful_conversions)} files")
        self.logger.info(f"Failed conversions: {len(self.failed_conversions)} files")
        self.logger.info(f"Output directory: {self.output_dir.absolute()}")
        self.logger.info(f"Index file: {self.output_dir / 'INDEX.md'}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Convert TwinCAT PDFs to Markdown format')
    parser.add_argument('--workers', '-w', type=int, default=1, 
                       help='Number of worker threads for parallel processing (default: 1)')
    parser.add_argument('--index', '-i', type=str, default='index.txt',
                       help='Path to index file containing PDF URLs (default: index.txt)')
    parser.add_argument('--output', '-o', type=str, default='docs',
                       help='Output directory for converted Markdown files (default: docs)')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Force reconversion of existing files (default: skip existing files)')
    
    args = parser.parse_args()
    
    converter = PDFToMarkdownConverter(
        index_file=args.index,
        output_dir=args.output,
        max_workers=args.workers,
        force_reconvert=args.force
    )
    converter.run()


if __name__ == "__main__":
    main()
