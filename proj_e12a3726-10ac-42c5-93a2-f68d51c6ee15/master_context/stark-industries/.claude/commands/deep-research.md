---
name: deep-research
description: Conduct comprehensive deep research combining organization context with Perplexity's sonar-deep-research model. Produces a structured research report artifact.
---

# Deep Research

Comprehensive research using internal organizational knowledge + Perplexity deep research for external sources.

## When to Use

- Complex research questions requiring multiple sources
- Market research, competitor analysis
- Technical deep-dives requiring external documentation
- Topics requiring both internal context and current web information

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `user_prompt` | Yes | The research query |
| `conversation_id` | Yes | For tracking |
| `project_id` | No | Scope to specific project context |
| `context_type` | No | "org" or "project" (default: "org") |

## Output

Creates artifact at `artifacts/research_reports/{date}_{topic-slug}.md`

Returns:
```json
{
  "success": true,
  "artifact_type": "CUSTOM_DOCUMENT",
  "artifact_path": "artifacts/research_reports/...",
  "display_name": "Research: {topic}",
  "summary": "Brief summary of findings...",
  "sources_count": {"internal": N, "external": M},
  "files_written": ["artifacts/research_reports/..."],
  "commit_message": "research: {topic}"
}
```

## Example

**Query**: "What are the best practices for RAG chunking strategies?"

**Result**: A comprehensive research report with:
- Internal findings from org knowledge base
- External research from Perplexity deep search
- Synthesized recommendations with citations
