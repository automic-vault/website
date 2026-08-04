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
