# Entity Rename Handling

When user requests to rename an entity, update the `ontology_draft.json` ONLY.

## Detection Triggers

Keywords: "rename", "change name", "call it", "update name", "change X to Y"

## Process

1. Load current `ontology_draft.json`
2. Find the entity to rename (by current name)
3. Update:
   - `name` field (slugified version)
   - `display_name` field (human-readable version)
   - `_meta.path` field (update the entity name in the path)
   - Update any child entity paths that reference the renamed parent
4. Write updated JSON to `artifacts/ontology_draft/ontology_draft.json`
5. Inform user: "I've updated the draft. The actual folder rename will happen when you Apply the changes."

## Example

User: "Rename consumer-mobile to mobile-apps"

Update in ontology_draft.json:
- `name`: "consumer-mobile" → "mobile-apps"
- `display_name`: "Mobile" → "Mobile Apps"
- `_meta.path`: `.../teams/consumer-mobile` → `.../teams/mobile-apps`

## Forbidden Actions

- ❌ Use `mv` or shell commands on entities folder
- ❌ Create new folders in entities/
- ❌ Delete old folders in entities/
- ❌ Modify any files in entities/

The Apply process handles folder operations. You only modify the draft JSON.
