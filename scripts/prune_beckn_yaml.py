#!/usr/bin/env python3
"""
prune_beckn_yaml.py — Remove all domain-level schemas from components.schemas
in api/v2.0.0/beckn.yaml, keeping only those that are referenced from
components.responses or components.parameters (and their transitive deps).

Everything in paths[] already points to external $refs at schema.beckn.io.
The remaining domain schemas (Context, Catalog, Intent, Fulfillment, etc.)
are dead weight — they're no longer referenced anywhere except by each other.

The "keep" set is computed as:
  1. All schemas referenced (directly or transitively) from
     components.responses.*.content.*.schema and
     components.parameters.*.schema
  2. All schemas transitively referenced by those schemas

Everything else is deleted using line-range surgery on the raw YAML text
to preserve all original formatting, comments and quoting styles.

Usage:
    cd /path/to/protocol-specifications-v2
    python3 scripts/prune_beckn_yaml.py [--dry-run]
"""

import argparse
import re
import sys
import os

import yaml  # pyyaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
YAML_PATH = os.path.join(REPO_ROOT, "api", "v2.0.0", "beckn.yaml")


# ---------------------------------------------------------------------------
# Phase 1: determine which schemas to keep
# ---------------------------------------------------------------------------

def collect_local_refs(obj) -> set[str]:
    """
    Walk a Python structure (dict/list/str) and return the set of schema names
    referenced via '$ref: '#/components/schemas/X'' patterns.
    """
    refs: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                m = re.match(r"^#/components/schemas/(.+)$", v)
                if m:
                    refs.add(m.group(1))
            else:
                refs |= collect_local_refs(v)
    elif isinstance(obj, list):
        for item in obj:
            refs |= collect_local_refs(item)
    return refs


def transitive_closure(seeds: set[str], schemas: dict) -> set[str]:
    """
    Starting from `seeds`, keep following local $ref pointers within `schemas`
    until no new names are discovered.
    """
    keep: set[str] = set()
    queue = list(seeds)
    while queue:
        name = queue.pop()
        if name in keep:
            continue
        keep.add(name)
        if name in schemas:
            for dep in collect_local_refs(schemas[name]):
                if dep not in keep:
                    queue.append(dep)
    return keep


# ---------------------------------------------------------------------------
# Phase 2: text-based line-range deletion (preserves YAML formatting)
# ---------------------------------------------------------------------------

def find_schema_blocks(lines: list[str], schema_names: set[str]) -> dict[str, tuple[int, int]]:
    """
    Scan the lines for the `  schemas:` block, then for each top-level schema
    entry `  <Name>:` at 4-space indent, record the [start, end) line range.

    Returns: { schema_name: (start_line_0indexed, end_line_0indexed_exclusive) }
    """
    # Find start of `  schemas:` block (2-space indent under `components:`)
    schemas_line = None
    for i, line in enumerate(lines):
        if re.match(r"^  schemas:\s*$", line):
            schemas_line = i
            break

    if schemas_line is None:
        raise ValueError("Could not find '  schemas:' line in YAML")

    # Walk from schemas_line+1 and find top-level entries (4-space indent key)
    # A top-level entry under `schemas:` looks like:    `    Name:\n`
    entry_re = re.compile(r"^    ([A-Za-z][A-Za-z0-9_]*):\s*$")

    # Also detect lines that signal we've left the schemas block:
    # any line at ≤2-space indent that isn't blank
    exit_re = re.compile(r"^[^ \t]|^  [^ \t]")   # indent 0 or 2 → new top-level section

    entries: list[tuple[str, int]] = []  # (name, start_line)
    in_schemas = False

    for i in range(schemas_line + 1, len(lines)):
        line = lines[i]

        # Detect exit from schemas block
        if exit_re.match(line) and line.strip() != "":
            break

        m = entry_re.match(line)
        if m:
            in_schemas = True
            entries.append((m.group(1), i))

    # Build ranges: each entry spans from its start line to just before the next entry
    # (or the end of the schemas block)
    result: dict[str, tuple[int, int]] = {}
    for idx, (name, start) in enumerate(entries):
        if idx + 1 < len(entries):
            end = entries[idx + 1][1]
        else:
            # Last entry: ends at blank line before next top-level section
            end = start + 1
            while end < len(lines) and (
                lines[end].strip() == "" or lines[end].startswith("    ")
            ):
                end += 1
        result[name] = (start, end)

    # Filter to only the names we want to remove
    return {name: rng for name, rng in result.items() if name in schema_names}


def delete_line_ranges(lines: list[str], ranges: list[tuple[int, int]]) -> list[str]:
    """
    Delete the given line ranges (0-indexed, end-exclusive) from `lines`.
    Ranges must be sorted and non-overlapping.
    """
    ranges_sorted = sorted(ranges)
    result: list[str] = []
    pos = 0
    for start, end in ranges_sorted:
        result.extend(lines[pos:start])
        pos = end
    result.extend(lines[pos:])
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print diff, don't write")
    args = parser.parse_args()

    print(f"Loading {YAML_PATH} …", file=sys.stderr)
    with open(YAML_PATH, "r", encoding="utf-8") as fh:
        raw = fh.read()
    lines = raw.splitlines(keepends=True)

    spec = yaml.safe_load(raw)

    components = spec.get("components", {})
    schemas: dict = components.get("schemas", {})
    responses: dict = components.get("responses", {})
    parameters_obj = components.get("parameters", {})

    # ── Step 1: find seeds (schemas directly referenced from responses + params) ──

    seeds: set[str] = set()
    seeds |= collect_local_refs(responses)
    seeds |= collect_local_refs(parameters_obj)

    print(f"\nDirect references from responses + parameters:", file=sys.stderr)
    for s in sorted(seeds):
        print(f"  {s}", file=sys.stderr)

    # ── Step 2: transitive closure within components.schemas ─────────────────

    keep = transitive_closure(seeds, schemas)

    print(f"\nSchemas to KEEP ({len(keep)}):", file=sys.stderr)
    for s in sorted(keep):
        print(f"  ✓ {s}", file=sys.stderr)

    remove = {name for name in schemas if name not in keep}
    print(f"\nSchemas to REMOVE ({len(remove)}):", file=sys.stderr)
    for s in sorted(remove):
        print(f"  ✗ {s}", file=sys.stderr)

    if not remove:
        print("\nNothing to remove. File unchanged.", file=sys.stderr)
        return

    if args.dry_run:
        print("\n--dry-run: no changes written.", file=sys.stderr)
        return

    # ── Step 3: find line ranges for each schema to remove ───────────────────

    blocks = find_schema_blocks(lines, remove)

    missing = remove - set(blocks.keys())
    if missing:
        print(f"\nWARNING: could not locate line ranges for: {missing}", file=sys.stderr)

    print(f"\nLine ranges to delete:", file=sys.stderr)
    for name in sorted(blocks.keys()):
        s, e = blocks[name]
        print(f"  {name}: lines {s+1}–{e} ({e-s} lines)", file=sys.stderr)

    # ── Step 4: delete ranges and write ──────────────────────────────────────

    ranges = list(blocks.values())
    new_lines = delete_line_ranges(lines, ranges)
    out = "".join(new_lines)

    with open(YAML_PATH, "w", encoding="utf-8") as fh:
        fh.write(out)

    before = len(lines)
    after = len(new_lines)
    print(
        f"\nDone. Deleted {before - after} lines ({len(remove)} schemas removed). "
        f"File: {before} → {after} lines.",
        file=sys.stderr,
    )
    print(f"Written: {YAML_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
