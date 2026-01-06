---
name: org-context-population
description: Extract entities from source documents into entities/ structure. Use when processing meetings, SOPs, company overviews, financial reports, org charts, or technical docs after source extraction (structured.json exists). NOT for raw source processing (use source extraction first), single field updates (edit directly), or pure code docs without organizational context.
---

# Organizational Context Population

Extract organizational knowledge from processed source documents into the entity structure.

**You are the intelligence.** Read documents holistically - don't just pattern-match keywords.

---

## Workflow

1. **Classify document** - Understand what type of document this is
2. **Discover entity structure** - Scan `entities/` for existing types, entities, and `_triage.yaml` locations
3. **Extract entities** - Identify entities matching existing types
4. **Merge with existing** - Prevent duplicates, handle conflicts
5. **Route unplaceable items** - Send ambiguous/unknown items to `_triage.yaml`
6. **Write and return** - Create/update files, return structured output

---

## Step 1: Classify Document

Read the source and determine what type of document it is. This guides extraction focus.

| Source Type | What to Look For | Creates/Updates |
|-------------|------------------|-----------------|
| `meeting` | Decisions, action items, attendees, concerns, terminology | ADR, person |
| `company_overview` | Org structure, leadership, products, financials, competitors | organization, person, team, product, competitor |
| `financial_report` | Revenue, metrics, funding, strategic goals | organization |
| `technical_doc` | Systems, architecture, technical processes | system, process, adr |
| `operational_doc` | Workflows, SOPs, procedures, process owners | process, person, team |
| `org_chart` | Teams, reporting structure, roles | team, person |
| `product_doc` | Products, pricing, features, roadmap | product, system, process |

**If unclear:** Flag for manual review rather than guessing.

---

## Step 2: Discover Entity Structure

Scan `entities/` to understand what exists:

```bash
ls entities/
# Example output: organization/ person/ team/ product/ system/ adr/
```

Build an index of existing entities for deduplication:
- Entity ID
- Normalized name (for matching)
- Type directory

**Only extract entities that fit existing type directories.** If document mentions something that doesn't fit (e.g., "vendor" but no `entities/vendor/`), flag it for review.

---

## Step 3: Extract Entities

Read the document and extract entities that match existing types.

**For each entity found:**
- Determine which existing type it belongs to
- Extract relevant information as flat YAML
- Use natural field names based on content

**Entity file structure:**
```yaml
id: john_smith
name: John Smith
role: CTO
team: leadership
email: john@company.com
_source_id: src_meeting_123
_sources: [src_onboarding_001, src_meeting_123]
_last_updated: "2025-12-27T10:00:00Z"
```

**Principles:**
- Extract what's actually in the document
- Use simple, flat structure
- Include `_source_id` (latest), `_sources` (all), and `_last_updated` for traceability

---

## Step 4: Merge with Existing

Before writing, check if entity already exists.

**Resolution:**
1. Normalize name (`"Dr. John Smith"` → `john_smith`)
2. Check for existing entity with same normalized name in that type
3. If match → merge; if no match → create new; if ambiguous → flag

**Merge rules:**

| Field Type | Behavior |
|------------|----------|
| Identity (name, id) | Keep existing unless new is more specific |
| Current state (role, status) | Most recent wins, track previous |
| Lists (skills, projects) | Append and deduplicate |
| Nested objects | Recursive merge |
| `_sources` | Append new source_id to list |

**Conflicts:** When values disagree and it's not an enhancement, add `_conflict` marker:

```yaml
role: Senior Engineer
_conflict:
  field: role
  existing_value: Senior Engineer
  new_value: Staff Engineer
  source_id: src_org_chart_2025
```

This allows generate-questions skill to create resolution questions.

---

## Step 5: Write and Return

**Write entities:**
```
entities/{type}/{entity_id}/context.yaml
```

Special case - organization files go directly in `entities/organization/`:
```
entities/organization/overview.yaml
entities/organization/vocabulary.yaml
```

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

**Return structured output:**
```json
{
  "status": "success",
  "source_id": "{source_id}",
  "source_type": "{detected_type}",
  "files_written": [
    "entities/person/john_smith/context.yaml",
    "entities/team/engineering/context.yaml"
  ],
  "commit_message": "feat(entities): Populate from {source_id}",
  "entities_created": ["john_smith", "engineering_team"],
  "entities_updated": ["jane_doe"],
  "triaged_count": 2,
  "conflicts": ["john_smith.role"]
}
```

---

## Examples

### Meeting → ADR + Person Updates

**Input:** Meeting transcript with decisions

