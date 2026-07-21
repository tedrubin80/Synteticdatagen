# Design

## Theme

Dark. Mood: a lit terminal window at 2am — matte black glass, one cold signal color cutting through, nothing decorative. This is a self-hosted dev tool, not a SaaS product; the visual language should read as "built by an engineer," not "generated from a template."

## Color Strategy

Restrained: near-black neutral surface + one committed primary (signal blue) + one secondary accent (terminal green) used sparingly for success/prompt states. Not a rainbow of tinted icon circles.

```css
:root {
  --bg:        oklch(0.09  0     0);      /* pure near-black, no hue tint */
  --surface:   oklch(0.15  0.006 230);    /* panels, terminal chrome, cards — faint cobalt glass tint */
  --surface-2: oklch(0.20  0.008 230);    /* raised surface: nav, hovered rows */
  --border:    oklch(0.28  0.01  230);    /* hairline borders on dark */
  --ink:       oklch(0.93  0.01  230);    /* body text, ~15:1 on bg */
  --muted:     oklch(0.60  0.014 230);    /* secondary text, ~5.5:1 on bg */
  --primary:   oklch(0.70  0.15  230);    /* cobalt signal blue — links, CTA, focus */
  --primary-ink: oklch(0.98 0 0);         /* white text on primary fills */
  --accent:    oklch(0.75  0.17  150);    /* terminal green — prompts, success, $ */
  --danger:    oklch(0.66  0.19  25);     /* errors only */
}
```

Rules:
- `--primary` and `--accent` are the only saturated colors. No per-feature color-coding (no "blue card, green card, orange card, red card" grids).
- Text on `--primary` or `--accent` fills is always `--primary-ink` (white) — both are mid-luminance saturated fills.
- No gradients, no glassmorphism, no `bg-opacity-10` icon-circle tints.

## Typography

Contrast pairing: system sans for UI text, real monospace for anything that is or resembles code/terminal output — the mono face is a first-class visual element, not an afterthought inside a `<code>` tag.

```css
--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
--font-mono: "JetBrains Mono", "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
```

- Body copy: `--font-sans`, `--ink`, max 70ch measure.
- Headings: `--font-sans`, weight 600–700, `letter-spacing: -0.02em`, `text-wrap: balance`.
- Display hero heading: `clamp(2rem, 5vw, 3.25rem)` — well under the 6rem ceiling; this is a quiet register, not a shout.
- Code / terminal blocks: `--font-mono`, real syntax coloring (string/number/boolean/comment tokens), never a plain gray block.

## Layout & Components

- **Terminal window** is the primary visual motif, used for real command output and real API responses — not decorative. Three-dot chrome, a realistic titlebar path, monospace body, actual `$` prompts.
- **No icon-in-tinted-circle feature grids.** Field types and endpoints are listed as compact code-styled tags or a real table, not badge pills in six different colors.
- **One CTA per page**, in the hero only. No repeated "Get Started" section at the bottom of every page.
- **No pricing-card treatment for "free."** Cost/limits are stated as plain text sentences, if at all — never a `$0/mo` card with a checklist.
- Cards, where genuinely useful (not the default), are flat: 1px `--border`, no shadow, no hover-lift.
- Spacing scale: 4px base grid (`0.25rem` increments), generous section padding (`clamp(3rem, 8vw, 6rem)` vertical) for a quiet, uncluttered rhythm.

## Motion

Minimal and functional: short (150–200ms) ease-out transitions on hover/focus states, a subtle cursor-blink on terminal prompts, no scroll-triggered reveal choreography. Respect `prefers-reduced-motion`.

## Anti-patterns to avoid

Bootstrap-default cards with `shadow-sm` + hover-lift, `bg-{color}-opacity-10` icon circles, Bootstrap Icons as primary visual interest, badge-pill chips for every list of things, gradient hero backgrounds, repeated bottom-of-page CTA sections, SaaS tier/pricing language.
