---
name: deep-research
description: Comprehensive deep research combining org context with Perplexity's sonar-deep-research. Creates structured research report artifacts.
---

# Deep Research Skill

Conduct comprehensive research by combining internal organizational knowledge with Perplexity's deep research capabilities. Produces a structured research report as an artifact.

## Input

Read from payload:
- `user_prompt` (required): The research query
- `project_id` (optional): Scope to project context
- `context_type` (optional): "org" or "project"

## Process

### Step 1: Parse Input & Context

```
Read payload from argument path
Parse user_prompt, project_id, context_type
Determine search scope:
  - "org" → entities/ only
  - "project" → entities/ + project_workspaces/project_{project_id}/
```

### Step 2: Search Internal Context

Search the organization's knowledge base for relevant information:

```
1. Glob entities/**/*.yaml → Read relevant entity files
2. Glob sources/*/structured.md → Read processed sources
3. Glob artifacts/**/*.md → Read existing artifacts
4. If project context: also search project_workspaces/project_{project_id}/
```

For each match:
- Extract relevant snippets
- Note the source path for citations
- Identify key facts and insights

**Internal findings format:**
```
- Finding: {insight}
  Source: {entity/source/artifact name}
  Path: {file_path}
```

### Step 3: Deep Web Research (Perplexity)

Call the Perplexity MCP tool for comprehensive external research:

```
mcp__perplexity__perplexity_research(
  query="{user_prompt}",
  strip_thinking=true
)
```

**Note**: This uses Perplexity's `sonar-deep-research` model which:
- Performs iterative multi-step searches
- Analyzes dozens of sources
- Provides comprehensive synthesis with citations

Parse the response to extract:
- Key findings organized by theme
- Source URLs for citations
- Conflicting viewpoints if present

### Step 4: Synthesize Report

Create a comprehensive research report combining both sources.

**Write to**: `artifacts/research_reports/{YYYY-MM-DD}_{topic-slug}.md`

```markdown
# Research Report: {Topic}

**Generated**: {YYYY-MM-DD HH:MM}
**Query**: {user_prompt}

## Executive Summary

{2-3 paragraph synthesis of key findings from both internal and external sources}

## Internal Findings

{Findings from organization's knowledge base}

### From Entities
{Relevant entity information with citations}

### From Sources
{Relevant source document findings}

### From Artifacts
{Relevant existing artifact insights}

## External Research

{Findings from Perplexity deep research, organized by theme}

### {Theme 1}
{Findings with source citations}

### {Theme 2}
{Findings with source citations}

## Synthesis & Recommendations

{Cross-referenced analysis combining internal knowledge with external research}

- **Key Insight 1**: {insight with supporting evidence}
- **Key Insight 2**: {insight with supporting evidence}

## Gaps & Further Research

{Topics that need more information or follow-up}

## Sources

### Internal
- [{Entity/Source/Artifact name}]({relative_path})

### External
- [{Source title}]({url})
```

### Step 5: Git Commit

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

### Step 6: Return Response

```json
{
  "success": true,
  "artifact_type": "CUSTOM_DOCUMENT",
  "file_path": "artifacts/research_reports/{date}_{slug}.md",
  "display_name": "Research: {topic}",
  "files_written": ["artifacts/research_reports/{date}_{slug}.md"],
  "commit_message": "research: {brief_topic}",
  "summary": "{2-3 sentence summary of key findings}",
  "sources_count": {
    "internal": {number_of_internal_sources},
    "external": {number_of_external_sources}
  }
}
```

## Error Handling

### Perplexity MCP Not Available

If `mcp__perplexity__perplexity_research` is not available:

1. Fall back to `WebSearch` tool with multiple targeted queries
2. Note in the report: "External research conducted via web search (deep research unavailable)"
3. Perform 5-10 targeted searches to approximate deep research coverage

### No Internal Context Found

If no relevant internal information exists:

1. Note in report: "No relevant internal documentation found"
2. Suggest: "Consider uploading relevant source documents to enhance future research"
3. Proceed with external research only

### Timeout Handling

Deep research may take 60-180 seconds. If the process is timing out:
- Ensure MCP client timeout is set to at least 180 seconds
- Consider breaking into smaller, focused queries

## Output Examples

**Success Response:**
```json
{
  "success": true,
  "artifact_type": "CUSTOM_DOCUMENT",
  "file_path": "artifacts/research_reports/2025-01-05_rag-chunking-strategies.md",
  "display_name": "Research: RAG Chunking Strategies",
  "files_written": ["artifacts/research_reports/2025-01-05_rag-chunking-strategies.md"],
  "commit_message": "research: RAG chunking strategies",
  "summary": "Research covers semantic chunking, sliding window, and recursive approaches. Internal docs show current 512-token chunks; external research suggests semantic boundaries improve retrieval by 15-20%.",
  "sources_count": {"internal": 3, "external": 12}
}
```

## Quality Guidelines

1. **Accuracy**: Only report findings that are actually present in sources
2. **Citations**: Every claim must have a citation (internal path or external URL)
3. **Synthesis**: Don't just list findings - draw connections and insights
4. **Actionability**: Include concrete recommendations where appropriate
5. **Gaps**: Be explicit about what information is missing or uncertain
