# CLAUDE.md

Guidance for Claude Code (and other AI assistants) working in this repository.

## Status: empty repository

**As of 2026-08-05 this repository contains no code.** It has no commits on any
branch and no refs on the remote (`https://github.com/chayobi03-cyber/Ainative`);
this file is the initial commit.

Everything below marked **TBD** is a placeholder. Do **not** treat a TBD section
as fact, and do not invent content for it. Fill each one in from the actual code
once it exists — the first substantial change to this repo should include an
update to this file.

## Project overview

**TBD** — what "Ainative" is, who it is for, and what problem it solves.

## Repository structure

**TBD** — top-level directories and what belongs in each. Currently the tree is:

```
.
└── CLAUDE.md
```

## Tech stack

**TBD** — languages, runtime versions, frameworks, and package manager. Once a
manifest exists (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, …),
record the pinned versions here and keep them in sync.

## Development workflow

**TBD** — the real commands, verified by running them. At minimum document:

| Purpose | Command |
| --- | --- |
| Install dependencies | TBD |
| Run locally | TBD |
| Run tests | TBD |
| Run a single test | TBD |
| Lint / format | TBD |
| Type check | TBD |
| Build | TBD |

Only list commands that have actually been run successfully in this repo.

## Conventions

**TBD** — naming, module layout, error handling, logging, testing style, and any
house rules that are not obvious from reading a single file. Prefer documenting
conventions that are already visible in the code over inventing new ones.

## Git and branching

These are established for this repository and are **not** TBD:

- Branch from the default branch; never commit directly to it.
- AI-assistant work goes on the branch assigned for the task
  (e.g. `claude/<topic>-<suffix>`). Do not push to a different branch without
  explicit permission.
- Push with `git push -u origin <branch-name>`.
- Open a pull request only when explicitly asked.
- Commit messages: short imperative subject line, body explaining *why* when the
  change is not self-evident.

## Notes for AI assistants

- Verify before documenting. Read the code or run the command; do not describe
  behavior inferred from a file name.
- When a TBD section above becomes answerable, replace it in the same change
  that makes it answerable.
- Keep this file short and accurate. A stale instruction is worse than a missing
  one.
- Secrets, tokens, and internal hostnames never belong in this file or in commit
  messages.
