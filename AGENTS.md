# Chisel — A tool for carving away excess

Disciplined engineering principle for AI agents. Before writing any code, stop at the first rung that holds:

1. **Does this need to exist at all?** Speculative need = skip it. (YAGNI)
2. **Boy Scout** — If touching existing files: leave every file cleaner than you found it. Rename one variable, delete dead code, split one long function.
3. **Already in this codebase?** A helper, util, type, or pattern already here → reuse it. (DRY: same *knowledge* lives once. Lookalike code that means different things stays separate.)
4. **Stdlib does it?** Use it.
5. **Native platform feature covers it?** `<input type="date">` over a picker lib, CSS over JS, DB constraint over app code.
6. **Already-installed dependency solves it?** Use it. Never add a new one for what a few lines can do.
7. **Can it be one line?** One line.
8. **Only then:** the minimum code that works.

**Bug fix = root cause, not symptom.** Grep every caller of the function you're about to touch. One guard in the shared function beats a guard in every caller. Fix it once where all callers route through.

The ladder is a reflex, not a research project — but it runs *after* you understand the problem, not instead of it. Read the task and the code it touches first, trace the real flow end to end, then climb.

## The Discipline Gate (Pass 2)

After writing code, scan the diff for:

- **Touched files** — leave cleaner than found. Delete dead code, tighten loose patterns.
- **New abstractions** — Rule of Three check. No interface with one implementation, no factory for one product, no config for a value that never changes.
- **New dependencies** — stdlib/native check. Every new dependency must survive this audit.
- **`chisel:` comments** — verify each names a ceiling *and* an upgrade path.
- **Verdict** — ship if clean; revise if any check fails.

## Rules

- No unrequested abstractions.
- No boilerplate, no scaffolding "for later."
- Deletion over addition. Boring over clever.
- Fewest files possible. Shortest working diff wins.
- Complex request? Ship the chiseled version and ask: "Did X; Y covers it. Need full X? Say so."
- Two stdlib options, same size? Pick the one correct on edge cases.
- Mark deliberate shortcuts with `chisel:` comment.

## Safety Boundaries

Never chisel away: input validation at trust boundaries, error handling that prevents data loss, security measures, accessibility basics, anything explicitly requested. If the user insists on the full version → build it, no re-arguing.

Never chisel on understanding. Read fully, trace the whole thing first, then carve. Laziness that skips comprehension to ship a small diff is the dangerous kind — it dresses up as efficiency and ships a confident wrong fix.

Hardware needs calibration knobs — a real clock drifts, a real sensor reads off. Leave the knob.

## Tests

Non-trivial logic (a branch, a loop, a parser, a money/security path) leaves ONE runnable check behind — the smallest thing that fails if the logic breaks. An `assert`-based self-check (`if __name__ == "__main__":`) or one small test file. No frameworks, no fixtures, no per-function suites unless asked. Trivial one-liners need no test.

## Comment Convention

All deliberate shortcuts use a `chisel:` prefix. Every `chisel:` comment must name the ceiling and the upgrade path:

```python
# chisel: global lock, per-account locks if throughput matters
# chisel: O(n²) scan, index if table exceeds 10K rows
# chisel: hardcoded timeout, make configurable if callers need different values
```
