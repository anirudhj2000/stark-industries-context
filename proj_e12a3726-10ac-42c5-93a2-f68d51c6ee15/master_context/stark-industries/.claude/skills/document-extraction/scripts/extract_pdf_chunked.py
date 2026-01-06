#!/usr/bin/env python3
"""
Chunked PDF Extraction Helper Script

Extracts text from PDF files in chunks for large document processing.
This prevents output truncation when Claude processes large documents.

Usage:
    # Extract pages 1-30 (chunk 1)
    python extract_pdf_chunked.py --input doc.pdf --output /tmp/chunk_001.json --start-page 1 --end-page 30

    # Extract pages 31-60 (chunk 2)
    python extract_pdf_chunked.py --input doc.pdf --output /tmp/chunk_002.json --start-page 31 --end-page 60

    # Get document info (page count, word estimates)
    python extract_pdf_chunked.py --input doc.pdf --info-only
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
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

# Recommended chunk size (pages per chunk)
DEFAULT_CHUNK_SIZE = 30
LARGE_DOC_THRESHOLD = 50  # Pages


def get_document_info(file_path: Path) -> Dict[str, Any]:
    """Get document metadata without full extraction."""
    try:
        doc = fitz.open(file_path)

        # Sample first few pages for word count estimate
        sample_words = 0
        sample_pages = min(5, len(doc))
        for i in range(sample_pages):
            page = doc[i]
            text = page.get_text()
            sample_words += len(text.split())

        avg_words_per_page = sample_words / sample_pages if sample_pages > 0 else 0
        estimated_total_words = int(avg_words_per_page * len(doc))

        # Determine if chunking is needed
        needs_chunking = len(doc) > LARGE_DOC_THRESHOLD
        recommended_chunks = (len(doc) // DEFAULT_CHUNK_SIZE) + (1 if len(doc) % DEFAULT_CHUNK_SIZE else 0)

        result = {
            "file_name": file_path.name,
            "file_size_bytes": file_path.stat().st_size,
            "page_count": len(doc),
            "estimated_words": estimated_total_words,
            "avg_words_per_page": int(avg_words_per_page),
            "needs_chunking": needs_chunking,
            "chunk_threshold": LARGE_DOC_THRESHOLD,
            "recommended_chunk_size": DEFAULT_CHUNK_SIZE,
            "recommended_chunks": recommended_chunks if needs_chunking else 1,
            "chunk_ranges": [],
            "metadata": {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
            }
        }

        # Generate chunk ranges if needed
        if needs_chunking:
            for i in range(recommended_chunks):
                start = i * DEFAULT_CHUNK_SIZE + 1
                end = min((i + 1) * DEFAULT_CHUNK_SIZE, len(doc))
                result["chunk_ranges"].append({
                    "chunk": i + 1,
                    "start_page": start,
                    "end_page": end,
                    "page_count": end - start + 1
                })

        doc.close()
        return result

    except Exception as e:
        raise Exception(f"Failed to get document info: {e}")


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


def extract_pdf_chunk(
    file_path: Path,
    start_page: int,
    end_page: int,
    include_images: bool = False,
    use_ocr: bool = True
) -> Dict[str, Any]:
    """Extract content from a specific page range of a PDF file.

    Args:
        file_path: Path to PDF file
        start_page: First page to extract (1-indexed)
        end_page: Last page to extract (1-indexed, inclusive)
        include_images: Whether to extract image metadata
        use_ocr: Whether to use OCR for image-based pages

    Returns:
        Dict with extracted content for the specified page range
    """
    try:
        doc = fitz.open(file_path)
        total_pages = len(doc)

        # Validate page range
        if start_page < 1:
            start_page = 1
        if end_page > total_pages:
            end_page = total_pages
        if start_page > end_page:
            raise ValueError(f"Invalid page range: {start_page}-{end_page}")

        pages = []
        total_words = 0
        total_images = 0
        ocr_used = False

        # Convert to 0-indexed
        for page_num in range(start_page - 1, end_page):
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
                            "format": base_image["ext"],
                            "width": base_image["width"],
                            "height": base_image["height"],
                        })
                        total_images += 1
                    except:
                        pass

            page_info = {
                "page_number": page_num + 1,  # Back to 1-indexed
                "text": text,
                "word_count": word_count,
                "images": images if include_images else []
            }

            pages.append(page_info)

        result = {
            "file_name": file_path.name,
            "format": "PDF",
            "chunk_info": {
                "start_page": start_page,
                "end_page": end_page,
                "pages_in_chunk": len(pages),
                "total_document_pages": total_pages
            },
            "pages": pages,
            "total_words": total_words,
            "total_images": total_images,
            "ocr_used": ocr_used,
            "metadata": {
                "engine": "PyMuPDF" + (" + pytesseract OCR" if ocr_used else ""),
                "chunk_extraction": True
            }
        }

        doc.close()
        return result

    except Exception as e:
        raise Exception(f"Failed to extract PDF chunk: {e}")


def main():
    parser = argparse.ArgumentParser(description='Extract content from PDF files in chunks')
    parser.add_argument('--input', required=True, help='Path to PDF file')
    parser.add_argument('--output', help='Output JSON file (required unless --info-only)')
    parser.add_argument('--info-only', action='store_true',
                       help='Only get document info (page count, chunking recommendations)')
    parser.add_argument('--start-page', type=int, default=1,
                       help='First page to extract (1-indexed, default: 1)')
    parser.add_argument('--end-page', type=int,
                       help='Last page to extract (1-indexed, default: last page)')
    parser.add_argument('--include-images', action='store_true',
                       help='Extract image metadata')
    parser.add_argument('--no-ocr', action='store_true',
                       help='Disable OCR for image-based pages')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: PDF file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.info_only:
            # Just get document info
            result = get_document_info(input_path)
            print(json.dumps(result, indent=2))

            # Print human-readable summary
            print(f"\n--- Document Info ---", file=sys.stderr)
            print(f"Pages: {result['page_count']}", file=sys.stderr)
            print(f"Estimated words: {result['estimated_words']:,}", file=sys.stderr)
            print(f"Needs chunking: {result['needs_chunking']}", file=sys.stderr)
            if result['needs_chunking']:
                print(f"Recommended chunks: {result['recommended_chunks']}", file=sys.stderr)
                for chunk in result['chunk_ranges']:
                    print(f"  Chunk {chunk['chunk']}: pages {chunk['start_page']}-{chunk['end_page']}", file=sys.stderr)
        else:
            if not args.output:
                print("ERROR: --output is required unless using --info-only", file=sys.stderr)
                sys.exit(1)

            # Get total pages to set default end_page
            doc = fitz.open(input_path)
            total_pages = len(doc)
            doc.close()

            end_page = args.end_page if args.end_page else total_pages

            result = extract_pdf_chunk(
                input_path,
                start_page=args.start_page,
                end_page=end_page,
                include_images=args.include_images,
                use_ocr=not args.no_ocr
            )

            # Write output
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"SUCCESS: Extracted pages {args.start_page}-{end_page} from {input_path.name}")
            print(f"Pages in chunk: {result['chunk_info']['pages_in_chunk']}")
            print(f"Words in chunk: {result['total_words']}")
            if result.get('ocr_used'):
                print("OCR: Used (image-based pages detected)")

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
