#!/usr/bin/env python3
"""
PDF Extraction Helper Script

Extracts text, tables, images, and metadata from PDF files using PyMuPDF.
For image-based PDFs (scanned documents), uses OCR via pytesseract.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import io

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF", file=sys.stderr)
    sys.exit(1)

# OCR support (optional)
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


def ocr_page(page, doc) -> str:
    """Extract text from page using OCR (for image-based PDFs)"""
    if not OCR_AVAILABLE:
        return ""

    try:
        # Render page to image at 300 DPI for better OCR accuracy
        mat = fitz.Matrix(300/72, 300/72)  # 300 DPI
        pix = page.get_pixmap(matrix=mat)

        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))

        # Run OCR
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"WARNING: OCR failed for page: {e}", file=sys.stderr)
        return ""


def extract_pdf(file_path: Path, include_images: bool = True, include_tables: bool = True, use_ocr: bool = True) -> Dict[str, Any]:
    """Extract content from PDF file including text, tables, images, and metadata.

    For image-based PDFs (scanned documents), automatically uses OCR if available.
    """
    try:
        doc = fitz.open(file_path)

        pages = []
        total_words = 0
        total_tables = 0
        total_images = 0
        ocr_used = False

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Extract text
            text = page.get_text()
            words = text.split()
            word_count = len(words)

            # If no text found and OCR is enabled, try OCR
            if word_count == 0 and use_ocr and OCR_AVAILABLE:
                text = ocr_page(page, doc)
                words = text.split()
                word_count = len(words)
                if word_count > 0:
                    ocr_used = True

            total_words += word_count

            # Extract images if requested
            images = []
            if include_images:
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    try:
                        base_image = doc.extract_image(xref)
                        images.append({
                            "index": img_index,
                            "xref": xref,
                            "format": base_image["ext"],
                            "width": base_image["width"],
                            "height": base_image["height"],
                            "size_bytes": len(base_image["image"])
                        })
                        total_images += 1
                    except:
                        # Some images may not be extractable
                        pass

            # Extract tables if requested (basic table detection via text blocks)
            tables = []
            if include_tables:
                blocks = page.get_text("dict")["blocks"]
                # Look for grid-like text patterns
                table_candidates = []
                for block in blocks:
                    if "lines" in block:
                        lines = block["lines"]
                        if len(lines) > 2:  # Potential table row
                            table_candidates.append({
                                "bbox": block["bbox"],
                                "line_count": len(lines)
                            })

                if table_candidates:
                    tables.append({
                        "candidates": len(table_candidates),
                        "note": "Table detection is approximate - may need manual review"
                    })
                    total_tables += len(table_candidates)

            page_info = {
                "page_number": page_num + 1,
                "width": page.rect.width,
                "height": page.rect.height,
                "rotation": page.rotation,
                "text": text,
                "word_count": word_count,
                "images": images,
                "tables": tables
            }

            pages.append(page_info)

        # Extract document metadata
        metadata = doc.metadata

        result = {
            "file_name": file_path.name,
            "file_size_bytes": file_path.stat().st_size,
            "format": "PDF",
            "page_count": len(doc),
            "pages": pages,
            "total_words": total_words,
            "total_images": total_images,
            "total_tables": total_tables,
            "ocr_used": ocr_used,
            "ocr_available": OCR_AVAILABLE,
            "metadata": {
                "engine": "PyMuPDF" + (" + pytesseract OCR" if ocr_used else ""),
                "pdf_version": doc.metadata.get("format", "PDF"),
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", "")
            }
        }

        doc.close()
        return result

    except Exception as e:
        raise Exception(f"Failed to extract PDF file: {e}")


def main():
    parser = argparse.ArgumentParser(description='Extract content from PDF files')
    parser.add_argument('--input', required=True, help='Path to PDF file')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--include-images', action='store_true', default=True,
                       help='Extract image information (default: True)')
    parser.add_argument('--include-tables', action='store_true', default=True,
                       help='Detect tables (default: True)')
    parser.add_argument('--no-images', action='store_true',
                       help='Skip image extraction')
    parser.add_argument('--no-tables', action='store_true',
                       help='Skip table detection')
    parser.add_argument('--ocr', action='store_true', default=True,
                       help='Use OCR for image-based PDFs (default: True)')
    parser.add_argument('--no-ocr', action='store_true',
                       help='Disable OCR even for image-based PDFs')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: PDF file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        include_images = not args.no_images
        include_tables = not args.no_tables
        use_ocr = not args.no_ocr
        result = extract_pdf(input_path, include_images=include_images, include_tables=include_tables, use_ocr=use_ocr)

        # Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"SUCCESS: Extracted {result['page_count']} pages from {input_path.name}")
        print(f"Total words: {result['total_words']}")
        if include_images:
            print(f"Total images: {result['total_images']}")
        if include_tables:
            print(f"Total tables detected: {result['total_tables']}")
        if result.get('ocr_used'):
            print("OCR: Used (image-based PDF detected)")
        elif result['total_words'] == 0 and not result.get('ocr_available'):
            print("OCR: Not available (install pytesseract and Pillow for OCR support)")

    except Exception as e:
        print(f"ERROR: Extraction failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
