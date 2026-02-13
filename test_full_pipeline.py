#!/usr/bin/env python3
"""Test full transformation pipeline"""

import json
import sys
sys.path.insert(0, 'scripts/v2.1/v2_to_v21_converter')

from becknVersionTransform import IRITransformer

# Load test data
with open('../DEG/examples/ev-charging/v2/08_00_on_confirm/v2_0_ev-charging-on-confirm.json') as f:
    data = json.load(f)

print("=== ORIGINAL DATA ===")
print(f"Keys in message.order: {list(data['message']['order'].keys())}")

# Create transformer with structural rules
transformer = IRITransformer(
    output_version="2.1",
    structural_rules_file='scripts/v2.1/v2_to_v21_converter/structural_transforms.yaml'
)

print("\n=== TRANSFORMING ===")
transformed, warnings, stats, applied_rules = transformer.transform_and_validate(data)

print(f"\n✓ IRI transformation complete")
print(f"✓ Structural rules applied: {len(applied_rules)}")
print(f"  Rules: {applied_rules}")

print("\n=== AFTER TRANSFORMATION ===")
order = transformed.get('message', {}).get('order', {})
print(f"Keys in message.order: {list(order.keys())[:10]}...")  # First 10 keys

# Check specific transformations
print("\n=== CHECKING TRANSFORMATIONS ===")

# 1. buyer → consumer
if 'consumer' in order:
    print("✓ consumer field created")
    if 'person' in order['consumer']:
        print(f"  ✓ consumer.person exists")
        print(f"     Keys: {list(order['consumer']['person'].keys())}")
else:
    print("✗ consumer field NOT created")
    if 'buyer' in order:
        print(f"  ! buyer still exists: {type(order['buyer'])}")

# 2. seller → provider
if 'provider' in order:
    print("\n✓ provider field created")
    if isinstance(order['provider'], dict) and 'descriptor' in order['provider']:
        print(f"  ✓ provider.descriptor exists")
        if 'id' in order['provider']['descriptor']:
            print(f"     ✓ provider.descriptor.id = {order['provider']['descriptor']['id']}")
else:
    print("\n✗ provider field NOT created")
    if 'seller' in order:
        print(f"  ! seller still exists: {order['seller']}")

# 3. payment → paymentAction + paymentTerms
if 'paymentAction' in order:
    print("\n✓ paymentAction created")
    print(f"  Keys: {list(order['paymentAction'].keys())}")
else:
    print("\n✗ paymentAction NOT created")

if 'paymentTerms' in order:
    print("✓ paymentTerms created")
    print(f"  Keys: {list(order['paymentTerms'].keys())}")
else:
    print("✗ paymentTerms NOT created")

if 'payment' in order:
    print("  ! payment still exists (should be removed)")
