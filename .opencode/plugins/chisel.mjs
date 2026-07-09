// chisel — OpenCode plugin.
//
// Injects the chisel ruleset into every chat's system prompt at the active
// level, persists /chisel mode switches, and registers /chisel-gate for
// manual discipline-gate invocation in lite mode.
//
// OpenCode loads this as a server plugin — add it to your opencode.json:
//   { "plugin": ["chisel"] }
// or point plugin.paths at the .opencode/plugins directory.

import fs from 'fs';
import os from 'os';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// --- persistent state -------------------------------------------------------
// Stored beside OpenCode's own config so mode survives across turns.

const statePath = path.join(
  process.env.XDG_CONFIG_HOME || path.join(os.homedir(), '.config'),
  'opencode',
  '.chisel-state.json',
);

const MODES = new Set(['full', 'lite', 'off']);
const DEFAULT = 'full';

function readState() {
  try {
    return JSON.parse(fs.readFileSync(statePath, 'utf8'));
  } catch {
    return { mode: DEFAULT, gatePending: false };
  }
}

function writeState(s) {
  fs.mkdirSync(path.dirname(statePath), { recursive: true });
  fs.writeFileSync(statePath, JSON.stringify(s, null, 2));
}

function currentMode() {
  // Environment variable wins (persistent default across sessions).
  const env = process.env.CHISEL_DEFAULT_MODE;
  if (env && MODES.has(env.toLowerCase())) return env.toLowerCase();
  return readState().mode;
}

// --- instruction builder ----------------------------------------------------
// Three sources, tried in order:
//   1.  SKILL.md from the chisel package (full detail)
//   2.  Inline fallback (compact, always available)
//
// For lite mode (without a pending gate) the Discipline Gate section is
// removed from the body so the agent doesn't auto-run it.

function stripFrontmatter(str) {
  return str.replace(/^---[\s\S]*?---\r?\n?/, '');
}

