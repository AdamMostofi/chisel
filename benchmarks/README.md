# Chisel Benchmark

This directory contains benchmark suites that measure chisel's impact on code quality.

## Methodology

### Analytical Benchmark

For each task, reference implementations are written by hand in two versions:

- **no-skill**: What a typical LLM produces without discipline rules — class hierarchies, strategy patterns, factories, abstract base classes, argument parsers, config objects, deep error hierarchies, verbose docstrings.

- **chiseled**: The same task solved with chisel's ladder — minimum code that works, stdlib/native first, no premature abstractions, no unnecessary deps, Boy Scout cleanliness, `chisel:` comments documenting shortcuts.

Both implement the exact same requirements and edge cases. The difference is structural, not functional.

### Why Analytical (Free) Over LLM Eval

| Approach | Cost | Reproducibility | Signal |
|----------|------|-----------------|--------|
| LLM eval | API costs per run | Model-dependent, noisy | Stochastic |
| **Analytical** | **Free** | **Perfect** | **Clean directional signal** |

The numbers represent the ceiling of what chisel enables. Real LLM results vary but the direction is proven.

### Metrics

| Metric | How measured |
|--------|-------------|
| **Lines of code** | Total lines (comments + blanks + code) |
| **Tokens (est.)** | Word count + punctuation clusters |
| **Dependencies** | Import/require/include statements |
| **Abstractions** | Class + interface + exported function definitions |
| **Complexity** | Branch count (if/for/while/and/or/case/catch/ternary) |
| **File size** | UTF-8 byte count |

## Results

### Simple Tasks (6 tasks)

| Metric | No-skill | Chiseled | Reduction |
|--------|----------|----------|-----------|
| Lines of code | 331 | 72 | **-78%** |
| Tokens (est.) | 2,259 | 550 | **-76%** |
| Dependencies | 9 | 5 | **-44%** |
| Abstractions | 23 | 6 | **-74%** |
| Complexity | 71 | 17 | **-76%** |
| File size | 9,610 bytes | 2,145 bytes | **-78%** |

### Complex Task — Order Pipeline (1 task)

A multi-concern business logic pipeline: order validation, tiered discounts (bronze/silver/gold), regional tax calculation, invoice output. Designed to tempt maximum over-engineering.

| Metric | No-skill | Chiseled | Reduction |
|--------|----------|----------|-----------|
| Lines of code | 236 | 32 | **-86%** |
| Tokens (est.) | 1,329 | 394 | **-70%** |
| Dependencies | 5 | 1 | **-80%** |
| Abstractions | 41 | 2 | **-95%** |
| Complexity | 69 | 14 | **-80%** |
| File size | 6,344 bytes | 1,252 bytes | **-80%** |

### Combined (All 7 tasks)

| Metric | No-skill | Chiseled | Reduction |
|--------|----------|----------|-----------|
| Lines of code | 567 | 104 | **-82%** |
| Tokens (est.) | 3,588 | 944 | **-74%** |
| Dependencies | 14 | 6 | **-57%** |
| Abstractions | 64 | 8 | **-88%** |
| Complexity | 140 | 31 | **-78%** |
| File size | 15,954 bytes | 3,397 bytes | **-79%** |

## How to Run

### Analytical benchmark (free, instant, no API key needed)
```bash
python3 score.py
```

### LLM eval via promptfoo (requires API key)
```bash
npm install -g promptfoo
promptfoo eval
promptfoo view
```

## Tasks

### Simple tasks

| # | Task | Language | What it stresses |
|---|------|----------|-----------------|
| 1 | Email validator | Python | YAGNI, stdlib reuse |
| 2 | Debounce function | TypeScript/JS | Minimum code, one-liner |
| 3 | CSV sum script | Python | Stdlib (csv module), no-opinion-parser |
| 4 | Countdown timer | JS | Platform features (setTimeout) |
| 5 | Rate limiter | Python | Minimum ceremony, threading reuse |
| 6 | Date picker | HTML | Native platform (&lt;input type=&quot;date&quot;&gt;) |

### Complex task

| # | Task | Language | What it stresses |
|---|------|----------|-----------------|
| 7 | Order pipeline | Python | Multi-concern: validation, discounts, tax, reporting — full business logic tempts over-engineering |

## File Structure

```
benchmarks/
├── README.md                         # This file — methodology + results
├── score.py                          # Analytical benchmark scorer
├── promptfooconfig.yaml              # LLM eval config (when API keys available)
├── run-benchmark.sh                  # LLM eval runner
├── tasks/                            # LLM eval task prompts
│   ├── 01-email-validator.txt        # to 06-date-picker.txt
├── reference/                        # Reference implementations (analytical)
│   ├── 01-email-validator-no-skill.py
│   ├── 01-email-validator-chiseled.py
│   ├── ...
│   ├── 07-order-pipeline-no-skill.py
│   └── 07-order-pipeline-chiseled.py
└── results/                          # Generated output
    └── analytical-benchmark.json
```

## Limitations

- **Aspirational**: Chiseled versions represent ideal output. Real LLM behavior varies, but converges toward these numbers.
- **Language bias**: Results are Python/JS/HTML heavy.
- **Selection bias**: Tasks chosen to highlight chisel's strengths.
