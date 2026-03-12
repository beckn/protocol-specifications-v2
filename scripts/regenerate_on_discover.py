#!/usr/bin/env python3
"""
Regenerate on_discover.json with enriched Offer objects.

Adds the following fields to every Offer object based on:
  - Offer/v2.0/attributes.yaml  : addOnItems, eligibleRegion
  - RetailCoreOffer/v2.0/attributes.yaml: timeRange (top-level daily window), holidays

Also enriches specific pizza offers with addOnItems referencing dip item IDs.
"""

import json
import copy
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES_DIR = os.path.join(BASE_DIR, "examples", "retail", "food-and-beverages", "IN", "pizza-delivery", "on_discover")
ON_DISCOVER_PATH = os.path.join(EXAMPLES_DIR, "on_discover.json")

# Bangalore delivery zones as GeoJSON polygons (simplified bounding boxes).
# Location/v2.0 only allows: @type, address, geo (additionalProperties: false)
BANGALORE_ZONES = [
    {
        "@type": "Location",
        "address": "MG Road & Central Bangalore, Bangalore, Karnataka, IN",
        "geo": {
            "type": "Polygon",
            "coordinates": [[
                [77.5800, 12.9600],
                [77.6050, 12.9600],
                [77.6050, 12.9800],
                [77.5800, 12.9800],
                [77.5800, 12.9600]
            ]]
        }
    },
    {
        "@type": "Location",
        "address": "Koramangala, Bangalore, Karnataka, IN",
        "geo": {
            "type": "Polygon",
            "coordinates": [[
                [77.6100, 12.9250],
                [77.6400, 12.9250],
                [77.6400, 12.9450],
                [77.6100, 12.9450],
                [77.6100, 12.9250]
            ]]
        }
    },
    {
        "@type": "Location",
        "address": "Indiranagar, Bangalore, Karnataka, IN",
        "geo": {
            "type": "Polygon",
            "coordinates": [[
                [77.6300, 12.9700],
                [77.6550, 12.9700],
                [77.6550, 12.9900],
                [77.6300, 12.9900],
                [77.6300, 12.9700]
            ]]
        }
    }
]

# Known holiday dates for Domino's India (illustrative)
DOMINOS_HOLIDAYS = ["2026-01-26", "2026-08-15", "2026-10-02", "2026-12-25"]

# Dip item IDs that are add-ons to pizza offers
DIP_ITEM_IDS = ["item-dip-cheesy", "item-dip-cheesy-jalapeno"]

# Sides that are add-ons to pizza offers
SIDES_ITEM_IDS = ["item-side-garlic-breadsticks", "item-side-stuffed-garlic-breadsticks", "item-side-crinkle-fries"]

# Item categories that should get dip add-ons
PIZZA_OFFER_PREFIXES = [
    "offer-margherita-",
    "offer-double-cheese-margherita-",
    "offer-farmhouse-",
    "offer-peppy-paneer-",
    "offer-veg-extravaganza-",
    "offer-chicken-dominator-",
    "offer-chicken-pepperoni-",
    "offer-chicken-fiesta-",
    "offer-keema-do-pyaza-",
    "offer-pm-tomato",
    "offer-pm-paneer-onion",
    "offer-pm-chicken-sausage",
]

WINGS_OFFER_IDS = ["offer-boneless-chicken-wings", "offer-chicken-meatballs-sauce"]

GARLIC_BREADSTICK_OFFER = "offer-garlic-breadsticks"

# Serviceability timing already present in offerAttributes — we add top-level timeRange
# to RetailCoreOfferAttributes as a daily window (same for all Domino's IN offers)
DAILY_TIME_RANGE = {
    "start": "11:00",
    "end": "23:30"
}


def is_pizza_offer(offer_id: str) -> bool:
    return any(offer_id.startswith(p) or offer_id == p for p in PIZZA_OFFER_PREFIXES)


def enrich_offer(offer: dict) -> dict:
    """Add schema-defined fields that are currently missing from the offer."""
    offer_id = offer.get("id", "")

    # 1. Add eligibleRegion (all three Bangalore zones for delivery)
    if "eligibleRegion" not in offer:
        offer["eligibleRegion"] = BANGALORE_ZONES

    # 2. Add addOnItems to pizza offers (dips + sides)
    if is_pizza_offer(offer_id) and "addOnItems" not in offer:
        offer["addOnItems"] = DIP_ITEM_IDS + SIDES_ITEM_IDS

    # Wings offers get breadstick add-ons
    if offer_id in WINGS_OFFER_IDS and "addOnItems" not in offer:
        offer["addOnItems"] = SIDES_ITEM_IDS

    # 3. Add top-level timeRange to offerAttributes (RetailCoreOfferAttributes)
    if "offerAttributes" in offer:
        oa = offer["offerAttributes"]
        if "timeRange" not in oa:
            oa["timeRange"] = DAILY_TIME_RANGE
        if "holidays" not in oa:
            oa["holidays"] = DOMINOS_HOLIDAYS

    return offer


def main():
    with open(ON_DISCOVER_PATH) as f:
        data = json.load(f)

    total_offers_enriched = 0

    for catalog in data.get("message", {}).get("catalogs", []):
        offers = catalog.get("offers", [])
        enriched = []
        for offer in offers:
            enriched.append(enrich_offer(offer))
            total_offers_enriched += 1
        catalog["offers"] = enriched

    with open(ON_DISCOVER_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"✓ Enriched {total_offers_enriched} offers in {ON_DISCOVER_PATH}")


if __name__ == "__main__":
    main()
