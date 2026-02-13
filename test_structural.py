#!/usr/bin/env python3
"""Test structural transformation"""

import json
import sys
sys.path.insert(0, 'scripts/v2.1/v2_to_v21_converter')

from becknVersionTransform import StructuralTransformer

# Load test data
with open('../DEG/examples/ev-charging/v2/08_00_on_confirm/v2_0_ev-charging-on-confirm.json') as f:
    data = json.load(f)

# Test structural transformer directly
st = StructuralTransformer('scripts/v2.1/v2_to_v21_converter/structural_transforms.yaml')
print(f'✓ Loaded {len(st.rules)} rules')
print(f'✓ Execution order: {st.settings.get("execution_order")}')

# Test path resolution
print('\n--- Testing Path Resolution ---')
buyer_val, found = st.get_value_at_path(data, '$.message.order.buyer')
print(f'buyer at $.message.order.buyer: found={found}')
if found:
    print(f'  Type: {type(buyer_val)}')
    if isinstance(buyer_val, dict):
        print(f'  Keys: {list(buyer_val.keys())}')

seller_val, found = st.get_value_at_path(data, '$.message.order.seller')
print(f'\nseller at $.message.order.seller: found={found}, value={seller_val}')

payment_val, found = st.get_value_at_path(data, '$.message.order.payment')
print(f'\npayment at $.message.order.payment: found={found}')
if found:
    print(f'  Type: {type(payment_val)}')
    if isinstance(payment_val, dict):
        print(f'  Keys: {list(payment_val.keys())}')

# Apply rules
print('\n--- Applying Structural Rules ---')
transformed, applied = st.apply_rules(data)

print(f'\n✓ Applied {len(applied)} rules: {applied}')

# Check results
print('\n--- Checking Results ---')
consumer_val, found = st.get_value_at_path(transformed, '$.message.order.consumer')
print(f'consumer created: {found}')
if found:
    print(f'  Value: {json.dumps(consumer_val, indent=2)}')

provider_val, found = st.get_value_at_path(transformed, '$.message.order.provider')
print(f'\nprovider created: {found}')
if found:
    print(f'  Value: {json.dumps(provider_val, indent=2)}')

payment_action_val, found = st.get_value_at_path(transformed, '$.message.order.paymentAction')
print(f'\npaymentAction created: {found}')
if found and isinstance(payment_action_val, dict):
    print(f'  Keys: {list(payment_action_val.keys())}')

payment_terms_val, found = st.get_value_at_path(transformed, '$.message.order.paymentTerms')
print(f'\npaymentTerms created: {found}')
if found and isinstance(payment_terms_val, dict):
    print(f'  Keys: {list(payment_terms_val.keys())}')
