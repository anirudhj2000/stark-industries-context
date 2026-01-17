---
name: ontology-setup
description: Infer organizational hierarchy and write ONTOLOGY_DRAFT JSON artifact. Use when (1) setting up new organization context, (2) user asks about org structure, (3) initializing entity hierarchies, or (4) user mentions "ontology", "org structure", "hierarchy", "departments", "teams", "company structure", "org chart", "divisions", or "business units". Supports Functional, Divisional, Product-Centric, Matrix, and Flat structures. Also supports "infer_files" mode for single-entity file inference.
---

# Ontology Setup

Infer organizational hierarchy through collaborative dialogue and create an ONTOLOGY_DRAFT artifact.

---

## Mode: infer_files (Single Entity File Inference)

When invoked with `mode: infer_files`, skip the full ontology workflow and return only the file list for a single entity.

### Input Format

```json
{
  "mode": "infer_files",
  "entity": {
    "name": "backend",
    "entity_type": "team",
    "order": 2
  }
}
```

### Process

1. **Determine base files from order level:**
   - `order: 0` (organization) → `[overview.yaml, brand.yaml, strategy.yaml, governance.yaml, _triage.yaml, competitors.yaml, vendors.yaml, partners.yaml, investors.yaml]`
   - `order: 1` (department/function/lob) → `[overview.yaml, _triage.yaml]`
   - `order: 2+` (team) → `[overview.yaml, _triage.yaml]`

2. **Add function-specific files** (if `entity_type` is department/function OR `order == 1`):
   - Look up entity name in **Function Config Lookup Table** below
   - Add those files to the list

3. **Add team-specific files** (if `entity_type` is team OR `order >= 2`):
   - Look up entity name in **Team Config Lookup Table** below
   - Add those files to the list

### Function Config Lookup Table

| Function Name | Files |
|---------------|-------|
| `engineering` | `tech_stack.yaml, system_architecture.yaml, api_integrations.yaml` |
| `product` | `roadmap.yaml, metrics.yaml` |
| `design` | `design_system.yaml, ux_research.yaml` |
| `data` | `data_models.yaml, data_pipelines.yaml, data_catalog.yaml` |
| `finance` | `financials.yaml, budget.yaml, forecasts.yaml` |
| `sales` | `pipeline.yaml, territories.yaml, playbooks.yaml` |
| `marketing` | `channels.yaml, campaigns.yaml, brand_assets.yaml` |
| `operations` | `processes.yaml, slas.yaml, runbooks.yaml` |
| `people` | `hiring_plan.yaml, programs.yaml, org_chart.yaml` |
| `legal` | `contracts.yaml, intellectual_property.yaml` |
| `it` | `infrastructure.yaml, vendor_systems.yaml` |
| `security` | `policies.yaml, incidents.yaml, access_controls.yaml` |
| `compliance` | `regulations.yaml, licenses.yaml` |
| `risk` | `risk_framework.yaml, limits.yaml` |
| `customer-success` | `health_metrics.yaml, slas.yaml` |
| `underwriting` | `guidelines.yaml, risk_appetite.yaml, pricing.yaml` |
| `claims` | `workflows.yaml, reserves.yaml, fraud.yaml` |
| `actuarial` | `models.yaml, assumptions.yaml` |
| `fulfillment` | `warehouse_ops.yaml, shipping.yaml, returns.yaml` |
| `merchandising` | `assortment.yaml, pricing.yaml, promotions.yaml` |
| `supply-chain` | `suppliers.yaml, inventory.yaml, logistics.yaml` |
| `manufacturing-quality` | `standards.yaml, inspections.yaml, certifications.yaml` |
| `clinical` | `protocols.yaml, workflows.yaml` |
| `revenue-cycle` | `billing.yaml, collections.yaml` |
| `technology` | `systems.yaml, integrations.yaml` |

### Team Config Lookup Table

| Team Name | Files |
|-----------|-------|
| `backend` | `tech_stack.yaml, system_architecture.yaml, api_integrations.yaml` |
| `frontend` | `tech_stack.yaml, design_tokens.yaml, component_library.yaml` |
| `mobile` | `tech_stack.yaml, app_releases.yaml` |
| `devops` | `infrastructure.yaml, ci_cd.yaml, monitoring.yaml` |
| `platform` | `tech_stack.yaml, system_architecture.yaml` |
| `sre` | `runbooks.yaml, slas.yaml, incidents.yaml` |
| `infra` | `infrastructure.yaml, ci_cd.yaml` |
| `design` | `design_system.yaml, ux_research.yaml` |
| `ux` | `design_system.yaml, ux_research.yaml` |
| `data` | `data_models.yaml, data_pipelines.yaml` |
| `analytics` | `dashboards.yaml, metrics.yaml` |
| `data-engineering` | `data_pipelines.yaml, data_catalog.yaml` |
| `product` | `roadmap.yaml, metrics.yaml` |
| `qa` | `test_strategy.yaml, test_cases.yaml` |
| `quality` | `test_strategy.yaml, test_cases.yaml` |

