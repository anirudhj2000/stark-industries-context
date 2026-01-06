#!/usr/bin/env python3
"""
Cleanup transcription with vocabulary normalization.

Uses OpenAI Responses API (primary) or Claude (fallback) for light cleanup.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import requests


def load_vocabulary(vocab_path: Path) -> list:
    """Load vocabulary terms from YAML file."""
    if not vocab_path or not vocab_path.exists():
        return []

    try:
        import yaml
        with open(vocab_path) as f:
            data = yaml.safe_load(f)
            # Handle both list format and dict with 'terms' key
            if isinstance(data, list):
                return data
            return data.get('terms', [])
    except Exception:
        return []


def load_team_members(members_path: Path) -> list:
    """Load team member names from JSON file."""
    if not members_path or not members_path.exists():
        return []

    try:
        with open(members_path) as f:
            data = json.load(f)
            # Handle both list format and dict with 'members' key
            if isinstance(data, list):
                return [m.get('name', m) if isinstance(m, dict) else m for m in data]
            return [m.get('name', m) if isinstance(m, dict) else m for m in data.get('members', [])]
    except Exception:
        return []


def cleanup_with_openai(text: str, vocabulary: list, team_members: list) -> str:
    """Cleanup transcription using OpenAI API."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    model = os.getenv('CLEANUP_MODEL', 'gpt-4o-mini')
    url = "https://api.openai.com/v1/chat/completions"

    # Build context about vocabulary and team
    context_parts = []
    if vocabulary:
        context_parts.append(f"Domain vocabulary: {', '.join(vocabulary[:50])}")
    if team_members:
        context_parts.append(f"Team members: {', '.join(team_members[:20])}")

    context = "\n".join(context_parts) if context_parts else ""

    prompt = f"""Clean up this transcription for readability. Fix:
- Obvious transcription errors
- Punctuation and capitalization
- Speaker name spelling (use provided team members if mentioned)
- Technical terms (use provided vocabulary)

Keep the original meaning and tone. Do NOT summarize or remove content.

{f"Context:{chr(10)}{context}" if context else ""}

Transcription:
{text}

Output only the cleaned transcription, no explanations."""

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 4096,
        },
        timeout=60
    )

    if not response.ok:
        raise requests.HTTPError(f"{response.status_code}: {response.text[:200]}")

    return response.json()['choices'][0]['message']['content']


def cleanup_with_claude(text: str, vocabulary: list, team_members: list) -> str:
    """Cleanup transcription using Claude API (fallback)."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    url = "https://api.anthropic.com/v1/messages"

    context_parts = []
    if vocabulary:
        context_parts.append(f"Domain vocabulary: {', '.join(vocabulary[:50])}")
    if team_members:
        context_parts.append(f"Team members: {', '.join(team_members[:20])}")

    context = "\n".join(context_parts) if context_parts else ""

    prompt = f"""Clean up this transcription for readability. Fix:
- Obvious transcription errors
- Punctuation and capitalization
- Speaker name spelling (use provided team members if mentioned)
- Technical terms (use provided vocabulary)

Keep the original meaning and tone. Do NOT summarize or remove content.

{f"Context:{chr(10)}{context}" if context else ""}

Transcription:
{text}

Output only the cleaned transcription, no explanations."""

    response = requests.post(
        url,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        },
        json={
            "model": "claude-3-haiku-20240307",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60
    )

    if not response.ok:
        raise requests.HTTPError(f"{response.status_code}: {response.text[:200]}")

    return response.json()['content'][0]['text']


def main():
    parser = argparse.ArgumentParser(description='Cleanup transcription')
    parser.add_argument('--input', required=True, help='Input JSON file with text_content')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--vocabulary', help='Path to vocabulary YAML file')
    parser.add_argument('--team-members', help='Path to team members JSON file')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Load input
    with open(input_path) as f:
        data = json.load(f)

    text = data.get('text_content') or data.get('text', '')
    if not text:
        print("ERROR: No text_content in input file", file=sys.stderr)
        sys.exit(1)

    # Load vocabulary and team members
    vocabulary = load_vocabulary(Path(args.vocabulary)) if args.vocabulary else []
    team_members = load_team_members(Path(args.team_members)) if args.team_members else []

    # Try OpenAI first, fallback to Claude
    try:
        cleaned_text = cleanup_with_openai(text, vocabulary, team_members)
        engine = 'openai'
    except Exception as e:
        print(f"OpenAI cleanup failed ({e}), trying Claude...", file=sys.stderr)
        try:
            cleaned_text = cleanup_with_claude(text, vocabulary, team_members)
            engine = 'claude'
        except Exception as e2:
            print(f"ERROR: Both cleanup engines failed. OpenAI: {e}, Claude: {e2}", file=sys.stderr)
            sys.exit(1)

    # Build output
    output = {
        **data,
        'text_content': cleaned_text,
        'cleanup_metadata': {
            'engine': engine,
            'original_word_count': len(text.split()),
            'cleaned_word_count': len(cleaned_text.split()),
            'vocabulary_terms_used': len(vocabulary),
            'team_members_used': len(team_members),
        }
    }

    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"SUCCESS: Cleaned transcription saved to {args.output}")
    print(f"Engine: {engine}, Words: {output['cleanup_metadata']['cleaned_word_count']}")


if __name__ == '__main__':
    main()
