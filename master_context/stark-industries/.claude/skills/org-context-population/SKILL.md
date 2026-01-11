---
name: org-context-population
description: Extract entities from source documents into entities/ structure. Use when processing meetings, SOPs, company overviews, financial reports, org charts, or technical docs after source extraction (structured.json exists). NOT for raw source processing (use source extraction first), single field updates (edit directly), or pure code docs without organizational context.
---

# Organizational Context Population

Extract organizational knowledge from processed source documents into the entity structure.

**You are the intelligence.** Read documents holistically - don't just pattern-match keywords.

---

## Core Rules

1. **NEVER create directories** - Only ontology-setup creates structure
2. **NEVER create new files** - Only update existing files or append to existing list files
3. **NEVER create person entities** - Can update existing person files, but new people always go to triage for user approval
4. **New entities → triage** - If no existing file matches, route to `_triage.yaml`
5. **Ambiguous references → triage** - Partial names like "Smith" (without first name) MUST be triaged with `candidates` list

---

## Workflow

1. **Classify document** - Understand what type of document this is
2. **Discover existing files** - Scan `entities/` for existing files (not just directories)
3. **Extract entities** - Identify entities matching existing files
4. **Merge or append** - Update existing files, append to list files
5. **Route new entities** - Send unplaceable items to `_triage.yaml`
6. **Return output** - Return structured output (no file creation)

---

## Step 1: Classify Document

Read the source and determine what type of document it is. This guides extraction focus.

| Source Type | What to Look For | Updates |
|-------------|------------------|---------|
| `meeting` | Decisions, action items, attendees, concerns, terminology | ADR files, person files |
| `company_overview` | Org structure, leadership, products, financials, competitors | organization files, competitors.yaml, vendors.yaml |
| `financial_report` | Revenue, metrics, funding, strategic goals | organization files |
| `technical_doc` | Systems, architecture, technical processes | system files, process files |
| `operational_doc` | Workflows, SOPs, procedures, process owners | process files, person files |
| `org_chart` | Teams, reporting structure, roles | team files, person files |
| `product_doc` | Products, pricing, features, roadmap | product files, system files |

**If unclear:** Flag for manual review rather than guessing.

---

## Step 2: Discover Existing Files

Run the scan script to get a structured index of existing files:

```bash
python {skill_dir}/scripts/scan_entities.py entities/ --pretty
```

Where `{skill_dir}` is this skill's directory path. The script scans the `entities/` directory in the current workspace.

**Output:**
```json
{
  "success": true,
  "entity_files": ["organization/overview.yaml", "person/john_smith/overview.yaml"],
  "list_files": ["organization/vendors.yaml", "organization/competitors.yaml"],
  "triage_files": ["_triage.yaml", "person/_triage.yaml"],
  "directories": ["organization", "person", "person/john_smith"]
}
```

Use this index to determine:
- `entity_files` → can be updated/merged
- `list_files` → can append entries to
- `triage_files` → route new entities here

**Only update files that already exist.** If a file doesn't exist, route to triage.

---

## Step 3: Extract Entities

Read the document and extract entities.

**For each entity found:**
- Check if a matching file already exists (use scan output)
- If yes → prepare merge/update
- If no → prepare triage entry
- If person and no existing file → **always triage** (never create person files)
- If ambiguous reference (e.g., "Smith" without first name) → **always triage** with `candidates` list

**For YAML structures:** See `references/yaml_schemas.md` for entity files, list files, and required metadata fields.

**Principles:**
- Extract what's actually in the document
- Use simple, flat structure
- Include `_source_id`, `_source_name`, `_sources` (with id+name), and `_last_updated` for traceability

---

## Step 4: Merge or Append

**For existing entity files (update):**

1. Normalize name (`"Dr. John Smith"` → `john_smith`)
2. Find matching file from scan output
3. Merge fields according to rules in `references/yaml_schemas.md`

**For existing list files (append):**

1. Check if entity already exists in the list (by id or normalized name)
2. If exists → merge the entry
3. If new → append to the list

**Conflicts:** When values disagree and it's not a clear enhancement, add `_conflict` marker (see `references/yaml_schemas.md` for format). This allows `generate-questions` skill to create resolution questions.

---

## Step 5: Route New Entities to Triage

**When to triage:**

| Situation | Action |
|-----------|--------|
| No matching file exists | → `_triage.yaml` |
| New person (even if structure exists) | → `_triage.yaml` (user must approve person creation) |
| Ambiguous match (multiple candidates) | → `_triage.yaml` |
| Major conflicts (core identity disagrees) | → `_triage.yaml` |

**Routing logic:**

1. Check scan output for matching file
2. If file exists → update/merge
3. If no file exists OR new person → find nearest `_triage.yaml` and append

**For triage file structure:** See `references/yaml_schemas.md`

**Log for visibility:**
```
INFO: Updated entities/organization/vendors.yaml (appended acme_corp)
INFO: Updated entities/person/john_smith/overview.yaml (merged role)
INFO: Triaged 'new person Jane Doe' → entities/_triage.yaml (new person requires approval)
INFO: Triaged ambiguous 'Smith' → entities/_triage.yaml
```

---

## Step 6: Return Output

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

**Return structured output:**
```json
{
  "status": "success",
  "source_id": "{source_id}",
  "source_type": "{detected_type}",
  "files_updated": [
    "entities/organization/vendors.yaml",
    "entities/person/john_smith/overview.yaml"
  ],
  "commit_message": "feat(entities): Populate from {source_id}",
  "entities_updated": ["acme_corp", "john_smith"],
  "entities_triaged": ["jane_doe", "ambiguous_smith"],
  "triaged_count": 2,
  "conflicts": ["john_smith.role"]
}
```

---

## Examples

| Scenario | Input | Action |
|----------|-------|--------|
| Company overview with vendors | Pitch deck mentions "Acme Cloud" | Append to `vendors.yaml` if exists, else triage |
| Meeting with role change | Transcript says "John is now VP" | Update existing `john_smith/overview.yaml`, track `_previous_roles` |
| New person mentioned | "Sarah Chen presented..." | **Always triage** - new people require user approval |
| Ambiguous reference | "Smith will lead..." | Triage with `candidates: [john_smith, jane_smith]` |
| Existing person, new info | Meeting mentions John's new project | Update existing file, append to `_sources` |

**For detailed YAML examples:** See `references/yaml_schemas.md`

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Creating new files | Only update existing files; triage new entities |
| Creating person files | **NEVER** - always triage new people for user approval |
| Creating directories | NEVER; only ontology-setup does this |
| Overwriting without merge | Always merge with existing content |
| Missing source traceability | Include `_source_id` in every update |
| Ignoring ambiguous references | "Smith will lead..." → triage with `candidates` list |
| Ignoring conflicts | Add `_conflict` markers for generate-questions |
| Discarding new entities | Route to `_triage.yaml` instead of dropping |
