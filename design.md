# Design — Automic Vault

The shared system below remains the baseline for content and translated pages.
All five homepages use the explicitly requested Tinycast direction described
at the end of this document.

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

## Homepage narrative

The landing page presents five outcomes: command-line protection, per-Launcher
policy, reviewed agent capabilities, Project Values, and Approval across Macs.
Use real screenshots for product proof, without drawn interface mockups. The
command-line section uses a compact terminal card with a keyboard-accessible copy
button, visible copy feedback, and a smaller, dimmer sandbox explanation. Preserve the
security qualification beside each outcome and keep translated homepages and
alternate text formats aligned. Japanese copy uses a plain polite register with
Japanese-capable system fonts; canonical product terms remain recognizable.


## English homepage direction · September 2026

Reference: <https://abue-ammar.github.io/tinycast/#gallery>.
The requested redesign uses a centered hero, a dotted black canvas, purple pill
CTAs, restrained Geist typography, and rounded screenshot galleries.
`www/homepage.css` owns its runtime tokens: canvas #040506, surface #0b0c0e,
ink #f5f5f6, muted #a1a1a6, rule #242428, accent #803bfa, and bright accent #af85ff.
Display type is Geist 600 with −0.045em tracking; utility labels use Geist Mono.
It replaces the older homepage stylesheets on all five language routes.

Keep the existing product explanations and security boundaries beneath the
experimental headlines. “Full access” describes the agent's execution mode,
not AV's Full Access preset. Keep that distinction next to the headline.
The hero demonstration is explicitly illustrated HTML, loops through Terminal/AWS and
Claude Code/SSH/GitHub scenes, holding each pending Approval for five seconds.
It pauses offscreen or in a hidden tab, offers pause/resume, and presents static
scenes with a Next control for reduced motion. Without JavaScript the AWS
Approval remains visible. SSH uses Allow Authentication policy, not Read Only;
that policy does not restrict remote commands or destinations. Each product screenshot appears once;
the Approval capture is large and links to its original size.
Japanese, German, French, and Simplified Chinese homepages share this layout.
Keep canonical product and policy names recognizable; translate demo narration,
controls, and authorization messages. Commands and captured product UI stay verbatim.


The section before the demo on all five homepages shows the GitHub hardening transformation
and pairs it with the same-token read/write/disclosure comparison. Place the
Homebrew proof first in the supporting row, followed by AWS and Docker. The
scanner follows the demo. Pair one large Approval capture with the Blessed Scripts explanation.
Hardening establishes the protected path; runtime Authorization Gates enforce
credential requests. Do not imply every process execution is intercepted.

Claude Code’s illustrated scene uses a warm terminal palette, a user request, a
brief planning message, a Thinking state, and Bash tool calls with indented output.
Commands appear as tool invocations; the Terminal scene retains typed shell input.

The demo ends at its playback controls; omit the policy-scope and illustration captions.

All five homepages use the packaging-led positioning: “CLI security
is broken. The packaging layer is where we fix it.” Pair it with Max Howell’s
first-person Homebrew founder line and concrete supported-tool coverage. Link his
name to About, which explains how installation connects to inherited authority.
Highlight the second headline sentence using the existing hero treatment.
The operation comparison shows why the same token needs separate decisions.
Translated homepages and About pages follow the English narrative. Keep curated
headlines aligned with the localization data and section order aligned with English.
Japanese uses a polite register for a global developer audience; native editorial
review of the September 21 acquisition copy remains outstanding.

Homepage Japanese and Simplified Chinese use platform sans-serif fallbacks;
Japanese emphasis uses color or weight, without synthetic italics.

The hero keeps its headline, supporting copy, and actions on one central axis.
A centered overview screenshot sits underneath at up to 624px wide, linked to the
original lossless WebP. Reduced top spacing brings the preview into the first screen.
