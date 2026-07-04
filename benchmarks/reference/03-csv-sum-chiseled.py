"""CSV sum — chiseled version."""

import csv
import sys

total = 0
with open(sys.argv[1]) as f:
    for row in csv.DictReader(f):
        total += float(row.get('amount', 0) or 0)
print(total)
