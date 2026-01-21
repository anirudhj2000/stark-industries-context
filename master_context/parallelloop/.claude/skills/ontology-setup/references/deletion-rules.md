# Entity Deletion Safety Check

When user requests to delete/remove an entity, check for assigned people first.

## Detection Triggers

Keywords: "remove", "delete", "get rid of" + entity name

## Check Process

1. Scan `entities/person/*/overview.yaml` for `team:` matching entity name (normalized, case-insensitive)
2. For parent entities, also check all child teams recursively
3. If no `entities/person/` directory exists, allow deletion

## Response Format

**If people found → BLOCK (use this EXACT format, do NOT mention Playbook or any app name):**

```
Cannot delete '{entity_name}' - these people are currently assigned:
- {person_name}
- {person_name}

Please reassign or remove them from the portal first.
```

Do NOT say "ask me again" or mention any app by name. Just list the people and the portal instruction.

**If no people found → ALLOW** and proceed with removal.

## Edge Cases

| Case | Action |
|------|--------|
| Person without `team:` field | Ignore (not assigned anywhere) |
| Team path like `engineering/backend` | Match both parts |
| No `entities/person/` directory | Allow deletion |
