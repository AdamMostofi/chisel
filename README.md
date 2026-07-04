# Chisel

<p align="center">
  <em>A tool for carving away excess.</em>
</p>

Chisel is a disciplined engineering principle for AI agents. It injects a decision ladder into every coding turn — questioning whether code needs to exist (YAGNI), leaving files cleaner than found (Boy Scout), reusing before rewriting (DRY), and proving patterns before abstracting (Rule of Three).

## How it works

### Pass 1 — The Ladder
An 8-rung decision ladder that finds the shortest correct path. Stop at the first rung that holds:

```
1. YAGNI → 2. Boy Scout → 3. DRY (reuse) → 4. Stdlib →
5. Native → 6. Installed dep → 7. One line → 8. Minimum code
```

### Pass 2 — The Discipline Gate
A diff-driven audit that auto-runs after every write (in full mode). Scans the actual diff for: files left cleaner, premature abstractions (Rule of Three), unnecessary dependencies, and proper `chisel:` comments.

## Modes

| Mode | Ladder | Gate | Trigger |
|------|--------|------|---------|
| **full** (default) | Auto | Auto | `/chisel` |
| **lite** | Auto | Manual (`/chisel-gate`) | `/chisel lite` |

## Install

OpenCode: add to `opencode.json`:

```json
{ "plugin": ["@adammostofi/chisel"] }
```

Or point at a local checkout:

```json
{ "plugin": ["./path/to/chisel/.opencode/plugins/chisel.mjs"] }
```

## License

MIT
