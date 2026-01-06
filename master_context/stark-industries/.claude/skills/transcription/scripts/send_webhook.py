#!/usr/bin/env python3
"""
Webhook Notification Helper

Sends completion webhooks to PlayBook backend.
"""
import argparse
import json
import sys
from datetime import datetime
import requests


def send_webhook(
    url: str,
    source_id: str,
    status: str = 'success',
    commit_sha: str = None,
    transcript_path: str = None,
    metadata_path: str = None,
    error: str = None
) -> bool:
    """Send webhook notification to PlayBook"""

    payload = {
        'event': 'command_completed',
        'command': 'transcribe_source',
        'command_id': f'transcribe_{source_id}',
        'status': status,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

    if status == 'success':
        # Read transcript preview
        transcript_preview = ""
        if transcript_path:
            try:
                with open(transcript_path) as f:
                    transcript_preview = f.read()[:500]  # First 500 chars
            except:
                pass

        # Read metadata
        metadata = {}
        if metadata_path:
            try:
                with open(metadata_path) as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
            except:
                pass

        payload['output'] = {
            'transcript_path': transcript_path,
            'structured_path': metadata_path,
            'commit_sha': commit_sha,
            'transcript_text': transcript_preview,
            'metadata': metadata
        }
    else:
        payload['error'] = error

    try:
        response = requests.post(
            url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()

        print(f"SUCCESS: Webhook sent to {url}")
        print(f"Response: {response.status_code}")
        return True

    except Exception as e:
        print(f"ERROR: Failed to send webhook: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description='Send webhook notification')
    parser.add_argument('--url', required=True, help='Webhook URL')
    parser.add_argument('--source-id', required=True)
    parser.add_argument('--status', default='success', choices=['success', 'error'])
    parser.add_argument('--commit-sha', help='Git commit SHA')
    parser.add_argument('--transcript-path', help='Path to transcript file')
    parser.add_argument('--metadata-path', help='Path to structured.json')
    parser.add_argument('--error', help='Error message if status is error')

    args = parser.parse_args()

    success = send_webhook(
        url=args.url,
        source_id=args.source_id,
        status=args.status,
        commit_sha=args.commit_sha,
        transcript_path=args.transcript_path,
        metadata_path=args.metadata_path,
        error=args.error
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
