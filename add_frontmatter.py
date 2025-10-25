#!/usr/bin/env python3
"""
Add Structured YAML Frontmatter to TwinCAT Documentation

This script adds enriched YAML frontmatter to all markdown files in docs/ directory
to improve vector search, filtering, and retrieval capabilities.
"""

import os
import re
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('frontmatter_additions.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Category mapping based on filename prefixes
CATEGORY_MAP = {
    # Communication
    'TF6100': 'Communication',
    'TF6000': 'Communication',
    'TF6010': 'Communication',
    'TF6020': 'Communication',
    'TF6250': 'Communication',
    'TF6255': 'Communication',
    'TF6270': 'Communication',
    'TF6271': 'Communication',
    'TF6280': 'Communication',
    'TF6281': 'Communication',
    'TF6300': 'Communication',
    'TF6310': 'Communication',
    'TF6311': 'Communication',
    'TF6340': 'Communication',
    'TF6350': 'Communication',
    'TF6360': 'Communication',
    'TF6420': 'Communication',
    'TF6421': 'Communication',
    'TF6500': 'Communication',
    'TF6510': 'Communication',
    'TF6600': 'Communication',
    'TF6610': 'Communication',
    'TF6620': 'Communication',
    'TF6650': 'Communication',
    'TF6701': 'Communication',
    'TF6710': 'IoT',
    'TF6720': 'IoT',
    'TF6730': 'IoT',
    'TF6760': 'IoT',
    'TF6770': 'IoT',
    'TF6771': 'IoT',
    'TE1000': 'Communication',
    'TwinCAT_3_ADS': 'Communication',
    'ADS-over-MQTT': 'IoT',
    'AmsNAT': 'Communication',
    'Secure_ADS': 'Communication',
    
    # Motion Control / NC
    'TF5': 'Motion_Control',
    'TF5200': 'Motion_Control',
    'TF5225': 'Motion_Control',
    'TF5240': 'Motion_Control',
    'TF5245': 'Motion_Control',
    'TF5261': 'Motion_Control',
    'TF5264': 'Motion_Control',
    'TF527x': 'Motion_Control',
    'TF5280': 'Motion_Control',
    'TF5290': 'Motion_Control',
    'TF5291': 'Motion_Control',
    'TF5292': 'Motion_Control',
    'TF5293': 'Motion_Control',
    'TF52xx': 'Motion_Control',
    'TF5400': 'Motion_Control',
    'TF5410': 'Motion_Control',
    'tf5420': 'Motion_Control',
    'tf5430': 'Motion_Control',
    'TF58': 'Motion_Control',
    'TF5810': 'Motion_Control',
    
    # PLC
    'TwinCAT_3_PLC': 'PLC',
    'TC3_PLC': 'PLC',
    'TE1000': 'PLC',
    'PLC_Lib': 'PLC',
    
    # HMI
    'TE2000': 'HMI',
    'TF1200': 'HMI',
    'TF1800': 'HMI',
    'TF1810': 'HMI',
    'TF2000': 'HMI',
    
    # Engineering Tools
    'TE13': 'Engineering_Tools',
    'TE1000': 'Engineering_Tools',
    'TE1010': 'Engineering_Tools',
    'TE1030': 'Engineering_Tools',
    'TE1111': 'Engineering_Tools',
    'TE1120': 'Engineering_Tools',
    'TE1130': 'Engineering_Tools',
    'TE1200': 'Engineering_Tools',
    'TE1210': 'Engineering_Tools',
    'TE131x': 'Engineering_Tools',
    'TE132x': 'Engineering_Tools',
    'TE13xx': 'Engineering_Tools',
    'TE1400': 'Engineering_Tools',
    'TE1401': 'Engineering_Tools',
    'TE1402': 'Engineering_Tools',
    'TE1410': 'Engineering_Tools',
    'TE1420': 'Engineering_Tools',
    'TE1421': 'Engineering_Tools',
    'TE1500': 'Engineering_Tools',
    'TE1510': 'Engineering_Tools',
    'TE1610': 'Engineering_Tools',
    'TE3500': 'Engineering_Tools',
    'TE3520': 'Engineering_Tools',
    'TC3_Project_Compare': 'Engineering_Tools',
    'TC3_SourceControl': 'Engineering_Tools',
    
    # Vision
    'TF7000': 'Vision',
    'TF7800': 'Vision',
    'TF7810': 'Vision',
    
    # Analytics
    'TF3500': 'Analytics',
    'TF3510': 'Analytics',
    'TF3520': 'Analytics',
    'TF3550': 'Analytics',
    'TF3600': 'Analytics',
    'TF3650': 'Analytics',
    'TF3680': 'Analytics',
    'TF3685': 'Analytics',
    
    # Machine Learning
    'tf3710': 'Analytics',
    'tf3820': 'Machine_Learning',
    'tf3830': 'Machine_Learning',
    'TF38x0': 'Machine_Learning',
    
    # Building Automation
    'TF8000': 'Building_Automation',
    'TF8010': 'Building_Automation',
    'TF8020': 'Building_Automation',
    'TF8040': 'Building_Automation',
    'TF8050': 'Building_Automation',
    'TF8310': 'Building_Automation',
    'TF8330': 'Building_Automation',
    'TF8360': 'Building_Automation',
    
    # Process Engineering
    'TF8400': 'Process_Engineering',
    'TF8540': 'Process_Engineering',
    'TF8550': 'Process_Engineering',
    'TF8560': 'Process_Engineering',
    'TF85xx': 'Process_Engineering',
    
    # Miscellaneous
    'TF8810': 'Communication',
    'TF3900': 'Utilities',
    'TF4100': 'Motion_Control',
    'TF4110': 'Motion_Control',
    'TF4500': 'Utilities',
    'TF5050': 'Motion_Control',
    'TF5055': 'Motion_Control',
    'TF5060': 'Motion_Control',
    'TF5065': 'Motion_Control',
    'TF50x0': 'Motion_Control',
    'TF5100': 'Motion_Control',
    'TF5110': 'Motion_Control',
    'TF5130': 'Motion_Control',
    
    # Fundamentals
    'TC3_Installation': 'Fundamentals',
    'TC3_Multiuser': 'Fundamentals',
    'TC3_Remote_Manager': 'Fundamentals',
    'TC3_User_Interface': 'Fundamentals',
    'TC170x': 'Fundamentals',
    'TwinCAT_3_': 'Fundamentals',
    'Product_overview': 'Fundamentals',
    'Licensing': 'Fundamentals',
    'Corrected_timestamps': 'Fundamentals',
    'EAP': 'Fundamentals',
    'Folder_and_file_types': 'Fundamentals',
    'Machine_update_at_file_level': 'Fundamentals',
    'MATLAB_Simulink': 'Engineering_Tools',
    'Autotuning': 'Motion_Control',
    'QRC': 'Fundamentals',
    'Riedel_Communications': 'Communication',
    'Software_Protection': 'Fundamentals',
}


# Content keywords for category detection
CONTENT_KEYWORDS = {
    'Communication': ['ads', 'mqtt', 'opc', 'ethercat', 'protocol', 'communication', 'network', 'tcp', 'udp', 'modbus', 'profinet'],
    'PLC': ['structured text', 'function block', 'plc programming', 'iec61131', 'plc', 'pou'],
    'Motion_Control': ['nc', 'cnc', 'axis', 'motion', 'camming', 'kinematic', 'servo', 'drive'],
    'HMI': ['hmi', 'visualization', 'web server', 'interface', 'client', 'server'],
    'Engineering_Tools': ['matlab', 'simulink', 'scope', 'profiler', 'simulation', 'analysis'],
    'Vision': ['vision', 'camera', 'image processing', 'vision', 'inspection'],
    'Fundamentals': ['installation', 'setup', 'configuration', 'basic', 'fundamental'],
    'IoT': ['iot', 'mqtt', 'cloud', 'https', 'rest', 'websocket'],
    'Building_Automation': ['bacnet', 'building', 'hvac', 'lighting'],
    'Safety': ['safe', 'safety', 'iec61508', 'twin safe'],
}


def detect_category(filename: str, content: str) -> str:
    """Detect category using hybrid approach (prefix + content analysis)."""
    # Try prefix-based mapping first
    for prefix, category in CATEGORY_MAP.items():
        if filename.startswith(prefix) or prefix in filename:
            logger.debug(f"Matched prefix '{prefix}' -> {category} for {filename}")
            return category
    
    # Content-based fallback
    content_lower = content.lower()
    matches = {}
    for category, keywords in CONTENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in content_lower)
        if score > 0:
            matches[category] = score
    
    if matches:
        best_category = max(matches.items(), key=lambda x: x[1])[0]
        logger.debug(f"Content-based match: {best_category} for {filename}")
        return best_category
    
    # Default fallback
    logger.warning(f"No category match for {filename}, defaulting to 'Fundamentals'")
    return 'Fundamentals'


