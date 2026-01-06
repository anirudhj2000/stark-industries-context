---
name: process-answer-media
description: Process media attachments (audio, video, image, document) in Q&A responses. Extracts text content and returns structured output.
---

# Process Answer Media Skill

## Purpose

Process media attachments submitted as answers to Q&A questions. Extracts text content from audio, video, images, and documents, then returns structured JSON output. The handler sends the webhook to Playbook.

## When to Use

- Command: `process-answer-media`
- Processing response media (audio recordings, video, screenshots, documents)
- Called by Playbook when user submits non-text response

## Input (from manifest/payload)

```json
{
  "response_id": "uuid",
  "question_id": "uuid",
  "media_urls": ["s3://bucket/path/to/file.mp3"],
  "callback_url": "https://playbook/api/v1/context/webhooks/completion/"
}
```

## What Agent SDK Already Did

Before you run, Agent SDK has already:
- Downloaded media files from S3 to workspace
- Set up environment variables
- Written manifest/payload to temp files

## What You Need to Do

1. Identify media type (audio/video/image/document)
2. Route to appropriate transcription engine
3. Clean up transcription with vocabulary normalization
4. Return structured JSON output (handler sends webhook)

## Prerequisites

- Media file downloaded to workspace
- API keys set: `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`

## Tools Available

- **Read**: Read files and vocabulary
- **Bash**: Execute helper scripts
- **Glob**: Find files by pattern

---

## Workflow Steps

### Step 1: Identify Media Type and File

**Instructions:**
1. Get media_urls from payload
2. Download file if not already present (Agent SDK usually handles this)
3. Determine content type from file extension

```bash
# List available media files
ls -la workspace/media/
```

**Media Type Routing:**
- `.mp3`, `.wav`, `.m4a`, `.webm` (audio) → audio processing
- `.mp4`, `.mov`, `.avi` (video) → video processing
- `.jpg`, `.png`, `.gif`, `.webp` (image) → image processing
- `.pdf`, `.docx`, `.xlsx` (document) → use existing extract_* scripts

---

### Step 2: Transcribe/Extract Content

**Route based on media type:**

#### Audio (< 5 min duration)
Use ElevenLabs for high accuracy:
```bash
python scripts/transcribe_audio.py \
  --engine elevenlabs \
  --input workspace/media/recording.mp3 \
  --output workspace/raw_transcription.json
```

#### Audio (>= 5 min) / Video / Image
Use Gemini for native multi-modal understanding:
```bash
python scripts/transcribe_with_gemini.py \
  --input workspace/media/file.mp4 \
  --output workspace/raw_transcription.json \
  --type video
```

#### Document
Delegate to existing document-extraction skill scripts.

---

### Step 3: Load Vocabulary (if available)

**Instructions:**
1. Check for project vocabulary file
2. Load team members for name normalization

```bash
# Find vocabulary file
ls entities/organization/*/vocabulary.yaml 2>/dev/null || echo "No vocabulary"

# Find team members
ls entities/persons/*.json 2>/dev/null | head -5
```

---

### Step 4: Cleanup Transcription

**Instructions:**
1. Run cleanup script with vocabulary context
2. Normalizes technical terms and speaker names

```bash
python scripts/cleanup_transcription.py \
  --input workspace/raw_transcription.json \
  --output workspace/cleaned_transcription.json \
  --vocabulary entities/organization/*/vocabulary.yaml \
  --team-members workspace/team_members.json
```

If vocabulary files don't exist, run without them:
```bash
python scripts/cleanup_transcription.py \
  --input workspace/raw_transcription.json \
  --output workspace/cleaned_transcription.json
```

---

### Step 5: Return Structured Output (CRITICAL)

**The handler will send the webhook. You just need to return valid JSON matching the schema.**

**Load results and prepare output:**

```python
import json
import sys

# Load manifest and payload from the file paths provided as arguments
# IMPORTANT: Do NOT use hardcoded paths - use the arguments passed to the command
# First argument = manifest path, Second argument = payload path
manifest_path = sys.argv[1]  # Path from first argument
payload_path = sys.argv[2]   # Path from second argument

with open(manifest_path, 'r') as f:
    manifest = json.load(f)

with open(payload_path, 'r') as f:
    payload = json.load(f)

response_id = payload.get('response_id', '')

# Load transcription results
with open('workspace/cleaned_transcription.json', 'r') as f:
    result = json.load(f)

text_content = result.get('text_content', '')
metadata = result.get('metadata', {})
cleanup_metadata = result.get('cleanup_metadata', {})
confidence = result.get('confidence', 0.9)
```

**Your final response MUST be valid JSON matching this schema:**

```json
{
  "response_id": "uuid-from-payload",
  "text_content": "Extracted and cleaned text content...",
  "processed_content": {
    "metadata": {
      "media_type": "audio",
      "word_count": 150,
      "duration_seconds": 45
    },
    "cleanup_metadata": {
      "engine": "elevenlabs",
      "vocabulary_terms_used": 5
    },
    "confidence": 0.95
  }
}
```

**Important:**
- The handler receives this JSON via structured output
- The handler sends the webhook to Playbook with proper format
- You do NOT need to send any webhook yourself

---

## Error Handling

1. **File not found**: Check media_urls, verify download completed
2. **API error**: Check API keys, try fallback engine
3. **Timeout**: Large files may need more time, check Gemini for long content

If processing fails, return an error response:

```json
{
  "response_id": "uuid-from-payload",
  "text_content": "",
  "error": "Transcription failed: specific error message"
}
```

---

## Output Schema

Your response must match this JSON schema:

```json
{
  "type": "object",
  "properties": {
    "response_id": {
      "type": "string",
      "description": "UUID of the response being processed"
    },
    "text_content": {
      "type": "string",
      "description": "Extracted text content from media"
    },
    "processed_content": {
      "type": "object",
      "properties": {
        "metadata": {
          "type": "object",
          "properties": {
            "media_type": {"type": "string"},
            "word_count": {"type": "integer"},
            "duration_seconds": {"type": "number"}
          }
        },
        "cleanup_metadata": {
          "type": "object",
          "properties": {
            "engine": {"type": "string"},
            "vocabulary_terms_used": {"type": "integer"}
          }
        },
        "confidence": {"type": "number"}
      }
    }
  },
  "required": ["response_id", "text_content"]
}
```

---

## Quick Reference

| Media Type | Engine | Script |
|------------|--------|--------|
| Audio < 5min | ElevenLabs | `transcribe_audio.py --engine elevenlabs` |
| Audio >= 5min | Gemini | `transcribe_with_gemini.py --type audio` |
| Video | Gemini | `transcribe_with_gemini.py --type video` |
| Image | Gemini | `transcribe_with_gemini.py --type image` |
| Document | Existing | `extract_pdf.py`, `extract_docx.py`, etc. |

---

## Environment Variables

Required:
- `GOOGLE_API_KEY` - For Gemini API
- `OPENAI_API_KEY` - For cleanup (primary)
- `ELEVENLABS_API_KEY` - For short audio transcription

Optional:
- `ANTHROPIC_API_KEY` - Cleanup fallback
- `GEMINI_MODEL` - Default: `gemini-2.0-flash`
- `CLEANUP_MODEL` - Default: `gpt-4o-mini`
