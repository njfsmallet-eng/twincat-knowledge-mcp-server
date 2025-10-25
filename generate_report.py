#!/usr/bin/env python3
"""
Generate Frontmatter Addition Report

Analyzes processed markdown files and generates statistics and validation report.
"""

import re
import yaml
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List


def analyze_frontmatter(filepath: Path) -> Dict:
    """Analyze frontmatter in a markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has frontmatter
        if not content.startswith('---'):
            return {'has_frontmatter': False, 'filename': filepath.name}
        
        # Extract YAML frontmatter
        match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {'has_frontmatter': False, 'filename': filepath.name}
        
        yaml_content = match.group(1)
        try:
            metadata = yaml.safe_load(yaml_content)
            
            return {
                'has_frontmatter': True,
                'filename': filepath.name,
                'metadata': metadata,
                'valid': True
            }
        except yaml.YAMLError as e:
            return {
                'has_frontmatter': True,
                'filename': filepath.name,
                'valid': False,
                'error': str(e)
            }
    except Exception as e:
        return {'has_frontmatter': False, 'filename': filepath.name, 'error': str(e)}


def generate_report():
    """Generate analysis report."""
    docs_dir = Path('docs')
    md_files = list(docs_dir.glob('*.md'))
    md_files = [f for f in md_files if f.name != 'INDEX.md']
    
    results = []
    categories = Counter()
    products = Counter()
    tags_all = Counter()
    languages = Counter()
    doc_types = Counter()
    versions = Counter()
    
    files_with_frontmatter = 0
    files_valid = 0
    files_with_version = 0
    files_with_date = 0
    
    for md_file in md_files:
        result = analyze_frontmatter(md_file)
        results.append(result)
        
        if result.get('has_frontmatter'):
            files_with_frontmatter += 1
            
        if result.get('valid'):
            files_valid += 1
            
            metadata = result.get('metadata', {})
            
            # Count categories
            if 'category' in metadata:
                categories[metadata['category']] += 1
            
            # Count products
            if 'product' in metadata:
                products[metadata['product']] += 1
            
            # Count languages
            if 'language' in metadata:
                languages[metadata['language']] += 1
            
            # Count document types
            if 'document_type' in metadata:
                doc_types[metadata['document_type']] += 1
            
            # Count versions
            if 'version' in metadata and metadata['version']:
                files_with_version += 1
                versions[metadata['version']] += 1
            
            # Count dates
            if 'release_date' in metadata and metadata['release_date']:
                files_with_date += 1
            
            # Count tags
            if 'tags' in metadata and isinstance(metadata['tags'], list):
                for tag in metadata['tags']:
                    tags_all[tag] += 1
    
    # Generate report
    report = []
    report.append("# Frontmatter Addition Report\n")
    report.append(f"*Generated on {Path('frontmatter_additions.log').stat().st_mtime if Path('frontmatter_additions.log').exists() else 'N/A'}*\n")
    report.append("\n")
    
    # Summary
    report.append("## Summary\n\n")
    report.append(f"- **Total files processed**: {len(md_files)}\n")
    report.append(f"- **Files with frontmatter**: {files_with_frontmatter}\n")
    report.append(f"- **Files with valid YAML**: {files_valid}\n")
    report.append(f"- **Files with version**: {files_with_version}\n")
    report.append(f"- **Files with release date**: {files_with_date}\n")
    report.append("\n")
    
    # Categories distribution
    report.append("## Category Distribution\n\n")
    for category, count in categories.most_common():
        report.append(f"- **{category}**: {count} files\n")
    report.append("\n")
    
    # Top products
    report.append("## Top 20 Products\n\n")
    for product, count in products.most_common(20):
        report.append(f"- **{product}**: {count} files\n")
    report.append("\n")
    
    # Languages
    report.append("## Language Distribution\n\n")
    for lang, count in languages.most_common():
        report.append(f"- **{lang}**: {count} files\n")
    report.append("\n")
    
    # Document types
    report.append("## Document Type Distribution\n\n")
    for doc_type, count in doc_types.most_common():
        report.append(f"- **{doc_type}**: {count} files\n")
    report.append("\n")
    
    # Top tags
    report.append("## Top 30 Tags\n\n")
    for tag, count in tags_all.most_common(30):
        report.append(f"- **{tag}**: {count} occurrences\n")
    report.append("\n")
    
    # Validation issues
    invalid_files = [r for r in results if r.get('has_frontmatter') and not r.get('valid')]
    if invalid_files:
        report.append("## Validation Issues\n\n")
        for issue in invalid_files:
            report.append(f"- **{issue['filename']}**: {issue.get('error', 'Unknown error')}\n")
        report.append("\n")
    
    # Missing frontmatter
    missing_files = [r for r in results if not r.get('has_frontmatter')]
    if missing_files:
        report.append("## Files Missing Frontmatter\n\n")
        for file_info in missing_files[:20]:  # Show first 20
            report.append(f"- {file_info['filename']}\n")
        if len(missing_files) > 20:
            report.append(f"\n*... and {len(missing_files) - 20} more files*\n")
        report.append("\n")
    
    # Save report
    with open('frontmatter_report.md', 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    print("Report generated: frontmatter_report.md")
    print(f"\nSummary:")
    print(f"  Files processed: {len(md_files)}")
    print(f"  Files with frontmatter: {files_with_frontmatter}")
    print(f"  Files with valid YAML: {files_valid}")
    print(f"  Files with version: {files_with_version}")
    print(f"  Files with release date: {files_with_date}")


if __name__ == '__main__':
    # Note: pyyaml might not be in requirements, but we'll try
    generate_report()