### Output Format

Return ONLY a JSON object with the files array:

```json
{
  "files": ["overview.yaml", "_triage.yaml", "tech_stack.yaml", "system_architecture.yaml", "api_integrations.yaml"]
}
```

### Examples

| Entity | Order | Type | Files |
|--------|-------|------|-------|
| `engineering` | 1 | department | `[overview.yaml, _triage.yaml, tech_stack.yaml, system_architecture.yaml, api_integrations.yaml]` |
| `backend` | 2 | team | `[overview.yaml, _triage.yaml, tech_stack.yaml, system_architecture.yaml, api_integrations.yaml]` |
| `frontend` | 2 | team | `[overview.yaml, _triage.yaml, tech_stack.yaml, design_tokens.yaml, component_library.yaml]` |
| `sales` | 1 | department | `[overview.yaml, _triage.yaml, pipeline.yaml, territories.yaml, playbooks.yaml]` |
| `custom-team` | 2 | team | `[overview.yaml, _triage.yaml]` (no special config) |

### Important

- **No user interaction** in this mode - just return files based on lookup tables
- **Normalize entity name** to lowercase with hyphens before lookup
- **Deduplicate** the final file list
- **Sort alphabetically** for consistency
- **If entity not in lookup tables**, use only base files for that order level

---

---

## CRITICAL: CHECK LOCK STATUS BEFORE GENERATION

**Before generating any ontology structure, you MUST check if manual editing is in progress.**

### Lock Check Process

1. **Call the lock status API** to check `edit_mode`
2. **If `edit_mode == "manual"`** → STOP and inform the user:
   ```
   Cannot generate ontology structure while manual editing is in progress.

   Please either:
   - Apply your manual changes first, or
   - Discard manual changes to allow chat generation
   ```
3. **If `edit_mode == "none"` or `edit_mode == "chat_pending"`** → Proceed with generation

### Why This Matters

The ontology system uses bidirectional locking:
- **Manual mode** blocks chat generation (user is actively editing in UI)
- **Chat pending mode** blocks manual editing (AI draft awaiting review)

This prevents conflicts where chat-generated structures overwrite manual work.

---

## OUTPUT IS PREVIEW-ONLY UNTIL USER ACCEPTS

**Important**: When this skill generates `ontology_draft.json`, it does NOT immediately apply to the database.

### What Happens After Generation

1. Skill writes `artifacts/ontology_draft/ontology_draft.json`
2. System detects the file and shows a **preview dialog** to the user
3. User reviews the structure visually
4. User clicks **Accept** to import the draft into the database
5. User clicks **Apply** to commit changes to git (folder structures + ontology.yaml)

**Until the user accepts**, the draft is just a preview. If they cancel, the draft is discarded.

### Implications for the Skill

- Do NOT tell users "I've created your org structure" - say "I've prepared a draft for your review"
- Do NOT mention database changes - the draft hasn't been imported yet
- DO mention they'll see a preview where they can accept or cancel

---

## CRITICAL: READ TEMPLATES.YAML FIRST

**Before doing ANYTHING else, you MUST read `references/templates.yaml`.**

This is non-negotiable. Do not:
- Start asking questions before reading the template
- Make up your own JSON structure
- Guess at file names, paths, or default teams
- Generate ANY output without first loading the template

```
MANDATORY FIRST ACTION:
Read references/templates.yaml → Extract and internalize:
  1. json_schema (the exact structure to follow)
  2. structures.<type> (hierarchy levels, paths, files, folders)
  3. function_config (files AND default_teams for EVERY function)
  4. team_config (extra files for specific team names)
  5. industry_functions (for divisional structures)
```

### Anti-Patterns (DO NOT DO)

| Wrong | Right |
|-------|-------|
| Making up file names | Use `function_config.<func>.files` |
| Omitting default_teams | Always include `function_config.<func>.default_teams` |
| Inventing JSON structure | Follow `json_schema` exactly |
| Generating incrementally | Build complete JSON in ONE pass |
| Asking user for function files | Infer from templates.yaml |

