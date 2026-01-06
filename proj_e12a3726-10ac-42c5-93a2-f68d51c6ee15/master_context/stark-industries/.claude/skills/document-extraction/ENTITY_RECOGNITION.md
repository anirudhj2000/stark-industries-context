# Entity Recognition Strategy

This document describes how to identify and tag known entities in documents.

## Overview

Entity recognition links document mentions to organizational entity records. Only tag entities that exist in the `entities/` directory.

## Recognition by Entity Type

### People

1. **Scan for full names** in document (e.g., "John Smith", "Jane Doe")
2. **Search entities/person/** for matches:
   ```bash
   grep -r "John Smith" entities/person/
   ```
3. **Confirm match** by reading the person's context.yaml file
4. **Apply footnote reference** in markdown: `**John Smith**[^e:john_smith]`

### Organizations

1. **Scan for company names** (e.g., "Acme Corp", "Competitor A", "Investor Fund")
2. **Check directories:**
   - `entities/organization/`
   - `entities/competitor/`
3. **Apply footnote reference** with entity ID and type

### Systems/Products

1. **Scan for system names** (e.g., "Mobile App", "Dashboard System", "Partner System")
2. **Check** `entities/system/`
3. **Apply footnote reference** with system ID

## Semantic Footnote Format

| Type | Format | Example |
|------|--------|---------|
| Person | `[^e:entity_id]` | `[^e:john_smith]` |
| Organization | `[^e:entity_id]` | `[^e:acme_corp]` |
| System | `[^e:entity_id]` | `[^e:mobile_app]` |

## Rules

- **Only tag known entities** - If not in `entities/`, don't tag
- **Minimal tagging** - Just ID and type, no extra context
- **Ignore unknown entities** - Do not flag or note them
- **Read-only operation** - Never modify entity files
- **Deduplicate** - Same entity uses same footnote ID throughout

## Enrichment Legend Entry

```markdown
### Entities ({N} found)

[^e:john_smith]: john_smith (person)
[^e:acme_corp]: acme_corp (organization)
[^e:mobile_app]: mobile_app (system)
```
