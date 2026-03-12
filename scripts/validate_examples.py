#!/usr/bin/env python3
"""
Beckn Protocol — Schema Compliance Validator
============================================
Validates all retail example JSON files against schemas fetched remotely from
https://schema.beckn.io/{SchemaName}/v2.0

Algorithm
---------
For each JSON file:
  1. Walk the entire JSON tree looking for objects with an "@type" key.
  2. For each typed object:
     a. Strip the "beckn:" prefix from @type to get the schema name.
     b. Construct the URL: https://schema.beckn.io/{SchemaName}/v2.0
     c. Fetch the YAML schema remotely (with caching so each schema URL is
        only fetched once per run).
     d. Convert YAML → dict (JSON Schema).
     e. All $ref values inside that schema which start with
        "https://schema.beckn.io/" are also fetched remotely on demand via a
        custom referencing.Registry.
     f. Validate the typed object against its schema using jsonschema with the
        Draft202012Validator (JSON Schema 2020-12).
     g. Record PASS / VALIDATION_FAILURE / URL_RESOLUTION_FAILURE.
  3. Emit a Markdown compliance report to plans/schema_compliance_report.md

Usage
-----
  python3 scripts/validate_examples.py

Requirements
------------
  pip install jsonschema pyyaml requests referencing
"""

import json
import os
import glob
import re
import datetime
import sys

import requests
import yaml
import referencing
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError, SchemaError

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES_DIR = os.path.join(BASE_DIR, "examples", "retail")
REPORT_PATH = os.path.join(BASE_DIR, "plans", "schema_compliance_report.md")

SCHEMA_BASE_URL = "https://schema.beckn.io"
VERSION = "v2.0"
REQUEST_TIMEOUT = 15  # seconds per HTTP request

# ─────────────────────────────────────────────────────────────────────────────
# In-process schema cache: URL → (status, schema_dict_or_error_message)
# ─────────────────────────────────────────────────────────────────────────────
_schema_cache: dict[str, tuple[str, object]] = {}


def fetch_schema(url: str) -> tuple[str, object]:
    """Fetch a YAML/JSON schema from a remote URL.

    Returns:
        ("ok", schema_dict)  — on success
        ("url_error", error_message)  — on HTTP/network failure
        ("parse_error", error_message)  — on YAML/JSON parse failure
    """
    if url in _schema_cache:
        return _schema_cache[url]

    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as exc:
        result = ("url_error", f"Network error fetching {url}: {exc}")
        _schema_cache[url] = result
        return result

    if resp.status_code != 200:
        result = ("url_error", f"HTTP {resp.status_code} for {url}")
        _schema_cache[url] = result
        return result

    # Try YAML first (schema.beckn.io returns YAML)
    try:
        schema = yaml.safe_load(resp.text)
        if not isinstance(schema, dict):
            raise ValueError("Root is not a dict")
        result = ("ok", schema)
    except Exception as exc:
        result = ("parse_error", f"YAML/JSON parse error for {url}: {exc}")

    _schema_cache[url] = result
    return result


def schema_url_for_type(beckn_type: str) -> str:
    """Derive the schema URL from a beckn @type value.

    E.g. "beckn:DiscoverAction" → "https://schema.beckn.io/DiscoverAction/v2.0"
         "DiscoverAction"        → "https://schema.beckn.io/DiscoverAction/v2.0"
    """
    name = beckn_type.split(":")[-1]  # strip namespace prefix
    return f"{SCHEMA_BASE_URL}/{name}/{VERSION}"


# ─────────────────────────────────────────────────────────────────────────────
# Build a referencing.Registry that resolves all $refs remotely
# ─────────────────────────────────────────────────────────────────────────────

def _retrieve_remote(uri: str):
    """Retriever callback for referencing.Registry — fetches schemas on demand."""
    status, result = fetch_schema(uri)
    if status != "ok":
        raise referencing.exceptions.NoSuchResource(uri)
    return Resource.from_contents(result, default_specification=DRAFT202012)


def make_registry(root_schema: dict) -> Registry:
    """Create a Registry pre-seeded with the root schema plus a remote retriever."""
    root_id = root_schema.get("$id", "")
    if root_id:
        resource = Resource.from_contents(root_schema, default_specification=DRAFT202012)
        registry = Registry(retrieve=_retrieve_remote).with_resource(root_id, resource)
    else:
        registry = Registry(retrieve=_retrieve_remote)
    return registry


