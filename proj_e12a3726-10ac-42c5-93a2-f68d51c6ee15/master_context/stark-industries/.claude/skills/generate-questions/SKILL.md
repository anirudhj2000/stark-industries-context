---
name: generate-questions
description: Use when analyzing organizational context to identify knowledge gaps - scans entities/ directory for TBD values, missing required fields, and _conflict markers, generates questions as git-backed YAML artifacts in QA tracker structure
---

# Generate Questions Skill

**Purpose:** Analyze `entities/` directory and generate targeted questions for knowledge gaps and conflicts.

**Intelligence Level:** HIGH - This skill contains ALL the AI analysis logic

---

## When to Use

- Before project planning to surface undefined requirements
- After bulk entity imports via `org-context-population` to find conflicts
- When entities have low completeness scores
- Periodically to identify stale/outdated information

## When NOT to Use

- For processing raw sources (use `org-context-population` instead)
- For harvesting Q&A answers (use `harvest-answers`)
- When no `entities/` directory exists yet
- For single-entity validation (overkill - just read the entity)

---

## Key Principles

1. **Entities-only analysis** - Only scan `entities/` directory (not `sources/` or `artifacts/`)
2. **Schema-driven gaps** - Required fields defined in `entities/schemas/`
3. **Inline conflict markers** - Find `_conflict` markers created by `org-context-population`
4. **Filtering support** - Filter by `question_types` and `focus_areas`

---

## Quick Reference

### Gap Signals

| Signal | Priority | Example | Question Type |
|--------|----------|---------|---------------|
| TBD/null values | normal | `joined_date: "TBD"` | gap_analysis |
| Low completeness | normal | `metadata.completeness: "partial"` | gap_analysis |
| Missing required field | **high** | Schema requires `name`, entity missing it | gap_analysis |
| `_conflict` marker | varies | Field has two conflicting source values | conflict_resolution |

### TBD Values Detected

`"TBD"`, `"tbd"`, `null`, `""`, `"N/A"`, `"Unknown"`, `"TBC"`

### Focus Area Mapping

| Focus Area | Entity Types Scanned |
|------------|---------------------|
| `technical` | `system`, `process` (category: technical) |
| `business` | `product`, `competitor`, `investor`, `organization` |
| `people` | `person`, `team` |
| `operations` | `process` (category: operational) |
| `all` | Everything (default) |

### Context Type Resolution

**CRITICAL**: Resolve `artifact_dir` from `context_type` in payload before any file operations:

```python
context_type = payload.get('context_type', 'project')
project_id = payload['project_id']

if context_type == 'project':
    artifact_dir = f"project_workspaces/project_{project_id}/artifacts/art_qa_tracker_{project_id}"
else:
    artifact_dir = f"artifacts/art_qa_tracker_{project_id}"
```

All artifact paths should use `{artifact_dir}` prefix.

### Artifact Structure

```
{artifact_dir}/
├── type.meta.json              # Artifact metadata
└── questions/
    ├── qna_20251207_abc12.yaml # Individual question
    └── ...
```

---

## Decision Flowchart

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTITY FIELD ANALYSIS                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Field has value │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
      ┌───────────┐  ┌───────────┐  ┌───────────┐
      │ Has value │  │ TBD/null  │  │ _conflict │
      └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
            │              │              │
            ▼              ▼              ▼
      ┌───────────┐  ┌───────────┐  ┌───────────┐
      │   SKIP    │  │gap_analysis│  │ conflict_ │
      │(no action)│  │  (normal) │  │resolution │
      └───────────┘  └───────────┘  └───────────┘

┌─────────────────────────────────────────────────────────────┐
│                    REQUIRED FIELD CHECK                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Schema requires │
                    │   this field?   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
      ┌───────────────┐            ┌───────────────┐
      │ YES + Missing │            │  NO or EXISTS │
      └───────┬───────┘            └───────┬───────┘
              │                             │
              ▼                             ▼
      ┌───────────────┐            ┌───────────────┐
      │  gap_analysis │            │     SKIP      │
      │   (**HIGH**)  │            │  (no action)  │
      └───────────────┘            └───────────────┘
