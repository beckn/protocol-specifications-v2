#!/usr/bin/env python3
"""
generate_endpoints.py
─────────────────────
Generates api/v2.0.0/beckn.yaml — a fully resolved, concrete OpenAPI
specification with one named path per known Beckn endpoint.

Inputs (all relative to the protocol-specifications-v2 root):
  api/v2.0.0/components/io/core.yaml      abstract IO spec (source of truth)
  api/v2.0.0/components/schema/core.yaml  transport-layer schemas
  ../core_schema/schema/**                data model schemas

Output:
  api/v2.0.0/beckn.yaml                   fully resolved, 20 concrete paths

Usage:
  cd protocol-specifications-v2
  python3 scripts/generate_endpoints.py [options]

  --core-schema PATH   path to core_schema/schema/ (default: ../core_schema/schema)
  --output PATH        output path (default: api/v2.0.0/beckn.yaml)
  --dry-run            preview without writing
"""

from __future__ import annotations
import argparse
import copy
import os
import sys
import textwrap
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml is required. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ─── Constants ────────────────────────────────────────────────────────────────

BECKN_IO = "https://schema.beckn.io/"

# Human-readable metadata for each known Beckn endpoint.
ENDPOINT_META: dict[str, dict] = {
    "beckn/discover": {
        "summary": "Discover — BAP sends a discovery request",
        "description": (
            "BAP sends a discovery intent to one or more BPPs to find catalogs "
            "matching the consumer's requirements. The intent may carry a free-text "
            "query, structured filters, spatial constraints, or media inputs."
        ),
        "direction": "BAP → BPP",
    },
    "beckn/on_discover": {
        "summary": "On-Discover — BPP returns matching catalogs",
        "description": (
            "BPP responds to a discover request with catalogs that match the "
            "expressed intent. Each catalog contains the provider's items, offers, "
            "fulfillment options, and pricing."
        ),
        "direction": "BPP → BAP (async callback)",
    },
    "beckn/select": {
        "summary": "Select — BAP selects items and requests a quote",
        "description": (
            "BAP sends the consumer's selected items and asks the BPP to generate "
            "a draft contract with pricing, taxes, and available fulfillment options."
        ),
        "direction": "BAP → BPP",
    },
    "beckn/on_select": {
        "summary": "On-Select — BPP returns a draft contract with quote",
        "description": (
            "BPP responds with a draft contract reflecting the selected items, "
            "computed pricing, applicable taxes, and fulfillment options."
        ),
        "direction": "BPP → BAP (async callback)",
    },
    "beckn/init": {
        "summary": "Init — BAP submits billing and fulfillment details",
        "description": (
            "BAP submits the consumer's billing address, chosen fulfillment option, "
            "and preferred payment method to initiate an order."
        ),
        "direction": "BAP → BPP",
    },
    "beckn/on_init": {
        "summary": "On-Init — BPP returns final terms and payment instructions",
        "description": (
            "BPP responds with the final order terms, complete price breakdown, "
            "and payment/settlement instructions. The consumer reviews these terms "
            "before confirming."
        ),
        "direction": "BPP → BAP (async callback)",
    },
    "beckn/confirm": {
        "summary": "Confirm — BAP confirms the order",
        "description": (
            "BAP confirms the order after the consumer has reviewed and accepted the "
            "final terms returned in on_init. This creates a binding order."
        ),
        "direction": "BAP → BPP",
    },
    "beckn/on_confirm": {
        "summary": "On-Confirm — BPP acknowledges order confirmation",
        "description": (
            "BPP acknowledges the confirmed order and returns the active contract "
            "with the assigned order identifier and fulfillment state."
        ),
        "direction": "BPP → BAP (async callback)",
    },
    "beckn/status": {
        "summary": "Status — BAP queries current order status",
        "description": (
            "BAP requests the current status of a previously confirmed order by "
            "providing the order identifier."
        ),
        "direction": "BAP → BPP",
    },
    "beckn/on_status": {
        "summary": "On-Status — BPP returns current order status",
        "description": (
            "BPP returns the current state of the order, including the latest "
            "fulfillment stage, tracking state, and any active alerts."
        ),
        "direction": "BPP → BAP (async callback)",
    },
    "beckn/track": {
        "summary": "Track — BAP requests a real-time tracking link",
        "description": (
            "BAP requests a real-time tracking URL or WebSocket handle for an "
            "active fulfillment leg."
        ),
        "direction": "BAP → BPP",
    },
    "beckn/on_track": {
        "summary": "On-Track — BPP returns tracking information",
        "description": (
            "BPP returns a tracking URL, WebSocket handle, or embedded real-time "
            "tracking feed for the active fulfillment."
        ),
        "direction": "BPP → BAP (async callback)",
    },
    "beckn/update": {
        "summary": "Update — BAP updates an active order",
        "description": (
            "BAP requests a modification to an active order, such as changing the "
            "fulfillment address, adjusting quantities, or adding items."
        ),
        "direction": "BAP → BPP",
    },
    "beckn/on_update": {
        "summary": "On-Update — BPP returns the updated contract",
        "description": (
            "BPP returns the updated contract reflecting the applied changes, "
            "including any pricing adjustments."
        ),
        "direction": "BPP → BAP (async callback)",
    },
    "beckn/cancel": {
        "summary": "Cancel — BAP cancels an active order",
        "description": (
            "BAP cancels an active order, providing a cancellation reason code "
            "as defined in the applicable cancellation policy."
        ),
        "direction": "BAP → BPP",
    },
    "beckn/on_cancel": {
        "summary": "On-Cancel — BPP confirms order cancellation",
        "description": (
            "BPP confirms the cancellation and returns the final contract state, "
            "including any applicable refund terms."
        ),
        "direction": "BPP → BAP (async callback)",
    },
    "beckn/rate": {
        "summary": "Rate — BAP submits ratings and feedback",
        "description": (
            "BAP submits one or more ratings for entities in the completed order "
            "(item, fulfillment, provider, or agent), optionally with feedback "
            "form submissions."
        ),
        "direction": "BAP → BPP",
    },
    "beckn/on_rate": {
        "summary": "On-Rate — BPP returns rating forms",
        "description": (
            "BPP returns rating forms for the BAP to present to the consumer, "
            "enabling collection of structured feedback."
        ),
        "direction": "BPP → BAP (async callback)",
    },
    "beckn/support": {
        "summary": "Support — BAP requests support contact information",
        "description": (
            "BAP requests support contact details for a specific order or entity. "
            "The consumer may also initiate a support callback request."
        ),
        "direction": "BAP → BPP",
    },
    "beckn/on_support": {
        "summary": "On-Support — BPP returns support contact details",
        "description": (
            "BPP returns support contact information including email address, "
            "telephone number, chat endpoint, and available support channels."
        ),
        "direction": "BPP → BAP (async callback)",
    },
}


