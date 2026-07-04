#!/usr/bin/env python3
"""Chisel analytical benchmark — compares no-skill vs chiseled reference implementations.

Measures:
  - Lines of code (total, source-only)
  - Token estimate (words + symbols)
  - Abstraction count (classes, interfaces, functions)
  - Dependency count (imports/requires)
  - Cyclomatic complexity estimate (branches)
  - File size (bytes)

Outputs a comparison table + JSON results.
"""

import ast
import json
import os
import re
import sys

REFS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reference')

TASKS = [
    ("Email validator", "01-email-validator"),
    ("Debounce", "02-debounce"),
    ("CSV sum", "03-csv-sum"),
    ("Countdown timer", "04-countdown"),
    ("Rate limiter", "05-rate-limiter"),
    ("Date picker", "06-date-picker"),
    ("Order pipeline", "07-order-pipeline"),
]


def count_lines(text):
    lines = text.splitlines()
    total = len(lines)
    source = sum(1 for l in lines if l.strip() and not l.strip().startswith(('//', '#', '<!--', '-->', '*')))
    blank = sum(1 for l in lines if not l.strip())
    comment = total - source - blank
    return total, source, blank, comment


def count_tokens(text):
    """Rough token estimate: words + punctuation clusters."""
    words = re.findall(r'\w+|[^\w\s]', text)
    return len(words)


def count_imports(text):
    """Count import/require/include statements."""
    patterns = [
        r'^import\s', r'^from\s', r'^require\s', r'^#include',
        r'<script\s+src=', r'<link\s+rel=["\']stylesheet["\']',
    ]
    count = 0
    for line in text.splitlines():
        stripped = line.strip()
        for p in patterns:
            if re.match(p, stripped):
                count += 1
                break
    return count


def count_abstractions(text, ext):
    """Rough count of classes, interfaces, exported functions."""
    classes = len(re.findall(r'^\s*(export\s+)?(class|interface)\s+\w+', text, re.MULTILINE))
    functions = len(re.findall(r'^\s*(export\s+)?(function|def)\s+\w+', text, re.MULTILINE))
    return classes + functions


def estimate_complexity(text, ext):
    """Estimate cyclomatic complexity: if/for/while/and/or/case/?. """
    branches = len(re.findall(r'\b(if|elif|else|for|while|and|or|case|switch|catch)\b', text))
    ternaries = text.count('?') // 2 + text.count(':') // 2
    return branches + ternaries


def score_file(filepath, label, ext):
    with open(filepath) as f:
        text = f.read()

    total_lines, source_lines, blank_lines, comment_lines = count_lines(text)
    tokens = count_tokens(text)
    imports = count_imports(text)
    abstractions = count_abstractions(text, ext)
    complexity = estimate_complexity(text, ext)
    bytes_len = len(text.encode('utf-8'))

    return {
        "label": label,
        "total_lines": total_lines,
        "source_lines": source_lines,
        "blank_lines": blank_lines,
        "comment_lines": comment_lines,
        "tokens": tokens,
        "imports": imports,
        "abstractions": abstractions,
        "complexity": complexity,
        "bytes": bytes_len,
    }


def delta(no_skill, chiseled, metric):
    a = no_skill[metric]
    b = chiseled[metric]
    if a == 0:
        return 0.0
    return round((a - b) / a * 100)


