# Output Formats Reference

This document defines the exact formats for document extraction outputs.

## structured.md Format

```markdown
# Document Title

**Source ID**: {source_id}
**Format**: PDF | DOCX | TXT | XLS | XLSX
**Pages**: {page_count} (if applicable)
**Word Count**: {word_count}
**Processed**: {ISO8601 timestamp}

---

## Content Sections

The company uses a **B2B**[^v:B2B] business model with **end-to-end**[^v:end-to-end] integration.

**John Smith**[^e:john_smith] founded the company in 2015 alongside **Jane Doe**[^e:jane_doe].

---

## Tables

### Table 1: {Table Title}

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data     | Data     | Data     |

---

## Enrichment Legend

### Vocabulary ({N} terms normalized)

[^v:B2B]: B2B (original: "business-to-business")
[^v:end-to-end]: end-to-end (original: "end to end supply chain")

### Entities ({N} found)

[^e:john_smith]: john_smith (person)
[^e:jane_doe]: jane_doe (person)
```

### Required Sections

1. **Header** - Source ID, format, word count, processed timestamp
2. **Content** - Full document with semantic footnote enrichment
3. **Tables** - Markdown-formatted tables (if any)
4. **Enrichment Legend** - Vocabulary and entity subsections

### Semantic Footnote IDs

| Type | Format | Example |
|------|--------|---------|
| Vocabulary | `[^v:canonical_term]` | `[^v:API]` |
| Entity | `[^e:entity_id]` | `[^e:john_smith]` |

Benefits:
- Same term/entity uses same footnote across entire document
- No duplicate definitions in legend
- Self-documenting references
- Works with large document chunking

---

## ingest_log.json Format

```json
{
  "source_id": "abc123",
  "source_type": "DOCUMENT",
  "output_file": "structured.md",

  "events": [
    {
      "timestamp": "2025-11-24T10:30:00Z",
      "event": "file_verified",
      "status": "success",
      "details": {
        "file_name": "document.pdf",
        "file_size_bytes": 524288,
        "file_format": "PDF",
        "page_count": 15
      }
    },
    {
      "timestamp": "2025-11-24T10:31:00Z",
      "event": "extraction_completed",
      "status": "success",
      "metrics": {
        "pages_processed": 15,
        "pages_no_text": [1],
        "ocr_used_on_pages": [],
        "word_count": 3500,
        "tables_found": 3,
        "images_found": 2
      }
    },
    {
      "timestamp": "2025-11-24T10:31:10Z",
      "event": "org_context_loaded",
      "status": "success",
      "details": {
        "vocabulary_terms": 150,
        "entities_indexed": 45
      }
    },
    {
      "timestamp": "2025-11-24T10:32:30Z",
      "event": "enrichment_completed",
      "status": "success",
      "metrics": {
        "entities_found": ["john_smith", "jane_doe"],
        "vocabulary_normalized": ["B2B", "end-to-end"]
      }
    },
    {
      "timestamp": "2025-11-24T10:32:32Z",
      "event": "content_verification",
      "status": "success",
      "metrics": {
        "extracted_words": 3500,
        "output_words": 3450,
        "preservation_ratio": 0.99
      }
    },
    {
      "timestamp": "2025-11-24T10:32:35Z",
      "event": "output_created",
      "status": "success",
      "files": [
        "structured.md",
        "ingest_log.json"
      ]
    }
  ]
}
```

### Top-Level Fields

| Field | Description |
|-------|-------------|
| `source_id` | UUID from command |
| `source_type` | Always "DOCUMENT" |
| `output_file` | Points to structured.md |

### Required Events

| Event | Purpose | Key Fields |
|-------|---------|------------|
| `file_verified` | File found and type confirmed | page_count, file_size |
| `extraction_completed` | Extraction finished | pages_processed, word_count |
| `org_context_loaded` | Organizational context loaded | vocabulary_terms, entities_indexed |
| `enrichment_completed` | Enrichment finished | entities_found[], vocabulary_normalized[] |
| `content_verification` | Word count comparison | extracted_words, output_words, preservation_ratio |
| `output_created` | Files created | files[] |
