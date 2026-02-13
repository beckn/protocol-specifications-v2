"""
Mapping rules and transformation functions for v2.0 → v2.1 conversion.

Handles:
- Envelope context key mapping (snake_case → camelCase)
- JSON-LD prefix removal (beckn:id → id)
- Structural transformations (Order, Payment, etc.)
- Descriptor field migrations
"""

from typing import Dict, Any, Optional, List
from copy import deepcopy


# Envelope context key mappings (snake_case → camelCase)
ENVELOPE_KEY_MAP = {
    "transaction_id": "transactionId",
    "message_id": "messageId",
    "bap_id": "bapId",
    "bap_uri": "bapUri",
    "bpp_id": "bppId",
    "bpp_uri": "bppUri",
    "schema_context": "schemas",
    "ack_status": "ackStatus",
    "key_id": "keyId",
}

# JSON-LD prefix removal mappings
PREFIX_REMOVAL_MAP = {
    "beckn:id": "id",
    "beckn:descriptor": "descriptor",
    "beckn:provider": "provider",
    "beckn:items": "items",
    "beckn:offers": "offers",
    "beckn:seller": "seller",  # Will be renamed to provider in Order
    "beckn:buyer": "buyer",    # Will be restructured in Order
    "beckn:orderItems": "orderItems",
    "beckn:orderedItem": "orderedItem",
    "beckn:fulfillment": "fulfillment",  # Will be wrapped to array
    "beckn:invoice": "invoice",          # Will be wrapped to array
    "beckn:payment": "payment",          # Will be decomposed
    "beckn:shortDesc": "shortDesc",
    "beckn:longDesc": "longDesc",
    "beckn:category": "category",
    "beckn:rating": "rating",
    "beckn:ratingValue": "ratingValue",
    "beckn:ratingCount": "ratingCount",
    "beckn:quantity": "quantity",
    "beckn:isActive": "isActive",
    "beckn:rateable": "rateable",
    "beckn:validity": "validity",
    "beckn:price": "price",
    "beckn:method": "method",
    "beckn:paymentStatus": "paymentStatus",
    "beckn:amount": "amount",
    "beckn:beneficiary": "beneficiary",
    "beckn:txnRef": "txnRef",
    "beckn:paidAt": "paidAt",
    "beckn:paymentURL": "paymentURL",
    "beckn:acceptedPaymentMethod": "acceptedPaymentMethod",
    "beckn:orderStatus": "orderStatus",
    "beckn:orderNumber": "orderNumber",
    "beckn:orderValue": "orderValue",
    "beckn:itemAttributes": "itemAttributes",
    "beckn:offerAttributes": "offerAttributes",
    "beckn:orderAttributes": "orderAttributes",
    "beckn:providerAttributes": "providerAttributes",
    "beckn:buyerAttributes": "buyerAttributes",
    "beckn:paymentAttributes": "paymentAttributes",
    "beckn:networkId": "networkId",
    "beckn:availableAt": "availableAt",
    "beckn:availabilityWindow": "availabilityWindow",
    "beckn:bppId": "bppId",
    "beckn:bppUri": "bppUri",
    "beckn:providerId": "providerId",
    "beckn:locations": "locations",
    "schema:name": "name",
    "schema:image": "images",  # Will extract first as thumbnailImage
    "schema:startDate": "startDate",
    "schema:endDate": "endDate",
    "schema:startTime": "startTime",
    "schema:endTime": "endTime",
    "schema:codeValue": "codeValue",
    "schema:description": "description",
}

# Fields to drop with warnings
DROPPED_FIELDS = {
    "tl_method": "Removed in v2.1, tracking transport method no longer used"
}

# v2.1 context URL
V21_CONTEXT_URL = "https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/context.jsonld"


def convert_envelope_keys(context: Dict[str, Any]) -> Dict[str, Any]:
    """Convert envelope context keys from snake_case to camelCase"""
    converted = {}
    for key, value in context.items():
        new_key = ENVELOPE_KEY_MAP.get(key, key)
        converted[new_key] = value
    
    # Override version to 2.1.0
    converted["version"] = "2.1.0"
    
    return converted


def remove_prefixes(obj: Any, path: str = "") -> Any:
    """Recursively remove JSON-LD prefixes from keys"""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # Map prefixed keys to unprefixed
            new_key = PREFIX_REMOVAL_MAP.get(key, key)
            
            # Special handling for dropped fields
            if key in DROPPED_FIELDS:
                continue  # Skip this field
            
            new_path = f"{path}.{new_key}" if path else new_key
            result[new_key] = remove_prefixes(value, new_path)
        return result
    elif isinstance(obj, list):
        return [remove_prefixes(item, f"{path}[]") for item in obj]
    else:
        return obj