# ─── Schema naming helpers ────────────────────────────────────────────────────

def action_to_schema_name(action: str) -> str:
    """
    Convert a beckn action value to a CamelCase request schema name.

    beckn/discover       → DiscoverRequest
    beckn/on_discover    → OnDiscoverRequest
    beckn/support        → SupportActionRequest  (avoids clash with SupportRequest data model)
    """
    # Strip 'beckn/' prefix; handle sub-namespaces like 'beckn/igm/raise_grievance'
    parts = action.split("/")[1:]  # drop 'beckn'
    joined = "_".join(parts)
    name = "".join(word.capitalize() for word in joined.split("_")) + "Request"

    # Avoid collision with the SupportRequest data model schema
    if action == "beckn/support":
        name = "SupportActionRequest"

    return name


def uri_to_schema_name(uri: str) -> str:
    """
    Extract the schema name from a schema.beckn.io URI.
    https://schema.beckn.io/Intent/v2.0 → Intent
    """
    parts = uri.rstrip("/").split("/")
    # URI pattern: https://schema.beckn.io/{Name}/{version}
    # Last two segments are Name and version; we want Name
    if len(parts) >= 2:
        return parts[-2]
    return parts[-1]


# ─── Schema loading ───────────────────────────────────────────────────────────

def load_yaml(path: str) -> dict:
    """Load a YAML file and return the parsed dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_registry(schema_dir: str) -> dict[str, dict]:
    """
    Walk core_schema/schema/ and build a mapping:
      https://schema.beckn.io/{Name}/{version}  →  parsed attributes.yaml dict
    """
    registry: dict[str, dict] = {}
    root = Path(schema_dir)
    for attrs in root.glob("*/*/attributes.yaml"):
        try:
            doc = load_yaml(str(attrs))
            schema_id = doc.get("$id")
            if schema_id:
                # Normalise: strip trailing slash
                registry[schema_id.rstrip("/")] = doc
        except Exception as exc:
            print(f"  WARNING: could not load {attrs}: {exc}", file=sys.stderr)
    return registry


# ─── $ref collection & rewriting ─────────────────────────────────────────────

def collect_refs(obj, found: set[str]) -> None:
    """Recursively collect all beckn.io $ref base URIs (no fragment)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str) and v.startswith(BECKN_IO):
                found.add(v.split("#")[0].rstrip("/"))
            else:
                collect_refs(v, found)
    elif isinstance(obj, list):
        for item in obj:
            collect_refs(item, found)