function buildInstructions(mode, gatePending) {
  if (mode === 'off') return '';
  const prefix = `CHISEL MODE ACTIVE — level: **${mode}**\n\n`;
  const skillPath = path.resolve(__dirname, '../../skills/chisel/SKILL.md');
  try {
    let body = stripFrontmatter(fs.readFileSync(skillPath, 'utf8'));
    if (mode === 'lite' && !gatePending) {
      // Strip the Discipline Gate section for plain lite mode.
      body = body.replace(/## The Discipline Gate \(Pass 2\)[\s\S]*?(?=\n## )/, '');
    }
    if (gatePending) {
      // Annotate the gate so the agent knows it was explicitly triggered.
      body = body.replace(
        /^## The Discipline Gate \(Pass 2\)/m,
        '## The Discipline Gate (Pass 2) — triggered via /chisel-gate',
      );
    }
    return prefix + body;
  } catch {
    return prefix + fallbackBody(mode, gatePending);
  }
}

function fallbackBody(mode, gatePending) {
  const ladder =
    '## The Ladder (Pass 1)\n\n' +
    'Before any code, stop at the first rung that holds ' +
    '(the ladder runs after you understand the problem, not instead of it):\n' +
    '1. **YAGNI** — Does this need to exist? Speculative need = skip it.\n' +
    '2. **Boy Scout** — Leave every file you touch cleaner than you found it.\n' +
    '3. **DRY** — Already in this codebase? Reuse it before rewriting.\n' +
    '4. **Stdlib** — Does the standard library do it? Use it.\n' +
    '5. **Native** — Does a native platform feature cover it? Use it.\n' +
    '6. **Installed dep** — Already-installed dependency? Use it. Never add a new one for a few lines.\n' +
    '7. **One line** — Can it be one expression? One line.\n' +
    '8. **Minimum code** — Only then: write the minimum that works.\n\n' +
    '**Bug fix = root cause, not symptom.** Grep every caller of the function ' +
    'you touch. Fix the shared function once — one guard there beats one per caller.';

  const gate =
    gatePending
      ? '## The Discipline Gate (Pass 2) — triggered via /chisel-gate\n\n' +
        'After writing code, scan the diff for:\n' +
        '- **Touched files** — leave cleaner than found. Delete dead code, tighten loose patterns.\n' +
        '- **New abstractions** — Rule of Three check. No interface with one implementation.\n' +
        '- **New dependencies** — stdlib/native check. Every new dep must survive audit.\n' +
        '- **`chisel:` comments** — each names a ceiling AND an upgrade path.\n' +
        '- **Verdict** — ship if clean; revise if any check fails.\n' +
        '```\n--- chisel discipline gate ---\n[TOUCHED FILES]\n[NEW ABSTRACTIONS]\n[NEW DEPENDENCIES]\n[CHISEL COMMENTS]\n[VERDICT]\n```'
      : '';

  const rules =
    '## Rules\n\n' +
    '- **No unrequested abstractions.** No interface with one implementation, ' +
    'no factory for one product, no config for a value that never changes.\n' +
    '- **No new dependency if stdlib or native platform covers it.**\n' +
    '- **No boilerplate, no scaffolding "for later."**\n' +
    '- **Deletion over addition. Boring over clever.**\n' +
    '- **Fewest files possible.**\n' +
    '- **Mark deliberate shortcuts** with `chisel:` comment that names the ' +
    'ceiling AND the upgrade path.\n' +
    '- **Two same-size stdlib options?** Pick the one correct on edge cases.';

  const output =
    '## Output Conventions\n\n' +
    'Code first. Then at most three short lines: what was skipped, when to add it. ' +
    'If the explanation is longer than the code, delete the explanation. ' +
    'Explanation the user explicitly asked for (report, walkthrough) is not debt — give it in full.\n' +
    'Pattern: `[code] → chisel: skipped [X], add when [Y].`';

  const safety =
    '## When NOT to Carve\n\n' +
    'Never simplify away: input validation at trust boundaries, error handling ' +
    'that prevents data loss, security measures, accessibility basics, hardware ' +
    'calibration knobs, anything the user explicitly requested.\n' +
    'Never skip understanding the problem. Read fully, trace the real flow, ' +
    'then carve. A small diff you do not understand is not discipline, ' +
    'it is a confident wrong fix.';

  const tests =
    '## Tests\n\n' +
    'Non-trivial logic (a branch, a loop, a parser, a money/security path) ' +
    'leaves ONE runnable check behind: an assert-based self-check ' +
    '(`if __name__ == "__main__":`) or one small test file. ' +
    'No frameworks, no fixtures. Trivial one-liners need no test.';

  const boundaries =
    '## Boundaries\n\n' +
    'Chisel governs what you build, not how you talk. ' +
    '"stop chisel" / "normal mode": revert to no discipline. ' +
    'Level persists until changed or session end.\n' +
    'The shortest path to done is the right path.';

  const parts = [ladder];
  if (gate) parts.push(gate);
  parts.push(rules, output, safety, tests, boundaries);
  return parts.join('\n\n');
}

// --- plugin export ----------------------------------------------------------
export default async ({ client } = {}) => {
  const log = (level, message) => {
    try {
      client &&
        client.app &&
        client.app.log({ body: { service: 'chisel', level, message } });
    } catch {
      // client.app.log is optional; ignore when unavailable.
    }
  };

  return {
    // Register the skills directory and slash commands so OpenCode discovers
    // skills/chisel/SKILL.md and shows /chisel /chisel-gate in the TUI palette.
    config(cfg) {
      cfg.skills = cfg.skills || {};
      cfg.skills.paths = cfg.skills.paths || [];
      const skillsDir = path.resolve(__dirname, '../../skills');
      if (!cfg.skills.paths.includes(skillsDir)) {
        cfg.skills.paths.push(skillsDir);
      }
      // Register slash commands so they appear in the TUI command palette.
      cfg.command = cfg.command || {};
      cfg.command.chisel = cfg.command.chisel || {
        template: '',
        description: 'Report or set chisel mode (full, lite, off)',
      };
      cfg.command['chisel-gate'] = cfg.command['chisel-gate'] || {
        template: '',
        description: 'Trigger discipline gate manually (lite mode)',
      };
    },

    // Prepend chisel rules to the system prompt every turn.
    async 'experimental.chat.system.transform'(_input, output) {
      const env = process.env.CHISEL_DEFAULT_MODE;
      const state = readState();
      const mode = (env && MODES.has(env.toLowerCase()))
        ? env.toLowerCase()
        : state.mode;
      if (mode === 'off') return;

      const gatePending = state.gatePending;
      if (gatePending) {
        // Clear the flag after reading — the gate instructions are now in the
        // prompt and the agent will act on them this turn.
        writeState({ mode, gatePending: false });
      }

      (output.system = output.system || []).push(
        buildInstructions(mode, gatePending),
      );
    },

    // Persist mode changes, handle /chisel-gate, and prevent LLM round-trip.
    async 'command.execute.before'(input, output) {
      if (!input || !input.command) return;

      const sendIgnored = async (text) => {
        try {
          await client.session.prompt({
            path: { id: input.sessionID },
            body: { noReply: true, parts: [{ type: 'text', text, ignored: true }] },
          });
        } catch {
          // client.session.prompt may not be available in all OpenCode versions.
          // Fall back to modifying output text.
          output.parts = [{ type: 'text', text }];
        }
      };

      if (input.command === 'chisel') {
        const arg = (input.arguments || '').trim().toLowerCase();
        if (!arg || arg === 'status') {
          await sendIgnored('chisel mode: ' + currentMode());
          throw new Error('__CHISEL_HANDLED__');
        }
        if (MODES.has(arg)) {
          writeState({ mode: arg, gatePending: false });
          await sendIgnored('chisel ' + arg);
          throw new Error('__CHISEL_HANDLED__');
        }
        await sendIgnored(
          'Invalid chisel mode: "' + arg + '". Valid: full, lite, off.',
        );
        throw new Error('__CHISEL_HANDLED__');
      }

      if (input.command === 'chisel-gate') {
        const s = readState();
        if (s.mode !== 'lite') {
          await sendIgnored(
            'chisel-gate only available in lite mode (current: ' + s.mode + ')',
          );
          throw new Error('__CHISEL_HANDLED__');
        }
        writeState({ ...s, gatePending: true });
        await sendIgnored('chisel-gate queued for next turn');
        throw new Error('__CHISEL_HANDLED__');
      }
    },
  };
};
