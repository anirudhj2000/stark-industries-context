#!/usr/bin/env python3
"""
Audio Transcription Helper Script

Transcribes audio files using ElevenLabs or OpenAI Whisper APIs.
"""
import argparse
import json
import os
import sys
from pathlib import Path
import requests


def transcribe_elevenlabs(audio_path: Path, language: str = "auto") -> dict:
    """Transcribe using ElevenLabs Speech-to-Text API (Scribe v1)"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not set in environment")

    url = "https://api.elevenlabs.io/v1/speech-to-text"

    # Determine content type based on file extension
    ext = audio_path.suffix.lower()
    content_types = {
        '.mp3': 'audio/mpeg',
        '.mp4': 'audio/mp4',
        '.m4a': 'audio/mp4',
        '.wav': 'audio/wav',
        '.webm': 'audio/webm',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
    }
    content_type = content_types.get(ext, 'audio/mpeg')

    with open(audio_path, 'rb') as f:
        files = {'file': (audio_path.name, f, content_type)}
        headers = {'xi-api-key': api_key}
        data = {
            'model_id': 'scribe_v1',
            'diarize': 'true',
            'timestamps_granularity': 'word'
        }
        if language != 'auto':
            data['language_code'] = language

        response = requests.post(url, headers=headers, files=files, data=data)

        # Better error handling - show response body on error
        if not response.ok:
            error_detail = response.text[:500] if response.text else "No details"
            if response.status_code == 401:
                raise requests.HTTPError(
                    f"401 Unauthorized: Invalid or missing ElevenLabs API key. "
                    f"Verify ELEVENLABS_API_KEY is set correctly. Detail: {error_detail}",
                    response=response
                )
            raise requests.HTTPError(
                f"{response.status_code} {response.reason}: {error_detail}",
                response=response
            )

    return response.json()


def transcribe_whisper(audio_path: Path, language: str = "auto") -> dict:
    """Transcribe using OpenAI Whisper API"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    url = "https://api.openai.com/v1/audio/transcriptions"

    # Determine content type based on file extension
    ext = audio_path.suffix.lower()
    content_types = {
        '.mp3': 'audio/mpeg',
        '.mp4': 'audio/mp4',
        '.m4a': 'audio/mp4',
        '.wav': 'audio/wav',
        '.webm': 'audio/webm',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
    }
    content_type = content_types.get(ext, 'audio/mpeg')

    with open(audio_path, 'rb') as f:
        # Must include filename and content-type for multipart upload
        files = {'file': (audio_path.name, f, content_type)}
        headers = {'Authorization': f'Bearer {api_key}'}
        data = {
            'model': 'whisper-1',
            'response_format': 'verbose_json'
        }
        if language != 'auto':
            data['language'] = language

        response = requests.post(url, headers=headers, files=files, data=data)

        # Better error handling - show response body on error
        if not response.ok:
            error_detail = response.text[:500] if response.text else "No details"
            raise requests.HTTPError(
                f"{response.status_code} {response.reason}: {error_detail}",
                response=response
            )

    return response.json()


def main():
    parser = argparse.ArgumentParser(description='Transcribe audio file')
    parser.add_argument('--engine', choices=['elevenlabs', 'whisper'], required=True)
    parser.add_argument('--input', required=True, help='Path to audio file')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--language', default='auto', help='Language code or auto')

    args = parser.parse_args()

    audio_path = Path(args.input)
    if not audio_path.exists():
        print(f"ERROR: Audio file not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.engine == 'elevenlabs':
            result = transcribe_elevenlabs(audio_path, args.language)
        else:
            result = transcribe_whisper(audio_path, args.language)

        # Standardize output format
        output = {
            'text': result.get('text', ''),
            'language': result.get('language', args.language),
            'duration': result.get('duration'),
            'words': len(result.get('text', '').split()),
            'engine': args.engine,
            'raw_response': result
        }

        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"SUCCESS: Transcription saved to {args.output}")
        print(f"Words: {output['words']}, Language: {output['language']}")

    except Exception as e:
        print(f"ERROR: Transcription failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
