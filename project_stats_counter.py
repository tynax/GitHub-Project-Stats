#!/usr/bin/env python3
"""
file_stats_counter.py

A utility script to count the total number of lines and characters in all text
and code files within a project directory. Simply place this script in the root
directory of your project and run it.
"""

import os
import re
from collections import defaultdict

# File extensions to analyze - add more as needed
TEXT_EXTENSIONS = {
    'Code': ['.py', '.js', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs',
             '.swift', '.kt', '.scala', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.sass',
             '.less', '.sql', '.sh', '.bash', '.lua', '.r', '.pl', '.pm', '.dart', '.groovy',
             '.vb', '.asm', '.f', '.f90', '.f95', '.m', '.swift', '.vue', '.elm', '.clj', '.ex',
             '.exs', '.erl', '.hrl', '.lisp', '.hs', '.xml'],
    'Markup': ['.md', '.rst', '.txt', '.tex', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg',
               '.conf', '.properties', '.csv', '.tsv'],
    'Documentation': ['.doc', '.docx', '.pdf', '.rtf', '.odt']
}

# Directories to exclude from analysis
EXCLUDE_DIRS = ['.git', 'node_modules', 'venv', '.venv', 'env', '.env', 'build', 'dist',
                '__pycache__', '.idea', '.vscode', 'vendor', 'bin', 'obj']

# Binary file signatures to detect quickly
BINARY_SIGNATURES = [
    b'\x89PNG', b'GIF8', b'BM', b'\xFF\xD8\xFF', b'PK\x03\x04',
    b'%PDF', b'\x7FELF', b'MZ', b'\xCF\xFA\xED\xFE', b'\xCA\xFE\xBA\xBE'
]


def is_binary(file_path, sample_size=8192):
    """
    Check if a file is binary by reading its first few bytes.
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(sample_size)

            # Check for known binary signatures
            for signature in BINARY_SIGNATURES:
                if header.startswith(signature):
                    return True

            # Check for null bytes which commonly indicate binary files
            if b'\x00' in header:
                return True

            # If more than 30% of the bytes are non-text, it's likely binary
            text_characters = bytes(range(32, 127)) + b'\r\n\t\b'
            binary_chars = sum(1 for byte in header if byte not in text_characters)
            return binary_chars / len(header) > 0.3 if header else False
    except (IOError, OSError):
        return True  # If we can't read the file, consider it binary to be safe

    return False


def get_file_extension_category(file_path):
    """
    Determine the category of a file based on its extension.
    """
    _, ext = os.path.splitext(file_path.lower())

    for category, extensions in TEXT_EXTENSIONS.items():
        if ext in extensions:
            return category

    # For unknown extensions, try to determine if it's text or binary
    if not is_binary(file_path):
        return "Other Text"

    return None  # Not a text file we're interested in


def count_lines_and_chars(file_path):
    """
    Count the number of lines and characters in a file.
    Returns a tuple of (lines, characters)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            lines = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
            chars = len(content)
            return lines, chars
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0, 0


def format_number(num):
    """Format a number with thousands separators."""
    return f"{num:,}"


def main():
    stats = defaultdict(lambda: {'files': 0, 'lines': 0, 'chars': 0})
    total_files = 0
    total_lines = 0
    total_chars = 0

    print("\nScanning files...\n")

    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            file_path = os.path.join(root, file)

            # Skip this script itself
            if os.path.samefile(file_path, __file__):
                continue

            category = get_file_extension_category(file_path)
            if not category:
                continue  # Skip binary or undesired files

            lines, chars = count_lines_and_chars(file_path)

            stats[category]['files'] += 1
            stats[category]['lines'] += lines
            stats[category]['chars'] += chars

            total_files += 1
            total_lines += lines
            total_chars += chars

    # Print results
    print("=" * 80)
    print(f"PROJECT STATISTICS SUMMARY")
    print("=" * 80)

    # Print by category
    categories = sorted(stats.keys())
    for category in categories:
        cat_stats = stats[category]
        print(f"\n{category} Files:")
        print(f"  Files:      {format_number(cat_stats['files'])}")
        print(f"  Lines:      {format_number(cat_stats['lines'])}")
        print(f"  Characters: {format_number(cat_stats['chars'])}")

    # Print totals
    print("\n" + "=" * 80)
    print(
        f"TOTAL: {format_number(total_files)} files, {format_number(total_lines)} lines, {format_number(total_chars)} characters")
    print("=" * 80)


if __name__ == "__main__":
    main()