```

---

## Workflow

### Phase 0-3: Setup and Scanning

**Load existing artifacts, configuration, schemas, and scan entities.**

1. **Read manifest + payload** from the file paths passed as arguments (do NOT use hardcoded paths)
2. **Resolve artifact_dir** from `context_type` and `project_id` in payload
3. **Load existing questions** from `{artifact_dir}/questions/` for deduplication
3. **Load schemas** from `entities/schemas/*.yaml` for required field definitions
4. **Scan entities** filtered by `focus_areas` parameter

**Key functions:** See `implementation.py` for `load_existing_questions()`, `load_schemas()`, `should_scan_entity()`

**Schema file format:**

```yaml
# entities/schemas/person.yaml
entity_type: person
required_fields:
  - path: "name"
    description: "Full name of the person"
  - path: "profile.primary_role"
    description: "Current role/title"
optional_fields:
  - path: "background.education"
    skip_gap_questions: true  # Don't generate questions for this
```

---

### Phase 4: Find Gaps (if "gap_analysis" in question_types)

**Gap detection scans all entity files for three signals:**

1. **TBD/null values** - Fields with placeholder values → `normal` priority
2. **Low completeness** - `metadata.completeness` is partial/minimal/low → `normal` priority
3. **Missing required fields** - Required by schema but absent → **`high` priority**

**Key function:** See `implementation.py` for `find_gaps()`

---

### Phase 5: Find Conflicts (if "conflict_resolution" in question_types)

**Conflict markers are inline `_conflict` fields created by `org-context-population`:**

```yaml
profile:
  role: "CEO"
  _conflict:
    field: "profile.role"
    existing_value: "CTO"
    new_value: "CEO"
    source_id: "4bae0c5c-..."
    severity: "high"
```

**Key function:** See `implementation.py` for `find_conflicts()`, `find_conflict_markers()`

---

### Phase 6: Generate Questions (with Deduplication)

**Transform gaps and conflicts into questions, skipping duplicates.**

For each gap/conflict:
1. Check `is_duplicate()` using (entity_id, entity_type, field_path) key
2. Generate unique `ref_id` via `generate_question_ref_id()` → `qna_YYYYMMDD_xxxxx`
3. Create question dict and artifact dict

**Key function:** See `implementation.py` for `generate_questions()`, `generate_gap_question()`, `generate_conflict_question()`

**Question artifact structure:**

```yaml
id: qna_20251207_abc12
text: "What is the value for 'profile.joined_date'..."
question_type: gap_analysis
source:
  entity_id: vivek_gupta
  entity_type: person
  field_path: profile.joined_date
  gap_type: undefined_value
generated_at: "2025-12-07T16:57:00Z"
generated_by_job: job_123
thread: []
harvest_cursor: null
```

---

### Phase 6.5: Write QnA Artifacts

**Create artifact files (task runner handles git).**

1. **Ensure structure** - Create `{artifact_dir}/questions/` if missing
2. **Write type.meta.json** - Artifact metadata (if first time)
3. **Write individual YAMLs** - One file per question: `questions/{ref_id}.yaml`

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

**Key function:** See `implementation.py` for `ensure_qa_tracker_structure()`, `write_qna_artifacts()`

**Example `type.meta.json`:**

```json
{
  "artifact_type": "QA_TRACKER",
  "artifact_id": "art_qa_tracker_my-project",
  "project_id": "my-project",
  "org_id": "my-org",
  "created_at": "2025-12-07T16:57:00Z",
  "version": "1.0"
}
```

---

### Phase 7: Return Structured Output (CRITICAL)

**The Agent SDK uses structured output to receive your results directly.**

## MANDATORY EXECUTION ORDER - DO NOT SKIP

**You MUST execute these steps IN ORDER before returning JSON:**

1. **WRITE ARTIFACTS TO DISK** (Phase 6.5) - Use the Write tool to create:
   - `{artifact_dir}/type.meta.json`
   - `{artifact_dir}/questions/{ref_id}.yaml` for each question

2. **THEN return JSON** - After files are written

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

**FAILURE TO WRITE ARTIFACTS = SKILL FAILURE**

If you skip artifact creation and only return JSON, the skill has FAILED even if questions are generated. The artifacts are the primary storage - the task runner will commit them to git.

**Return this JSON structure as your final output:**

```json
{
  "questions": [
    {
      "text": "What is the value for 'profile.joined_date' in person 'vivek_gupta'? Currently set to 'TBD'.",
      "question_type": "gap_analysis",
      "priority": "normal",
      "context": {
        "gap_type": "undefined_value",
        "entity_id": "vivek_gupta",
        "entity_type": "person",
        "field": "profile.joined_date"
      },
      "suggested_assignees": [],
      "min_responses": 1,
      "agent_sdk_ref_id": "qna_20251206_abc12"
    }
  ],
  "files_written": [
    "{artifact_dir}/type.meta.json",
    "{artifact_dir}/questions/qna_20251206_abc12.yaml"
  ],
  "commit_message": "qna: create question artifacts for project {project_id}",
  "metadata": {
    "job_id": "job_456",
    "generated_at": "2025-12-05T10:00:00Z",
    "gaps_found": 5,
    "conflicts_found": 2,
    "questions_generated": 7,
    "focus_areas": ["all"],
    "question_types": ["gap_analysis", "conflict_resolution"]
  },
  "artifact_type": "QA_TRACKER",
  "file_path": "{artifact_dir}/type.meta.json",
  "display_name": "Generated 7 questions"
}
```

**CRITICAL - file_path requirements:**
- MUST be a FILE path, NOT a directory path
- MUST end with a file extension (`.json`, `.md`, `.png`, etc.)
- For QA_TRACKER: Always use `type.meta.json` NOT `questions/`
- WRONG: `{artifact_dir}/questions/` (directory!)
- CORRECT: `{artifact_dir}/type.meta.json` (file!)

**Required fields for each question:**
- `text` (string): The question text
- `question_type` (string): One of "gap_analysis", "conflict_resolution", "clarification", "factual", "opinion"
- `priority` (string): One of "high", "normal", "low"
- `agent_sdk_ref_id` (string): Unique ID in format `qna_YYYYMMDD_xxxxx`

**Optional fields:**
- `context` (object): Additional context about the question source
- `suggested_assignees` (array): User IDs to assign
- `min_responses` (integer): Minimum responses needed (default: 1)

**The Agent SDK handler will:**
1. Receive this structured output directly (no file reading)
2. POST the questions to Playbook API
3. Handle all HTTP communication

**You just need to return the JSON structure above as your final output.**

---

## Error Handling

**If analysis fails:**

```python
{
    "status": "error",
    "job_id": job_id,
    "error": error_message,
    "partial_results": {
        "questions_generated": partial_count,
        "entities_scanned": scanned_count
    }
}
```

**If schema files missing:**

- Log warning but continue
- Skip "missing required fields" check for entities without schemas
- Still check for TBD values and completeness

---

## Quality Standards

1. **Entities-only**: Never scan `sources/` or `artifacts/`
2. **Schema-driven**: Use `entities/schemas/` for required field definitions
3. **Evidence-based**: Include entity_id and field path in context
4. **Filtered**: Respect `question_types` and `focus_areas` parameters
5. **Prioritized**: Missing required fields are high priority

---

## Success Criteria

**ARTIFACT CREATION (MANDATORY - DO FIRST):**
- [ ] **Directory created**: `{artifact_dir}/questions/`
- [ ] **type.meta.json written** with artifact metadata
- [ ] **Individual YAMLs written**: `questions/{ref_id}.yaml` for each question
- [ ] **files_written** array includes all created files
- [ ] **commit_message** returned for task runner

**QUESTION GENERATION:**
- [ ] Only `entities/` directory scanned
- [ ] Gaps detected via three signals (TBD, completeness, required fields)
- [ ] Conflicts detected via `_conflict` inline markers
- [ ] Questions filtered by `question_types` and `focus_areas`

**FINAL OUTPUT:**
- [ ] Final response is valid JSON matching the structured output schema
- [ ] No HTTP calls made (Agent SDK handler does that)

---

## Smart Question Generation

**Principle:** Don't ask generic questions like "What additional information should be added?" Instead, identify what's specifically missing and explain why it matters.

**For incomplete entities:**

1. **Compare entity against schema** to find which optional fields are missing
2. **Generate specific questions** about each missing field
3. **Explain the value** of having that information

**Examples (use as guidance, not templates):**

| Bad (Generic) | Good (Smart) |
|---------------|--------------|
| "Person 'arnav' is incomplete. What should be added?" | "What companies did Arnav work at before Leap? This helps understand his industry background." |
| "Team 'engineering_team' needs more info." | "Who are the current members of the Engineering team besides the leadership? This helps understand team capacity." |
| "Product 'yocket' is partial." | "What is Yocket's pricing structure? The current value shows 'TBC'." |

**Key principles:**

- **Be specific** - Name the exact field/information that's missing
- **Explain the value** - Why would having this information help?
- **Use natural language** - Don't expose internal field names directly
- **Context matters** - A missing `joined_date` for a founder matters more than for a recent hire

**For TBD/undefined values:**

- Reference the specific field
- If there's an approximate/partial value (like "~₹3,00,000"), include it: "Currently shown as ~₹3,00,000..."
- Do NOT mention "TBC", "TBD", or "marked as" in the question text - just ask directly
- Frame the question around what decision/action is blocked by this gap

**Example:**
- Bad: "What is the pricing? Currently marked as 'TBC'."
- Good: "What is Yocket's exact pricing structure? Are there tiered packages or payment plans?"
- Good (with partial data): "What is Yocket's exact pricing? Currently shown as ~₹3,00,000 - are there tiers?"

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| **Skipping artifact creation entirely** | **CRITICAL**: You MUST write files to disk before returning JSON |
| Only returning JSON without writing files | Write artifacts FIRST, return JSON with files_written SECOND |
| Running git add/commit/push | **NEVER** - task runner handles all git operations |
| Scanning `sources/` or `artifacts/` directories | Only scan `entities/` |
| Generic questions ("Person X needs more info") | Use Smart Question Generation patterns - be specific |
| Forgetting to check for duplicates | Load existing artifacts in Phase 0 before generating |
| Making HTTP calls to Playbook | Never - return structured JSON, handler does HTTP |
| Using TBD/TBC in question text | Ask directly without mentioning placeholder values |

---

## Notes

- **This skill has ALL the intelligence** - Gap detection, conflict detection, question generation
- **Artifact creation** - Write individual question YAMLs to `{artifact_dir}/questions/`
- **Structured output** - Your final JSON response is automatically extracted by the SDK
- **Agent SDK handles HTTP** - POSTs questions directly to Playbook from the structured output
- **Playbook is just orchestration** - Triggers, receives results
- **Assignee suggestion** - Deferred (returns empty array for now)
- **Git operations** - Task runner handles all git operations using `files_written` and `commit_message` from your output
