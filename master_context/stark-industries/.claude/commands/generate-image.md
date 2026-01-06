---
name: generate-image
description: Generate diagrams and visualizations from organizational context. Explores context repo, crafts intelligent prompts, supports editing.
---

# Generate Image Command

Read the skill file for full instructions:
`.claude/skills/image-generation/SKILL.md`

## Quick Reference

1. **Read payload** from arguments (manifest path, payload path)
2. **Resolve output path** from `context_type` and `project_id`
3. **Explore context repo** to find data relevant to the user's request
4. **Craft a focused prompt** with style requirements (Apple-like, no gradients, no purple)
5. **Generate image** using the script
6. **Return structured output** (task runner handles git)

## Style Requirements (Always Apply)

- Clean, minimal, Apple-like aesthetic
- NO gradients - flat colors only
- NO purple - use blues, grays, whites, blacks
- Simple sans-serif typography
- Generous whitespace

## Commands

**New generation:**
```bash
python .claude/skills/image-generation/scripts/generate_image.py \
  --prompt "YOUR PROMPT" \
  --output "{output_dir}/{timestamp}_{type}.png" \
  --aspect-ratio "16:9" \
  --image-size "2K"
```

**Editing** (when `input_images` in payload):
```bash
python .claude/skills/image-generation/scripts/generate_image.py \
  --prompt "EDIT INSTRUCTIONS" \
  --output "{output_dir}/{timestamp}_{type}_edited.png" \
  --input-image "/path/to/image.png" \
  --aspect-ratio "16:9"
```

## Output

```json
{
  "success": true,
  "image_path": "...",
  "diagram_type": "...",
  "files_written": ["..."],
  "commit_message": "image: generate {diagram_type} diagram",
  "description": "..."
}
```

**Note:** DO NOT run git add, git commit, or git push. The task runner handles all git operations.