---

## Output Format

**Always plain conversational text.** No JSON wrappers.

```
Let's set up your organization structure! How is your company organized?

1. Functional - Departments serve the whole company (Engineering, Finance, Sales...)
2. Divisional - Each business unit/LOB has its own functions
3. Product-Centric (Pods) - Cross-functional teams organized around products
4. Matrix / Hybrid - Functions + Business Units with shared resources
5. Flat - Minimal hierarchy, self-organizing teams
```

**At completion**: Describe the draft and mention the preview dialog.
```
I've prepared a draft organizational structure for your review. It's a Functional structure with 4 departments and 6 teams total.

You should see a preview dialog where you can review the structure visually. Click Accept to import it, or Cancel to discard.
```

## Output Path

**EXACT PATH (no variations):** `artifacts/ontology_draft/ontology_draft.json`

This is a **singleton** - one draft per organization. The skill always writes to the same path, overwriting any previous draft. The system handles versioning automatically.

**Note**: The system detects this file and creates/updates the ONTOLOGY_DRAFT artifact in Playbook. Each update increments the version number in the artifact metadata.

## Workflow

```
0. CHECK LOCK STATUS (mandatory - block if edit_mode == "manual")
1. READ references/templates.yaml (mandatory, no exceptions)
2. Ask org structure type (1 question)
3. Ask follow-up based on type (1 question)
4. [If uncertain] Ask one clarifying question
5. Show inferred structure → User confirms or modifies
   - FOR MODIFICATIONS: If user requests entity deletion, run safety check first
   - See "Entity Deletion Safety Check" section below
6. Build COMPLETE JSON using templates.yaml → Write artifact
   - Include display_name for EVERY node (auto-generated from name)
7. Tell user about preview dialog (Accept/Cancel)
```

### Step 0: Check Lock Status (MANDATORY)

**This step happens BEFORE any user interaction or template loading.**

```python
# Pseudo-code for lock check:
lock_status = call_api("GET /api/v1/organizations/{org_id}/ontology/lock-status/")

if lock_status.edit_mode == "manual":
    # STOP - cannot generate while manual editing in progress
    respond("""
    Cannot generate ontology structure while manual editing is in progress.

    Please either:
    - Apply your manual changes first, or
    - Discard manual changes to allow chat generation
    """)
    return  # Do not proceed

# If edit_mode is "none" or "chat_pending", continue to Step 0b
```

### Step 0b: Load Templates (MANDATORY)

**This step happens BEFORE any user interaction.**

```python
# Pseudo-code for what you must do:
templates = read("references/templates.yaml")

# Cache these for later use:
json_schema = templates.json_schema
structures = templates.structures
function_config = templates.function_config
team_config = templates.team_config  # Extra files for specific team names
industry_functions = templates.industry_functions
```

You cannot proceed to Step 1 without completing Step 0.

## Step 1: Organization Structure Type

```
How is your organization structured?

1. Functional - Departments serve the whole company (Engineering, Finance, Sales...)
2. Divisional - Each business unit/LOB has its own functions
3. Product-Centric (Pods) - Cross-functional teams organized around products
4. Matrix / Hybrid - Functions + Business Units with shared resources
5. Flat - Minimal hierarchy, self-organizing teams

Enter 1-5:
```

## Step 2: Follow-up Based on Structure

**One question only:**

| Structure | Question | Example Response |
|-----------|----------|------------------|
| Functional | What departments exist? | engineering, product, sales, finance |
| Divisional | What LOBs/divisions exist? | consumer, enterprise, international |
| Product-Centric | What products/pods exist? | checkout, invoicing, reporting |
| Matrix | Functions AND business units? | functions: eng, product \| units: consumer, enterprise |
| Flat | What teams exist? | platform, growth, ops |

## Step 3: Clarify if Uncertain

Skip if confident. Ask **one** question only when:

| Uncertainty | Ask |
|-------------|-----|
| Unknown industry (for divisional) | "What industry? (tech/fintech/retail/healthcare/other)" |
| Non-standard function name | "Does [X] have sub-teams? Which?" |
| Ambiguous product functions | "What functions does [product] have?" |

**Rules:** Prefer inference over asking. If user says "skip", use defaults from `references/templates.yaml`.

## Step 4: Show Inferred Structure

Load patterns from `references/templates.yaml` and display a tree:

