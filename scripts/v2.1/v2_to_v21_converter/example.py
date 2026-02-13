#!/usr/bin/env python3
"""
Simple example demonstrating the v2.0 → v2.1 converter.
"""

import json
from v2_to_v21_converter import convert_v2_to_v21


def main():
    """Run a simple conversion example"""
    
    # Sample v2.0 Order payload
    v2_order = {
        "context": {
            "version": "2.0.0",
            "action": "on_confirm",
            "transaction_id": "txn-abc-123",
            "message_id": "msg-def-456",
            "timestamp": "2024-04-10T16:10:50+05:30",
            "bap_id": "buyer-app.example.com",
            "bpp_id": "seller-platform.example.com"
        },
        "message": {
            "order": {
                "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/tags/core-v2.0.0-rc2/schema/core/v2/context.jsonld",
                "@type": "beckn:Order",
                "beckn:id": "order-2024-001",
                "beckn:orderStatus": "CONFIRMED",
                "beckn:orderNumber": "ORD-12345",
                "beckn:seller": {
                    "beckn:id": "tech-store-premium",
                    "beckn:descriptor": {
                        "@type": "beckn:Descriptor",
                        "schema:name": "Tech Store Premium",
                        "schema:image": [
                            "https://example.com/logo.png"
                        ]
                    }
                },
                "beckn:buyer": {
                    "beckn:id": "customer-john-doe",
                    "beckn:displayName": "John Doe",
                    "beckn:email": "john@example.com",
                    "beckn:telephone": "+91-9876543210"
                },
                "beckn:orderItems": [
                    {
                        "beckn:lineId": "line-001",
                        "beckn:orderedItem": "laptop-gaming-pro",
                        "beckn:quantity": {
                            "beckn:unitQuantity": 1
                        },
                        "beckn:price": {
                            "currency": "INR",
                            "value": 85000
                        }
                    }
                ],
                "beckn:payment": {
                    "beckn:method": "UPI",
                    "beckn:paymentStatus": "COMPLETED",
                    "beckn:amount": {
                        "currency": "INR",
                        "value": 85000
                    },
                    "beckn:beneficiary": "BPP",
                    "beckn:txnRef": "UPI-2024-001-ABCD"
                },
                "beckn:fulfillment": {
                    "beckn:id": "fulfillment-delivery-001",
                    "beckn:mode": "DELIVERY",
                    "beckn:fulfillmentStatus": "OUT_FOR_DELIVERY"
                }
            }
        }
    }
    
    print("=" * 70)
    print("Beckn v2.0 → v2.1 Conversion Example")
    print("=" * 70)
    print()
    
    # Convert
    result = convert_v2_to_v21(v2_order)
    
    # Display conversion report
    print(result.report.summary())
    print()
    
    # Show key transformations
    print("Key Transformations:")
    print("-" * 70)
    
    ctx_v21 = result.converted_payload["context"]
    print(f"✓ Context version: 2.0.0 → {ctx_v21['version']}")
    print(f"✓ transaction_id → transactionId: {ctx_v21['transactionId']}")
    print(f"✓ message_id → messageId: {ctx_v21['messageId']}")
    print()
    
    order_v21 = result.converted_payload["message"]["order"]
    print("✓ Order.seller → Order.provider")
    print(f"  Provider ID: {order_v21['provider']['id']}")
    print()
    
    print("✓ Order.buyer → Order.consumer (with person identity)")
    print(f"  Person ID: {order_v21['consumer']['person']['id']}")
    print(f"  Person name: {order_v21['consumer']['person'].get('name', 'N/A')}")
    print()
    
    print("✓ Payment → PaymentTerms + PaymentAction")
    print(f"  Payment Terms collected by: {order_v21['paymentTerms']['collectedBy']}")
    print(f"  Payment Action status: {order_v21['paymentAction']['paymentStatus']}")
    print()
    
    print("✓ fulfillment → fulfillments[] (wrapped to array)")
    print(f"  Fulfillments count: {len(order_v21['fulfillments'])}")
    print()
    
    print("✓ Descriptor: schema:name → name, schema:image → thumbnailImage")
    desc = order_v21['provider']['descriptor']
    print(f"  Name: {desc.get('name', 'N/A')}")
    if 'thumbnailImage' in desc:
        print(f"  Thumbnail: {desc['thumbnailImage']}")
    print()
    
    # Output converted payload
    print("=" * 70)
    print("Converted v2.1 Payload (excerpt):")
    print("=" * 70)
    print(json.dumps(result.converted_payload, indent=2)[:1500] + "\n...")
    print()
    
    print("✓ Conversion complete!")
    print(f"  • Mapped fields: {len(result.report.mapped_fields)}")
    print(f"  • Dropped fields: {len(result.report.dropped_fields)}")
    print(f"  • Warnings: {len(result.report.warnings)}")


if __name__ == "__main__":
    main()
