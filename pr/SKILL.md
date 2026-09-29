---
name: pr
description: Review changes and publish a draft PR. Use when asked to create or update a pull request.
---

## Preflight

- Run bundled `bash scripts/pr-preflight` from the target worktree before review; publication runs its own preflight.
- For a default or spent branch, carry only intended commits onto a fresh branch from the reported base.
- Publish only to the current branch's writable remote. Do not switch to a parent/upstream repository or create/sync a fork unless explicitly asked.

## Review

- Using the preflight base and head, review the prospective commits and complete `base...head` diff for scope and actionable issues.
- Fix and report findings within the authorized scope and commit the fixes. Ask when resolution requires a material scope decision; report unresolved blockers without publishing.
- Run repository checks with CI-equivalent options when available; reuse passing results for the same revision when applicable. Expected visual changes need scoped assertions, not blanket bypasses.
- For UI changes, follow [UI evidence](references/ui-evidence.md).
- If the reviewed revisions change, repeat the affected review, checks, and UI captures before publication.

## Package

- Use the repo PR template exactly when present.
- When repo conventions are unclear, consult recently merged PRs or history for vocabulary, scope, and level of detail.
- Title: `<type>(<scope>): <plain-language outcome>`. Explain the complete change's value to an unfamiliar reviewer without relying on the description. Use familiar repository terms and the narrowest Conventional Commits type; omit unhelpful scope and reserve `style` for formatting only.
- Add issue-closing syntax when the change resolves an issue.
- Omit generic command output.
- Without a template, use `## Purpose`, `## Solution`, and `## Verification` for substantive changes: explain the need, approach, relevant trade-offs, and evidence. A short paragraph is enough for trivial changes.

## Publish / Update

- Read the current draft description and preserve relevant content when updating. Publish with `bash scripts/pr-publish REVIEWED_BASE REVIEWED_HEAD TITLE < /tmp/pr-body.md`.
- Wait for required checks on the published head. Fix failures caused by the change, commit, and return to Review.
- Publish drafts by default. Mark ready or merge only when explicitly requested; reviewer requests, auto-merge, and review submissions require separate authorization.
- Return the PR URL, verification status, and unresolved blockers.
