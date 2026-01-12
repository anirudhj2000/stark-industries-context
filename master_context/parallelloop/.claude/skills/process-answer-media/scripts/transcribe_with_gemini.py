#!/usr/bin/env python3
"""
Multi-modal transcription using Google Gemini API.

Handles audio, video, and image content extraction.
Uses Gemini's native multi-modal understanding for accurate transcription.
"""
import argparse
import base64
import json
import os
import sys
from pathlib import Path

import requests


def get_mime_type(file_path: Path, media_type: str) -> str:
    """Get MIME type from file extension."""
    ext = file_path.suffix.lower()
    mime_map = {
        # Audio
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.webm': 'audio/webm',
        '.ogg': 'audio/ogg',
        '.m4a': 'audio/mp4',
        '.flac': 'audio/flac',
        # Video
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo',
        '.mkv': 'video/x-matroska',
        # Image
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    return mime_map.get(ext, f'{media_type}/*')


def transcribe_with_gemini(file_path: Path, media_type: str) -> dict:
    """
    Transcribe/extract content using Gemini API.

    Args:
        file_path: Path to media file
        media_type: One of 'audio', 'video', 'image'

    Returns:
        Dict with text_content, confidence, metadata
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set in environment")

    model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # Read and encode file
    with open(file_path, 'rb') as f:
        file_data = base64.standard_b64encode(f.read()).decode('utf-8')

    mime_type = get_mime_type(file_path, media_type)

    # Build prompt based on media type
    prompts = {
        'audio': (
            "Transcribe this audio file accurately. Include speaker identification "
            "if multiple speakers are present. Output the transcription as plain text."
        ),
        'video': (
            "Transcribe all spoken content in this video. Also describe any important "
            "visual elements, text on screen, or diagrams shown. Format as plain text "
            "with visual descriptions in [brackets]."
        ),
        'image': (
            "Extract all text visible in this image. If it's a diagram, whiteboard, "
            "or handwritten notes, describe the content and structure. If it's a "
            "screenshot of a document, extract the full text."
        ),
    }

    prompt = prompts.get(media_type, prompts['audio'])

    # Build request
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": file_data
                    }
                }
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192,
        }
    }

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=300  # 5 min timeout for large files
    )

    if not response.ok:
        error_detail = response.text[:500] if response.text else "No details"
        raise requests.HTTPError(
            f"{response.status_code} {response.reason}: {error_detail}",
            response=response
        )

    result = response.json()

    # Extract text from response
    try:
        text_content = result['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError):
        text_content = ""

    # Get file size for metadata
    file_size = file_path.stat().st_size

    return {
        'text_content': text_content,
        'confidence': 0.9,  # Gemini doesn't return confidence scores
        'metadata': {
            'model': model,
            'media_type': media_type,
            'mime_type': mime_type,
            'file_size_bytes': file_size,
            'word_count': len(text_content.split()),
        }
    }


def main():
    parser = argparse.ArgumentParser(description='Transcribe media with Gemini')
    parser.add_argument('--input', required=True, help='Path to media file')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--type', required=True, choices=['audio', 'video', 'image'],
                        help='Media type')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        result = transcribe_with_gemini(input_path, args.type)

        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"SUCCESS: Transcription saved to {args.output}")
        print(f"Words: {result['metadata']['word_count']}")

    except Exception as e:
        print(f"ERROR: Transcription failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