```
Organization
│
└── [Top Level: Products/Departments/LOBs/Teams]
    ├── entity-name
    │   └── [Children: Functions/Teams]
    │       ├── child-1
    │       └── child-2
    └── entity-name-2
        └── ...

Summary: X entities × Y children = Z total
```

Ask: **Confirm? (or describe changes)**

## Step 5: Completion

1. Create folder: `artifacts/ontology_draft/` (if it doesn't exist)
2. Build COMPLETE `ontology_draft.json` in ONE pass (see detailed instructions below)
3. Write file to: `artifacts/ontology_draft/ontology_draft.json` (overwrites any existing draft)
4. Tell the user a draft has been prepared and they'll see a preview dialog
5. Remind them to click Accept to import, or Cancel to discard

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

### ontology_draft.json Schema

**You MUST build the complete JSON in a single pass. No iterations. No "I'll add that later."**

#### Build Process (follow exactly):

```
1. Start with structure_type and organization node (order: 0, display_name: "Organization")
   - NORMALIZE all user-provided names to slug format (see name_format in templates.yaml)
   - Slug rules: lowercase, replace spaces/underscores with hyphens, alphanumeric + hyphens only
2. For each user-provided entity (product/department/LOB/team):
   a. Create node with name, display_name, type, order, children[], _meta
   b. Generate display_name from name (see display_name_rules in templates.yaml)
   c. Get ORDER from structures.<type>.levels[].level (0, 1, 2, 3...)
   d. Get path from structures.<type>.levels[].path
   e. Get base files from structures.<type>.levels[].files
   f. Get folders from structures.<type>.levels[].folders
3. For each function in the entity:
   a. Look up function_config.<function_name>
   b. ADD function_config.<function>.files to _meta.files
   c. ADD function_config.<function>.default_teams as children
   d. Each team child also needs proper _meta with path, files, AND display_name
4. For each team (flat structure OR team under function):
   a. Look up team_config.<team_name>
   b. If found, ADD team_config.<team>.files to _meta.files
   c. This adds domain-specific files (e.g., backend gets tech_stack.yaml)
   d. Generate display_name for the team node
5. Verify completeness before writing
```

#### Display Name Generation

For every node, generate `display_name` from `name` using these rules:

1. Replace underscores `_` and hyphens `-` with spaces
2. Capitalize first letter of each word (Title Case)
3. Preserve common acronyms: IT, HR, QA, SRE, API, CTO, CEO, CFO, COO, VP, SVP, EVP, LOB, SMB

**Examples:**
- `"engineering"` → `"Engineering"`
- `"data-engineering"` → `"Data Engineering"`
- `"customer-success"` → `"Customer Success"`
- `"it"` → `"IT"`
- `"sre"` → `"SRE"`
- `"team-1"` → `"Team 1"`

**Apply to EVERY node** including organization, departments, teams, LOBs, products, functions.

#### Example: Product-Centric with Engineering Function

```yaml
# From templates.yaml:
structures.product_centric.default_functions: [engineering, product, design, data]
function_config.engineering:
  files: [tech_stack.yaml, system_architecture.yaml, api_integrations.yaml]
  default_teams: [frontend, backend]
```

This means EVERY engineering function node MUST have:
- `_meta.files`: [...base files, tech_stack.yaml, system_architecture.yaml, api_integrations.yaml]
- `children`: [frontend team node, backend team node]

#### Example: Teams with team_config

```yaml
# From templates.yaml:
team_config.backend:
  files: [tech_stack.yaml, system_architecture.yaml, api_integrations.yaml]

team_config.frontend:
  files: [tech_stack.yaml, design_tokens.yaml, component_library.yaml]
```

This means:
- "backend" team → `_meta.files`: [overview.yaml, _triage.yaml, tech_stack.yaml, system_architecture.yaml, api_integrations.yaml]
- "frontend" team → `_meta.files`: [overview.yaml, _triage.yaml, tech_stack.yaml, design_tokens.yaml, component_library.yaml]
- "founders" team (not in team_config) → `_meta.files`: [overview.yaml, _triage.yaml]

#### Building the `levels` Array

**REQUIRED:** The output MUST include a `levels` array with path patterns for each entity type.

1. Read `structures.<type>.levels` from templates.yaml
2. For each level, extract:
   - `entity_type`: from `levels[].entity_type`
   - `order`: from `levels[].level`
   - `path_pattern`: from `levels[].path`
3. Include ALL levels for the chosen structure type

**Example for product_centric:**
```json
"levels": [
  {"entity_type": "organization", "order": 0, "path_pattern": "entities/organization"},
  {"entity_type": "product", "order": 1, "path_pattern": "entities/product/{name}"},
  {"entity_type": "function", "order": 2, "path_pattern": "entities/product/{parent}/functions/{name}"},
  {"entity_type": "team", "order": 3, "path_pattern": "entities/product/{grandparent}/functions/{parent}/teams/{name}"}
]
```

#### Verification Checklist (before writing):

- [ ] **`levels` array is present** with all entity types and path_patterns
- [ ] Every node has a `display_name` field (auto-generated from name)
- [ ] Every node has an `order` field matching its level depth (0, 1, 2, 3...)
- [ ] Every function has files from `function_config.<func>.files`
- [ ] Every function has children from `function_config.<func>.default_teams`
- [ ] Every team has files from `team_config.<team>.files` (if exists)
- [ ] Every team child has proper `_meta` with path and files
- [ ] No empty arrays where defaults exist
- [ ] All paths follow `structures.<type>.levels[].path` pattern

```json
{
  "structure_type": "<type>",
  "levels": [
    {"entity_type": "organization", "order": 0, "path_pattern": "entities/organization"},
    {"entity_type": "product", "order": 1, "path_pattern": "entities/product/{name}"},
    {"entity_type": "function", "order": 2, "path_pattern": "entities/product/{parent}/functions/{name}"},
    {"entity_type": "team", "order": 3, "path_pattern": "entities/product/{grandparent}/functions/{parent}/teams/{name}"}
  ],
  "organization": {
    "name": "organization",
    "display_name": "Organization",
    "type": "organization",
    "order": 0,
    "children": [...],
    "_meta": { "path": "...", "files": [...], "folders": [...] }
  }
}
```

**IMPORTANT: The `levels` array must include all entity types with their path patterns from `structures.<type>.levels[].path`.**

**IMPORTANT: Every node MUST include an `order` field indicating its depth in the hierarchy:**
- `order: 0` = organization (root)
- `order: 1` = first level below org (department, lob, product, team in flat)
- `order: 2` = second level (function, team under department)
- `order: 3` = third level (team under function under lob)

The `order` value comes from `structures.<type>.levels[].level` in templates.yaml.

## Inference Reference

All rules in `references/templates.yaml`:

| What | Location |
|------|----------|
| Industry → Functions | `industry_functions.<industry>.functions` |
| Function → Teams | `function_config.<function>.default_teams` |
| Function → Files | `function_config.<function>.files` |
| Team → Files | `team_config.<team>.files` |
| Structure → Paths | `structures.<type>.levels[].path` |

**Fallbacks:** Unknown industry → `default.functions`, Unknown function → empty children, Unknown team → base files only

## Rules

| Rule | Why |
|------|-----|
| ONE question per turn | Don't overwhelm |
| Multiple choice preferred | Easier to answer |
| Always conversational | User sees responses directly |
| No JSON in chat | System reads file, not chat output |
| Write ontology_draft.json | System imports to Playbook DB |
| Read templates.yaml FIRST | Source of truth for all structure |

---

## Common Failures

- **Not reading templates.yaml first** → Made-up file names, 4 iterations to fix
- **Missing default_teams** → Check `function_config.<func>.default_teams` for EVERY function
- **Missing function files** → Check `function_config.<func>.files` for EVERY function
- **Missing team files** → Check `team_config.<team>.files` for known team names
- **Incremental generation** → Build COMPLETE JSON in ONE pass, not iteratively
- **Missing display_name** → Every node needs `display_name` (auto-generated from name)
- **Deleting entities with people** → Check for assigned people before deletion

---

## Entity Deletion Safety Check

When user requests to delete/remove an entity, check for assigned people first.

**Detection triggers:** "remove", "delete", "get rid of" + entity name

**Check process:**
1. Scan `entities/person/*/overview.yaml` for `team:` matching entity name (normalized, case-insensitive)
2. For parent entities, also check all child teams recursively
3. If no `entities/person/` directory exists, allow deletion

**If people found → BLOCK (use this EXACT format, do NOT mention Playbook or any app name):**

```
Cannot delete '{entity_name}' - these people are currently assigned:
- {person_name}
- {person_name}

Please reassign or remove them from the portal first.
```

Do NOT say "ask me again" or mention any app by name. Just list the people and the portal instruction.

**If no people found → ALLOW** and proceed with removal.

**Edge cases:**
- Person without `team:` field → ignore
- Team path like `engineering/backend` → match both parts