def extract_product_code(filename: str) -> str:
    """Extract product code from filename."""
    # Common patterns: TE1000, TF6100, TC3_PLC, etc.
    patterns = [
        r'(TE\d{4})',
        r'(TF\d{4,5})',
        r'(TC\d+)',
        r'(TC3_[A-Z_]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            return match.group(1)
    
    # Fallback: use filename without extension
    return Path(filename).stem.split('_')[0]


def extract_language(filename: str) -> str:
    """Extract language from filename."""
    lang_match = re.search(r'_([A-Z]{2})$', filename)
    if lang_match:
        return lang_match.group(1)
    return 'EN'  # Default


def extract_version(content: str) -> Optional[str]:
    """Extract version from content."""
    patterns = [
        r'Version:\s*([\d.]+)',
        r'v([\d.]+)',
        r'Build\s*([\d.]+)',
        r'TC3\s+([\d.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content[:1000])  # Search first 1000 chars
        if match:
            return match.group(1)
    return None


def extract_date(content: str) -> Optional[str]:
    """Extract release date from content."""
    patterns = [
        r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
        r'(\d{2}/\d{2}/\d{4})',  # MM/DD/YYYY
        r'(\d{1,2}/\d{1,2}/\d{4})',  # M/D/YYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content[:500])  # Search first 500 chars
        if match:
            date_str = match.group(1)
            # Normalize to YYYY-MM-DD
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    if len(parts[2]) == 4:  # YYYY
                        return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            else:
                return date_str
    return None


def extract_title(filename: str, content: str) -> str:
    """Extract title from filename or content."""
    # Try to extract from content first (more descriptive)
    title_patterns = [
        r'Manual \| [A-Z]{2} ([^|]+?) \|',
        r'#\s+(.+?)\n',
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, content[:200])
        if match:
            title = match.group(1).strip()
            return title
    
    # Fallback to filename
    name = Path(filename).stem
    # Replace underscores and cleanup
    title = name.replace('_', ' ').replace('EN', '').replace('DE', '').strip()
    return title


def extract_source_url(content: str) -> Optional[str]:
    """Extract source PDF URL from content."""
    pattern = r'\*Source:\s*(https://[^*]+)\*'
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    return None


def generate_tags(title: str, content: str, category: str) -> List[str]:
    """Generate relevant tags from title and content."""
    tags = set()
    
    # Add important keywords from title
    title_words = re.findall(r'[A-Z][a-z]+|[A-Z]{2,}', title)
    tags.update(w.upper() for w in title_words if len(w) > 2)
    
    # Add category-specific tags
    content_lower = content[:500].lower()
    
    # Common TwinCAT keywords
    keywords = {
        'ADS': ['ads'],
        'MQTT': ['mqtt'],
        'OPC_UA': ['opc ua', 'opc ua'],
        'OPC': ['opc'],
        'EtherCAT': ['ethercat', 'ether cat'],
        'PLC': ['plc', 'plc', 'structured text'],
        'HMI': ['hmi', 'visualization'],
        'NC': ['cnc', 'nc ', 'motion'],
        'MATLAB': ['matlab'],
        'Simulink': ['simulink'],
        'IoT': ['iot', 'cloud', 'mqtt'],
        'Safety': ['safe', 'safety', 'twin safe'],
    }
    
    for tag, patterns in keywords.items():
        if any(pattern in content_lower for pattern in patterns):
            tags.add(tag)
    
    # Limit to 8 tags max
    return sorted(list(tags))[:8]


def extract_document_type(content: str) -> str:
    """Infer document type from content."""
    content_lower = content[:500].lower()
    
    if 'library' in content_lower or 'lib' in content_lower:
        return 'Library'
    elif 'manual' in content_lower or 'handbook' in content_lower:
        return 'Manual'
    elif 'reference' in content_lower:
        return 'Reference'
    elif 'guide' in content_lower:
        return 'Guide'
    else:
        return 'Manual'


def extract_metadata(filepath: Path) -> Dict:
    """Extract metadata from file."""
    filename = filepath.name
    
    # Read file
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Extract all metadata
    title = extract_title(filename, content)
    product = extract_product_code(filename)
    category = detect_category(filename, content)
    language = extract_language(filename)
    version = extract_version(content)
    release_date = extract_date(content)
    source_pdf = extract_source_url(content)
    tags = generate_tags(title, content, category)
    document_type = extract_document_type(content)
    
    metadata = {
        'title': title,
        'product': product,
        'category': category,
        'tags': tags,
        'language': language,
        'document_type': document_type,
        'version': version,
        'source_pdf': source_pdf,
        'release_date': release_date,
    }
    
    return metadata


def format_yaml_frontmatter(metadata: Dict) -> str:
    """Format metadata as YAML frontmatter."""
    lines = ['---']
    
    # Mandatory fields
    lines.append(f"title: \"{metadata['title']}\"")
    lines.append(f"product: \"{metadata['product']}\"")
    lines.append(f"category: \"{metadata['category']}\"")
    lines.append(f"tags: {json.dumps(metadata['tags'])}")
    lines.append(f"language: \"{metadata['language']}\"")
    lines.append(f"document_type: \"{metadata['document_type']}\"")
    
    # Optional fields (only if present)
    if metadata['version']:
        lines.append(f"version: \"{metadata['version']}\"")
    
    if metadata['source_pdf']:
        lines.append(f"source_pdf: \"{metadata['source_pdf']}\"")
    
    if metadata['release_date']:
        lines.append(f"release_date: \"{metadata['release_date']}\"")
    
    lines.append('---')
    lines.append('')  # Empty line after frontmatter
    
    return '\n'.join(lines)


def add_frontmatter_to_file(filepath: Path) -> bool:
    """Add YAML frontmatter to a single file."""
    try:
        # Read existing file
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Generate metadata
        metadata = extract_metadata(filepath)
        frontmatter = format_yaml_frontmatter(metadata)
        
        # Find where to insert frontmatter (after existing title line if present)
        # Skip lines that look like the old header format
        content_start = 0
        for i, line in enumerate(lines):
            if line.strip() and not (line.strip().startswith('#') or line.strip().startswith('*Source:') or line.strip() == '---'):
                content_start = i
                break
        
        # Preserve original content
        original_content = ''.join(lines[content_start:])
        
        # Write new file with frontmatter + content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
            f.write(original_content)
        
        logger.info(f"OK Processed: {filepath.name}")
        return True
        
    except Exception as e:
        logger.error(f"ERROR processing {filepath.name}: {e}")
        return False


def main():
    """Main execution."""
    logger.info("Starting frontmatter addition process")
    
    # Find all markdown files in docs/
    docs_dir = Path('docs')
    if not docs_dir.exists():
        logger.error("docs/ directory not found!")
        return
    
    md_files = list(docs_dir.glob('*.md'))
    logger.info(f"Found {len(md_files)} markdown files")
    
    # Skip INDEX.md
    md_files = [f for f in md_files if f.name != 'INDEX.md']
    
    # Create backup
    backup_dir = Path('docs_backup')
    if not backup_dir.exists():
        logger.info("Creating backup of docs/ directory...")
        shutil.copytree(docs_dir, backup_dir)
        logger.info(f"Backup created in {backup_dir}/")
    
    # Process files
    success_count = 0
    for md_file in md_files:
        if add_frontmatter_to_file(md_file):
            success_count += 1
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing complete!")
    logger.info(f"Successfully processed: {success_count}/{len(md_files)} files")
    logger.info(f"{'='*60}")


if __name__ == '__main__':
    main()
