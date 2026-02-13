#!/usr/bin/env python3
"""
Normalize and patch schema/core/v2.1/updated.vocab.jsonld.

Goals:
- Deduplicate @graph nodes by @id (keep first occurrence, merge missing keys).
- Apply v2.0 -> v2.1 mapping updates (Consumer hierarchy, legacy aliases, etc.).
- Add proxy beckn:* terms to avoid schema.org IRIs in updated.context.jsonld.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[3]
VOCAB_PATH = ROOT / "schema/core/v2.1/updated.vocab.jsonld"


def load_vocab(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dedupe_graph(graph: List[Dict[str, Any]]) -> Tuple[List[str], Dict[str, Dict[str, Any]], List[str]]:
    ordered_ids: List[str] = []
    id_map: Dict[str, Dict[str, Any]] = {}
    conflicts: List[str] = []

    for item in graph:
        item_id = item.get("@id")
        if not item_id:
            continue
        if item_id not in id_map:
            id_map[item_id] = item
            ordered_ids.append(item_id)
            continue

        existing = id_map[item_id]
        for key, value in item.items():
            if key not in existing:
                existing[key] = value
            elif existing[key] != value:
                conflicts.append(
                    f"Conflict for {item_id} field {key}: keeping {existing[key]!r}, ignoring {value!r}"
                )

    return ordered_ids, id_map, conflicts


def ensure_node(
    ordered_ids: List[str],
    id_map: Dict[str, Dict[str, Any]],
    node_id: str,
    defaults: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if node_id in id_map:
        node = id_map[node_id]
    else:
        node = {"@id": node_id}
        id_map[node_id] = node
        ordered_ids.append(node_id)
    if defaults:
        node.update(defaults)
    return node


def set_types(node: Dict[str, Any], types: List[str]) -> None:
    existing = node.get("@type")
    if not existing:
        node["@type"] = types[0] if len(types) == 1 else types
        return

    if isinstance(existing, list):
        combined = list(dict.fromkeys(existing + types))
    else:
        combined = list(dict.fromkeys([existing] + types))
    node["@type"] = combined[0] if len(combined) == 1 else combined


def ensure_property(
    ordered_ids: List[str],
    id_map: Dict[str, Dict[str, Any]],
    node_id: str,
    label: str,
    comment: str,
    domain: Any | None = None,
    range_includes: Any | None = None,
    sub_property_of: Any | None = None,
    equivalent_property: Any | None = None,
    deprecated: bool | None = None,
) -> Dict[str, Any]:
    node = ensure_node(
        ordered_ids,
        id_map,
        node_id,
        {
            "rdfs:label": label,
            "rdfs:comment": comment,
        },
    )
    set_types(node, ["rdf:Property"])
    if domain is not None:
        node["rdfs:domain"] = domain
    if range_includes is not None:
        node["schema:rangeIncludes"] = range_includes
    if sub_property_of is not None:
        node["rdfs:subPropertyOf"] = sub_property_of
    if equivalent_property is not None:
        node["owl:equivalentProperty"] = equivalent_property
    if deprecated is not None:
        node["owl:deprecated"] = deprecated
    return node


def ensure_class(
    ordered_ids: List[str],
    id_map: Dict[str, Dict[str, Any]],
    node_id: str,
    label: str,
    comment: str,
    sub_class_of: Any | None = None,
    equivalent_class: Any | None = None,
    deprecated: bool | None = None,
) -> Dict[str, Any]:
    node = ensure_node(
        ordered_ids,
        id_map,
        node_id,
        {
            "rdfs:label": label,
            "rdfs:comment": comment,
        },
    )
    set_types(node, ["rdfs:Class"])
    if sub_class_of is not None:
        node["rdfs:subClassOf"] = sub_class_of
    if equivalent_class is not None:
        node["owl:equivalentClass"] = equivalent_class
    if deprecated is not None:
        node["owl:deprecated"] = deprecated
    return node


def patch_vocab(ordered_ids: List[str], id_map: Dict[str, Dict[str, Any]]) -> None:
    # Consumer hierarchy
    ensure_class(
        ordered_ids,
        id_map,
        "beckn:Consumer",
        "Consumer",
        "Abstract consumer entity - can be a Person or Organization in v2.1",
    )
    ensure_class(
        ordered_ids,
        id_map,
        "beckn:PersonAsConsumer",
        "Person As Consumer",
        "A person acting in consumer role. Maps to v2.0 Buyer.",
        sub_class_of=[{"@id": "beckn:Consumer"}, {"@id": "schema:Person"}],
    )
    ensure_class(
        ordered_ids,
        id_map,
        "beckn:OrgAsConsumer",
        "Organization As Consumer",
        "An organization acting in consumer role.",
        sub_class_of=[{"@id": "beckn:Consumer"}, {"@id": "schema:Organization"}],
    )
    ensure_class(
        ordered_ids,
        id_map,
        "beckn:Buyer",
        "Buyer (DEPRECATED - v2.0 legacy)",
        "DEPRECATED: Use beckn:PersonAsConsumer or beckn:OrgAsConsumer in v2.1. Legacy v2.0 class for person purchasing items.",
        sub_class_of={"@id": "beckn:PersonAsConsumer"},
        equivalent_class={"@id": "beckn:PersonAsConsumer"},
        deprecated=True,
    )

    # Proxy schema.org terms to avoid schema IRIs in context
    ensure_class(
        ordered_ids,
        id_map,
        "beckn:Person",
        "Person",
        "Proxy for schema:Person to avoid schema.org IRIs in context.",
        equivalent_class={"@id": "schema:Person"},
    )
    ensure_class(
        ordered_ids,
        id_map,
        "beckn:Organization",
        "Organization",
        "Proxy for schema:Organization to avoid schema.org IRIs in context.",
        equivalent_class={"@id": "schema:Organization"},
    )
    ensure_class(
        ordered_ids,
        id_map,
        "beckn:PriceSpecification",
        "Price Specification",
        "Proxy for schema:PriceSpecification to avoid schema.org IRIs in context.",
        equivalent_class={"@id": "schema:PriceSpecification"},
    )
    for prop, label in [
        ("email", "Email"),
        ("telephone", "Telephone"),
        ("age", "Age"),
        ("duration", "Duration"),
        ("knowsLanguage", "Knows language"),
        ("worksFor", "Works for"),
    ]:
        ensure_property(
            ordered_ids,
            id_map,
            f"beckn:{prop}",
            label,
            f"Proxy for schema:{prop} to avoid schema.org IRIs in context.",
            equivalent_property={"@id": f"schema:{prop}"},
        )

    # Legacy displayName -> Descriptor.name
    ensure_property(
        ordered_ids,
        id_map,
        "beckn:displayName",
        "Display name (legacy v2 IRI)",
        "DEPRECATED: Use beckn:name (Descriptor.name). This legacy property IRI is retained for backward compatibility with Beckn v2.0.",
        equivalent_property={"@id": "beckn:name"},
        sub_property_of={"@id": "beckn:name"},
        deprecated=True,
    )

    # Fulfillment state model
    ensure_class(
        ordered_ids,
        id_map,
        "beckn:FulfillmentState",
        "Fulfillment State",
        "State specific to fulfillment lifecycle (v2.1)",
        sub_class_of={"@id": "beckn:State"},
    )
    ensure_property(
        ordered_ids,
        id_map,
        "beckn:currentFulfillmentState",
        "Current fulfillment state",
        "Scoped current state for a fulfillment.",
        domain=["beckn:Fulfillment"],
        range_includes="beckn:FulfillmentStateDescriptor",
        sub_property_of={"@id": "beckn:currentState"},
    )
    ensure_property(
        ordered_ids,
        id_map,
        "beckn:fulfillmentStatus",
        "Fulfillment status (legacy v2 IRI)",
        "DEPRECATED: Use beckn:currentFulfillmentState with FulfillmentStateDescriptor.",
        domain="beckn:Fulfillment",
        range_includes="beckn:FulfillmentState",
        sub_property_of={"@id": "beckn:currentFulfillmentState"},
        deprecated=True,
    )

    # buyer/seller legacy properties
    ensure_property(
        ordered_ids,
        id_map,
        "beckn:buyer",
        "Buyer (legacy v2 property)",
        "DEPRECATED: Use beckn:consumer. Legacy v2.0 buyer property retained for backward compatibility.",
        domain="beckn:Order",
        range_includes="beckn:Buyer",
        equivalent_property={"@id": "beckn:consumer"},
        sub_property_of={"@id": "beckn:consumer"},
        deprecated=True,
    )
    ensure_property(
        ordered_ids,
        id_map,
        "beckn:seller",
        "Seller (legacy v2 property)",
        "DEPRECATED: Use beckn:provider. Legacy v2.0 seller property retained for backward compatibility.",
        domain="beckn:Order",
        range_includes="beckn:Provider",
        equivalent_property={"@id": "beckn:provider"},
        sub_property_of={"@id": "beckn:provider"},
        deprecated=True,
    )

    # Snake_case legacy properties -> camelCase
    legacy_props = {
        "transaction_id": "transactionId",
        "ack_status": "ackStatus",
        "tl_method": "tlMethod",
        "expires_at": "expiresAt",
        "mime_type": "mimeType",
        "submission_id": "submissionId",
        "text_search": "textSearch",
        "key_id": "keyId",
        "media_search": "mediaSearch",
    }
    for legacy, modern in legacy_props.items():
        ensure_property(
            ordered_ids,
            id_map,
            f"beckn:{legacy}",
            f"{legacy} (legacy v2 IRI)",
            f"DEPRECATED: Use beckn:{modern}. This legacy snake_case IRI is retained for backward compatibility with Beckn v2.0.",
            equivalent_property={"@id": f"beckn:{modern}"},
            deprecated=True,
        )

    # Scoped descriptor properties (per parent)
    descriptor_scopes = [
        ("Catalog", "CatalogDescriptor"),
        ("Item", "ItemDescriptor"),
        ("Offer", "OfferDescriptor"),
        ("Provider", "ProviderDescriptor"),
        ("Order", "OrderDescriptor"),
        ("OrderItem", "OrderItemDescriptor"),
        ("Fulfillment", "FulfillmentDescriptor"),
        ("Payment", "PaymentDescriptor"),
        ("Invoice", "InvoiceDescriptor"),
        ("Location", "LocationDescriptor"),
        ("Policy", "PolicyDescriptor"),
        ("State", "StateDescriptor"),
        ("FulfillmentState", "FulfillmentStateDescriptor"),
        ("Alert", "AlertDescriptor"),
        ("Instruction", "InstructionDescriptor"),
        ("Entitlement", "EntitlementDescriptor"),
        ("Credential", "CredentialDescriptor"),
        ("Skill", "SkillDescriptor"),
        ("Participant", "ParticipantDescriptor"),
        ("FulfillmentAgent", "FulfillmentAgentDescriptor"),
        ("SupportInfo", "SupportInfoDescriptor"),
        ("Constraint", "ConstraintDescriptor"),
        ("CancellationPolicy", "CancellationPolicyDescriptor"),
    ]

    for parent, descriptor_class in descriptor_scopes:
        prop_name = descriptor_class[0].lower() + descriptor_class[1:]
        ensure_property(
            ordered_ids,
            id_map,
            f"beckn:{prop_name}",
            f"{parent} descriptor",
            f"Scoped descriptor for {parent} metadata.",
            domain=f"beckn:{parent}",
            range_includes=f"beckn:{descriptor_class}",
            sub_property_of={"@id": "beckn:descriptor"},
        )


def main() -> None:
    vocab = load_vocab(VOCAB_PATH)
    graph = vocab.get("@graph", [])
    ordered_ids, id_map, conflicts = dedupe_graph(graph)

    patch_vocab(ordered_ids, id_map)

    vocab["@graph"] = [id_map[node_id] for node_id in ordered_ids]

    with VOCAB_PATH.open("w", encoding="utf-8") as handle:
        json.dump(vocab, handle, indent=2, ensure_ascii=False)

    if conflicts:
        conflict_log = ROOT / "scripts/v2.1/ontology_tools/updated_vocab_conflicts.log"
        with conflict_log.open("w", encoding="utf-8") as handle:
            handle.write("\n".join(conflicts))


if __name__ == "__main__":
    main()