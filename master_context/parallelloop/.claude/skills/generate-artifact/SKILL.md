---
name: generate-artifact
description: Use when user says "create a doc", "save this as...", or "generate a PRD/TDD/FRD" and there's enough context in the conversation. Creates immediately WITHOUT dialogue - for dialogue-based creation use prd-brainstorm/tdd-brainstorm/frd-brainstorm instead.
---

# Generate Artifact Skill

Create documents immediately from conversation context. No dialogue - just generate.

**When to use this vs brainstorm skills:**
| Skill | Trigger | Behavior |
|-------|---------|----------|
| `generate-artifact` | "create a PRD", "save this" | Immediate - extracts from conversation |
| `prd-brainstorm` | "@prd let's brainstorm" | Dialogue - asks questions first |

## Artifact Type Detection

| User Says | Type | Prefix |
|-----------|------|--------|
| "create a PRD" | PRD | `art_prd_` |
| "create a TDD" | TDD | `art_tdd_` |
| "create an FRD" | FRD | `art_frd_` |
| "create meeting notes" | NOTES | `art_notes_` |
| "create a doc" | **Infer** | varies |
| "save this" | **Infer** | varies |

**Context inference for "create a doc":**
- Product requirements discussed → PRD
- Technical architecture discussed → TDD
- Feature specifications discussed → FRD
- Meeting/discussion topics → NOTES
- Unclear → ask user: "What type of document? PRD, TDD, FRD, or meeting notes?"

## Process

### 1. Read Payload (if provided)

If payload file exists (second argument):
```bash
# Read project_id from payload
project_id=$(jq -r '.project_id // empty' "$PAYLOAD_FILE")
```

### 2. Detect Artifact Type

Parse user request and conversation context to determine type.

### 3. Find Template

```bash
# Search for template
template_path=".claude/templates/${type}.md"  # e.g., prd.md, tdd.md
```

- If template exists → use it
- If not → infer structure from artifact type

### 4. Generate Content

Extract from conversation:
- Main topic/subject
- Key points discussed
- Decisions made
- Requirements (if applicable)
- Action items (if applicable)

Fill template or create inferred structure.

### 5. Write Output

```bash
artifact_id=$(uuidgen | tr '[:upper:]' '[:lower:]' | cut -c1-8)

# With project context:
if [ -n "$project_id" ]; then
  output_dir="project_workspaces/project_${project_id}/artifacts/art_${type}_${project_id}_${artifact_id}"
else
  output_dir="artifacts/art_${type}_${artifact_id}"
fi

mkdir -p "$output_dir"
# Write content.md
```

### 6. Respond

Describe what was created naturally:
```
I've created the PRD for [project name]. It covers [key sections].

Would you like me to make any changes?
```

**DO NOT run git commands.** Task runner handles git.

## Error Handling

**Not enough context:**
```
I don't have enough context to create this document.
Could you share more about [missing element]?
```

**Ambiguous type:**
```
What type of document would you like?
- A) PRD (product requirements)
- B) TDD (technical design)
- C) FRD (functional requirements)
- D) Meeting notes
```
