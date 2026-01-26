# Aesthetics Guide

Commit to a BOLD aesthetic direction. The key is intentionality, not intensity.

## Aesthetic Directions

Pick one and execute with precision:

| Direction | Characteristics |
|-----------|-----------------|
| Brutally minimal | Extreme whitespace, single accent, stark typography |
| Maximalist chaos | Layered elements, bold colors, controlled disorder |
| Retro-futuristic | Neon accents, gradients, tech-inspired shapes |
| Organic/natural | Soft curves, earth tones, flowing layouts |
| Luxury/refined | Subtle animations, premium typography, restrained palette |
| Playful/toy-like | Rounded corners, bright colors, bouncy animations |
| Editorial/magazine | Strong grid, dramatic typography, whitespace |
| Brutalist/raw | Exposed structure, monospace fonts, raw borders |
| Art deco/geometric | Gold accents, symmetry, decorative patterns |
| Industrial/utilitarian | Dark grays, functional layout, minimal decoration |

## Typography

**DO**: Use distinctive, characterful fonts from Google Fonts:
- Display: Playfair Display, Fraunces, Space Grotesk, Clash Display, Syne
- Body: DM Sans, Plus Jakarta Sans, Outfit, Manrope, Source Serif Pro

**DON'T**: Arial, Inter, Roboto, system-ui, sans-serif defaults

Pair a distinctive display font with a refined body font.

## Color

**DO**:
- Commit to a cohesive palette (3-5 colors max)
- Use CSS variables for consistency
- Dominant color with sharp accents
- High contrast for readability

**DON'T**:
- Purple gradients on white (overused AI aesthetic)
- Evenly-distributed rainbow palettes
- Low-contrast text

Example palettes:
```css
/* Dark tech */
:root { --bg: #0a0a0a; --surface: #161616; --accent: #22d3ee; --text: #fafafa; }

/* Warm editorial */
:root { --bg: #faf7f2; --surface: #fff; --accent: #c45d3a; --text: #1a1a1a; }

/* Luxury dark */
:root { --bg: #1a1a2e; --surface: #16213e; --accent: #d4af37; --text: #f1f1f1; }
```

## Motion & Animation

**High-impact moments**:
- Page load with staggered reveals (`animation-delay`)
- Scroll-triggered transitions
- Hover states that surprise

**CSS-only preferred**:
```css
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.card { animation: fadeUp 0.6s ease-out backwards; }
.card:nth-child(1) { animation-delay: 0.1s; }
.card:nth-child(2) { animation-delay: 0.2s; }
```

## Spatial Composition

- Unexpected layouts over predictable grids
- Asymmetry creates visual interest
- Overlap elements for depth
- Generous negative space OR controlled density (pick one)

## Backgrounds & Details

Create atmosphere, not flat colors:
- Gradient meshes
- Subtle noise/grain textures
- Geometric patterns
- Layered transparencies
- Dramatic shadows

```css
/* Subtle grain overlay */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background: url("data:image/svg+xml,...") repeat;
  opacity: 0.03;
  pointer-events: none;
}
```

## Anti-Patterns (NEVER DO)

- Generic font stacks (Inter, Roboto, Arial)
- Purple-on-white gradients
- Predictable card grids with no variation
- Cookie-cutter hero sections
- Same design across different contexts
- Converging on "safe" choices

Every design should feel unique to its context.
