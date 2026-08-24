# Roadmap — asset-gen-framework

An index of where things live, not a summary of what they say. Read the docs themselves for
content.

## Framework Design.md

Covers the project-agnostic asset generation framework: what it is, how it is called, and its
plumbing.

- What this is
  - A CLI, driven by an agent
  - Called from another project's session
  - Language
  - fey-tactics
- The prompt manifest
  - One script, per-asset inputs are data
  - One entry is one call
  - Choosing a model
  - Sample images
  - Providing base assets to build from
  - Filenames
  - Format checking
- What it generates
  - What the framework does not generate
  - Sprite sheets
  - Video
  - Artistic consistency
  - Looping
- Drafts and approval
  - An authoring tool, not a build step
  - Drafts, then approval
- The record
  - The per-asset record
  - Regenerating, and leaving nothing behind
- Open Questions

See the design docs under `Docs/asset-gen-framework/` for actual content — this file is only a
map.
