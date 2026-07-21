# Product

## Register

product

## Users

Developers, QA engineers, and students who need realistic fake data fast — to seed a database, test an API, build a demo, or complete a class assignment. They reach for this instead of hand-rolling fixtures or paying for a data-generation SaaS. They use it three ways: a CLI for scripting, a REST API for integration, and a web UI for one-off generation. Many will read the source or self-host it rather than use a hosted instance.

## Product Purpose

SynGen is a free, open-source synthetic data generator. It produces realistic structured data (35+ field types spanning general, call-center, and demographic categories) in CSV, JSON, or SQL, and can also learn a schema from a real Kaggle dataset and generate a synthetic clone of it. It exists as a straightforward, no-cost, self-hostable utility — not a funnel toward a paid tier. Success looks like: a developer gets from "I need test data" to a working export in under a minute, with no account friction, no upsell, and no ambiguity about cost or limits.

## Brand Personality

Minimal, quiet, precise. Talks like a tool built by an engineer for engineers: no marketing gloss, no hype adjectives, no invented urgency. Confidence comes from showing real output (actual CLI runs, actual JSON/CSV/SQL), not from claims. Copy is plain and factual over persuasive.

## Anti-references

Explicitly not this:
- Generic Bootstrap-template SaaS landing pages: icon-in-tinted-circle feature grids, badge-pill chips scattered everywhere, rocket-takeoff/lightning-bolt stock icon sets, card-hover-lift micro-interactions applied uniformly to everything.
- SaaS pricing/tier framing of any kind — "free tier," "N requests/day" as a marketed limit, "$0/mo" pricing-card treatment, "Create Free Account" as a repeated CTA pattern. This is not a product with tiers; it's open-source software.
- A CTA section repeated at the bottom of every page. One clear call to action per page, in the hero, and no more.
- Decorative gradients, glassmorphism, or gradient text used for emphasis instead of real content.

## Design Principles

- **Show, don't badge.** Real terminal sessions, real command output, real code samples carry the page — not icon grids or badges standing in for substance.
- **One page, one action.** Every page has exactly one primary call to action, placed once, in the hero.
- **No SaaS framing.** No tiers, no pricing cards for "free," no account-gated value proposition. It's software you run, not a service you subscribe to.
- **Plain over persuasive.** Copy states what the tool does; it doesn't sell.
- **Respect the existing stack.** Flask/Jinja2 templates, existing routes and blocks stay intact — this is a visual/content layer redesign, not a framework migration.

## Accessibility & Inclusion

Standard WCAG AA: body text ≥4.5:1 contrast, large/bold text ≥3:1, full keyboard navigation, visible focus states, and `prefers-reduced-motion` alternatives for any animation.
