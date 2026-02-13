#!/usr/bin/env python3
"""
Update schema/core/v2.1/updated.context.jsonld to:
- remove schema.org IRIs
- add legacy aliases and scoped descriptor contexts
- use scoped currentFulfillmentState under Fulfillment
"""

import json
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[3]
CONTEXT_PATH = ROOT / "schema/core/v2.1/updated.context.jsonld"


LEGACY_SNAKE_CASE = {
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


SCHEMA_PROXY = {
    "Person": "beckn:Person",
    "Organization": "beckn:Organization",
    "PriceSpecification": "beckn:PriceSpecification",
    "email": "beckn:email",
    "telephone": "beckn:telephone",
    "age": "beckn:age",
    "duration": "beckn:duration",
    "knowsLanguage": "beckn:knowsLanguage",
    "worksFor": "beckn:worksFor",
    "price": "beckn:price",
    "unitCode": "beckn:unitCode",
    "unitText": "beckn:unitText",
    "eligibleQuantity": "beckn:eligibleQuantity",
    "displayName": "beckn:name",
}


DESCRIPTOR_SCOPES = {
    "Catalog": "catalogDescriptor",
    "Item": "itemDescriptor",
    "Offer": "offerDescriptor",
    "Provider": "providerDescriptor",
    "Order": "orderDescriptor",
    "OrderItem": "orderItemDescriptor",
    "Fulfillment": "fulfillmentDescriptor",
    "Payment": "paymentDescriptor",
    "Invoice": "invoiceDescriptor",
    "Location": "locationDescriptor",
    "Policy": "policyDescriptor",
    "State": "stateDescriptor",
    "FulfillmentState": "fulfillmentStateDescriptor",
    "Alert": "alertDescriptor",
    "Instruction": "instructionDescriptor",
    "Entitlement": "entitlementDescriptor",
    "Credential": "credentialDescriptor",
    "Skill": "skillDescriptor",
    "Participant": "participantDescriptor",
    "FulfillmentAgent": "fulfillmentAgentDescriptor",
    "SupportInfo": "supportInfoDescriptor",
    "Constraint": "constraintDescriptor",
    "CancellationPolicy": "cancellationPolicyDescriptor",
}


def load_context(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ensure_entry(context: Dict[str, Any], key: str, value: Any) -> None:
    context[key] = value


def ensure_nested_context(context: Dict[str, Any], class_name: str, prop_key: str, prop_id: str) -> None:
    entry = context.get(class_name)
    if not isinstance(entry, dict):
        entry = {"@id": f"beckn:{class_name}"}
    nested = entry.get("@context")
    if not isinstance(nested, dict):
        nested = {}
    nested[prop_key] = prop_id
    entry["@context"] = nested
    context[class_name] = entry


def main() -> None:
    data = load_context(CONTEXT_PATH)
    context = data.get("@context", {})

    # Remove any schema:* mappings by replacing with beckn proxies
    for key, replacement in SCHEMA_PROXY.items():
        if key in context:
            context[key] = replacement

    # Remove schema prefix entirely
    context.pop("schema", None)

    # Legacy aliases
    ensure_entry(context, "buyer", "beckn:consumer")
    ensure_entry(context, "seller", "beckn:provider")
    ensure_entry(context, "orderedItem", "beckn:itemId")

    for legacy_key, modern_key in LEGACY_SNAKE_CASE.items():
        ensure_entry(context, legacy_key, f"beckn:{modern_key}")

    # Scoped descriptors
    for class_name, prop_key in DESCRIPTOR_SCOPES.items():
        ensure_nested_context(context, class_name, "descriptor", f"beckn:{prop_key}")

    # Scoped fulfillment current state
    ensure_nested_context(context, "Fulfillment", "currentState", "beckn:currentFulfillmentState")

    data["@context"] = context

    with CONTEXT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()