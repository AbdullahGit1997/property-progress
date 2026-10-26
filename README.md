# Property Progress

A small Python command-line tool that turns a fictional property transaction checklist into a clear progress update. Built as a portfolio exercise inspired by Homey's Junior Software Engineer (AI-Native) role. Independent demo; not affiliated with Homey.

## Why this project

Buyers need to know what is outstanding and who to follow up with. This tool shows completed milestones, flags overdue items, and suggests a next action from the earliest outstanding deadline. It demonstrates a small feature delivered end to end: data validation, business rules, persistent updates, useful output, and tests.

## Run it

Requires Python 3.10 or later. No dependencies, accounts, or API keys.

```sh
python tracker.py example.json --today 2026-10-26
```

On Windows, use `py` instead of `python` if that is how Python is installed.

```text
Property: 12 Sample Lane (fictional)
As of: 2026-10-26
Progress: 1/4 milestones complete

[OVERDUE] searches: Search update received | Solicitor | due 2026-10-23
[PENDING] mortgage: Mortgage offer received | Broker | due 2026-10-28
[PENDING] enquiries: Enquiry update received | Solicitor | due 2026-10-30

Next action: Follow up with Solicitor about search update received.
Demo checklist only; milestone completion does not confirm legal readiness.
```

Copy `example.json` to `my-case.json` to experiment without changing the fixture. Mark a task complete:

```sh
python tracker.py my-case.json --complete searches --today 2026-10-26
python -m unittest -v
```

Without `--today`, the tool uses the current local date. A task is overdue only when its deadline is before that date. Completing a task saves it to the input JSON file. Unknown IDs fail without changing the file. Writes replace the file after preparing the complete JSON.

## Design choices and limits

- Standard library only: easy for a reviewer to run and understand.
- JSON storage: sufficient for a single-user demo; no concurrent editing support.
- Deterministic summaries: no LLM calls. The AI experience demonstrated is the development workflow, not an AI feature inside the product.
- Dates and milestones are fictional, manually supplied examples. This is not a conveyancing workflow or legal readiness assessment.
- Deadline order is a simple follow-up heuristic. It does not model dependencies or the importance of individual tasks.

## How AI was used

Codex helped interpret the brief, choose a small scope, and generate the implementation, tests, and documentation in this session. See [AI_WORKFLOW.md](AI_WORKFLOW.md). This initial version is AI-assisted work; before presenting it, I should run it, understand the code, and make a change I can explain.

## Suggested next change

Add a `--reopen TASK_ID` command, with a test proving a completed milestone becomes pending again. This is a small, useful improvement to make independently and discuss in an interview.

## Publish on GitHub

Create an empty GitHub repository named `property-progress`, then run these commands from this folder, replacing `YOUR_USERNAME`:

```sh
git init
git add .
git commit -m "Build property progress tracker with tested milestone updates"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/property-progress.git
git push -u origin main
```

## Interview walkthrough

1. Explain the user problem: visibility of outstanding property milestones.
2. Run the example with a fixed date to show a reproducible result.
3. Complete `searches` in a copy and explain how the next action changes.
4. Run the tests and explain the deadline boundary and invalid-ID case.
5. Explain what AI generated, what you checked yourself, and what you would improve.
