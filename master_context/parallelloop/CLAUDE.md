# Organization Context Repository

Git-versioned organizational knowledge.

## Directory Structure

| Path | Purpose |
|------|---------|
| `entities/` | Org hierarchy (teams, departments, products) |
| `entities/person/` | Team members (not in ontology) |
| `sources/` | Processed source materials |
| `artifacts/` | Generated outputs |
| `project_workspaces/project_{id}/` | Project-specific work |
| `.claude/` | Skills and commands |
| `ontology.yaml` | Organization structure definition (source of truth) |

### Person Structure
```
entities/person/{person_id}/
└── context.yaml    # Name and context information
```

## Ontology Schema

`ontology.yaml` defines the organization hierarchy.

```yaml
version: '1.1'
structure_type: functional | divisional | product_centric | matrix | flat
generated_at: ISO-8601 timestamp
entities:
  - name: organization
    slug: organization
    entity_type: organization
    order: 0                    # depth in hierarchy
    level: organization
    path: entities/organization
    children:
      - name: entity-name
        slug: entity-name
        entity_type: product | department | lob | team | function
        order: 1
        level: product | department | lob | team
        path: entities/<level>/<slug>
        children: [...]         # nested entities
```

**Entity types by structure:**

| Structure | Level 1 | Level 2 | Level 3 |
|-----------|---------|---------|---------|
| Functional | department | team | - |
| Divisional | lob | function | team |
| Product-Centric | product | function | team |
| Matrix | department + lob | function | team |
| Flat | team | - | - |

**Order field:** Indicates hierarchy depth (0=org, 1=first level, 2=second level, etc.)

## Chat Behavior

**NEVER modify the repo without a skill or command.** Any modification (creating artifacts, editing entities, updating ontology, etc.) must be governed by an existing skill or command. If none exists for the requested operation, inform the user that the operation is not supported.

**Questions**: Read `ontology.yaml` first to understand the hierarchy, then search based on `context_type` in `<chat_context>`:
- `org` → search `entities/`
- `project` → search `entities/` + `project_workspaces/project_{project_id}/`

**Actions**: Invoke the appropriate skill. If no skill matches, say what you can help with instead.

**Response style**: Direct answers, cite sources by document name.

**User-invocable skills**: Some skills require user initiation (via `@` in chat or dashboard actions). When a task needs such a skill, simply inform the user that this operation requires them to initiate it - don't mention skill names or technical details.