def convert_descriptor(descriptor: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Descriptor field structure"""
    result = deepcopy(descriptor)
    
    # schema:name → name (already handled by remove_prefixes)
    # schema:image → thumbnailImage (extract first image)
    if "images" in result and isinstance(result["images"], list) and result["images"]:
        result["thumbnailImage"] = result["images"][0]
        del result["images"]
    
    return result


def convert_buyer_to_consumer(buyer: Dict[str, Any]) -> Dict[str, Any]:
    """Convert v2.0 Buyer to v2.1 Consumer with person identity"""
    consumer = {
        "@context": V21_CONTEXT_URL,
        "@type": "beckn:Consumer",
        "person": {
            "@context": V21_CONTEXT_URL,
            "@type": "schema:Person",
            "id": buyer.get("id", "")
        }
    }
    
    # Map buyer fields to person
    person = consumer["person"]
    if "displayName" in buyer:
        person["name"] = buyer["displayName"]
    if "telephone" in buyer:
        person["telephone"] = buyer["telephone"]
    if "email" in buyer:
        person["email"] = buyer["email"]
    
    # Preserve buyerAttributes as consumerAttributes
    if "buyerAttributes" in buyer:
        consumer["consumerAttributes"] = buyer["buyerAttributes"]
    
    return consumer


def decompose_payment(payment: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Decompose v2.0 Payment into v2.1 PaymentTerms + PaymentAction
    
    Returns:
        (payment_terms, payment_action)
    """
    # PaymentTerms: who collects, settlement terms
    payment_terms = {
        "@context": V21_CONTEXT_URL,
        "@type": "beckn:PaymentTerms"
    }
    
    # Map beneficiary to collectedBy
    beneficiary = payment.get("beneficiary", "BPP")
    payment_terms["collectedBy"] = beneficiary
    
    # If there are settlement-related fields, add settlementTerms
    # (In practice, v2.0 Payment may not have all these; we provide a basic structure)
    if any(k in payment for k in ["amount", "beneficiary"]):
        settlement_term = {
            "@context": V21_CONTEXT_URL,
            "@type": "beckn:SettlementTerm"
        }
        if "amount" in payment:
            settlement_term["amount"] = payment["amount"]
        if "beneficiary" in payment:
            # Map to payTo structure (simplified)
            settlement_term["settlementStatus"] = "PENDING"
        
        payment_terms["settlementTerms"] = [settlement_term]
    
    # Preserve paymentAttributes if present
    if "paymentAttributes" in payment:
        payment_terms["paymentTermsAttributes"] = payment["paymentAttributes"]
    
    # PaymentAction: status, transaction refs, amount
    payment_action = {
        "@context": V21_CONTEXT_URL,
        "@type": "beckn:PaymentAction"
    }
    
    if "paymentStatus" in payment:
        payment_action["paymentStatus"] = payment["paymentStatus"]
    if "amount" in payment:
        payment_action["amount"] = payment["amount"]
    if "txnRef" in payment:
        payment_action["txnRef"] = payment["txnRef"]
    if "paidAt" in payment:
        payment_action["paidAt"] = payment["paidAt"]
    if "paymentURL" in payment:
        payment_action["paidTo"] = payment["paymentURL"]
    if "method" in payment:
        payment_action["paymentMethod"] = {"method": payment["method"]}
    
    return payment_terms, payment_action


def convert_tracking(tracking: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Tracking object (drop tl_method, rename expires_at)"""
    result = {}
    
    for key, value in tracking.items():
        if key == "expires_at":
            result["expiresAt"] = value
        elif key == "tl_method":
            # Drop this field (will be logged as warning)
            continue
        else:
            result[key] = value
    
    return result


def convert_form(form: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Form object (rename mime_type, submission_id)"""
    result = {}
    
    for key, value in form.items():
        if key == "mime_type":
            result["mimeType"] = value
        elif key == "submission_id":
            result["submissionId"] = value
        else:
            result[key] = value
    
    return result


def convert_order(order: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert v2.0 Order to v2.1 Order with structural changes:
    - seller → provider
    - buyer → consumer (with person identity)
    - payment → paymentTerms + paymentAction
    - fulfillment → fulfillments[] (wrap to array)
    - invoice → invoices[] (wrap to array)
    """
    result = deepcopy(order)
    
    # seller → provider
    if "seller" in result:
        result["provider"] = result.pop("seller")
    
    # buyer → consumer
    if "buyer" in result:
        result["consumer"] = convert_buyer_to_consumer(result.pop("buyer"))
    
    # payment → paymentTerms + paymentAction
    if "payment" in result:
        payment_terms, payment_action = decompose_payment(result.pop("payment"))
        result["paymentTerms"] = payment_terms
        result["paymentAction"] = payment_action
    
    # fulfillment → fulfillments[] (wrap single to array)
    if "fulfillment" in result and not isinstance(result["fulfillment"], list):
        result["fulfillments"] = [result.pop("fulfillment")]
    elif "fulfillment" in result:
        result["fulfillments"] = result.pop("fulfillment")
    
    # invoice → invoices[] (wrap single to array)
    if "invoice" in result and not isinstance(result["invoice"], list):
        result["invoices"] = [result.pop("invoice")]
    elif "invoice" in result:
        result["invoices"] = result.pop("invoice")
    
    # orderedItem → itemId in OrderItems
    if "orderItems" in result:
        for item in result["orderItems"]:
            if "orderedItem" in item:
                item["itemId"] = item.pop("orderedItem")
    
    return result


def convert_entity(entity: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
    """
    Convert a v2.0 entity to v2.1 format
    
    Args:
        entity: The entity object
        entity_type: Type hint (Order, Item, Catalog, etc.)
    """
    # First remove prefixes
    converted = remove_prefixes(entity)
    
    # Apply type-specific conversions
    if entity_type == "Order":
        converted = convert_order(converted)
    
    # Convert descriptor if present
    if "descriptor" in converted and isinstance(converted["descriptor"], dict):
        converted["descriptor"] = convert_descriptor(converted["descriptor"])
    
    # Convert tracking if present
    if "tracking" in converted and isinstance(converted["tracking"], dict):
        converted["tracking"] = convert_tracking(converted["tracking"])
    
    # Convert form if present
    if "form" in converted and isinstance(converted["form"], dict):
        converted["form"] = convert_form(converted["form"])
    
    return converted