def resolve_transitively(seeds: list[str], registry: dict[str, dict]) -> dict[str, dict]:
    """
    Starting from seed URIs, transitively load all referenced schemas.
    Returns {schema_name: cleaned_schema_dict} where the schema is stripped
    of $id/$schema (kept inside title/description for traceability).
    """
    resolved: dict[str, dict] = {}
    queue = list(seeds)
    visited: set[str] = set()

    while queue:
        uri = queue.pop(0)
        if uri in visited:
            continue
        visited.add(uri)

        doc = registry.get(uri)
        if not doc:
            print(f"  WARNING: $ref not in registry: {uri}", file=sys.stderr)
            continue

        name = uri_to_schema_name(uri)
        if name in resolved:
            continue

        # Store cleaned schema (keep $id as x-source-id for traceability; remove $schema)
        cleaned = {k: v for k, v in doc.items() if k != "$schema"}
        # Move $id to an extension field so it doesn't confuse OpenAPI tooling
        if "$id" in cleaned:
            cleaned["x-source-id"] = cleaned.pop("$id")
        resolved[name] = cleaned

        # Queue any new $refs found in this schema
        new_refs: set[str] = set()
        collect_refs(cleaned, new_refs)
        for ref in new_refs:
            if ref not in visited:
                queue.append(ref)

    return resolved


def rewrite_refs(obj, name_map: dict[str, str]):
    """
    Rewrite https://schema.beckn.io/X/v2.0[#fragment] → #/components/schemas/X[fragment].
    name_map maps URI → component schema name.
    """
    if isinstance(obj, dict):
        result: dict = {}
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str) and v.startswith(BECKN_IO):
                base = v.split("#")[0].rstrip("/")
                fragment = v[len(base):]
                comp_name = name_map.get(base)
                result[k] = f"#/components/schemas/{comp_name}{fragment}" if comp_name else v
            else:
                result[k] = rewrite_refs(v, name_map)
        return result
    if isinstance(obj, list):
        return [rewrite_refs(item, name_map) for item in obj]
    return obj


# ─── BecknAction parsing ──────────────────────────────────────────────────────

def parse_endpoints(beckn_action: dict) -> list[dict]:
    """
    Extract each if/then branch from BecknAction.allOf.
    Returns a list of:
      { action: str, message_props: dict, message_required: list[str] }
    """
    results = []
    for block in beckn_action.get("allOf", []):
        try:
            action = block["if"]["properties"]["context"]["properties"]["action"]["const"]
        except (KeyError, TypeError):
            continue
        then_msg = block.get("then", {}).get("properties", {}).get("message", {})
        results.append(
            {
                "action": action,
                "message_props": copy.deepcopy(then_msg.get("properties", {})),
                "message_required": then_msg.get("required", []),
            }
        )
    return results


# ─── Schema builders ──────────────────────────────────────────────────────────

def build_request_schema(action: str, message_props: dict, message_required: list) -> dict:
    """
    Build a concrete OpenAPI schema for one endpoint's request envelope.
    context.action is constrained to this specific action value.
    """
    name = action_to_schema_name(action)
    msg_schema: dict = {
        "description": f"Action-specific payload for `{action}`.",
        "type": "object",
    }
    if message_required:
        msg_schema["required"] = message_required
    if message_props:
        msg_schema["properties"] = message_props

    return {
        "title": name,
        "description": (
            f"Beckn Protocol request envelope for the `{action}` endpoint.\n\n"
            f"`context.action` MUST be set to `{action}`."
        ),
        "type": "object",
        "required": ["context", "message"],
        "additionalProperties": False,
        "properties": {
            "context": {
                "description": (
                    f"Transaction context. "
                    f"`context.action` MUST be `{action}`."
                ),
                "allOf": [{"$ref": "#/components/schemas/Context"}],
            },
            "message": msg_schema,
        },
    }