def main():
    results = []

    for task_name, prefix in TASKS:
        ns_path = os.path.join(REFS_DIR, f"{prefix}-no-skill.py")
        ch_path = os.path.join(REFS_DIR, f"{prefix}-chiseled.py")

        # Check for any file extension (no-skill and chiseled may differ)
        for ns_ext in ['.py', '.ts', '.js', '.html']:
            ns_path = os.path.join(REFS_DIR, f"{prefix}-no-skill{ns_ext}")
            if os.path.exists(ns_path):
                for ch_ext in ['.py', '.ts', '.js', '.html']:
                    ch_path = os.path.join(REFS_DIR, f"{prefix}-chiseled{ch_ext}")
                    if os.path.exists(ch_path):
                        break
                break

        if not os.path.exists(ns_path) or not os.path.exists(ch_path):
            print(f"SKIP: {task_name} — reference files not found")
            continue

        no_skill = score_file(ns_path, f"{task_name} (no-skill)", os.path.splitext(ns_path)[1])
        chiseled = score_file(ch_path, f"{task_name} (chiseled)", os.path.splitext(ch_path)[1])

        results.append((task_name, no_skill, chiseled))

    # Print summary table
    print("=" * 98)
    print(f"{'Task':<22} {'Metric':<16} {'No-skill':<12} {'Chiseled':<12} {'Reduction':<10} {'Saved':<10}")
    print("=" * 98)

    totals_ns = {"total_lines": 0, "tokens": 0, "imports": 0, "abstractions": 0, "complexity": 0, "bytes": 0}
    totals_ch = {"total_lines": 0, "tokens": 0, "imports": 0, "abstractions": 0, "complexity": 0, "bytes": 0}

    for task_name, ns, ch in results:
        for metric, display in [
            ("total_lines", "Lines of code"),
            ("tokens", "Tokens (est.)"),
            ("imports", "Dependencies"),
            ("abstractions", "Abstractions"),
            ("complexity", "Complexity"),
            ("bytes", "File size"),
        ]:
            pct = delta(ns, ch, metric)
            saved = ns[metric] - ch[metric]
            print(f"{task_name:<22} {display:<16} {ns[metric]:<12} {ch[metric]:<12} {pct:<9}% {saved:<9}")
            totals_ns[metric] += ns[metric]
            totals_ch[metric] += ch[metric]

        print("-" * 98)

    # Totals
    print("=" * 98)
    print(f"{'TOTAL':<22} {'':<16} {'':<12} {'':<12} {'':<10} {'':<10}")
    print("-" * 98)
    for metric, display in [
        ("total_lines", "Lines of code"),
        ("tokens", "Tokens (est.)"),
        ("imports", "Dependencies"),
        ("abstractions", "Abstractions"),
        ("complexity", "Complexity"),
        ("bytes", "File size"),
    ]:
        pct = delta(totals_ns, totals_ch, metric)
        saved = totals_ns[metric] - totals_ch[metric]
        print(f"{'TOTAL':<22} {display:<16} {totals_ns[metric]:<12} {totals_ch[metric]:<12} {pct:<9}% {saved:<9}")

    print("=" * 98)

    # Summary line
    avg_loc_pct = delta(totals_ns, totals_ch, "total_lines")
    avg_tok_pct = delta(totals_ns, totals_ch, "tokens")
    avg_dep_pct = delta(totals_ns, totals_ch, "imports")
    avg_abs_pct = delta(totals_ns, totals_ch, "abstractions")
    print(f"\nSummary: chisel cuts LOC by {avg_loc_pct}%, tokens by {avg_tok_pct}%, "
          f"dependencies by {avg_dep_pct}%, abstractions by {avg_abs_pct}%.")

    # Save JSON
    json_path = os.path.join(REFS_DIR, "..", "results", "analytical-benchmark.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    output = {
        "summary": {
            "loc_reduction_pct": avg_loc_pct,
            "token_reduction_pct": avg_tok_pct,
            "dependency_reduction_pct": avg_dep_pct,
            "abstraction_reduction_pct": avg_abs_pct,
        },
        "tasks": [
            {
                "name": name,
                "no_skill": ns,
                "chiseled": ch,
            }
            for name, ns, ch in results
        ],
        "totals": {
            "no_skill": totals_ns,
            "chiseled": totals_ch,
        }
    }
    with open(json_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nDetailed results saved to: {json_path}")


if __name__ == '__main__':
    main()