**Creates:**
```yaml
# entities/adr/quarterly_review_2025_q4/context.yaml
id: quarterly_review_2025_q4
title: Q4 Quarterly Review
date: "2025-12-15"
attendees: [john_smith, jane_doe]
decisions:
  - Migrate to new platform by Q1
  - Hire 3 engineers
actions:
  - owner: john_smith
    task: Draft migration plan
    due: "2025-12-30"
_source_id: src_meeting_456
```

**Updates:**
```yaml
# entities/person/john_smith/context.yaml (merged)
decisions_made:
  - quarterly_review_2025_q4
actions_assigned:
  - quarterly_review_2025_q4/migration_plan
_source_id: src_meeting_456
_sources: [src_onboarding_001, src_meeting_456]
```

### Company Overview → Multiple Entities

**Input:** Company pitch deck

**Creates/updates:** organization files, person entities for leadership, product entities, competitor entities.

---

## Triage Routing

When information can't be placed in an existing folder, route it to `_triage.yaml` at the appropriate level. **Don't lose information** — triage captures what doesn't fit current structure.

**Triage situations:**

1. **No matching folder:** Information relates to an entity but no subfolder fits
2. **Unrecognized entity type:** Document mentions entities that don't fit existing directories
3. **Ambiguous match:** Multiple existing entities could match
4. **Major conflicts:** Core identity fields disagree
5. **Partial information:** Not enough context to create a proper entity

**Routing logic:**

```
1. CLASSIFY: What type of information is this? (person, team, project, system, etc.)

2. FIND ENTITY: Which entity does this relate to most?
   - Is it about a specific person? → entities/person/{slug}/
   - Is it about a team? → entities/team/{slug}/
   - Is it organization-wide? → entities/organization/

3. TRY TO PLACE: Look at folders within that entity
   - Does the entity have a folder where this fits? (adrs/, systems/, projects/)
   - If yes → place it there
   - If no → go to step 4

4. TRIAGE: Put in that entity's _triage.yaml
   - If _triage.yaml exists → append to inbox
   - If _triage.yaml doesn't exist → CREATE it, then append
```

**Examples:**

| Information | Belongs To | Try To Place | Result |
|-------------|------------|--------------|--------|
| "New API architecture decision" | `entities/team/platform/` | `adrs/` folder exists | Place in `adrs/api_architecture.yaml` |
| "Vendor contract with Acme" | `entities/organization/` | No `vendors/` folder | Create/append to `entities/organization/_triage.yaml` |
| "John's certification expired" | `entities/person/john_smith/` | No `certifications/` folder | Create/append to `entities/person/john_smith/_triage.yaml` |
| "Unknown entity type 'supplier'" | Can't determine | No entity matches | Create/append to `entities/_triage.yaml` |

**Triage file structure:**
```yaml
inbox:
  - item: "Vendor contract with Acme Corp"
    source: "src_meeting_456"
    added_date: "2025-12-27T10:00:00Z"
    suggested_destination: "Consider creating vendors/ folder or add to competitors/"
    context:
      attempted_placement: "No vendors/ folder exists"
      raw_text: "Our vendor Acme Corp provides..."
  - item: "Person 'Smith' mentioned - ambiguous match"
    source: "src_org_chart_2025"
    added_date: "2025-12-27T10:00:00Z"
    suggested_destination: "Clarify which Smith via generate-questions"
    context:
      candidates: ["john_smith", "jane_smith"]
      raw_text: "Smith will lead the project..."
```

**Creating triage when needed:**

```python
# Pseudocode
def place_or_triage(info, entity_path):
    # 1. Check what folders exist in this entity
    existing_folders = list_dirs(entity_path)

    # 2. Does info fit any existing folder?
    target_folder = find_matching_folder(info, existing_folders)

    if target_folder:
        # Place it
        write_to(f"{entity_path}/{target_folder}/{info.slug}.yaml", info)
    else:
        # Triage it
        triage_path = f"{entity_path}/_triage.yaml"
        if not exists(triage_path):
            create_file(triage_path, {"inbox": []})
        append_to_inbox(triage_path, info)
```

**Log for visibility:**
```
INFO: Placed 'API architecture decision' → entities/team/platform/adrs/
INFO: Triaged 'vendor Acme Corp' → entities/organization/_triage.yaml (created)
INFO: Triaged ambiguous 'Smith' → entities/person/_triage.yaml
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Creating new type directories | Only use existing `entities/{type}/` directories |
| Overwriting without merge | Always check for existing entity first |
| Missing source traceability | Include `_source_id` in every entity |
| Inventing structure | Extract what's in the document, don't embellish |
| Ignoring conflicts | Add `_conflict` markers for generate-questions |
| Discarding unplaceable items | Route to `_triage.yaml` instead of dropping |
| Losing context in triage | Include `context` with raw_text and candidates for resolution |
