# Output Formats Reference

This document defines the exact formats for transcription outputs.

## Overview

Three files are created:
1. **structured.md** - Primary output: enriched meeting notes
2. **transcript.md** - Reference: raw transcript (legal/compliance record)
3. **ingest_log.json** - Processing timeline

---

## structured.md Format

```markdown
# Meeting Notes: {Meeting Title}

**Source ID**: {source_id}
**Date**: {date}
**Duration**: {HH:MM:SS}
**Attendees**: John Smith[^1], Bob Wilson[^2], Alice Brown
**Processed**: {ISO8601 timestamp}

---

## Executive Summary

[2-3 sentence overview of meeting purpose and key outcomes]

---

## Discussion Topics

### 1. {Topic Title}[^3]

**Related Context**: {Initiative name}, {System name}[^4]

**Key Points:**
- Point with **entity mention**[^1] and details
- Another key discussion point
- Third point about **system**[^5]

**Decisions:**
- ✓ Decision description
- ✓ Another decision

**Action Items:**
- [ ] **Owner Name**[^1]: Task description (Due: {date})
- [ ] Another Owner: Another task

---

### 2. {Next Topic Title}

[Continue with more topics...]

---

## Summary of Decisions ({N} total)

1. First decision
2. Second decision
3. [More decisions...]

---

## Summary of Action Items ({N} total)

**High Priority:**
- [ ] **Owner**[^1]: Task (Due: {date})
- [ ] **Owner**[^2]: Task (Due: {date})

**Medium Priority:**
- [ ] Owner: Task
- [More action items...]

---

## Enrichment Legend

### Vocabulary ({N} terms normalized)

[^3]: Process Improvement Initiative (original: "process reconciliation project")
[^5]: Mobile App (original: "mobile application")

### Entities ({N} found)

[^1]: john_smith (person)
[^2]: bob_wilson (person)
[^4]: partner_system (system)
```

### Required Sections

1. **Header** - Source ID, date, duration, attendees, processed timestamp
2. **Executive Summary** - 2-3 sentences
3. **Discussion Topics** - One section per topic with:
   - Related Context (if org matches found)
   - Key Points
   - Decisions
   - Action Items
4. **Summary of Decisions** - Consolidated list
5. **Summary of Action Items** - Consolidated, prioritized
6. **Enrichment Legend** - Vocabulary + entities

---

## transcript.md Format

```markdown
# Transcript: {Meeting Title}

**Source ID**: {source_id}
**Date**: {date}
**Duration**: {HH:MM:SS}
**Speakers**: {count} ({names})
**Language**: {language}
**Engine**: {engine}
**Confidence**: {score}
**Processed**: {ISO8601 timestamp}

---

## Full Transcript

[00:00:00] **Speaker 1**: Welcome everyone...

[00:00:08] **Speaker 2**: Thanks for having me...

[00:01:15] **Speaker 1**: Let's start with the first topic...

[Continue with all segments...]

---

## Metadata

**Total Words**: {word_count}
**Average Speaking Rate**: {words/minute}
**Total Segments**: {count}

**Speaker Distribution**:
- Speaker 1: {percentage}% ({word_count} words, {segment_count} segments)
- Speaker 2: {percentage}% ({word_count} words, {segment_count} segments)

**Transcription Quality**:
- Engine: {engine}
- Confidence Score: {score}
- Language Detected: {language}
```

### Important Notes

- **Legal/compliance record** - NO enrichment, NO modifications
- Pure, unmodified transcript with timestamps
- Speaker labels and segments preserved exactly

---

## ingest_log.json Format

```json
{
  "source_id": "abc123",
  "source_type": "AUDIO",
  "output_files": ["structured.md", "transcript.md", "ingest_log.json"],

  "events": [
    {
      "timestamp": "2025-11-24T10:00:00Z",
      "event": "file_verified",
      "status": "success",
      "details": {
        "file_size_bytes": 25600000,
        "file_format": "MP3",
        "duration_seconds": 4530
      }
    },
    {
      "timestamp": "2025-11-24T10:00:05Z",
      "event": "transcription_started",
      "engine": "elevenlabs",
      "language": "auto"
    },
    {
      "timestamp": "2025-11-24T10:05:30Z",
      "event": "transcription_completed",
      "status": "success",
      "metrics": {
        "duration_seconds": 325,
        "word_count": 4250,
        "speaker_count": 3,
        "confidence": 0.95
      }
    },
    {
      "timestamp": "2025-11-24T10:05:35Z",
      "event": "transcript_created",
      "status": "success",
      "file": "transcript.md"
    },
    {
      "timestamp": "2025-11-24T10:05:40Z",
      "event": "org_context_loaded",
      "status": "success",
      "details": {
        "vocabulary_terms": 150,
        "entities_indexed": 45
      }
    },
    {
      "timestamp": "2025-11-24T10:06:00Z",
      "event": "topics_extracted",
      "status": "success",
      "metrics": {
        "topics_identified": 3,
        "topics_enriched_with_org_context": 2
      }
    },
    {
      "timestamp": "2025-11-24T10:07:30Z",
      "event": "meeting_notes_generated",
      "status": "success",
      "metrics": {
        "topics": 3,
        "decisions": 5,
        "action_items": 8
      }
    },
    {
      "timestamp": "2025-11-24T10:08:00Z",
      "event": "enrichment_completed",
      "status": "success",
      "metrics": {
        "vocabulary_normalized": 2,
        "entities_linked": 5
      }
    },
    {
      "timestamp": "2025-11-24T10:08:05Z",
      "event": "structured_outputs_created",
      "status": "success",
      "files": ["structured.md", "transcript.md", "ingest_log.json"]
    }
  ]
}
```

### Required Events

| Event | Purpose | Key Fields |
|-------|---------|------------|
| `file_verified` | Audio/video file found | file_size, format, duration |
| `transcription_started` | API called | engine, language |
| `transcription_completed` | Raw transcript received | word_count, speaker_count, confidence |
| `transcript_created` | transcript.md written | file |
| `org_context_loaded` | Context indexed | vocabulary_terms, entities_indexed |
| `topics_extracted` | AI identified topics | topics_identified, topics_enriched |
| `meeting_notes_generated` | structured.md created | topics, decisions, action_items |
| `enrichment_completed` | Entity/vocab applied | vocabulary_normalized, entities_linked |
| `structured_outputs_created` | All files written | files[] |
