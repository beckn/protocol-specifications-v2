#!/usr/bin/env python3
"""
sort_schemas.py — Sort #/components/schemas alphabetically in a YAML file.

Usage:
    python3 tools/sort_schemas.py [path/to/file.yaml]

Default target: protocol-specifications-v2/api/v2.0.0/beckn-proposed.yaml

Strategy:
    - Reads the YAML file as raw text to preserve formatting, comments, and
      YAML quirks (multiline strings, anchors, etc.).
    - Locates the `  schemas:` key inside `components:`.
    - Splits out each top-level schema block (identified by a 2-space-indented
      key at the `schemas` child level, i.e. 4-space indented keys).
    - Sorts the blocks case-insensitively by their key name.
    - Writes the result back to the same file.

The script is idempotent — running it twice produces the same output.
"""

import re
import sys
import os

DEFAULT_TARGET = os.path.join(
    os.path.dirname(__file__),
    "..",
    "protocol-specifications-v2",
    "api",
    "v2.0.0",
    "beckn-proposed.yaml",
)


def sort_schemas_in_file(filepath: str) -> None:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines(keepends=True)

    # ------------------------------------------------------------------ #
    # 1. Find the line index where `  schemas:` begins (inside components)
    # ------------------------------------------------------------------ #
    # We look for `components:` first, then `  schemas:` after it.
    components_idx = None
    schemas_idx = None

    for i, line in enumerate(lines):
        if re.match(r'^components:\s*$', line):
            components_idx = i
        if components_idx is not None and re.match(r'^  schemas:\s*$', line):
            schemas_idx = i
            break

    if schemas_idx is None:
        print("ERROR: Could not find 'components: / schemas:' section.")
        sys.exit(1)

    print(f"Found 'schemas:' at line {schemas_idx + 1}")

    # ------------------------------------------------------------------ #
    # 2. Collect all schema blocks starting after `  schemas:`
    #    Each schema key is a 4-space-indented identifier followed by ':'
    #    e.g.  "    DiscoverAction:"
    # ------------------------------------------------------------------ #
    schema_key_re = re.compile(r'^    (\w[\w\-]*)\s*:')

    # Find the range of lines that belong to schemas section.
    # The section ends when we hit a line that is at the same or lower
    # indentation as `  schemas:` (i.e. indentation < 4 spaces) and is
    # not empty/comment.
    section_start = schemas_idx + 1  # first line after `  schemas:`

    # Find where the schemas section ends
    section_end = len(lines)  # default: end of file
    for i in range(section_start, len(lines)):
        line = lines[i]
        stripped = line.rstrip('\n')
        if stripped == '' or stripped.startswith('#'):
            continue
        # Non-empty, non-comment line: check indentation
        indent = len(stripped) - len(stripped.lstrip())
        if indent < 4:
            section_end = i
            break

    print(f"Schemas section: lines {section_start + 1}–{section_end} "
          f"(0-indexed {section_start}–{section_end - 1})")

    schema_lines = lines[section_start:section_end]

    # Split schema_lines into individual schema blocks
    blocks = []      # list of (key_name, list_of_lines)
    current_key = None
    current_block = []

    for line in schema_lines:
        m = schema_key_re.match(line)
        if m:
            if current_key is not None:
                blocks.append((current_key, current_block))
            current_key = m.group(1)
            current_block = [line]
        else:
            current_block.append(line)

    if current_key is not None:
        blocks.append((current_key, current_block))

    print(f"Found {len(blocks)} schema blocks.")
    if blocks:
        print(f"  Before sort — first: '{blocks[0][0]}', last: '{blocks[-1][0]}'")

    # ------------------------------------------------------------------ #
    # 3. Sort blocks alphabetically (case-insensitive)
    # ------------------------------------------------------------------ #
    sorted_blocks = sorted(blocks, key=lambda b: b[0].lower())

    if sorted_blocks:
        print(f"  After sort  — first: '{sorted_blocks[0][0]}', last: '{sorted_blocks[-1][0]}'")

    # ------------------------------------------------------------------ #
    # 4. Reconstruct the file
    # ------------------------------------------------------------------ #
    sorted_schema_lines = []
    for _key, block_lines in sorted_blocks:
        sorted_schema_lines.extend(block_lines)

    new_lines = (
        lines[:section_start]
        + sorted_schema_lines
        + lines[section_end:]
    )

    new_content = "".join(new_lines)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Done. Written back to: {filepath}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TARGET
    target = os.path.normpath(target)
    if not os.path.isfile(target):
        print(f"ERROR: File not found: {target}")
        sys.exit(1)
    sort_schemas_in_file(target)
