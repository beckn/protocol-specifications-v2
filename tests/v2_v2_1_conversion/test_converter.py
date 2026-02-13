"""
Tests for the main converter module.
"""

import json
import pytest
from pathlib import Path

from v2_to_v21_converter import convert_v2_to_v21


# Test fixture directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(filename: str):
    """Load a test fixture JSON file"""
    with open(FIXTURES_DIR / filename) as f:
        return json.load(f)


def test_convert_order_payload():
    """Test conversion of a complete Order payload"""
    v2_payload = load_fixture("v2_order_payload.json")
    
    result = convert_v2_to_v21(v2_payload)
    
    # Check envelope context was converted
    assert result.converted_payload["context"]["version"] == "2.1.0"
    assert "transactionId" in result.converted_payload["context"]
    assert "messageId" in result.converted_payload["context"]
    assert "transaction_id" not in result.converted_payload["context"]
    
    # Check Order was converted
    order = result.converted_payload["message"]["order"]
    
    # seller → provider
    assert "provider" in order
    assert "seller" not in order
    assert order["provider"]["id"] == "provider-456"
    
    # buyer → consumer with person
    assert "consumer" in order
    assert "buyer" not in order
    assert order["consumer"]["@type"] == "beckn:Consumer"
    assert "person" in order["consumer"]
    assert order["consumer"]["person"]["@type"] == "schema:Person"
    assert order["consumer"]["person"]["id"] == "buyer-789"
    
    # payment → paymentTerms + paymentAction
    assert "paymentTerms" in order
    assert "paymentAction" in order
    assert "payment" not in order
    assert order["paymentTerms"]["collectedBy"] == "BPP"
    assert order["paymentAction"]["paymentStatus"] == "COMPLETED"
    
    # fulfillment → fulfillments[] (array wrap)
    assert "fulfillments" in order
    assert "fulfillment" not in order
    assert isinstance(order["fulfillments"], list)
    assert len(order["fulfillments"]) == 1
    
    # invoice → invoices[] (array wrap)
    assert "invoices" in order
    assert "invoice" not in order
    assert isinstance(order["invoices"], list)
    assert len(order["invoices"]) == 1
    
    # orderedItem → itemId
    assert order["orderItems"][0]["itemId"] == "item-laptop-001"
    assert "orderedItem" not in order["orderItems"][0]
    
    # Check prefixes were removed
    assert "id" in order
    assert "beckn:id" not in order


def test_envelope_key_conversion():
    """Test envelope context key mapping"""
    v2_payload = {
        "context": {
            "transaction_id": "abc",
            "message_id": "def",
            "bap_id": "bap.test",
            "bpp_id": "bpp.test",
            "version": "2.0.0"
        },
        "message": {}
    }
    
    result = convert_v2_to_v21(v2_payload)
    ctx = result.converted_payload["context"]
    
    assert ctx["transactionId"] == "abc"
    assert ctx["messageId"] == "def"
    assert ctx["bapId"] == "bap.test"
    assert ctx["bppId"] == "bpp.test"
    assert ctx["version"] == "2.1.0"


def test_descriptor_conversion():
    """Test Descriptor field conversion"""
    v2_payload = {
        "context": {"version": "2.0.0"},
        "message": {
            "item": {
                "@type": "beckn:Item",
                "beckn:descriptor": {
                    "@type": "beckn:Descriptor",
                    "schema:name": "Test Item",
                    "beckn:shortDesc": "Short description",
                    "schema:image": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
                }
            }
        }
    }
    
    result = convert_v2_to_v21(v2_payload)
    descriptor = result.converted_payload["message"]["item"]["descriptor"]
    
    # schema:name → name
    assert descriptor["name"] == "Test Item"
    assert "schema:name" not in descriptor
    
    # schema:image → thumbnailImage (first image)
    assert descriptor["thumbnailImage"] == "https://example.com/image1.jpg"
    assert "images" not in descriptor
    
    # shortDesc preserved
    assert descriptor["shortDesc"] == "Short description"


def test_dropped_fields_warning():
    """Test that dropped fields generate warnings"""
    v2_payload = {
        "context": {"version": "2.0.0"},
        "message": {
            "tracking": {
                "@type": "beckn:Tracking",
                "tl_method": "http/get",
                "url": "https://track.example.com",
                "expires_at": "2025-01-01T00:00:00Z",
                "trackingStatus": "ACTIVE"
            }
        }
    }
    
    result = convert_v2_to_v21(v2_payload)
    
    # tl_method should be dropped
    tracking = result.converted_payload["message"]["tracking"]
    assert "tl_method" not in tracking
    assert "expiresAt" in tracking  # expires_at renamed
    
    # Check warning was generated
    assert any("tl_method" in str(w) for w in result.report.warnings)


def test_strict_mode():
    """Test strict mode fails on warnings"""
    v2_payload = {
        "context": {"version": "2.0.0"},
        "message": {
            "tracking": {
                "@type": "beckn:Tracking",
                "tl_method": "http/get",
                "url": "https://track.example.com"
            }
        }
    }
    
    with pytest.raises(ValueError, match="strict mode"):
        convert_v2_to_v21(v2_payload, strict=True)


def test_report_generation():
    """Test that conversion report is generated"""
    v2_payload = load_fixture("v2_order_payload.json")
    
    result = convert_v2_to_v21(v2_payload)
    
    # Check report has content
    assert len(result.report.mapped_fields) > 0
    assert len(result.report.stats) > 0
    
    # Check summary can be generated
    summary = result.report.summary()
    assert "Beckn v2.0 → v2.1 Conversion Report" in summary
    assert "Statistics:" in summary


def test_payment_decomposition():
    """Test Payment → PaymentTerms + PaymentAction decomposition"""
    v2_payload = {
        "context": {"version": "2.0.0"},
        "message": {
            "order": {
                "@type": "beckn:Order",
                "beckn:id": "order-1",
                "beckn:orderStatus": "CONFIRMED",
                "beckn:seller": {"beckn:id": "seller-1"},
                "beckn:buyer": {"beckn:id": "buyer-1"},
                "beckn:orderItems": [{"beckn:orderedItem": "item-1"}],
                "beckn:payment": {
                    "beckn:method": "UPI",
                    "beckn:paymentStatus": "COMPLETED",
                    "beckn:amount": {"currency": "INR", "value": 1000},
                    "beckn:beneficiary": "BPP",
                    "beckn:txnRef": "TXN123"
                }
            }
        }
    }
    
    result = convert_v2_to_v21(v2_payload)
    order = result.converted_payload["message"]["order"]
    
    # Check PaymentTerms
    assert "paymentTerms" in order
    assert order["paymentTerms"]["@type"] == "beckn:PaymentTerms"
    assert order["paymentTerms"]["collectedBy"] == "BPP"
    
    # Check PaymentAction
    assert "paymentAction" in order
    assert order["paymentAction"]["@type"] == "beckn:PaymentAction"
    assert order["paymentAction"]["paymentStatus"] == "COMPLETED"
    assert order["paymentAction"]["txnRef"] == "TXN123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