# ─────────────────────────────────────────────────────────────────────────────
# Walk a JSON tree and collect all typed objects
# ─────────────────────────────────────────────────────────────────────────────

def collect_typed_objects(node, path="$"):
    """Recursively collect (json_path, obj) for all dicts with an '@type' key."""
    results = []
    if isinstance(node, dict):
        if "@type" in node:
            results.append((path, node))
        for key, value in node.items():
            results.extend(collect_typed_objects(value, f"{path}.{key}"))
    elif isinstance(node, list):
        for i, item in enumerate(node):
            results.extend(collect_typed_objects(item, f"{path}[{i}]"))
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Validate a single typed object
# ─────────────────────────────────────────────────────────────────────────────

def validate_typed_object(obj: dict, json_path: str, source_file: str) -> dict:
    """Validate a single typed object against its remote schema.

    Returns a result dict with keys:
        file, path, type, schema_url,
        status (PASS | VALIDATION_FAILURE | URL_RESOLUTION_FAILURE | SCHEMA_PARSE_ERROR),
        errors (list of str)
    """
    beckn_type = obj.get("@type", "")
    schema_url = schema_url_for_type(beckn_type)

    result = {
        "file": source_file,
        "path": json_path,
        "type": beckn_type,
        "schema_url": schema_url,
        "status": None,
        "errors": [],
    }

    # 1. Fetch the schema
    status, payload = fetch_schema(schema_url)

    if status == "url_error":
        result["status"] = "URL_RESOLUTION_FAILURE"
        result["errors"] = [payload]
        return result

    if status == "parse_error":
        result["status"] = "SCHEMA_PARSE_ERROR"
        result["errors"] = [payload]
        return result

    schema = payload  # dict

    # 2. Build registry
    try:
        registry = make_registry(schema)
    except Exception as exc:
        result["status"] = "SCHEMA_PARSE_ERROR"
        result["errors"] = [f"Registry build error: {exc}"]
        return result

    # 3. Validate
    try:
        validator = Draft202012Validator(schema, registry=registry)
        validation_errors = list(validator.iter_errors(obj))
    except SchemaError as exc:
        result["status"] = "SCHEMA_PARSE_ERROR"
        result["errors"] = [f"Invalid schema at {schema_url}: {exc.message}"]
        return result
    except referencing.exceptions.NoSuchResource as exc:
        result["status"] = "URL_RESOLUTION_FAILURE"
        result["errors"] = [f"Could not resolve $ref: {exc}"]
        return result
    except Exception as exc:
        result["status"] = "SCHEMA_PARSE_ERROR"
        result["errors"] = [f"Unexpected validator error: {exc}"]
        return result

    if validation_errors:
        result["status"] = "VALIDATION_FAILURE"
        result["errors"] = [
            f"[{'.'.join(str(p) for p in e.absolute_path) or '<root>'}] {e.message}"
            for e in validation_errors
        ]
    else:
        result["status"] = "PASS"

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Process one JSON file
# ─────────────────────────────────────────────────────────────────────────────

def validate_file(filepath: str) -> list[dict]:
    """Parse a JSON file and validate all typed objects within it."""
    rel_path = os.path.relpath(filepath, BASE_DIR)

    try:
        with open(filepath) as f:
            data = json.load(f)
    except Exception as exc:
        return [{
            "file": rel_path,
            "path": "$",
            "type": "N/A",
            "schema_url": "N/A",
            "status": "PARSE_ERROR",
            "errors": [f"JSON parse error: {exc}"],
        }]

    typed_objects = collect_typed_objects(data)
    if not typed_objects:
        return [{
            "file": rel_path,
            "path": "$",
            "type": "N/A",
            "schema_url": "N/A",
            "status": "NO_TYPED_OBJECTS",
            "errors": ["No objects with @type found in this file"],
        }]

    results = []
    for path, obj in typed_objects:
        r = validate_typed_object(obj, path, rel_path)
        results.append(r)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Generate Markdown report
# ─────────────────────────────────────────────────────────────────────────────

