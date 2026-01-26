---
name: transcription
description: Use when processing AUDIO sources or generating meeting notes from recordings - supports both org-level and project-level contexts via context_type field. Transcribes audio files and creates structured minutes with topics, decisions, action items, and entity/vocabulary enrichment.
disable-model-invocation: true
---

# Transcription - Meeting Notes Generation

## Purpose

Transcribe audio files and generate structured meeting notes with entity/vocabulary enrichment. Transform raw transcripts into actionable meeting minutes organized by topics, with decisions, action items, and organizational context.

**Supports both org-level and project-level contexts** - output path determined by `context_type` field.

## When to Use

- Command: `transcribe_audio`
- Processing sources with type AUDIO
- Creating meeting minutes from audio files
- Both org-level (`context_type: "org"`) and project-level (`context_type: "project"`) processing

## Output Path Resolution (CRITICAL)

**Read `is_worktree_mode` and `context_type` from payload to determine output path:**

| is_worktree_mode | context_type | Output Base Path |
|------------------|--------------|------------------|
| `True` | Any | `sources/{source_id}/` |
| `False` | `"project"` | `project_workspaces/project_{project_id}/sources/{source_id}/` |
| `False` | `"org"` | `sources/{source_id}/` |

**Example:**
```python
# From payload
is_worktree_mode = payload.get("is_worktree_mode", False)
context_type = payload.get("context_type", "org")
project_id = payload.get("project_id")
source_id = payload.get("source_id")

# Worktree mode: workspace IS the isolated project, use sources/ directly
# Folder mode: workspace is shared, use project_workspaces/ for project context
if is_worktree_mode:
    output_base = f"sources/{source_id}"
elif context_type == "project" and project_id:
    output_base = f"project_workspaces/project_{project_id}/sources/{source_id}"
else:
    output_base = f"sources/{source_id}"
```

## What Agent SDK Already Did

Before you run, Agent SDK has:
- Downloaded file from S3 to `{output_base}/raw/`
- Validated manifest
- Sent "running" webhook to Playbook

## What You Need to Do

1. **Resolve output path** from `context_type` and `project_id`
2. Transcribe audio file
3. Create raw transcript file (transcript.md)
4. Load organizational entities using `load_entities.py`
5. Extract topics and enrich with org context
6. Generate meeting notes with enrichment
7. Create 3 output files
8. Return structured output (task runner handles git)

## Output Files

| File | Purpose |
|------|---------|
| `structured.md` | Primary: enriched meeting notes with topics, decisions, actions |
| `transcript.md` | Reference: raw transcript (legal/compliance record, NO enrichment) |
| `ingest_log.json` | Processing timeline and metrics |

See [OUTPUT_FORMATS.md](OUTPUT_FORMATS.md) for complete format specifications.

---

## Workflow

### Step 0: Read Manifest + Payload (FIRST)

**Read manifest and payload from the file paths passed as arguments:**

```python
import json
import sys

# First argument = manifest path, Second argument = payload path
manifest_path = sys.argv[1]
payload_path = sys.argv[2]

with open(manifest_path, 'r') as f:
    manifest = json.load(f)

with open(payload_path, 'r') as f:
    payload = json.load(f)

# Extract key information
org_slug = manifest['org']['slug']
source_id = payload['source_id']
is_worktree_mode = payload.get('is_worktree_mode', False)
context_type = payload.get('context_type', 'project')
project_id = payload.get('project_id')
```

**IMPORTANT**: Do NOT use hardcoded paths - read from the arguments.

### Step 0.5: Resolve Output Path

```python
# Worktree mode: workspace IS the isolated project, use sources/ directly
# Folder mode: workspace is shared, use project_workspaces/ for project context
if is_worktree_mode:
    output_base = f"sources/{source_id}"
elif context_type == "project" and project_id:
    output_base = f"project_workspaces/project_{project_id}/sources/{source_id}"
else:
    output_base = f"sources/{source_id}"
```

**Use `{output_base}` for all file paths below.**

### Step 1: Locate and Verify Source File

```bash
ls -lh {output_base}/raw/
```

### Step 2: Transcribe Audio

```bash
python .claude/skills/transcription/scripts/transcribe_audio.py \
  --engine elevenlabs \
  --input {output_base}/raw/audio.mp3 \
  --output /tmp/transcript_raw.json \
  --language auto
```

**Engine Selection:**
| Engine | Best For |
|--------|----------|
| ElevenLabs | High accuracy, speaker separation, conversational audio |
| Whisper | Technical content, multiple languages, noisy audio |

