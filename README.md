# chisel

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/AdamMostofi/chisel)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Stars](https://img.shields.io/github/stars/AdamMostofi/chisel?style=flat)](https://github.com/AdamMostofi/chisel)

**A tool for carving away excess.**

Chisel is a disciplined engineering principle for AI agents. It injects a
decision ladder into every coding turn -- questioning whether code needs to
exist (YAGNI), leaving files cleaner than found (Boy Scout), reusing before
rewriting (DRY), and proving patterns before abstracting (Rule of Three).

Chisel is for developers who are tired of AI agents that generate
under-tested abstractions, speculative flexibility, library soup, and
class hierarchies for single-use code. It is for teams that want AI to
produce code that looks like a person wrote it -- deliberate, minimal,
correct.

---

## Before / After

### 1. Date picker

A date-of-birth input with age validation (must be 13+).

```
  WITHOUT CHISEL                          WITH CHISEL
  ───────────────                         ────────────
  <link href="flatpickr.css">             <label for="dob">Date of Birth</label>
  <script src="flatpickr.js"></script>    <input type="date" id="dob" name="dob"
  <input type="text" id="dob">                  max="2013-07-04" required>
  <script>
    flatpickr("#dob", {
      maxDate: new Date(),
      dateFormat: "Y-m-d",
      onChange: validateAge
    });
    function validateAge(dates) {
      // age calculation, error display...
    }
  </script>
```

- **52 lines** of HTML + CSS + JS + library dependency
- **5 lines** of HTML. Native platform feature. Zero JS. Zero dependencies.

### 2. Rate limiter

A decorator that limits function calls to N per time window.

```
  WITHOUT CHISEL                          WITH CHISEL
  ───────────────                         ────────────
  class RateLimitExceeded(Exception):     def rate_limit(calls=10, per=60):
      pass                                    lock = threading.Lock()
                                              timestamps = []
  class RateLimiter:                          def decorator(fn):
      def __init__(self, calls, per):             @wraps(fn)
          ...                                     def wrapper(*args, **kwargs):
      def acquire(self):                              with lock:
          with self._lock:                                ...
              ...                                     return fn(*args, **kwargs)
      def __call__(self, fn):                      return wrapper
          ...                                  return decorator

  def rate_limit(calls=10, per=60):
      ...
```

- **46 lines**, 3 imports, exception class, decorator class, factory, threading primitives
- **22 lines**, same imports, same behavior. Closure instead of class. No exception class (reuse built-in).

### 3. Order pipeline

A business-logic pipeline: order validation, tiered discounts, regional tax,
invoice output. Designed to tempt maximum over-engineering.

```
  WITHOUT CHISEL                          WITH CHISEL
  ───────────────                         ────────────
  5 dataclasses (OrderItem, Customer,     def process_order(order):
    Order, ProcessedOrder, CustomerTier)      if not order.get('items'):
  2 Enum classes                                 return None
  2 ABCs + 5 strategy subclasses             subtotal = ...
  2 factory classes                          discount = ...
  Validation pipeline with                   tax = ...
    dedicated validator classes              return { ... }
  InvoiceGenerator class
  OrderProcessor orchestration class        def process_orders(orders):
                                               return [r for o in orders
                                                       if (r := process_order(o))]
```

- **236 lines**, 7 imports, 41 abstractions, 206% overhead vs functionality
- **32 lines**, 1 import, 2 abstractions. Dicts instead of dataclasses. Functions instead of strategy pattern.

---

## How It Works

Chisel operates as a **two-pass system** on every coding turn.

### Pass 1 -- The Ladder

An 8-rung decision ladder. Stop at the first rung that holds. Climb
sequentially -- each rung filters out a class of over-engineering before
you reach for your editor.

```
1. YAGNI           Does this need to exist at all?
2. Boy Scout       Leave files cleaner than found.
3. DRY             Reuse what is already in the codebase.
4. Stdlib          Standard library has it?
5. Native          Platform feature covers it?
6. Installed dep   Already-installed package solves it?
7. One line        Can it be one line?
8. Minimum code    Write the minimum that works.
```

**Bug fix rule (attached to the ladder):** Fix the root cause, not the
symptom. Grep every caller of the function you are about to touch. One guard
in the shared function beats a guard in every caller.

### Pass 2 -- The Discipline Gate

A diff-driven audit that auto-runs after every write (in full mode). Scans
the actual diff for:

- **Touched files** -- were they left cleaner than found?
- **New abstractions** -- Rule of Three check (< 3 instances? warn).
- **New dependencies** -- could stdlib or native platform replace them?
- **`chisel:` comments** -- does each name a ceiling AND an upgrade path?

Outputs a structured report:

```
--- chisel discipline gate ---

[TOUCHED FILES]
  src/processor.py -- clean (deleted dead code path)
  src/types.py -- WARN: no improvements made

[NEW ABSTRACTIONS]
  WARN: CustomerTier enum created with 1 instance.
  Rule of Three: keep inline until 3+ instances.

[NEW DEPENDENCIES]
  FLAG: pandas added. Stdlib csv module covers this task.

[CHISEL COMMENTS]
  src/cache.py:10 -- chisel: in-memory cache,
  chisel: ceiling + upgrade path present.

[VERDICT]
  2 warnings. Review flagged items before proceeding.
```

### Modes

| Mode  | Pass 1 (Ladder) | Pass 2 (Gate)              | Trigger      |
|-------|-----------------|----------------------------|--------------|
| full  | Auto            | Auto after every write      | `/chisel`    |
| lite  | Auto            | Manual (`/chisel-gate`)    | `/chisel lite` |

---

## Benchmark Results

Analytical comparison of no-skill vs chiseled reference implementations for
7 tasks (6 simple + 1 complex business pipeline). Reference implementations
are hand-written to the same spec -- the difference is structural, not
functional.

### Combined (All 7 Tasks)

| Metric          | No-skill | Chiseled | Reduction |
|-----------------|----------|----------|-----------|
| Lines of code   | 567      | 104      | **-82%** |
| Tokens (est.)   | 3,588    | 944      | **-74%** |
| Dependencies    | 14       | 6        | **-57%** |
| Abstractions    | 64       | 8        | **-88%** |
| Complexity      | 140      | 31       | **-78%** |
| File size       | 15,954 B | 3,397 B  | **-79%** |

### Simple Tasks (6)

| Metric          | No-skill | Chiseled | Reduction |
|-----------------|----------|----------|-----------|
| Lines of code   | 331      | 72       | **-78%** |
| Tokens (est.)   | 2,259    | 550      | **-76%** |
| Dependencies    | 9        | 5        | **-44%** |
| Abstractions    | 23       | 6        | **-74%** |
| Complexity      | 71       | 17       | **-76%** |
| File size       | 9,610 B  | 2,145 B  | **-78%** |

### Complex Task (Order Pipeline)

| Metric          | No-skill | Chiseled | Reduction |
|-----------------|----------|----------|-----------|
| Lines of code   | 236      | 32       | **-86%** |
| Tokens (est.)   | 1,329    | 394      | **-70%** |
| Dependencies    | 5        | 1        | **-80%** |
| Abstractions    | 41       | 2        | **-95%** |
| Complexity      | 69       | 14       | **-80%** |
| File size       | 6,344 B  | 1,252 B  | **-80%** |

Results represent the ceiling of what chisel enables. Real LLM output varies
but converges toward these numbers. Methodology and reference implementations
in [benchmarks/](benchmarks/).

---

## Install

Add to your `opencode.json`:

```json
{ "plugin": ["@adammostofi/chisel"] }
```

Or point at a local checkout:

```json
{ "plugin": ["./path/to/chisel/.opencode/plugins/chisel.mjs"] }
```

---

## Commands

| Command               | What it does                                     |
|-----------------------|--------------------------------------------------|
| `/chisel`             | Report current mode (full, lite, or off).        |
| `/chisel full`        | Set full mode (ladder + auto discipline gate).   |
| `/chisel lite`        | Set lite mode (ladder only, manual gate).        |
| `/chisel off`         | Disable chisel.                                  |
| `/chisel-gate`        | Trigger discipline gate manually (lite mode).    |

---

## Why "chisel"?

A chisel is a tool for carving away everything that is not the solution.
Each strike is deliberate. You do not chisel blindly -- you read the grain
first (understand the problem), then carve.

The name reflects the philosophy: the best code is the code never written.
The best abstraction is the one you did not create until the pattern proved
itself across three real instances. You do not build for speculation. You
build for the shape that exists today, and you leave every file you touch
cleaner than you found it.

---

## FAQ

**Does this mean I can't write abstractions?**

No. It means prove the pattern first. The Rule of Three: 3+ concrete
instances before extracting shared code. One instance is a fact. Two is a
coincidence. Three is a pattern. Extract at three and let the friction
between the instances tell you what shape the abstraction should take.

**What about performance-critical code?**

The ladder picks edge-case-correct options. When two stdlib options are
equally terse, the tiebreaker is correctness on empty inputs, boundary
values, and edge states. Performance is not sacrificed -- unnecessary code
is removed. The code that remains does less, so it runs faster.

**What if I need the full version of something?**

Build it. The "When NOT to Carve" section explicitly exempts anything the
user asks for. If you say "I need the full configurable version," chisel
delivers it without re-arguing.

**Does this work with TypeScript / Python / Go / Rust?**

Yes. The ladder is language-agnostic. Stdlib means your language's standard
library. Native means your platform (browser, OS, database engine). The
principles apply to any code in any language.

**How is this different from a linter or formatter?**

Linters enforce syntax and style. Chisel enforces *structural discipline* --
whether code should exist at all, whether it is shaped correctly, whether
the abstractions are premature, whether the dependencies are necessary.
Chisel catches things linters cannot: YAGNI violations, missing `chisel:`
comments, and Rule of Three failures.

**Do I have to use every rung?**

No. Stop at the first rung that holds. If stdlib covers it (rung 4), you
never reach rungs 5-8. The ladder is a filter, not a checklist. Climb only
until you find your answer, then stop.

---

## Safety / When NOT to Carve

Never simplify away:

- **Input validation at trust boundaries** -- type checks, schema validation,
  sanitization at HTTP/file/env boundaries.
- **Error handling that prevents data loss** -- transaction rollback,
  partial-write safeguards, distinct catch blocks.
- **Security measures** -- authentication, authorization, rate limits, CSRF
  tokens, CSP headers, encryption, secrets management.
- **Accessibility basics** -- ARIA labels, keyboard navigation, focus
  management, color contrast, screen-reader semantics.
- **Anything the user explicitly requests** -- if the user says "I need
  the full version," build it. No re-arguing.
- **Hardware calibration knobs** -- real clocks drift, real sensors read
  off. Leave the calibration knob.

Never skip understanding the problem. The ladder shortens the solution,
never the reading. Trace the whole thing first -- every file the change
touches, the actual flow, the data that moves through it -- before picking
a rung. Disciplined laziness that skips comprehension is the dangerous kind:
it ships a confident wrong fix. Read fully, then carve.

---

## License

MIT. The shortest license that works.