def generate_report(all_results: list[dict], elapsed: float) -> str:
    """Generate a Markdown compliance report from all validation results."""

    # Aggregate counts
    by_status: dict[str, int] = {}
    by_file: dict[str, dict] = {}
    url_failures: dict[str, list] = {}  # schema_url → list of file+path
    validation_failures: list[dict] = []

    for r in all_results:
        s = r["status"]
        by_status[s] = by_status.get(s, 0) + 1

        f = r["file"]
        if f not in by_file:
            by_file[f] = {"PASS": 0, "VALIDATION_FAILURE": 0,
                          "URL_RESOLUTION_FAILURE": 0, "SCHEMA_PARSE_ERROR": 0,
                          "OTHER": 0, "types_checked": set()}
        if s in by_file[f]:
            by_file[f][s] += 1
        else:
            by_file[f]["OTHER"] += 1
        by_file[f]["types_checked"].add(r["type"])

        if s == "URL_RESOLUTION_FAILURE":
            key = r["schema_url"]
            if key not in url_failures:
                url_failures[key] = []
            url_failures[key].append({"file": r["file"], "path": r["path"], "error": r["errors"]})

        if s == "VALIDATION_FAILURE":
            validation_failures.append(r)

    total = len(all_results)
    n_pass = by_status.get("PASS", 0)
    n_vf = by_status.get("VALIDATION_FAILURE", 0)
    n_uf = by_status.get("URL_RESOLUTION_FAILURE", 0)
    n_pe = by_status.get("SCHEMA_PARSE_ERROR", 0) + by_status.get("NO_TYPED_OBJECTS", 0) + by_status.get("PARSE_ERROR", 0)
    n_files = len(by_file)

    pass_pct = round(100 * n_pass / total, 1) if total else 0

    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Beckn Retail Examples — Schema Compliance Report",
        "",
        f"> Generated: {now}  ",
        f"> Validator: `scripts/validate_examples.py`  ",
        f"> Schema source: `https://schema.beckn.io/{{SchemaName}}/v2.0` (remote, live)  ",
        f"> Elapsed: {elapsed:.1f}s",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Files validated | {n_files} |",
        f"| Total typed objects checked | {total} |",
        f"| ✅ PASS | **{n_pass}** ({pass_pct}%) |",
        f"| ❌ VALIDATION_FAILURE | **{n_vf}** |",
        f"| 🔴 URL_RESOLUTION_FAILURE | **{n_uf}** |",
        f"| ⚠️ SCHEMA_PARSE_ERROR / OTHER | **{n_pe}** |",
        "",
        "---",
        "",
    ]

    # ── URL Resolution Failures ──────────────────────────────────────────────
    if url_failures:
        lines += [
            "## URL Resolution Failures",
            "",
            "These schema URLs could not be fetched from `https://schema.beckn.io/`.",
            "",
        ]
        for url, hits in sorted(url_failures.items()):
            error_msg = hits[0]["error"][0] if hits[0]["error"] else "Unknown"
            lines += [
                f"### `{url}`",
                "",
                f"**Error:** `{error_msg}`  ",
                f"**Affected objects:** {len(hits)}",
                "",
                "| File | JSON Path |",
                "|---|---|",
            ]
            for h in hits[:20]:  # cap at 20 per URL
                lines.append(f"| `{h['file']}` | `{h['path']}` |")
            if len(hits) > 20:
                lines.append(f"| *(+{len(hits)-20} more)* | |")
            lines.append("")
        lines += ["---", ""]
    else:
        lines += [
            "## URL Resolution Failures",
            "",
            "✅ No URL resolution failures — all schema URLs resolved successfully.",
            "",
            "---",
            "",
        ]

    # ── Validation Failures ──────────────────────────────────────────────────
    if validation_failures:
        lines += [
            "## Validation Failures",
            "",
            "These typed objects failed JSON Schema validation.",
            "",
        ]
        # Group by file
        by_vf_file: dict[str, list] = {}
        for r in validation_failures:
            by_vf_file.setdefault(r["file"], []).append(r)

        for fname, failures in sorted(by_vf_file.items()):
            lines += [
                f"### `{fname}`",
                "",
                f"**{len(failures)} failure(s)**",
                "",
                "| JSON Path | @type | Schema URL | Errors |",
                "|---|---|---|---|",
            ]
            for r in failures:
                err_str = "; ".join(r["errors"][:3])  # cap at 3 errors per object
                if len(r["errors"]) > 3:
                    err_str += f" (+{len(r['errors'])-3} more)"
                # escape pipe chars
                err_str = err_str.replace("|", "\\|")
                lines.append(f"| `{r['path']}` | `{r['type']}` | [`{r['schema_url'].split('/')[-2]}/{r['schema_url'].split('/')[-1]}`]({r['schema_url']}) | {err_str} |")
            lines.append("")
        lines += ["---", ""]
    else:
        lines += [
            "## Validation Failures",
            "",
            "✅ No validation failures — all typed objects pass their remote schemas.",
            "",
            "---",
            "",
        ]

    # ── Per-file summary ─────────────────────────────────────────────────────
    lines += [
        "## Per-File Results",
        "",
        "| File | Objects | ✅ Pass | ❌ Fail | 🔴 URL Err | Types Checked |",
        "|---|---|---|---|---|---|",
    ]
    for fname in sorted(by_file.keys()):
        d = by_file[fname]
        obj_total = d["PASS"] + d["VALIDATION_FAILURE"] + d["URL_RESOLUTION_FAILURE"] + d["SCHEMA_PARSE_ERROR"] + d["OTHER"]
        types_str = ", ".join(sorted(d["types_checked"])[:5])
        if len(d["types_checked"]) > 5:
            types_str += f" (+{len(d['types_checked'])-5})"
        lines.append(f"| `{fname}` | {obj_total} | {d['PASS']} | {d['VALIDATION_FAILURE']} | {d['URL_RESOLUTION_FAILURE']} | {types_str} |")

    lines += ["", "---", ""]

    # ── Schema URLs encountered ───────────────────────────────────────────────
    schema_urls_seen = {}
    for r in all_results:
        url = r["schema_url"]
        schema_urls_seen[url] = schema_urls_seen.get(url, {"ok": 0, "err": 0})
        if r["status"] in ("URL_RESOLUTION_FAILURE", "SCHEMA_PARSE_ERROR"):
            schema_urls_seen[url]["err"] += 1
        else:
            schema_urls_seen[url]["ok"] += 1

    lines += [
        "## Schema URLs Encountered",
        "",
        "| Schema URL | Objects | Status |",
        "|---|---|---|",
    ]
    for url in sorted(schema_urls_seen.keys()):
        d = schema_urls_seen[url]
        status_icon = "✅" if d["err"] == 0 else "❌"
        lines.append(f"| [`{url}`]({url}) | {d['ok'] + d['err']} | {status_icon} |")

    lines += ["", "---", "", "*End of report.*", ""]

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import time

    json_files = sorted(glob.glob(
        os.path.join(EXAMPLES_DIR, "**", "*.json"),
        recursive=True
    ))

    print(f"Found {len(json_files)} JSON files in {EXAMPLES_DIR}")
    print("Validating... (fetches schemas live from https://schema.beckn.io/)")
    print()

    all_results = []
    start = time.time()

    for i, filepath in enumerate(json_files, 1):
        rel = os.path.relpath(filepath, BASE_DIR)
        print(f"[{i:3d}/{len(json_files)}] {rel}")
        file_results = validate_file(filepath)
        all_results.extend(file_results)

        # Print per-object summary
        for r in file_results:
            icon = {"PASS": "  ✓", "VALIDATION_FAILURE": "  ✗", "URL_RESOLUTION_FAILURE": "  🔴",
                    "SCHEMA_PARSE_ERROR": "  ⚠", "NO_TYPED_OBJECTS": "  —", "PARSE_ERROR": "  !"}.get(r["status"], "  ?")
            print(f"{icon} {r['type']:<45} {r['schema_url']}")
            for err in r["errors"][:2]:
                print(f"       → {err[:120]}")

    elapsed = time.time() - start

    # Counts
    by_status: dict[str, int] = {}
    for r in all_results:
        s = r["status"]
        by_status[s] = by_status.get(s, 0) + 1

    print()
    print("=" * 72)
    print("COMPLIANCE SUMMARY")
    print("=" * 72)
    total = len(all_results)
    for s in ["PASS", "VALIDATION_FAILURE", "URL_RESOLUTION_FAILURE", "SCHEMA_PARSE_ERROR", "NO_TYPED_OBJECTS", "PARSE_ERROR"]:
        n = by_status.get(s, 0)
        if n:
            print(f"  {s:<30} {n:>5} / {total}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print("=" * 72)

    # Generate report
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    report = generate_report(all_results, elapsed)
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"\nReport written → {REPORT_PATH}")


if __name__ == "__main__":
    main()