def build_path(action: str) -> dict:
    """Build the OpenAPI path entry for a concrete Beckn endpoint."""
    schema_name = action_to_schema_name(action)
    meta = ENDPOINT_META.get(action, {})
    summary = meta.get("summary", action)
    description = meta.get("description", "")
    direction = meta.get("direction", "")
    if direction:
        description += f"\n\n**Direction:** {direction}"

    return {
        "post": {
            "summary": summary,
            "description": description,
            "operationId": action.replace("/", "_"),
            "tags": [action.split("/")[1].replace("on_", "").capitalize()],
            "parameters": [{"$ref": "#/components/parameters/AuthorizationHeader"}],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{schema_name}"}
                    }
                },
            },
            "responses": {
                "200": {"$ref": "#/components/responses/Ack"},
                "400": {"$ref": "#/components/responses/NackBadRequest"},
                "401": {"$ref": "#/components/responses/NackUnauthorized"},
                "409": {"$ref": "#/components/responses/AckNoCallback"},
                "500": {"$ref": "#/components/responses/ServerError"},
            },
        }
    }


# ─── YAML dump with no aliases ────────────────────────────────────────────────

class NoAliasDumper(yaml.Dumper):
    """YAML Dumper that never emits aliases — all repeated nodes are written in full."""
    def ignore_aliases(self, data):
        return True


# ─── Main generator ───────────────────────────────────────────────────────────

