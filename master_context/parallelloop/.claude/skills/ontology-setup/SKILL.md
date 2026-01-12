---
name: ontology-setup
description: Infer organizational hierarchy and write ONTOLOGY_DRAFT JSON artifact. Use when (1) setting up new organization context, (2) user asks about org structure, (3) initializing entity hierarchies, or (4) user mentions "ontology", "org structure", "hierarchy", "departments", "teams", "company structure", "org chart", "divisions", or "business units". Supports Functional, Divisional, Product-Centric, Matrix, and Flat structures.
---

# Ontology Setup

Infer organizational hierarchy through collaborative dialogue and create an ONTOLOGY_DRAFT artifact.

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

**At completion**: Just describe the result naturally.
```
I've set up the organizational structure for your company. It's a Functional structure with 4 departments and 6 teams total.

Would you like me to make any changes before finalizing?
```

## Output Path

**EXACT PATH (no variations):** `artifacts/ontology_draft/ontology_draft.json`

This is a **singleton** - one draft per organization. The skill always writes to the same path, overwriting any previous draft. The system handles versioning automatically.

**Note**: The system detects this file and creates/updates the ONTOLOGY_DRAFT artifact in Playbook. Each update increments the version number in the artifact metadata.

## Workflow

```
0. READ references/templates.yaml FIRST (mandatory, no exceptions)
1. Ask org structure type (1 question)
2. Ask follow-up based on type (1 question)
3. [If uncertain] Ask one clarifying question
4. Show inferred structure → User confirms or modifies
   - FOR MODIFICATIONS: If user requests entity deletion, run safety check first
   - See "Entity Deletion Safety Check" section below
5. Build COMPLETE JSON using templates.yaml → Write artifact
   - Include display_name for EVERY node (auto-generated from name)
```

### Step 0: Load Templates (MANDATORY)

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
4. Describe the result naturally (no JSON shown to user)

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

### ontology_draft.json Schema

**You MUST build the complete JSON in a single pass. No iterations. No "I'll add that later."**

#### Build Process (follow exactly):

```
1. Start with structure_type and organization node (order: 0, display_name: "Organization")
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
- `"data_engineering"` → `"Data Engineering"`
- `"customer-success"` → `"Customer Success"`
- `"it"` → `"IT"`
- `"sre"` → `"SRE"`
- `"team_1"` → `"Team 1"`

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

#### Verification Checklist (before writing):

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
- **Deleting entities with people** → Always check `entities/person/*/overview.yaml` before deletion

---

## Entity Deletion Safety Check

When a user requests to **delete or remove** an entity from the structure, you MUST check for assigned people before proceeding.

### Step 1: Detect Deletion Request

Recognize deletion intent from user messages:
- "Remove the data team"
- "Delete the engineering department"
- "Get rid of the consumer LOB"
- "I want to remove [entity_name]"

### Step 2: Check for Assigned People

Before removing ANY entity, scan for people assigned to it:

```
Scan: entities/person/*/overview.yaml
Look for: team: field matching entity name (case-insensitive, normalized)
```

**Check logic:**
1. List all folders in `entities/person/`
2. For each person folder, read `overview.yaml`
3. Get the `team:` field value
4. Normalize both entity name and team value (lowercase, replace `-` with `_`)
5. If they match, add person to the blocked list

### Step 3: Block or Allow Deletion

**If people are found (BLOCK):**

```
I cannot delete '{entity_name}' because the following people are assigned to it:

- John Smith (entities/person/john_smith/overview.yaml)
- Sarah Chen (entities/person/sarah_chen/overview.yaml)

**To proceed with deletion:**
1. Reassign these people to a different team by editing their `team:` field
2. Or remove the person entities if they've left the organization

Once all people are reassigned, ask me again to delete '{entity_name}'.
```

**If no people found (ALLOW):**

Proceed with the entity removal from the JSON structure as requested.

### Step 4: Recursive Child Check

When deleting a **parent entity** (e.g., a department with teams), check ALL children:

```
User: "Delete the engineering department"

Must check:
1. entities/person/* where team: "engineering"
2. entities/person/* where team: "frontend" (child team)
3. entities/person/* where team: "backend" (child team)

If ANY person is found in the parent or children → BLOCK deletion
```

### Deletion Safety Examples

| User Request | Entities to Check | Result |
|--------------|-------------------|--------|
| "Remove backend team" | team: backend | Block if people found |
| "Delete engineering" | team: engineering, frontend, backend | Block if any match |
| "Remove consumer LOB" | All functions and teams under consumer | Block if any match |
| "Delete empty_team" | team: empty_team | Allow (no people) |

### Edge Cases

| Scenario | Behavior |
|----------|----------|
| No `entities/person/` directory | Allow deletion (no people exist) |
| Person file has no `team:` field | Ignore that person |
| Team field has path (e.g., `engineering/backend`) | Match against both "engineering" and "backend" |

