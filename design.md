# Design — Automic Vault

A locked design system for the website. Page redesigns extend this system; they
do not invent route-specific themes.

## Genre

Modern-minimal, technical, and austere.

## Macrostructure family

- Marketing pages: Split Studio with alternating text and real product proof.
- Content pages: Long Document with a 60–65ch reading measure.
- Index pages: Index-First with staggered incident rows.

## Theme

- `--color-paper`: `oklch(8% 0.006 255)`
- `--color-paper-2`: `oklch(13% 0.006 255)`
- `--color-paper-3`: `oklch(16% 0.006 255)`
- `--color-ink`: `oklch(94% 0.01 82)`
- `--color-ink-2`: `oklch(70% 0.014 82)`
- `--color-rule`: `oklch(27% 0.008 255)`
- `--color-rule-2`: `oklch(36% 0.01 255)`
- `--color-accent`: `oklch(68% 0.15 246)`
- `--color-focus`: `oklch(76% 0.13 82)`

## Typography

- Display: Geist, weight 800, roman.
- Body: Geist, weight 400–500.
- Mono: Geist Mono, weight 600–700, reserved for labels and code.
- Display tracking: `-0.04em`.
- Display scale: `clamp(2.75rem, 5vw + 1rem, 5.25rem)`.

## Spacing

The 4-point named scale lives in `www/tokens.css`. Layout CSS uses those named
tokens instead of introducing a second scale.

## Motion

- Static by default on content and index pages.
- Hover and press feedback use `--ease-out` and transform/opacity only.
- Focus rings appear instantly.
- Reduced motion removes spatial movement.

## CTA voice

- Primary: compact outlined control with a cobalt border.
- Secondary: quiet text or neutral outline.
- Labels are short, specific, and always one line.

## Navigation and footer

- Navigation: N5 floating pill, content-sized and detached from the viewport.
- Footer: Ft5 statement rhythm, with one large closing line and a compact link row.

## Per-page allowances

- Marketing pages may use supplied product screenshots without decorative frames.
- Blog index pages may use small supplied incident images as row identifiers.
- Content and legal pages remain typography-led.

## What pages must share

- Cobalt-dark palette, Geist pair, floating navigation, grid texture, CTA voice,
  focus treatment, and footer rhythm.
- Stable URLs, semantic heading order, alternate-language links, and readable
  45–75 character measures.

## What pages may differ on

- Content density and image placement within their declared macrostructure family.
- About may use one supplied illustration; legal pages do not need one.
- Incident articles may show one supplied incident image in the opening block.

## Exports

### tokens.css

```css
:root {
  --color-paper: oklch(8% 0.006 255);
  --color-paper-2: oklch(13% 0.006 255);
  --color-paper-3: oklch(16% 0.006 255);
  --color-ink: oklch(94% 0.01 82);
  --color-ink-2: oklch(70% 0.014 82);
  --color-rule: oklch(27% 0.008 255);
  --color-rule-2: oklch(36% 0.01 255);
  --color-accent: oklch(68% 0.15 246);
  --color-accent-ink: oklch(8% 0.006 255);
  --color-focus: oklch(76% 0.13 82);
  --font-display: "Geist", system-ui, sans-serif;
  --font-body: "Geist", system-ui, sans-serif;
  --font-outlier: "Geist Mono", ui-monospace, monospace;
  --space-xs: 0.5rem;
  --space-sm: 0.75rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2.5rem;
  --space-2xl: 4rem;
  --space-3xl: 6rem;
  --text-base: 1rem;
  --text-md: 1.25rem;
  --text-xl: 1.9531rem;
  --text-3xl: 3.0518rem;
  --text-display: clamp(2.75rem, 5vw + 1rem, 5.25rem);
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in: cubic-bezier(0.7, 0, 0.84, 0);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --dur-micro: 120ms;
  --dur-short: 220ms;
  --dur-long: 420ms;
  --rule-hair: 1px;
  --rule-fine: 2px;
  --radius-card: 8px;
  --radius-pill: 999px;
  --radius-input: 8px;
}
```

### Tailwind v4 `@theme`

```css
@theme {
  --color-paper: oklch(8% 0.006 255);
  --color-paper-2: oklch(13% 0.006 255);
  --color-paper-3: oklch(16% 0.006 255);
  --color-ink: oklch(94% 0.01 82);
  --color-ink-2: oklch(70% 0.014 82);
  --color-rule: oklch(27% 0.008 255);
  --color-accent: oklch(68% 0.15 246);
  --color-focus: oklch(76% 0.13 82);
  --font-display: "Geist", system-ui, sans-serif;
  --font-body: "Geist", system-ui, sans-serif;
  --font-outlier: "Geist Mono", ui-monospace, monospace;
  --spacing-sm: 0.75rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2.5rem;
  --text-md: 1.25rem;
  --text-xl: 1.9531rem;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --radius-card: 8px;
  --radius-pill: 999px;
}
```

### DTCG

```json
{
  "$schema": "https://design-tokens.github.io/community-group/format/",
  "color": {
    "paper": { "$value": "oklch(8% 0.006 255)", "$type": "color" },
    "ink": { "$value": "oklch(94% 0.01 82)", "$type": "color" },
    "accent": { "$value": "oklch(68% 0.15 246)", "$type": "color" },
    "focus": { "$value": "oklch(76% 0.13 82)", "$type": "color" }
  },
  "font": {
    "display": { "$value": "Geist, system-ui, sans-serif", "$type": "fontFamily" },
    "body": { "$value": "Geist, system-ui, sans-serif", "$type": "fontFamily" },
    "outlier": { "$value": "Geist Mono, ui-monospace, monospace", "$type": "fontFamily" }
  },
  "space": {
    "md": { "$value": "1rem", "$type": "dimension" },
    "xl": { "$value": "2.5rem", "$type": "dimension" }
  },
  "duration": {
    "micro": { "$value": "120ms", "$type": "duration" },
    "short": { "$value": "220ms", "$type": "duration" }
  }
}
```

### shadcn/ui

```css
:root {
  --background: 8% 0.006 255;
  --foreground: 94% 0.01 82;
  --card: 13% 0.006 255;
  --card-foreground: 94% 0.01 82;
  --primary: 68% 0.15 246;
  --primary-foreground: 8% 0.006 255;
  --muted: 27% 0.008 255;
  --muted-foreground: 70% 0.014 82;
  --border: 27% 0.008 255;
  --input: 27% 0.008 255;
  --ring: 76% 0.13 82;
  --radius: 8px;
}
```
