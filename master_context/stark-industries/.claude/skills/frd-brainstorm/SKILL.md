---
name: frd-brainstorm
description: Create a Functional Requirements Document through collaborative dialogue. Checks for PRD first, gathers functional details adaptively. Use when user tags @frd.
---

# FRD Brainstorm Agent

## Output Format

**Always plain conversational text.** No JSON wrappers - artifacts are detected automatically via git.

```
I found the PRD. Based on the goals outlined, let's define the functional requirements.

What are the main features or capabilities needed?
- A) User authentication and profiles
- B) Core task management
- C) Collaboration features
- D) All of the above
```

**At completion**: Just describe the result naturally.
```
I've created the FRD for Simple Tasks. It details the user personas, feature specifications, and user flows.

Would you like me to make any changes?
```

## Output Path

Read from the **payload file** (second argument):
- `project_id` - Required for output path
- `project_name` - Use for display_name (fallback: extract from project brief or use "Untitled Project")

Generate `artifact_id`: `uuidgen | tr '[:upper:]' '[:lower:]' | cut -c1-8`

Artifacts are written to: `project_workspaces/project_{project_id}/artifacts/art_frd_{project_id}_{artifact_id}/content.md`

## Process

### Phase 1: Prerequisite Check (First Message Only)

1. Read `project_id` from the payload file
2. **Explore organization context**:
   - Run `Glob("entities/**/*.yaml")` to discover org structure
   - Read relevant files to understand existing systems
3. **Explore project context**:
   - Run `Glob("project_workspaces/project_{project_id}/**/*")` to see what exists
   - Read sources (`*/structured.md`) and artifacts
4. Check for existing PRD at `project_workspaces/project_{project_id}/artifacts/art_prd_*/content.md`
5. Check for existing FRD at `project_workspaces/project_{project_id}/artifacts/art_frd_*/content.md`
6. **Use context to inform questions** - Reference discovered context. Call out how features relate to existing org systems.

**If PRD missing:**
```
I notice there's no PRD for this project yet. The PRD defines the problem, goals, and high-level requirements that the FRD builds upon.

Would you like to:
- A) Create the PRD first using @prd
- B) Proceed without it (I'll gather some PRD-level context as we go)
```

**If PRD exists:**
- Read and extract: problem statement, goals, user stories, requirements
- Use as context to ask more targeted questions

**If FRD exists:**
```
I found an existing FRD. Would you like to:
- A) Revise the existing FRD
- B) Create a new version
```

### Phase 2: Core Understanding (Required)

Ask ONE question per turn. If PRD exists, skip questions already answered there.

1. **Features**: "What are the main features or capabilities needed?"
   - If PRD exists: "The PRD mentions [features]. Are these the core features to detail, or are there others?"

2. **User Personas**: "Who are the primary users and what are their key characteristics?"
   - A) [Inferred from PRD if available]
   - B) Different personas (please describe)

3. **Primary User Flow**: "Walk me through the main user journey - what does a typical interaction look like?"

### Phase 3: Adaptive Drill-Down

Based on answers, explore areas needing detail:

- **Feature Details**: For each major feature, ask about inputs, outputs, validation
- **Business Rules**: "What business rules or logic apply to [feature]?"
- **Integrations**: "Does this need to integrate with other systems?"
- **Data Requirements**: "What data does this feature need to capture or display?"
- **Error Handling**: "What happens when things go wrong?"

**Adaptive Logic:**
| Signal | Action |
|--------|--------|
| Detailed answer | Move to next topic |
| Vague answer | Ask follow-up to clarify |
| "not sure" / "skip" | Note as open question, move on |
| References PRD | Pull context, reduce redundant questions |

### Phase 4: Propose Generation

When minimum info gathered (3+ feature areas + primary user flow):

```
I have enough to create the FRD covering user personas, feature specifications, user flows, and data requirements.

Ready to generate, or anything to add?
```

### Phase 5: Generate Artifact

On user confirmation:

1. Load template from `references/frd-template.md` (relative to this skill)
2. Fill sections using gathered information + PRD context
3. Create output directory and write `content.md`
4. Describe the result naturally (no JSON)

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Proceeding Without PRD

If user chooses to proceed without PRD:
1. Gather broader context (some PRD-level questions about problem/goals)
2. Add note in generated doc: "Note: Created without PRD - consider creating one for completeness"

## Rules

| Rule | Why |
|------|-----|
| Check PRD first | Sequential dependency |
| Soft redirect | User decides, not forced |
| ONE question per turn | Don't overwhelm |
| Use PRD context | Avoid redundant questions |
| Always conversational | User sees responses directly |
| No JSON output | Artifacts detected via git |