def generate(
    core_schema_dir: str,
    transport_path: str,
    output_path: str,
    dry_run: bool = False,
) -> None:

    print(f"[1/6] Building schema registry from {core_schema_dir} ...")
    registry = build_registry(core_schema_dir)
    print(f"      {len(registry)} schemas loaded")

    print("[2/6] Loading transport schemas ...")
    transport = load_yaml(transport_path)
    transport_components = transport.get("components", {})

    print("[3/6] Parsing BecknAction endpoints ...")
    beckn_action_uri = "https://schema.beckn.io/BecknAction/v2.0"
    beckn_action = registry.get(beckn_action_uri)
    if beckn_action is None:
        print(f"ERROR: BecknAction not found in registry: {beckn_action_uri}", file=sys.stderr)
        sys.exit(1)

    raw_endpoints = parse_endpoints(beckn_action)
    if not raw_endpoints:
        print("ERROR: No if/then endpoints found in BecknAction.allOf", file=sys.stderr)
        sys.exit(1)
    print(f"      {len(raw_endpoints)} endpoints found")

    print("[4/6] Resolving data model schemas transitively ...")
    # Seed with Context, BecknEndpoint, LineageEntry, Message (always required)
    seeds: set[str] = {
        "https://schema.beckn.io/Context/v2.0",
        "https://schema.beckn.io/BecknEndpoint/v2.0",
        "https://schema.beckn.io/LineageEntry/v2.0",
        "https://schema.beckn.io/Message/v2.0",
    }
    # Add all refs from each endpoint's message properties
    endpoint_schemas: dict[str, dict] = {}
    paths: dict[str, dict] = {}

    for ep in raw_endpoints:
        action = ep["action"]
        collect_refs(ep["message_props"], seeds)
        endpoint_schemas[action_to_schema_name(action)] = build_request_schema(
            action, ep["message_props"], ep["message_required"]
        )
        paths[f"/{action}"] = build_path(action)

    # Resolve all seeds transitively
    data_model_schemas = resolve_transitively(list(seeds), registry)
    print(f"      {len(data_model_schemas)} data model schemas resolved")

    # Build URI → name map for ref rewriting
    ref_map: dict[str, str] = {}
    for uri in registry:
        ref_map[uri.rstrip("/")] = uri_to_schema_name(uri)

    print("[5/6] Rewriting $refs to #/components/schemas/ ...")
    data_model_schemas = {n: rewrite_refs(s, ref_map) for n, s in data_model_schemas.items()}
    endpoint_schemas = {n: rewrite_refs(s, ref_map) for n, s in endpoint_schemas.items()}

    print("[6/6] Assembling beckn.yaml ...")

    # Merge all schemas:
    #   1. Transport (Signature, Ack, Error, ...) from components/schema/core.yaml
    #   2. Data model schemas (from core_schema, refs rewritten)
    #   3. Endpoint request schemas (concrete per-action envelopes)
    all_schemas: dict = {}
    all_schemas.update(transport_components.get("schemas", {}))
    all_schemas.update(data_model_schemas)
    all_schemas.update(endpoint_schemas)

    output_doc = {
        "openapi": "3.1.1",
        "info": {
            "title": "Beckn Protocol API Specification Version 2",
            "description": textwrap.dedent("""\
                The API specification of Beckn Protocol — a fully resolved, concrete OpenAPI
                specification with one named path per known Beckn endpoint.

                **Interaction model:** All Beckn interactions are asynchronous. The caller sends
                a request and receives a synchronous `Ack` (HTTP 200). The actual response
                arrives as a separate callback on the caller's registered callback endpoint
                using the corresponding `on_<action>` endpoint.

                **Authentication:** All requests MUST carry a Beckn Signature in the
                `Authorization` header. See the `Signature` schema for the expected format.

                ---

                ⚠️ **THIS FILE IS AUTO-GENERATED. Do not edit directly.**

                | Source | Path |
                |--------|------|
                | Abstract IO spec | `api/v2.0.0/components/io/core.yaml` |
                | Transport schemas | `api/v2.0.0/components/schema/core.yaml` |
                | Data model schemas | `https://github.com/beckn/core_schema` |
                | Generator | `scripts/generate_endpoints.py` |

                Regenerate: `cd protocol-specifications-v2 && python3 scripts/generate_endpoints.py`
                """),
            "version": "2.0.0",
            "contact": {"name": "Beckn Protocol", "url": "https://beckn.io"},
            "license": {
                "name": "CC-BY-NC-SA 4.0 International",
                "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en",
            },
        },
        "paths": paths,
        "components": {
            "schemas": all_schemas,
            "parameters": transport_components.get("parameters", {}),
            "responses": transport_components.get("responses", {}),
        },
    }

    if dry_run:
        print(f"\n[DRY RUN] Would write to: {output_path}")
        print(f"  Paths:   {len(paths)}")
        print(f"  Schemas: {len(all_schemas)}")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(
            "# AUTO-GENERATED — DO NOT EDIT DIRECTLY\n"
            "# Sources: api/v2.0.0/components/io/core.yaml  |  "
            "api/v2.0.0/components/schema/core.yaml  |  "
            "github.com/beckn/core_schema\n"
            "# Regenerate: cd protocol-specifications-v2 && "
            "python3 scripts/generate_endpoints.py\n"
            "#\n"
        )
        yaml.dump(
            output_doc,
            f,
            Dumper=NoAliasDumper,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )

    print(f"\n✓ Written to: {output_path}")
    print(f"  Paths:   {len(paths)}")
    print(f"  Schemas: {len(all_schemas)}")


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main() -> None:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent  # protocol-specifications-v2/

    parser = argparse.ArgumentParser(
        description="Generate resolved Beckn Protocol endpoint YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--core-schema",
        default=str(repo_root.parent / "core_schema" / "schema"),
        metavar="PATH",
        help="Path to core_schema/schema directory (default: ../core_schema/schema)",
    )
    parser.add_argument(
        "--transport-schemas",
        default=str(repo_root / "api" / "v2.0.0" / "components" / "schema" / "core.yaml"),
        metavar="PATH",
        help="Path to transport schemas YAML",
    )
    parser.add_argument(
        "--output",
        default=str(repo_root / "api" / "v2.0.0" / "beckn.yaml"),
        metavar="PATH",
        help="Output path for generated beckn.yaml",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be generated without writing any files",
    )
    args = parser.parse_args()

    print("Beckn Endpoint Generator")
    print("=" * 50)
    print(f"Core schema dir:   {args.core_schema}")
    print(f"Transport schemas: {args.transport_schemas}")
    print(f"Output:            {args.output}")
    print()

    generate(
        core_schema_dir=args.core_schema,
        transport_path=args.transport_schemas,
        output_path=args.output,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
