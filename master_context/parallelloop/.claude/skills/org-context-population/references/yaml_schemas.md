# YAML Schemas Reference

Structure templates for entity files, list files, triage entries, and conflict markers.

## Contents

- [Entity File Structure](#entity-file-structure)
- [List File Structure](#list-file-structure)
- [Triage File Structure](#triage-file-structure)
- [Conflict Markers](#conflict-markers)
- [Required Metadata Fields](#required-metadata-fields)
- [Merge Rules Quick Reference](#merge-rules-quick-reference)

---

## Entity File Structure

Individual entity files (e.g., `person/john_smith/overview.yaml`):

```yaml
id: john_smith
name: John Smith
role: CTO
team: leadership
email: john@company.com
_source_id: src_meeting_123
_source_name: "Q4 Planning Meeting"
_sources:
  - id: src_onboarding_001
    name: "Employee Onboarding Doc"
  - id: src_meeting_123
    name: "Q4 Planning Meeting"
_last_updated: "2025-12-27T10:00:00Z"
```

**With role history tracking:**
```yaml
id: john_smith
name: John Smith
role: VP Engineering
_previous_roles: ["Senior Engineer", "Staff Engineer"]
decisions_made:
  - quarterly_review_2025_q4
_source_id: src_meeting_456
_source_name: "Promotion Announcement"
_sources:
  - id: src_onboarding_001
    name: "Employee Onboarding Doc"
  - id: src_meeting_456
    name: "Promotion Announcement"
_last_updated: "2025-12-27T10:00:00Z"
```

---

## List File Structure

Files containing arrays of entities (e.g., `organization/vendors.yaml`):

```yaml
vendors:
  - id: acme_corp
    name: Acme Corp
    relationship: cloud_provider
    contract_value: "$50k/year"
    _source_id: src_meeting_123
    _source_name: "Q4 Planning Meeting"
  - id: globex
    name: Globex Inc
    relationship: legal_services
    _source_id: src_overview_001
    _source_name: "Company Overview 2025"
```

**Competitors example (`organization/competitors.yaml`):**
```yaml
competitors:
  - id: rival_inc
    name: Rival Inc
    market_position: "Direct competitor in enterprise segment"
    _source_id: src_pitch_deck_001
    _source_name: "Series B Pitch Deck"
  - id: other_co
    name: Other Co
    market_position: "Adjacent market, potential threat"
    _source_id: src_strategy_doc_002
    _source_name: "2025 Strategy Document"
```

---

## Triage File Structure

For routing new entities that have no existing file (`_triage.yaml`):

```yaml
inbox:
  - item: "New vendor: Acme Corp"
    entity_type: vendor
    _source_id: src_meeting_456
    _source_name: "Vendor Review Meeting"
    added_date: "2025-12-27T10:00:00Z"
    suggested_destination: "Add to entities/organization/vendors.yaml"
    context:
      raw_text: "Our vendor Acme Corp provides cloud services..."
      extracted_data:
        id: acme_corp
        name: Acme Corp
        relationship: cloud_provider

  - item: "Person 'Smith' mentioned - ambiguous match"
    entity_type: person
    _source_id: src_org_chart_2025
    _source_name: "2025 Org Chart"
    added_date: "2025-12-27T10:00:00Z"
    suggested_destination: "Clarify which Smith via generate-questions"
    context:
      candidates: ["john_smith", "jane_smith"]
      raw_text: "Smith will lead the project..."

  - item: "New person: Sarah Chen"
    entity_type: person
    _source_id: src_meeting_456
    _source_name: "Vendor Review Meeting"
    added_date: "2025-12-27T10:00:00Z"
    suggested_destination: "Create via ontology-setup after user approval"
    context:
      raw_text: "Sarah Chen from the data team presented..."
      extracted_data:
        id: sarah_chen
        name: Sarah Chen
        team: data
        role: unknown
```

---

## Conflict Markers

When values disagree and it's not a clear enhancement:

```yaml
role: Senior Engineer
_conflict:
  field: role
  existing_value: Senior Engineer
  new_value: Staff Engineer
  source_id: src_org_chart_2025
```

This allows `generate-questions` skill to create resolution questions.

**Multiple conflicts:**
```yaml
role: Senior Engineer
location: NYC
_conflicts:
  - field: role
    existing_value: Senior Engineer
    new_value: Staff Engineer
    source_id: src_org_chart_2025
  - field: location
    existing_value: NYC
    new_value: SF
    source_id: src_hr_update_001
```

---

## Required Metadata Fields

Every update must include:

| Field | Purpose | Example |
|-------|---------|---------|
| `_source_id` | Latest source that modified this entity | `src_meeting_123` |
| `_source_name` | Human-readable name of latest source | `"Q4 Planning Meeting"` |
| `_sources` | All sources that contributed data (id + name) | See below |
| `_last_updated` | ISO-8601 timestamp of update | `"2025-12-27T10:00:00Z"` |

**`_sources` format:**
```yaml
_sources:
  - id: src_onboarding_001
    name: "Employee Onboarding Doc"
  - id: src_meeting_123
    name: "Q4 Planning Meeting"
```

---

## Merge Rules Quick Reference

| Field Type | Behavior |
|------------|----------|
| Identity (name, id) | Keep existing unless new is more specific |
| Current state (role, status) | Most recent wins, track previous in `_previous_*` |
| Lists (skills, projects) | Append and deduplicate |
| Nested objects | Recursive merge |
| `_sources` | Append new source_id to list |
