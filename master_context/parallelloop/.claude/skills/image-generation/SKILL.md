---
name: image-generation
description: Generate diagrams and visualizations from organizational context. Claude explores the context repository, understands the request, and crafts an intelligent prompt for Gemini image generation. Supports both new generation and editing existing images.
---

# Image Generation Skill

Generate visual diagrams by understanding user requests and crafting targeted prompts from organizational context.

**Think deeply before crafting the prompt.** Take time to:
- Understand exactly what the user wants
- Explore the context repo thoroughly
- Plan the diagram structure in detail
- Write a comprehensive prompt (200-500 words)

## How This Works

1. **Understand** the user's request (you have full conversation context)
2. **Explore** the context repository to find ALL relevant data
3. **Think** about the best way to visualize this information
4. **Craft** a detailed, comprehensive prompt (not a one-liner)
5. **Generate** by calling the image generation script

## Output Path Resolution

Determine output directory from payload:

```python
context_type = payload.get("context_type", "org")
project_id = payload.get("project_id")

if context_type == "project" and project_id:
    output_dir = f"project_workspaces/project_{project_id}/artifacts/art_image_{project_id}"
else:
    output_dir = f"artifacts/art_image_{project_id}"
```

## Context Repository Structure

The workspace contains organizational data you can explore using Read, Glob, Grep:

| Path | Content |
|------|---------|
| `entities/product/*/context.yaml` | Products and offerings |
| `entities/team/*/context.yaml` | Teams and departments |
| `entities/person/*/context.yaml` | People |
| `entities/system/*/context.yaml` | Systems and services |
| `entities/process/*/context.yaml` | Workflows and processes |
| `entities/organization/*/context.yaml` | Organization overview |
| `project_workspaces/project_{id}/sources/*/structured.md` | Project-specific sources |

**Explore what's relevant to the request.** Find the entities that matter for the diagram.

## Visual Style Requirements

**ALWAYS apply these style guidelines:**

- Clean, minimal, professional design
- **NO gradients** - use flat, solid colors only
- **NO purple** - prefer blues, grays, greens, oranges
- **NO logos or brand marks** - do not include any company logos
- Simple sans-serif typography
- Color-coded sections (e.g., blue for orchestration, green for services, orange for storage)
- Professional, technical diagram aesthetic

Include these style requirements in your prompt to Gemini.

## Crafting the Prompt

**Be VERBOSE and DETAILED.** Describe exactly what you want to see. A good prompt is 200-500 words.

### Critical: Specify EXACT Text

The image model renders text better when you specify **exact words** to display:

**BAD:** "A box showing the authentication service responsibilities"
**GOOD:** "A box labeled 'Auth Service' containing the text: '• User login', '• Token validation', '• Session management'"

For every text element in your diagram, write out the exact words that should appear.

### Principles

1. **Specify exact text word-for-word** - Write out every label, title, bullet point, and annotation exactly as it should appear. Don't describe it, write it.

2. **Describe the layout** - How should elements be arranged? (hierarchy, layers, grid, flow, radial)

3. **List every element explicitly** - Name each box, node, or item with its exact label text.

4. **Specify connections with labels** - "Arrow from A to B labeled 'API Request'"

5. **Assign colors purposefully** - Use color to group related items or distinguish categories.

6. **Describe font and style** - "Bold title text", "smaller subtitle", "bullet list inside box"

7. **End with constraints** - "Do NOT add any text, labels, or elements not listed above"

### What makes a BAD prompt
- "Create an architecture diagram" (no specifics)
- "Show the authentication flow" (doesn't specify exact text)
- "Include the main components" (which ones? what labels?)

### What makes a GOOD prompt
- Writes out every word that should appear in the image
- Specifies exact labels: "Box labeled 'PostgreSQL Database'"
- Includes exact bullet text: "containing: '• Users table', '• Sessions table'"
- Describes text style: "title in bold, subtitles in gray"
- Ends with: "Do NOT add any text not specified above"

## Generate Image

**New image generation:**
```bash
python .claude/skills/image-generation/scripts/generate_image.py \
  --prompt "YOUR CRAFTED PROMPT" \
  --output "{output_dir}/$(date +%Y%m%d_%H%M%S)_{descriptive_name}.png" \
  --aspect-ratio "16:9" \
  --image-size "2K"
```

**Editing existing image** (when `input_images` in payload):
```bash
python .claude/skills/image-generation/scripts/generate_image.py \
  --prompt "YOUR EDITING INSTRUCTIONS" \
  --output "{output_dir}/$(date +%Y%m%d_%H%M%S)_{descriptive_name}_edited.png" \
  --input-image "/path/to/previous/image.png" \
  --aspect-ratio "16:9"
```

For multiple input images, use `--input-image` multiple times.

**File naming:** Use descriptive names like `product_portfolio`, `team_hierarchy`, `system_architecture`, `data_flow`, not just `architecture` or `workflow`.

## Image Editing Mode

When editing existing images from the conversation:

1. **Find the image path** from `<conversation_artifacts>` in the chat context
   - Each artifact has a `path:` field showing the workspace-relative path
   - Example: `path: artifacts/art_image_proj123/20241115_143022_diagram.png`

2. **Craft an editing prompt** describing the changes

3. **Pass the image** via `--input-image` flag:
```bash
python .claude/skills/image-generation/scripts/generate_image.py \
  --prompt "YOUR EDITING INSTRUCTIONS" \
  --output "{output_dir}/$(date +%Y%m%d_%H%M%S)_{descriptive_name}_edited.png" \
  --input-image "artifacts/art_image_proj123/original.png" \
  --aspect-ratio "16:9"
```

**Examples of editing requests:**
- "Make it horizontal" → Describe the layout change
- "Add a title" → Describe what title to add
- "Change the colors to green" → Describe the color change
- "Combine these two diagrams" → Pass multiple `--input-image` flags

## After Generation

Artifacts are automatically detected by the system via git commits.

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations automatically after your skill completes.

After the image is generated and script completes successfully:

1. **Describe the result naturally**:
   - "I've generated a system architecture diagram showing the three-tier platform"
   - "Here's the org chart you requested, showing the engineering team structure"

2. **Mention key elements if relevant**:
   - "The diagram shows Playbook as the orchestration layer, with Agent SDK handling execution"
   - "The chart includes 12 team members across 3 departments"

3. **Offer to continue**:
   - "Would you like me to add more detail or create a different view?"
   - "Should I make any modifications to this diagram?"

**Just communicate naturally** - the system handles artifact registration behind the scenes.

## Error Handling

If entities directory is empty or no relevant data found, explain naturally:
- "I couldn't find relevant organizational data to create this diagram. The entities directory appears to be empty."
- "To generate this visualization, you'll need to add organizational data to the context repository first."

## Prerequisites

- `GOOGLE_API_KEY` environment variable set
- Python packages: `google-genai`, `Pillow`
