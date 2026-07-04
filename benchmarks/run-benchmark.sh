#!/usr/bin/env bash
# chisel benchmark runner
# Usage: ./run-benchmark.sh [--provider openai:gpt-4o-mini]
set -euo pipefail

PROVIDER="${1:-openai:gpt-4o-mini}"

echo "=== chisel benchmark ==="
echo "Provider: $PROVIDER"
echo ""

# Check promptfoo installed
if ! command -v promptfoo &>/dev/null; then
  echo "ERROR: promptfoo not found. Install it: npm install -g promptfoo"
  exit 1
fi

# Run evaluation
promptfoo eval --config promptfooconfig.yaml --provider "$PROVIDER"

# Show results
echo ""
echo "=== Results ==="
promptfoo show output

echo ""
echo "Done. Open results: promptfoo view"
