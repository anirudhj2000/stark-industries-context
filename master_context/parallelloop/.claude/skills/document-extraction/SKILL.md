---
name: document-extraction
description: Use when processing DOCUMENT sources (PDF, DOCX, TXT, XLS, XLSX) - supports both org-level and project-level contexts via context_type field. Extracts content with entity/vocabulary enrichment into clean markdown with footnote-style annotations.
disable-model-invocation: true
---

# Document Extraction

## Purpose

Extract text, tables, and metadata from documents with entity/vocabulary enrichment. Transform into clean, readable markdown with footnote-style enrichment linking to organizational entities.

**Supports both org-level and project-level contexts** - output path determined by `context_type` field.

## When to Use

- Command: `process_document`
- Processing sources with type DOCUMENT
- File types: PDF, DOCX, TXT, XLS, XLSX
- Both org-level (`context_type: "org"`) and project-level (`context_type: "project"`) processing

## Output Path Resolution (CRITICAL)

**Read `context_type` from payload to determine output path:**

| context_type | project_id | Output Base Path |
|--------------|------------|------------------|
| `"project"` | Present | `project_workspaces/project_{project_id}/sources/{source_id}/` |
| `"org"` or missing | N/A | `sources/{source_id}/` |

**Example:**
```python
# From payload
context_type = payload.get("context_type", "org")
project_id = payload.get("project_id")
source_id = payload.get("source_id")

if context_type == "project" and project_id:
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
2. Extract content from document
3. Load organizational entities (vocabulary, entities) using `load_entities.py`
4. Apply enrichment (vocabulary normalization, entity linking)
5. Create output files (structured.md, ingest_log.json)
6. Return structured output (task runner handles git)

---

## Enrichment Approach

### Vocabulary Normalization

Normalize variant terminology to canonical forms:
- Document: "application programming interface"
- Output: "**API**[^v:API] integration"
- Footnote: `[^v:API]: API (original: "application programming interface")`

### Entity Linking

Link mentions to repository records:
- Document: "John Smith founded the company"
- Output: "**John Smith**[^e:john_smith] founded the company"
- Footnote: `[^e:john_smith]: john_smith (person)`

### What We DON'T Do

- Validate facts or detect inconsistencies
- Add background context or insights
- Generate Q&A or action items
- Update entity/vocabulary files (read-only)
- Tag unknown entities

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
context_type = payload.get('context_type', 'project')
project_id = payload.get('project_id')
```

**IMPORTANT**: Do NOT use hardcoded paths - read from the arguments.

### Step 0.5: Resolve Output Path

```python
if context_type == "project" and project_id:
    output_base = f"project_workspaces/project_{project_id}/sources/{source_id}"
else:
    output_base = f"sources/{source_id}"
```

**Use `{output_base}` for all file paths below.**

### Step 1: Identify Document Type

```bash
ls -lh {output_base}/raw/
file {output_base}/raw/document.pdf
```

### Step 2: Extract Content

**PDF:**
```bash
python .claude/skills/document-extraction/scripts/extract_pdf.py \
  --input {output_base}/raw/document.pdf \
  --output /tmp/extracted.json \
  --include-images --include-tables
```

**DOCX:**
```bash
python .claude/skills/document-extraction/scripts/extract_docx.py \
  --input {output_base}/raw/document.docx \
  --output /tmp/extracted.json
```

**TXT:**
```bash
python .claude/skills/document-extraction/scripts/extract_txt.py \
  --input {output_base}/raw/document.txt \
  --output /tmp/extracted.json
```

**Excel (XLS/XLSX):**
```bash
python .claude/skills/document-extraction/scripts/extract_excel.py \
  --input {output_base}/raw/spreadsheet.xlsx \
  --output /tmp/extracted.json --include-formulas
```

**For 50+ page documents:** See [LARGE_DOCUMENTS.md](LARGE_DOCUMENTS.md)

### Step 3: Load Organizational Entities

**Use the entity loading script:**

```bash
python .claude/skills/document-extraction/scripts/load_entities.py --pretty
```

This loads:
1. Organization vocabulary from `entities/organization/*/vocabulary.yaml`
2. All entity types: system, process, team, person, product, competitor
3. Build mental index of vocabulary terms, people, organizations, systems

**Note:** Document extraction is a **producer** of source content - it only needs org entities for vocabulary enrichment, not other project sources.

See [ENTITY_RECOGNITION.md](ENTITY_RECOGNITION.md) for recognition strategy.

### Step 4: Apply Enrichment

1. Read extracted content from `/tmp/extracted.json`
2. Scan for vocabulary variants → replace with canonical forms
3. Scan for known entities → insert footnote references
4. Build enriched markdown with semantic footnotes
5. Create footnote legend at end
6. Track: `entities_found[]`, `vocabulary_normalized[]`

### Step 5: Create Output Files

**CRITICAL:** Create both files in a SINGLE message using parallel Write calls.

1. `{output_base}/structured.md`
2. `{output_base}/ingest_log.json`

See [OUTPUT_FORMATS.md](OUTPUT_FORMATS.md) for complete format specifications.

### Step 6: Return Output

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

Return structured JSON:

```json
{
  "status": "success",
  "source_id": "{source_id}",
  "files_written": ["{output_base}/structured.md", "{output_base}/ingest_log.json"],
  "commit_message": "ingest: extract {format} for {source_id} - {page_count} pages",
  "metrics": {
    "page_count": 10,
    "word_count": 5000,
    "tables_found": 3,
    "images_found": 5,
    "vocabulary_normalized": 12,
    "entities_linked": 8
  }
}
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Document file not found | `echo "ERROR: Document file not found"` → exit 1 |
| Extraction fails | `echo "ERROR: Extraction failed: {error}"` → exit 1 |
| Org context not found | `echo "WARNING: ..."` → proceed without enrichment |
| Git commit fails | `echo "ERROR: Git commit failed"` → exit 1 |

Agent SDK catches errors and sends error webhooks.

---

## Success Criteria

- [ ] Document file located and type identified
- [ ] Content extracted (text, tables, images)
- [ ] Organizational context loaded
- [ ] Enrichment applied with semantic footnotes
- [ ] Content verification passed (extracted_words ≈ output_words within 80%)
- [ ] structured.md created with enrichment legend
- [ ] ingest_log.json created with events and metrics
- [ ] `files_written` array returned with all created files
- [ ] `commit_message` returned for task runner

---

## Quick Reference

| Script | Purpose |
|--------|---------|
| `extract_pdf.py` | PDF extraction (PyMuPDF + OCR) |
| `extract_docx.py` | DOCX extraction (python-docx) |
| `extract_txt.py` | Plain text extraction |
| `extract_excel.py` | Excel extraction (openpyxl) |
| `extract_pdf_chunked.py` | Large PDF chunked extraction |

| Reference | Content |
|-----------|---------|
| [OUTPUT_FORMATS.md](OUTPUT_FORMATS.md) | structured.md and ingest_log.json specs |
| [LARGE_DOCUMENTS.md](LARGE_DOCUMENTS.md) | Chunked processing for 50+ pages |
| [ENTITY_RECOGNITION.md](ENTITY_RECOGNITION.md) | Entity recognition strategy |

---

## What Happens Next

After you complete:
1. Return commit SHA to Agent SDK
2. Agent SDK sends "completed" webhook to Playbook

**You do NOT send webhooks** - Agent SDK handles that.

---

## Notes

- **Read-only operation**: Never modifies entity or vocabulary files
- **High confidence tagging**: Only tags what exists in repository
- **Human-first design**: Clean, readable markdown with natural flow
- **Content verification**: Always verify extracted ≈ output word counts
