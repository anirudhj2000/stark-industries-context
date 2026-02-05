# Meeting Notes: Active Days Counter Technical Discussion

**Source ID**: 8afa8230-f502-49d3-8a50-a2035c18ab12
**Date**: 2026-02-05
**Duration**: 00:16:50
**Attendees**: Speaker 0, Speaker 1, Speaker 2
**Processed**: 2026-02-05T08:23:00Z

---

## Executive Summary

This technical discussion covered development approaches including TDD vs prototyping for frontend development, code structure and skill-based architecture, and various integration points for the product. The team discussed integration options with tools like Jira, Confluence, Google Calendar, Google Drive, Slack, and meeting recording services, with a focus on building out the playbook and agent SDK functionality.

---

## Discussion Topics

### 1. Development Approach: TDD vs Prototyping

**Key Points:**
- Discussion on whether to use TDD (Test-Driven Development) or prototyping approach
- Prototyping considered more effective for greenfield frontend development
- Existing codebase constraints (brownfield vs greenfield) affect the approach
- Theme-based development for frontend prototypes discussed

**Decisions:**
- TDD or prototyping approach depends on whether working with existing codebase or greenfield
- For frontend, prototyping with themes yields better results

---

### 2. Code Structure and Skills Architecture

**Key Points:**
- Discussion about code maps and skill-based architecture
- Team described as "plumbing" - connecting different components
- Deterministic skill invocation with installation ID and script
- Submodule context and access patterns discussed
- App settings and installation configuration mentioned

**Decisions:**
- Skills should be deterministically invoked with proper context
- Submodule access needs proper configuration

---

### 3. Release Planning and Architecture

**Key Points:**
- Discussion about sonnet release timeline (expected within a week)
- Parallel development tracks mentioned
- Architectural alignment considered important
- Permission changes discussed

**Decisions:**
- Changes being made for upcoming release
- Architecture needs to be properly aligned

---

### 4. Integrations and Third-Party Tools

**Key Points:**
- **Jira** integration for issue tracking
- **Confluence** for documentation
- **Composio** mentioned for integration handling (~$8 cost reference)
- **Google Calendar** for scheduling and events
- **Google Drive** for file search and storage
- **Google Meet/Teams** for meeting recordings
- **Slack** for notifications and agent communication
- Custom fields and API handling discussed
- Discussion about file search capabilities within Google Drive

**Decisions:**
- Meeting recordings integration from Google Meet/Teams considered optional for now
- Integration approach should be flexible with custom fields support
- Manual integration acceptable as fallback

---

### 5. Playbook and Agent SDK

**Key Points:**
- Playbook intelligence integrated with agent functionality
- Via playbook to agent SDK connection pattern
- Everything treated as an action in the system
- Per-user, per-project chat functionality discussed
- Parallel Loop tracking for questions and actions

**Action Items:**
- [ ] **Team**: Set up playbook to agent SDK integration
- [ ] **Team**: Implement action-based system for events and meetings
- [ ] **Team**: Use current project as use case for Parallel Loop

---

### 6. Gmail and Notifications

**Key Points:**
- Gmail link integration discussed
- Filtering messages and pop-up notifications
- Slack notifications as alternative

---

## Summary of Decisions (6 total)

1. Use prototyping approach for greenfield frontend development
2. Skills should be deterministically invoked with proper installation context
3. Architecture alignment is critical before release
4. Meeting recording integration (Google Meet/Teams) is optional for now
5. Integration approach should support custom fields via API
6. Everything in the system should be treated as an action

---

## Summary of Action Items (4 total)

**High Priority:**
- [ ] Set up playbook to agent SDK integration for next week
- [ ] Implement action-based system for meetings and events

**Medium Priority:**
- [ ] Use current project as use case for Parallel Loop demonstration
- [ ] Set up file search capability for Google Drive integration

---

## Enrichment Legend

### Vocabulary (0 terms normalized)

*No vocabulary terms matched organizational dictionary.*

### Entities (0 found)

*No organizational entities matched in this transcript. The recording contains mixed Hindi-English conversation which may have affected entity recognition.*

---

## Notes

This transcript contains significant code-switching between Hindi and English, which is common in technical discussions in multilingual environments. Some portions may not have transcribed accurately due to the mixed language content and informal conversational style.