### Step 3: Create Raw Transcript File

1. Read raw transcript from `/tmp/transcript_raw.json`
2. Format as markdown with timestamps and speaker labels
3. Calculate metadata (word count, speaker distribution, confidence)
4. Write to `{output_base}/transcript.md`

**IMPORTANT:** This is a legal/compliance record. NO enrichment, NO modifications.

### Step 4: Load Organizational Entities

**Use the entity loading script:**

```bash
python .claude/skills/transcription/scripts/load_entities.py --pretty
```

This loads:
1. Organization vocabulary from `entities/organization/*/vocabulary.yaml`
2. All entity types: system, process, team, person, product, competitor
3. Strategic initiatives from `strategic.yaml`

**Note:** Transcription is a **producer** of source content - it only needs org entities for vocabulary enrichment, not other project sources.

### Step 5: Extract Topics with AI

Analyze transcript to identify:
- Discussion topics with boundaries
- Key points per topic
- Decisions made (with owners)
- Action items (with owners, deadlines, priorities)
- Executive summary (2-3 sentences)

See [ENRICHMENT.md](ENRICHMENT.md) for detailed extraction strategy.

### Step 6: Enrich Topics with Organizational Context

For each topic, check for organizational matches:
- System mentions → `entities/system/`
- Initiative alignment → `strategic.yaml`
- Product mentions → `entities/product/`

Add "Related Context" annotations when matches found.

### Step 7: Generate Meeting Notes with Enrichment

1. Apply entity enrichment (people, systems, products)
2. Apply vocabulary normalization
3. Build enriched markdown with footnotes
4. Track: `entities_found[]`, `vocabulary_normalized[]`

See [ENRICHMENT.md](ENRICHMENT.md) for enrichment details.

### Step 8: Create Output Files

**CRITICAL:** Create all THREE files in a SINGLE message using parallel Write calls:

1. `{output_base}/structured.md`
2. `{output_base}/transcript.md`
3. `{output_base}/ingest_log.json`

### Step 9: Return Output

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

Return structured JSON:

```json
{
  "status": "success",
  "source_id": "{source_id}",
  "files_written": [
    "{output_base}/structured.md",
    "{output_base}/transcript.md",
    "{output_base}/ingest_log.json"
  ],
  "commit_message": "ingest: transcribe audio for {source_id} - {duration}",
  "metrics": {
    "duration": "45:00",
    "word_count": 5000,
    "num_speakers": 3,
    "num_topics": 5,
    "num_decisions": 3,
    "num_actions": 8,
    "vocabulary_normalized": 12,
    "entities_linked": 15
  }
}
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Audio file not found | `echo "ERROR: Source file not found"` → exit 1 |
| Transcription API fails | `echo "ERROR: Transcription failed: {error}"` → exit 1 |
| Org context not found | `echo "WARNING: ..."` → proceed without enrichment |
| Git commit fails | `echo "ERROR: Git commit failed"` → exit 1 |

Agent SDK catches errors and sends error webhooks.

---

## Success Criteria

- [ ] Audio file located and verified
- [ ] Transcription API called successfully
- [ ] transcript.md created with raw transcript
- [ ] Organizational context loaded
- [ ] Topics extracted and enriched
- [ ] structured.md created with proper formatting
- [ ] ingest_log.json created with timeline
- [ ] `files_written` array returned with all created files
- [ ] `commit_message` returned for task runner

---

## Quick Reference

| Script | Purpose |
|--------|---------|
| `transcribe_audio.py` | Transcribe with ElevenLabs or Whisper |
| `create_structured_metadata.py` | Generate metadata structure |

| Reference | Content |
|-----------|---------|
| [OUTPUT_FORMATS.md](OUTPUT_FORMATS.md) | structured.md, transcript.md, ingest_log.json specs |
| [ENRICHMENT.md](ENRICHMENT.md) | Topic extraction and enrichment details |

---

## What Happens Next

After you complete:
1. Return commit SHA to Agent SDK
2. Agent SDK sends "completed" webhook to Playbook

**You do NOT send webhooks** - Agent SDK handles that.

---

## Notes

- **Dual output**: Meeting notes (primary) + raw transcript (reference)
- **Read-only operation**: Never modifies entity or vocabulary files
- **Best-effort matching**: Gracefully handles missing entities
- **AI + Org context**: Topics identified by AI, enriched with organizational knowledge
