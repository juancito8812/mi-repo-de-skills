---
name: interface-design
description: Craft-first interface design for dashboards, admin panels, SaaS apps, tools, settings pages, data interfaces, and interactive products. Use when designing, building, reviewing, auditing, or refining product UI where visual craft, layout hierarchy, tokens, states, visual direction, or design-system consistency matter. Not for marketing pages, landing pages, campaigns, or brand-only work.
version: "1.1.0"
license: MIT
metadata:
  author: juancito8812
---

# Interface Design

## Checklist

- [ ] Domain exploration done: domain, color world, signature, defaults
- [ ] Intent stated: who, what must they accomplish, how should it feel
- [ ] Focal point identified per view
- [ ] Type scale defined with ratio (1.2, 1.25, or 1.333)
- [ ] Color palette: ~60/30/10 distribution
- [ ] Squint test passed
- [ ] Signature test passed (could someone identify the product without the name?)
- [ ] Before writing each component: Intent + Hierarchy + Palette + Depth + Surfaces + Typography + Spacing stated

## System File Template

Save design decisions to `.interface-design/system.md`:

```markdown
# Design System — [Project Name]

## Intent
- **User**: [who, when, context]
- **Task**: [what they must accomplish]
- **Feel**: [3-5 words describing the emotional direction]

## Token System
### Colors
- `--surface`: [#hex] — [purpose]
- `--text-primary`: [#hex]
- `--accent`: [#hex]
- `--border`: [#hex]

### Typography
- Display: [typeface]
- Body: [typeface]
- Scale: [ratio], base [n]px

### Spacing
- Base unit: [4 or 8]px
- Density: [tight / default / airy]

## Signature Element
[The one thing this interface will be remembered by]

## Structure
[Brief description of layout approach]
```

## (Rest of the skill content follows — see below)

Build product interfaces with the craft of a top design team — Linear, Vercel, Stripe, Apple. The difference between those and generic output is not talent. It is that every decision was *decided*, the hierarchy is unmistakable, and a hundred small details are correct at once. This skill is how you get there.

## Scope

**Use for:** Dashboards, admin panels, SaaS apps, tools, settings pages, data interfaces.
**Not for:** Landing pages, marketing sites, campaigns, brand-only work.

## The Problem

You will generate generic output. Your training has seen thousands of dashboards, and the patterns are strong. You can follow this entire process — explore the domain, name a signature, state your intent — and still produce a template: warm colors on cold structures, friendly fonts on generic layouts.

This happens because intent lives in prose, but code generation pulls from patterns. The gap between them is where defaults win. Process helps, but it doesn't guarantee craft. You have to catch yourself, and you have to know the concrete moves that defaults don't.

**The bar:** If another AI, given a similar prompt, would produce substantially the same output, you have failed. Not different for its own sake — different because the interface emerged from *this* user, *this* task, *this* world.

## Where Defaults Hide

Defaults disguise themselves as infrastructure — the parts that feel like they just need to work, not be designed.

- **Typography feels like a container.** But type isn't holding your design, it *is* your design. The weight of a headline, the personality of a label, the texture of a paragraph shape how the product feels before anyone reads a word.
- **Navigation feels like scaffolding.** But navigation *is* the product — where you are, where you can go, what matters. A page floating in space is a component demo, not software.
- **Data feels like presentation.** But a number on screen is not design. What does it *mean* to the person looking?
- **Token names feel like implementation detail.** But `--ink` and `--parchment` evoke a world; `--gray-700` and `--surface-2` evoke a template.

## Intent First

Before touching code, answer these:

- **Who is this human?** Not "users." The actual person. Where are they when they open this?
- **What must they accomplish?** The verb. Grade these submissions. Find the broken deployment.
- **What should this feel like?** In words that mean something. "Clean and modern" means nothing.

**Intent must be systemic.** Saying "warm" then using cold colors is not following through. Check every token against the stated intent.

## Product Domain Exploration

Produce all four before proposing any direction:

- **Domain** — concepts, metaphors, vocabulary. Minimum 5.
- **Color world** — what colors exist *naturally* here? List 5+.
- **Signature** — one element that could only exist for THIS product.
- **Defaults** — 3 obvious choices you must avoid.

## Visual Hierarchy & Composition

### One focal point per view
Every screen has one thing the user came to do. That thing dominates — through size, contrast, position, or the space around it.

### Type scale is a ratio, weight beats size
Pick a ratio and step it: ~1.2 (dense), ~1.25 (most product UI), ~1.333 (expressive). A 14px base at 1.25: caption 11 · body 14 · h4 16 · h3 18 · h2 22 · h1 28 · display 44+.

### Density is a decision
Name the values: tool panel at 12-16px padding feels tight; same card at 24px feels like a brochure.

### Proportions speak
A 280px sidebar vs 360px sidebar declares different relationships. If you can't articulate what a proportion is saying, it isn't saying anything.

### Distribution: ~60/30/10
A dominant neutral surface, a secondary tone, and ~10% accent.

## Craft Foundations

**Surface elevation.** Build a numbered system — base, then increasing levels. Each jump is only a few percentage points of lightness.

**Borders.** Low-opacity rgba blends with background; solid hex borders look harsh.

**The squint test:** blur your eyes at the interface. You should still perceive hierarchy — what's above what, where sections divide — but nothing should jump out.

## Before Writing Each Component

State these before writing UI code:

```
Intent:
Hierarchy:
Palette:
Depth:
Surfaces:
Typography:
Spacing:
```

If you can't explain WHY for each, you're defaulting.

## Use What Exists

**Controls: native → primitive → hand-roll.** Native HTML first. Headless primitives second (Radix, React Aria, Ark). Hand-roll last.

**Styling: system → component → token → utility.** If the project has a design system, use it.

## Design System Essentials

- Token architecture: every color traces to primitives
- Text hierarchy: primary, secondary, tertiary, muted
- Spacing: base unit (4 or 8px), multiples only
- Depth: choose ONE (borders, shadows, layered, surface-color shifts)
- Border radius scale
- Dark mode: shadows are weak on dark — lean on borders

## Polish & Motion

- Concentric radius: outer = inner + padding
- Tabular numbers on dynamic values
- States: default, hover, active, focus, disabled, loading, empty, error
- Hit areas: 44×44px minimum
- Motion: duration <300ms, custom ease-out, only transform + opacity

## Workflow

1. Inspect existing app, tokens, components, and `.interface-design/system.md` if present
2. Domain exploration (domain, color world, signature, defaults)
3. Propose direction → confirm
4. Build → run checks (swap test, squint test, signature test, token test)
5. Save to `.interface-design/system.md`

## Exit Criteria

- [ ] Intent stated and verifiable in every token
- [ ] Signature element named and implemented
- [ ] Squint test: hierarchy visible without reading
- [ ] Token system documented in `.interface-design/system.md`
- [ ] All states handled (default, hover, active, focus, disabled, loading, empty, error)
