# Agent Instructions

## Scope

Odin is Windows-focused Python desktop automation for Path of Exile. Preserve user control: do not start, click, or automate game actions unless user explicitly asks.

## Working Rules

- Keep changes small. Reuse existing modules and PySide6 patterns.
- Python requirement is 3.10+; retain compatible syntax.
- Keep runtime config (`userconfig.json`) and user-created JSON blueprints untracked.
- Run relevant checks after code changes. No automated test suite exists yet; at minimum compile changed Python files with `python -m py_compile <files>` when Python is available.
- Do not change pinned dependencies unless task requires it.

## Git Safety and Commit Workflow

1. Before changing files, record `git rev-parse HEAD` and inspect `git status --short`. If HEAD is unavailable or working tree has changes that must not be committed, stop and request direction. The recorded commit is the rollback point.
2. After verifying work, stage all intended changes with `git add -A` and create one descriptive commit. Format: `<type>: <concise change>` (example: `docs: add project guidance`).
3. Report commit hash and rollback command: `git revert <commit>` for a shared commit or `git reset --hard <previous-commit>` only when user confirms destructive local rollback.

## Change Log Rule

For every change made with Pi, add one entry under `## Unreleased` in `changelog.md` in same change. Include date, concise summary, files changed, and verification performed. Do not add entries for changes not made with Pi.
