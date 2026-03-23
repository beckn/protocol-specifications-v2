#!/usr/bin/env python3
"""
migrate_examples.py — Update pizza-delivery-2.0 examples to comply with beckn.yaml v2.0.0

Changes applied (per schema analysis):
  1. context.action: strip "beckn/" prefix → bare action name
  2. Contract["@context"]: "…/Contract/v2.0/context.jsonld" → "https://schema.beckn.io/Contract/v2.0"
     (matches the const in the Contract schema)
  3. Descriptor["@context"]: normalize all Descriptor context IRIs to "https://schema.beckn.io/"
  4. Location["@context"]: normalize all Location context IRIs to "https://schema.beckn.io/"
  5. Commitment["@context"]: normalize all Commitment context IRIs to "https://schema.beckn.io/"
  6. Consideration["@context"]: normalize Consideration context IRIs to "https://schema.beckn.io/"
  7. Participant["@context"]: normalize Participant context array entries
  8. support.supportRequest: add "@context": "https://schema.beckn.io/", fix "@type" → "beckn:Support"
  9. on_support.message: rename "supportInfo" → "support", fix @context/@type, restructure channels
     as beckn:Attributes objects per the Support schema
"""

import json
import os
import re
import sys
from pathlib import Path

EXAMPLES_ROOT = Path(__file__).parent

# ─────────────────────────────────────────────────────────────
# Normalization helpers
# ─────────────────────────────────────────────────────────────

BECKN_BASE = "https://schema.beckn.io/"
CONTRACT_CONTEXT = "https://schema.beckn.io/Contract/v2.0"   # const from schema


def strip_beckn_action_prefix(action: str) -> str:
    """'beckn/discover' → 'discover'"""
    if action and action.startswith("beckn/"):
        return action[len("beckn/"):]
    return action


def normalize_simple_context(value):
    """
    Any "@context" that is a plain string ending with /context.jsonld or pointing to
    schema.beckn.io/<Type>/v2.x should be normalised to "https://schema.beckn.io/" unless
    it is the Contract context (handled separately).
    """
    if not isinstance(value, str):
        return value
    # Contract context → keep its specific const value
    if "Contract" in value:
        return CONTRACT_CONTEXT
    # All other schema.beckn.io/* URLs → base IRI
    if value.startswith("https://schema.beckn.io/"):
        return BECKN_BASE
    return value


def normalize_context_array(arr):
    """
    Participant @context arrays: strip /context.jsonld suffixes, return as-is list of IRIs.
    We keep them as arrays but normalise each entry.
    """
    if not isinstance(arr, list):
        return arr
    result = []
    for item in arr:
        if isinstance(item, str) and item.startswith("https://schema.beckn.io/"):
            # Drop the /context.jsonld suffix; keep the versioned IRI
            item = re.sub(r"/context\.jsonld$", "", item)
        result.append(item)
    return result


def walk_and_fix(obj):
    """
    Recursively walk a parsed JSON object and apply all normalization rules.
    Returns the mutated object.
    """
    if isinstance(obj, dict):
        # Fix @context at this level
        if "@context" in obj:
            ctx = obj["@context"]
            if isinstance(ctx, str):
                obj["@context"] = normalize_simple_context(ctx)
            elif isinstance(ctx, list):
                obj["@context"] = normalize_context_array(ctx)

        # Recurse into all values
        for key in list(obj.keys()):
            obj[key] = walk_and_fix(obj[key])

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            obj[i] = walk_and_fix(item)

    return obj


def fix_context_action(data: dict) -> dict:
    """Strip 'beckn/' prefix from context.action."""
    ctx = data.get("context", {})
    if "action" in ctx:
        ctx["action"] = strip_beckn_action_prefix(ctx["action"])
    return data


def fix_support_request(data: dict) -> dict:
    """
    support/*.json — SupportAction schema requires:
      message.supportRequest["@context"] = "https://schema.beckn.io/"
      message.supportRequest["@type"]    = "beckn:Support"
    """
    msg = data.get("message", {})
    sr = msg.get("supportRequest")
    if sr is None:
        return data
    # Ensure @context is present
    if "@context" not in sr:
        sr["@context"] = BECKN_BASE
    else:
        sr["@context"] = normalize_simple_context(sr["@context"])
    # Fix @type to beckn:Support
    if sr.get("@type") in (None, "Support", "beckn:SupportRequest"):
        sr["@type"] = "beckn:Support"
    return data


