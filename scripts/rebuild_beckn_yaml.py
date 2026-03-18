#!/usr/bin/env python3
"""
rebuild_beckn_yaml.py — Generate api/v2.0.0/beckn.yaml from the two source files:

  Source 1:  api/v2.0.0/components/io/core.yaml
             Abstract IO spec — defines the generic endpoint structure, auth,
             and response codes (GET + POST).

  Source 2:  api/v2.0.0/components/schema/core.yaml
             Transport-layer schemas, parameters, and responses (Ack, Signature,
             Error, NackBadRequest, etc.).

The generator:
  1. Reads `io/core.yaml` for the abstract endpoint template (GET + POST operations).
  2. Reads `schema/core.yaml` for the concrete components block.
  3. Expands the single generic `/beckn/{becknEndpoint}` path into 20 concrete
     per-action paths (discover, on_discover, select, …, on_support), each with:
       requestBody.$ref: 'https://schema.beckn.io/{Action}Action/v2.0'
  4. Writes `api/v2.0.0/beckn.yaml` with an AUTO-GENERATED header.

Usage:
    cd /path/to/protocol-specifications-v2
    python3 scripts/rebuild_beckn_yaml.py [--dry-run]
"""

import argparse
import copy
import os
import sys

import yaml  # pyyaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
IO_CORE_YAML = os.path.join(REPO_ROOT, "api", "v2.0.0", "components", "io", "core.yaml")
SCHEMA_CORE_YAML = os.path.join(REPO_ROOT, "api", "v2.0.0", "components", "schema", "core.yaml")
OUTPUT_YAML = os.path.join(REPO_ROOT, "api", "v2.0.0", "beckn.yaml")

# ---------------------------------------------------------------------------
# Action mapping — order matters (determines path order in output file)
# ---------------------------------------------------------------------------

NAMESPACE_BASE = "https://schema.beckn.io"
VERSION = "v2.0"

# Ordered list of (beckn_endpoint_value, ActionClassName)
# beckn_endpoint_value matches the BecknEndpoint schema const values
# (full beckn/-prefixed strings, e.g. "beckn/discover").
ACTIONS: list[tuple[str, str]] = [
    ("beckn/discover",    "DiscoverAction"),
    ("beckn/on_discover", "OnDiscoverAction"),
    ("beckn/select",      "SelectAction"),
    ("beckn/on_select",   "OnSelectAction"),
    ("beckn/init",        "InitAction"),
    ("beckn/on_init",     "OnInitAction"),
    ("beckn/confirm",     "ConfirmAction"),
    ("beckn/on_confirm",  "OnConfirmAction"),
    ("beckn/status",      "StatusAction"),
    ("beckn/on_status",   "OnStatusAction"),
    ("beckn/track",       "TrackAction"),
    ("beckn/on_track",    "OnTrackAction"),
    ("beckn/update",      "UpdateAction"),
    ("beckn/on_update",   "OnUpdateAction"),
    ("beckn/cancel",      "CancelAction"),
    ("beckn/on_cancel",   "OnCancelAction"),
    ("beckn/rate",        "RateAction"),
    ("beckn/on_rate",     "OnRateAction"),
    ("beckn/support",     "SupportAction"),
    ("beckn/on_support",  "OnSupportAction"),
]


def canonical_iri(action_class: str) -> str:
    return f"{NAMESPACE_BASE}/{action_class}/{VERSION}"


# ---------------------------------------------------------------------------
# YAML dumper — preserves insertion order, no sorting, literal strings
# ---------------------------------------------------------------------------

class _IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, indentless=False)


def _literal_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_IndentDumper.add_representer(str, _literal_presenter)


