"""CSV sum — no-skill version. ArgumentParser, error handling, docstrings."""

import argparse
import csv
import sys


class CSVSumError(Exception):
    """Base exception for CSV sum operations."""
    pass


class EmptyFileError(CSVSumError):
    """Raised when the CSV file is empty."""
    pass


class MissingColumnError(CSVSumError):
    """Raised when the required column is missing."""
    pass


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Sum the amount column in a CSV file.'
    )
    parser.add_argument('file', help='Path to the CSV file')
    parser.add_argument(
        '--column', '-c',
        default='amount',
        help='Column name to sum (default: amount)'
    )
    return parser.parse_args()


def read_csv(filepath, column):
    """Read a CSV file and return the sum of the specified column."""
    try:
        with open(filepath, 'r', newline='') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise EmptyFileError(f"File is empty: {filepath}")
            if column not in reader.fieldnames:
                raise MissingColumnError(
                    f"Column '{column}' not found. "
                    f"Available: {', '.join(reader.fieldnames)}"
                )
            total = 0
            for row in reader:
                try:
                    total += float(row[column])
                except (ValueError, TypeError):
                    continue
            return total
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied: {filepath}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    args = parse_arguments()
    total = read_csv(args.file, args.column)
    print(total)


if __name__ == '__main__':
    main()
