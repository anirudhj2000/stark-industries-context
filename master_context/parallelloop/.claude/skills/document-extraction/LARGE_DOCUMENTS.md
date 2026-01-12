# Large Document Handling (50+ Pages)

For documents with 50+ pages, use chunked processing to avoid output truncation.

## Why Chunked Processing?

- Claude's output has token limits (~16K tokens per response)
- A 180-page document has ~30,000-50,000 words
- Without chunking, enriched output gets truncated
- Chunked processing ensures ALL content is preserved

## When to Use

| Document Size | Processing Mode |
|--------------|-----------------|
| < 50 pages | Standard workflow |
| 50+ pages | Chunked processing |

## Chunked Processing Workflow

### Step 1: Check Document Size

```bash
python3 .claude/skills/document-extraction/scripts/extract_pdf_chunked.py \
  --input sources/{source_id}/raw/document.pdf \
  --info-only
```

Output:
```json
{
  "page_count": 180,
  "estimated_words": 35000,
  "needs_chunking": true,
  "recommended_chunks": 7,
  "chunk_ranges": [
    {"chunk": 1, "start_page": 1, "end_page": 30},
    {"chunk": 2, "start_page": 31, "end_page": 60}
  ]
}
```

### Step 2: Extract in Chunks

Extract in batches of 30 pages:

```bash
# Chunk 1: Pages 1-30
python3 .claude/skills/document-extraction/scripts/extract_pdf_chunked.py \
  --input sources/{source_id}/raw/document.pdf \
  --output /tmp/chunk_001.json \
  --start-page 1 --end-page 30

# Chunk 2: Pages 31-60
python3 .claude/skills/document-extraction/scripts/extract_pdf_chunked.py \
  --input sources/{source_id}/raw/document.pdf \
  --output /tmp/chunk_002.json \
  --start-page 31 --end-page 60

# Continue for all chunks...
```

### Step 3: Process Each Chunk

For each chunk:
1. Read chunk JSON from `/tmp/chunk_NNN.json`
2. Apply enrichment with semantic footnotes (`[^v:term]`, `[^e:entity_id]`)
3. Write chunk content to `sources/{source_id}/structured_chunk_NNN.md`
4. Track enrichments in memory (deduplicated by semantic ID)
5. **DO NOT** include Enrichment Legend in chunk files

**Chunk File Format:**
```markdown
## Section from Chunk N

The company uses a **B2B**[^v:B2B] business model...

**John Smith**[^e:john_smith] leads the team...
```

No header, no legend - just content with semantic footnote refs.

### Step 4: Compile Final Output

After all chunks are processed:

1. **Concatenate chunks:**
   ```bash
   cat sources/{source_id}/structured_chunk_*.md > /tmp/compiled_content.md
   ```

2. **Write final structured.md:**
   - Add header (Source ID, Format, Pages, Word Count, Processed date)
   - Include compiled content from `/tmp/compiled_content.md`
   - Add consolidated Enrichment Legend at end

3. **Clean up chunk files:**
   ```bash
   rm sources/{source_id}/structured_chunk_*.md
   ```

## Content Verification (Required)

**ALWAYS** verify content preservation after compilation:

```
extracted_words ≈ output_words (within 80%)
```

Log verification in `ingest_log.json`:
```json
{
  "event": "content_verification",
  "status": "success",
  "metrics": {
    "extracted_words": 35000,
    "output_words": 34200,
    "preservation_ratio": 0.98
  }
}
```
