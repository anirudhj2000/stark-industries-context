# Topic Extraction and Enrichment

This document details how to extract topics from transcripts and enrich them with organizational context.

## Topic Extraction (AI Analysis)

### Step 1: Identify Discussion Topics

Analyze the raw transcript to detect topic boundaries:

1. **Read raw transcript** from `/tmp/transcript_raw.json`
2. **Detect topic boundaries** by analyzing conversation flow:
   - Significant pauses or transitions
   - Explicit topic changes ("Let's move on to...", "Next item...")
   - Shifts in subject matter
3. **Group related segments** by topic
4. **Extract topic titles** from conversation context

### Step 2: Extract Decisions Per Topic

For each topic, identify decisions made:

- Look for approval/rejection language ("We've decided...", "Approved", "Let's go with...")
- Identify commitments made
- Note decision owners
- Capture context for each decision

### Step 3: Extract Action Items Per Topic

For each topic, identify action items:

- Look for task assignments ("Can you...", "Please...", "Action item...")
- Identify owners (who will do it)
- Extract deadlines if mentioned ("by Friday", "end of month")
- Note priority indicators ("urgent", "high priority", "when you get a chance")

### Step 4: Generate Executive Summary

Create 2-3 sentences covering:
- Meeting purpose
- Key outcomes
- Major decisions or next steps

---

## Organizational Context Enrichment

### Loading Context

1. **Identify organization ID** from working directory:
   ```bash
   pwd
   # Should be in: master_context/{org_id}/
   ```

2. **Load vocabulary**:
   ```bash
   find entities/organization -name "vocabulary.yaml" -type f
   ```

3. **Index entities**:
   ```bash
   find entities -name "*.yaml" -type f
   ```

4. **Load strategic initiatives**:
   ```bash
   find entities/organization -name "strategic.yaml" -type f
   ```

### Building Mental Index

Index the following for matching:
- **Vocabulary terms** - Acronyms, internal terminology, canonical forms
- **People names** - Leadership, key stakeholders
- **Systems/products** - Internal apps, dashboards, partner systems
- **Strategic initiatives** - Goals, targets, projects

---

## Topic Enrichment

### Matching Strategy

For each AI-identified topic, check for organizational matches:

| Check | Source | Match Criteria |
|-------|--------|----------------|
| System mentions | entities/system/ | Topic discusses known system |
| Initiative alignment | strategic.yaml | Topic relates to strategic initiatives |
| Product mentions | entities/product/ | Topic discusses known products |

### Creating Related Context

When matches found, add to topic header:

```markdown
### 1. Process Improvement Initiative[^3]

**Related Context**: Engineering velocity improvement, Partner System integration[^4]
```

If no match: topic stands alone (no Related Context line)

---

## Entity Enrichment

### People Recognition

1. Scan notes for **people names** (speakers, action item owners)
2. Match to `entities/person/` using exact/partial/fuzzy matching
3. If match found: apply footnote `**John Smith**[^1]`
4. If no match: leave as plain text (graceful fallback)

### System/Product Recognition

1. Scan notes for **system mentions**
2. Match to `entities/system/` or `entities/product/`
3. Apply footnotes: `**Mobile App**[^5]`

### Vocabulary Normalization

1. Scan for `vocabulary.yaml` variants
2. Replace with canonical forms
3. Apply footnotes: `**API**[^3]`
4. Legend entry: `[^3]: API (original: "application programming interface")`

---

## Enrichment Tracking

Track all enrichments for the legend:

```python
entities_found = ["john_smith", "bob_wilson", "partner_system"]
vocabulary_normalized = ["Process Improvement Initiative", "Mobile App"]
```

These populate the Enrichment Legend in structured.md.

---

## Best Practices

- **Best effort matching** - Gracefully handle missing entities
- **Read-only operation** - Never modify entity or vocabulary files
- **Consistent footnotes** - Same entity uses same footnote ID throughout
- **Topic-first structure** - Organize by topics, not chronologically
