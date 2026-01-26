---
name: frontend-design
description: Create distinctive, production-grade HTML interfaces. Use when user asks to build web pages, components, landing pages, dashboards, posters, or any visual HTML output. Outputs self-contained HTML. Avoids generic AI aesthetics.
---

# Frontend Design

Create self-contained HTML with distinctive design.

## Output Format

**Always plain conversational text.** No JSON wrappers - artifacts are detected automatically via git.

```
I've created a dark-themed pricing table with three tiers using DM Sans and a cyan accent.

Would you like me to adjust the colors or add more details to each tier?
```

## Workflow

1. **Parse context** from `<chat_context>` for `project_id`
2. **Explore project** (if project_id exists): `Glob("project_workspaces/project_{project_id}/**/*")`
3. **Choose aesthetic direction** - See [references/aesthetics.md](references/aesthetics.md)
4. **Generate HTML** - Self-contained, responsive, production-grade
5. **Write file** to artifact path
6. **Describe result naturally** - What you created, key design choices, offer to iterate (no JSON)

## Output Path

```
# With project context:
project_workspaces/project_{project_id}/artifacts/art_html_{project_id}_{artifact_id}/{descriptive-name}.html

# Without project context:
artifacts/art_html_{artifact_id}/{descriptive-name}.html
```

- `artifact_id`: Short unique identifier (e.g., `20250123_a1b2c3`)
- `{descriptive-name}.html`: Descriptive filename like `pricing-table.html`, `landing-page.html` - this becomes the artifact title

## HTML Requirements

- **Self-contained**: Inline `<style>`, no external CSS (Google Fonts OK)
- **Complete**: Valid HTML5 with `<!DOCTYPE html>`, viewport meta
- **Responsive**: Works on mobile and desktop
- **No external navigation**: Do NOT use `<a href="...">` links to other pages
- **In-page interactions only**: CTAs and buttons must use JavaScript to change views within the same page (show/hide sections, tabs, accordions, state changes)

## Example

**User**: "Create a pricing table for our SaaS product"

**Write to**: `project_workspaces/project_abc123/artifacts/art_html_abc123_20250123_x1y2z3/pricing-table.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pricing</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #0a0a0a; --card: #161616; --accent: #22d3ee; }
        * { margin: 0; box-sizing: border-box; }
        body { font-family: 'DM Sans', sans-serif; background: var(--bg); color: #fff; min-height: 100vh; padding: 4rem 2rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; max-width: 1000px; margin: 0 auto; }
        .card { background: var(--card); border-radius: 1rem; padding: 2rem; border: 1px solid #222; }
        .card.featured { border-color: var(--accent); }
        .price { font-size: 3rem; font-weight: 700; }
        .price span { font-size: 1rem; color: #888; }
    </style>
</head>
<body>
    <div class="grid">
        <div class="card">
            <h3>Starter</h3>
            <p class="price">$9<span>/mo</span></p>
        </div>
        <div class="card featured">
            <h3>Pro</h3>
            <p class="price">$29<span>/mo</span></p>
        </div>
        <div class="card">
            <h3>Enterprise</h3>
            <p class="price">$99<span>/mo</span></p>
        </div>
    </div>
</body>
</html>
```

**Then respond naturally** (no JSON):
> I've created a dark-themed pricing table with three tiers using DM Sans and a cyan accent. Would you like me to adjust the colors or add more details to each tier?

## Rules

| Rule | Why |
|------|-----|
| Always conversational | User sees responses directly |
| No JSON output | Artifacts detected via git |
| No git commands | Task runner handles commits |

## Design Guidelines

See [references/aesthetics.md](references/aesthetics.md) for:
- Typography choices (avoid generic fonts)
- Color and theme guidance
- Motion and animation patterns
- Anti-patterns to avoid