def dump_yaml(data: dict) -> str:
    return yaml.dump(
        data,
        Dumper=_IndentDumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def resolve_io_refs(io_spec: dict, schema_components: dict) -> dict:
    """
    Replace the `$ref: "../schema/core.yaml#/components/..."` JSON References
    in `io_spec.components` with the inlined values from `schema_components`.
    """
    comp = io_spec.get("components", {})
    # io/core.yaml has components.schemas/parameters/responses as $ref strings
    # pointing to ../schema/core.yaml#/components/...
    # We replace each with the resolved dict from schema_core.
    resolved = {}
    for key, value in comp.items():
        if isinstance(value, dict) and "$ref" in value:
            # e.g. {"$ref": "../schema/core.yaml#/components/schemas"}
            ref = value["$ref"]
            # Extract the fragment: "../schema/core.yaml#/components/schemas" → "schemas"
            if "#/components/" in ref:
                fragment_key = ref.split("#/components/")[-1]
                resolved[key] = schema_components.get(fragment_key, {})
            else:
                resolved[key] = value
        else:
            resolved[key] = value
    return resolved


def build_concrete_path(
    endpoint: str,
    action_class: str,
    abstract_path_item: dict,
) -> dict:
    """
    Build a concrete path item for /beckn/{endpoint} (POST only).

    The abstract io/core.yaml has GET + POST under a single path. For the
    generated beckn.yaml we only emit POST (the standard Beckn action call
    pattern). The GET (Query Mode) path is retained as-is in io/core.yaml
    and is not replicated per-action — it lives at the abstract level.

    requestBody.$ref is replaced with the canonical schema.beckn.io IRI.
    """
    post_op = abstract_path_item.get("post", {})
    # Deep-copy so mutations don't affect the template
    concrete_post = copy.deepcopy(post_op)

    # Rewrite requestBody schema ref
    try:
        rb = concrete_post["requestBody"]["content"]["application/json"]["schema"]
        rb["$ref"] = canonical_iri(action_class)
    except KeyError:
        pass  # no requestBody → leave as-is

    # Update summary and description to be action-specific
    action_name = action_class.replace("Action", "")  # e.g. "Discover"
    concrete_post["summary"] = (
        concrete_post.get("summary", "").replace(
            "Dispatch a Beckn protocol action", f"Beckn {action_name}"
        )
        or f"Beckn {action_name}"
    )
    # Replace generic operationId if present
    # endpoint is now "beckn/discover" → strip "beckn/" prefix, then remove underscores
    if "operationId" in concrete_post:
        bare = endpoint.split("/", 1)[-1]  # e.g. "discover", "on_discover"
        concrete_post["operationId"] = bare.replace("_", "")  # e.g. "discover", "ondiscover"

    return {"post": concrete_post}


def generate(io_spec: dict, schema_spec: dict) -> dict:
    """
    Produce the full beckn.yaml spec dict.
    """
    schema_components = schema_spec.get("components", {})
    abstract_path_item = io_spec.get("paths", {}).get("/{becknEndpoint}", {})

    # ── Build ordered paths dict ──────────────────────────────────────────────
    # endpoint is now a full beckn/-prefixed value (e.g. "beckn/discover"),
    # so the path key is simply "/{endpoint}" → "/beckn/discover".
    paths: dict = {}
    for endpoint, action_class in ACTIONS:
        path_key = f"/{endpoint}"
        paths[path_key] = build_concrete_path(endpoint, action_class, abstract_path_item)

    # ── Resolve components ────────────────────────────────────────────────────
    components = resolve_io_refs(io_spec, schema_components)

    # ── Build output spec ─────────────────────────────────────────────────────
    out: dict = {
        "openapi": io_spec.get("openapi", "3.1.1"),
        "info": {
            **io_spec.get("info", {}),
            "title": "Beckn Protocol API",
            "description": (
                "The API specification of Beckn Protocol — a fully resolved, concrete OpenAPI\n"
                "specification with one named path per known Beckn endpoint.\n"
                "\n"
                "Each Beckn Network Participant (BAP, BPP, Registry, CDS, CPS) receives\n"
                "a request and receives a synchronous `Ack` (HTTP 200). The actual response\n"
                "arrives as a separate callback on the caller's registered callback endpoint\n"
                "using the corresponding `on_<action>` endpoint.\n"
                "\n"
                "AUTO-GENERATED — DO NOT EDIT DIRECTLY.\n"
                "Sources: api/v2.0.0/components/io/core.yaml | api/v2.0.0/components/schema/core.yaml\n"
                "Regenerate: `cd protocol-specifications-v2 && python3 scripts/rebuild_beckn_yaml.py`\n"
            ),
        },
        "paths": paths,
        "components": components,
    }

    return out


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the generated spec to stdout; don't write the file.")
    args = parser.parse_args()

    for path in (IO_CORE_YAML, SCHEMA_CORE_YAML):
        if not os.path.exists(path):
            print(f"ERROR: source not found: {path}", file=sys.stderr)
            sys.exit(1)

    print(f"Reading io spec:     {IO_CORE_YAML}", file=sys.stderr)
    print(f"Reading schema spec: {SCHEMA_CORE_YAML}", file=sys.stderr)

    io_spec = load_yaml(IO_CORE_YAML)
    schema_spec = load_yaml(SCHEMA_CORE_YAML)

    out = generate(io_spec, schema_spec)

    header = (
        "# AUTO-GENERATED — DO NOT EDIT DIRECTLY\n"
        "# Sources:\n"
        "#   api/v2.0.0/components/io/core.yaml      — abstract IO / endpoint template\n"
        "#   api/v2.0.0/components/schema/core.yaml  — transport-layer schemas\n"
        "#   https://schema.beckn.io                  — action schemas (external IRIs)\n"
        "# Regenerate: cd protocol-specifications-v2 && python3 scripts/rebuild_beckn_yaml.py\n"
        "#\n"
    )
    content = header + dump_yaml(out)

    # Log summary
    print(f"\nGenerated {len(out['paths'])} paths:", file=sys.stderr)
    # Build a lookup: path_key → action_class
    path_to_action = {f"/{ep}": cls for ep, cls in ACTIONS}
    for path_key in out["paths"]:
        action_cls = path_to_action.get(path_key, "?")
        iri = canonical_iri(action_cls)
        print(f"  {path_key:35s}  → {iri}", file=sys.stderr)

    schemas_kept = list(out.get("components", {}).get("schemas", {}).keys())
    print(f"\nTransport schemas ({len(schemas_kept)}): {', '.join(schemas_kept)}", file=sys.stderr)

    if args.dry_run:
        print("\n--- DRY-RUN OUTPUT ---")
        print(content)
        print("--- END DRY-RUN ---\n")
        print("(No file written — pass without --dry-run to write)", file=sys.stderr)
        return

    with open(OUTPUT_YAML, "w", encoding="utf-8") as fh:
        fh.write(content)

    lines = content.count("\n")
    print(f"\nWritten: {OUTPUT_YAML}  ({lines} lines)", file=sys.stderr)


if __name__ == "__main__":
    main()
