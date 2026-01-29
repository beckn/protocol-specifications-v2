# EV Charging — Charging Offer Definition Bundle (v1)

This bundle defines **EV-specific attribute extensions for Offer** (commercial terms). It reuses Beckn core objects and adds only domain-specific attributes relevant to charging tariffs and policies.

Attach these schemas as follows:

| **Attribute Schema** | **Attach To** | **Purpose** |
| --- | --- | --- |
| ChargingOffer | Offer.attributes | Tariff details beyond core price fields – e.g., eligibleQuantity, idle fee policies and offer-specific rules. |
| --- | --- | --- |

## **🧭 Role and Design**

- **Aligned with Beckn Core**
  Uses canonical Beckn schemas for common objects and reuses canonical components from:
  - [core.yaml](../../core/v2/attributes.yaml) - Catalog, Item, Offer, Provider, Attributes, Location, Address, GeoJSONGeometry
  - [api/beckn.yaml](../../../api/beckn.yaml) - Unified API specification for discovery and transaction endpoints
- **Adds EV semantics only**
  Introduces domain-specific elements such as per-kWh/time pricing models and idle fee policies.
- **Designed for interoperability**
  Enables CPOs, aggregators, and apps to exchange structured tariff data across Beckn networks.

## **🗺️ Local Namespace Mapping**

The beckn namespace is mapped **locally**:

{ "beckn": "./vocab.jsonld#" }

Vocabulary files live in ./vocab.jsonld and use this same local mapping.

When publishing, replace ./vocab.jsonld# with an absolute URL, e.g.:

<https://schemas.example.org/ev-charging-offer/v1/vocab.jsonld#>

This supports both local development and public hosting.

## **📂 Files and Folders**

| **File / Folder** | **Purpose** |
| --- | --- |
| **attributes.yaml** | OpenAPI 3.1.1 attribute schema for ChargingOffer (Offer.attributes), annotated with x-jsonld. |
| **context.jsonld** | Maps properties to schema.org and local beckn: IRIs for ChargingOffer. |
| **vocab.jsonld** | Local vocabulary for ChargingOffer domain terms (buyerFinderFee, idleFeePolicy, etc.). |
| **profile.json** | Lists included schemas, operational/index hints, and guidance for implementers. |
| **renderer.json** | Templates for rendering offer chips and pricing detail UI. |
| **examples/** | Working examples showing how ChargingOffer attaches to Beckn Offer. |
| --- | --- |

## 🏷️ Tags
`ev-charging, charging-offer, tariffs, pricing, idle-fee, beckn, json-ld, schema.org, openapi`