def fix_on_support(data: dict) -> dict:
    """
    on_support/*.json — OnSupportAction schema requires:
      message.support  (NOT message.supportInfo)
      support["@context"] = "https://schema.beckn.io/"
      support["@type"]    = "beckn:Support"
      support.channels[]  = array of Attributes objects (beckn:Attributes)

    The old shape had:
      message.supportInfo with keys: name, channels[], telephone, email, url, etc.

    New shape:
      message.support with the same keys but "@context"/"@type" normalized, and
      channels is an array of beckn:Attributes objects.
    """
    msg = data.get("message", {})

    # Handle both old key name and new key name
    support_obj = msg.pop("supportInfo", None) or msg.get("support")
    if support_obj is None:
        return data

    # Normalize @context / @type
    support_obj["@context"] = BECKN_BASE
    support_obj["@type"] = "beckn:Support"

    # Normalize channels: old format was ["PHONE","EMAIL","WHATSAPP"]
    # New format: array of Attributes objects
    old_channels = support_obj.get("channels", [])
    if old_channels and isinstance(old_channels[0], str):
        # Convert each channel string to an Attributes object
        channel_type_map = {
            "PHONE": {
                "@context": BECKN_BASE,
                "@type": "beckn:PhoneChannel",
                "descriptor": {"@type": "beckn:Descriptor", "name": "Phone Support"},
                "value": support_obj.get("telephone", "")
            },
            "EMAIL": {
                "@context": BECKN_BASE,
                "@type": "beckn:EmailChannel",
                "descriptor": {"@type": "beckn:Descriptor", "name": "Email Support"},
                "value": support_obj.get("email", "")
            },
            "WHATSAPP": {
                "@context": BECKN_BASE,
                "@type": "beckn:WhatsAppChannel",
                "descriptor": {"@type": "beckn:Descriptor", "name": "WhatsApp Support"},
                "value": support_obj.get("telephone", "")
            },
            "CHAT": {
                "@context": BECKN_BASE,
                "@type": "beckn:ChatChannel",
                "descriptor": {"@type": "beckn:Descriptor", "name": "Chat Support"},
                "value": support_obj.get("url", "")
            },
            "VIDEO": {
                "@context": BECKN_BASE,
                "@type": "beckn:VideoChannel",
                "descriptor": {"@type": "beckn:Descriptor", "name": "Video Support"},
                "value": ""
            },
        }
        new_channels = []
        for ch in old_channels:
            if ch in channel_type_map:
                new_channels.append(channel_type_map[ch])
            else:
                # Generic fallback
                new_channels.append({
                    "@context": BECKN_BASE,
                    "@type": "beckn:SupportChannel",
                    "descriptor": {"@type": "beckn:Descriptor", "name": ch},
                    "value": ""
                })
        support_obj["channels"] = new_channels

    # Remove flattened fields that are now inside channels (keep them for reference too)
    # Actually keep them — the Support schema does not disallow extra fields at this level;
    # the spec only requires @context, @type. Extra fields like telephone/email are fine.

    msg["support"] = support_obj
    return data


def process_file(path: Path) -> tuple[bool, str]:
    """
    Load a JSON file, apply all migrations, write back if changed.
    Returns (changed, description).
    """
    try:
        original_text = path.read_text(encoding="utf-8")
        data = json.loads(original_text)
    except Exception as e:
        return False, f"ERROR reading: {e}"

    original_data = json.dumps(data, ensure_ascii=False)

    # Apply migrations in order
    data = fix_context_action(data)

    # Detect file type from action or path
    action = data.get("context", {}).get("action", "")
    rel_path_str = str(path.relative_to(EXAMPLES_ROOT))

    if "support/" in rel_path_str and "on_support" not in rel_path_str:
        data = fix_support_request(data)

    if "on_support" in rel_path_str:
        data = fix_on_support(data)

    # Apply global @context normalization on the whole payload
    data = walk_and_fix(data)

    new_data = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if new_data != original_text:
        path.write_text(new_data, encoding="utf-8")
        return True, "updated"
    return False, "no change"


def main():
    changed_count = 0
    total_count = 0

    json_files = sorted(EXAMPLES_ROOT.rglob("*.json"))
    # Skip this script's own output if any
    json_files = [f for f in json_files if f.name != "migrate_examples.py"]

    for path in json_files:
        total_count += 1
        changed, msg = process_file(path)
        status = "✓ UPDATED" if changed else "  no change"
        print(f"{status}  {path.relative_to(EXAMPLES_ROOT)}")
        if changed:
            changed_count += 1

    print(f"\n{'─'*60}")
    print(f"Processed {total_count} files — {changed_count} updated.")


if __name__ == "__main__":
    main()
