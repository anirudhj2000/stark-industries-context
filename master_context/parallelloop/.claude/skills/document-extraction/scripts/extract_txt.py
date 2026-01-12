#!/usr/bin/env python3
"""
TXT/Plain Text Extraction Helper Script

Extracts text content from plain text files with basic structure detection.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import re


def detect_headings(lines: List[str]) -> List[Dict[str, Any]]:
    """Detect potential headings in plain text"""
    headings = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Detect patterns that suggest headings:
        # 1. All caps lines (e.g., "INTRODUCTION")
        # 2. Lines ending with colon (e.g., "Overview:")
        # 3. Lines with numeric prefixes (e.g., "1. Introduction")
        # 4. Lines that are underlined (next line is all =, -, or *)

        is_heading = False
        heading_type = None

        # Check if all caps
        if stripped.isupper() and len(stripped.split()) <= 10:
            is_heading = True
            heading_type = "all_caps"

        # Check if ends with colon
        elif stripped.endswith(':') and len(stripped.split()) <= 10:
            is_heading = True
            heading_type = "colon"

        # Check if starts with number
        elif re.match(r'^\d+[\.\)]\s+', stripped):
            is_heading = True
            heading_type = "numbered"

        # Check if underlined
        elif i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and all(c in '=-*_' for c in next_line) and len(next_line) >= len(stripped) * 0.5:
                is_heading = True
                heading_type = "underlined"

        if is_heading:
            headings.append({
                "line_number": i + 1,
                "text": stripped,
                "type": heading_type
            })

    return headings


def extract_txt(file_path: Path, encoding: str = 'utf-8') -> Dict[str, Any]:
    """Extract content from plain text file with basic structure analysis"""
    try:
        # Try to read with specified encoding
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            # Fallback to latin-1 if utf-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            encoding = 'latin-1'

        lines = content.split('\n')
        line_count = len(lines)

        # Count words
        total_words = len(content.split())

        # Count characters
        char_count = len(content)
        char_count_no_spaces = len(content.replace(' ', '').replace('\n', '').replace('\t', ''))

        # Detect headings
        headings = detect_headings(lines)

        # Detect paragraphs (consecutive non-empty lines)
        paragraphs = []
        current_paragraph = []

        for line in lines:
            stripped = line.strip()
            if stripped:
                current_paragraph.append(line)
            elif current_paragraph:
                # Empty line marks end of paragraph
                para_text = '\n'.join(current_paragraph)
                paragraphs.append({
                    "text": para_text,
                    "word_count": len(para_text.split())
                })
                current_paragraph = []

        # Don't forget last paragraph
        if current_paragraph:
            para_text = '\n'.join(current_paragraph)
            paragraphs.append({
                "text": para_text,
                "word_count": len(para_text.split())
            })

        result = {
            "file_name": file_path.name,
            "file_size_bytes": file_path.stat().st_size,
            "format": "TXT",
            "content": content,
            "line_count": line_count,
            "paragraph_count": len(paragraphs),
            "paragraphs": paragraphs,
            "heading_count": len(headings),
            "headings": headings,
            "total_words": total_words,
            "char_count": char_count,
            "char_count_no_spaces": char_count_no_spaces,
            "metadata": {
                "engine": "plain_text_parser",
                "encoding": encoding,
                "detected_structure": {
                    "has_headings": len(headings) > 0,
                    "has_paragraphs": len(paragraphs) > 1,
                    "avg_paragraph_length": total_words / len(paragraphs) if paragraphs else 0
                }
            }
        }

        return result

    except Exception as e:
        raise Exception(f"Failed to extract TXT file: {e}")


def main():
    parser = argparse.ArgumentParser(description='Extract content from plain text files')
    parser.add_argument('--input', required=True, help='Path to TXT file')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--encoding', default='utf-8', help='Text encoding (default: utf-8)')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: TXT file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        result = extract_txt(input_path, encoding=args.encoding)

        # Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"SUCCESS: Extracted {result['line_count']} lines from {input_path.name}")
        print(f"Total words: {result['total_words']}, Paragraphs: {result['paragraph_count']}")
        print(f"Detected headings: {result['heading_count']}")

    except Exception as e:
        print(f"ERROR: Extraction failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
