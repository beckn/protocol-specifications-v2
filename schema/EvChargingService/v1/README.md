# EV Charging — Charging Service Definition Bundle (v1)
---
<p align="center">
  <img
    alt="Migration Notice"
    src="https://capsule-render.vercel.app/api?type=soft&color=0:b42318,100:7a271a&height=100&section=header&text=MIGRATION%20NOTICE&fontSize=54&fontColor=ffffff&animation=fadeIn"
  />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Effective-2026--02--06-fde2e0?style=for-the-badge&labelColor=b42318" alt="Effective: 2026-02-06" />
  <img src="https://img.shields.io/badge/Removal-2026--02--20-dbeafe?style=for-the-badge&labelColor=075985" alt="Removal: 2026-02-20" />
</p>

## This folder is being moved. **Migrate now.**

**What’s changing:** This schema is being migrated to **[DEG Specification](https://github.com/beckn/DEG)**.  
**Impact:** Run-time references to files in this folder may continue to work until the removal date, after which they will fail.

### Recommended action
1. Switch to **DEG Specification Repository** (see **[Announcements](https://github.com/beckn/DEG/discussions/categories/announcements)** for migration guide).
2. Update your integrations before **2026-02-20**.
3. If blocked, open an issue with logs and request context.

<p>
  <!-- Replace MIGRATION_GUIDE_LINK with the real URL (your HTML had REPLACEMENT_LINK placeholder) -->
  <a href="https://github.com/beckn/DEG/issues/new">
    <img src="https://img.shields.io/badge/Report%20an%20issue-b42318?style=for-the-badge" alt="Report an issue" />
  </a>
  <a href="https://github.com/beckn/DEG/discussions/categories/announcements">
    <img src="https://img.shields.io/badge/Announcements-111827?style=for-the-badge" alt="Announcements" />
  </a>
  <a href="https://github.com/beckn/DEG">
    <img src="https://img.shields.io/badge/DEG%20Specification-2563eb?style=for-the-badge" alt="DEG Specification" />
  </a>
</p>

<table width="100%" cellpadding="12" cellspacing="0" border="0" bgcolor="#ffe4e6">
  <tr>
    <td>
      <strong>Heads-up:</strong> If you maintain downstream specs or SDKs, pin versions and communicate timelines clearly.
    </td>
  </tr>
</table>

<p align="center">
  <img
    alt="Migration Notice End"
    src="https://capsule-render.vercel.app/api?type=soft&color=0:b42318,100:7a271a&height=25&section=header&text=End%20of%20notice&fontSize=15&fontColor=ffffff&animation=fadeIn"
  />
</p>

---

# Overview

This bundle defines **EV-specific attribute extensions only** (no Beckn core objects).

It reuses core Beckn schemas for Item, Offer, Order/Fulfillment, and Provider, and adds only **domain-specific attributes**relevant to electric-vehicle charging.

Attach these schemas as follows:

| **Attribute Schema** | **Attach To** | **Purpose** |
| --- | --- | --- |
| ChargingService | Item.attributes | Technical and contextual details of a charging connector or station - e.g., connector type, power capacity, socket count, reservation capability, and amenities. |
| --- | --- | --- |
| ChargingOffer | Offer.attributes | Tariff details beyond core price fields - e.g., per-kWh or time-based pricing, idle fee policies, buyer-finder fees, and accepted payment methods. |
| --- | --- | --- |
| ChargingSession | Order.fulfillments\[\].attributes | Real-time or completed charging session data - energy consumed, session duration, total cost, telemetry intervals, and tracking links. |
| --- | --- | --- |
| ChargingProvider | Provider.attributes | Operator identifiers, statutory registrations, and extended contact details for the charging provider. |
| --- | --- | --- |


## **🧭 Role and Design**

- **Aligned with Beckn Core**
  Uses canonical Beckn schemas for common objects and reuses canonical components from:
  - [core.yaml](../../core/v2/attributes.yaml) - Catalog, Item, Offer, Provider, Attributes, Location, Address, GeoJSONGeometry
  - [api/beckn.yaml](../../../api/beckn.yaml) - Unified API specification for discovery and transaction endpoints
- **Adds EV semantics only  
    **Introduces domain-specific elements such as connectors, power ratings, roaming networks, charging periods, and session telemetry.
- **Designed for interoperability  
    **Enables charging-point operators, aggregators, and mobility apps to exchange structured data seamlessly across Beckn networks.

## **🗺️ Local Namespace Mapping**

The beckn namespace is mapped **locally**:

{ "beckn": "./vocab.jsonld#" }

Vocabulary files live in ./vocab.jsonld and use this same local mapping.

When publishing, replace ./vocab.jsonld# with an absolute URL, e.g.:

<https://schemas.example.org/ev-charging/v1/vocab.jsonld#>

This supports both local development and public hosting.

## **📂 Files and Folders**

| **File / Folder** | **Purpose** |
| --- | --- |
| **attributes.yaml** | OpenAPI 3.1.1 attribute schema for ChargingService (Item.attributes), annotated with x-jsonld. Reuses canonical Beckn components (e.g., Location via \$ref). |
| **context.jsonld** | Maps all properties to schema.org and local beckn: IRIs for ChargingService. Defines semantic equivalences (e.g., serviceLocation ≡ beckn:availableAt). |
| **vocab.jsonld** | Local vocabulary for ChargingService domain terms (connectorType, chargingSpeed, ocppId, etc.) in JSON-LD format with RDFS definitions and semantic relationships. |
| **profile.json** | Lists included schemas (references all 4 standalone v1 folders), operational/index hints, minimal attributes for discovery, and privacy guidance for implementers. |
| **renderer.json** | Defines rendering templates (HTML + JSON data paths) for discovery cards, offer chips, and session status views used in UI implementations. |
| **examples/** | Contains working examples showing each attribute type (ChargingService, ChargingOffer, ChargingSession, ChargingPointOperator) in the context of Beckn discover and transaction flows. |
| --- | --- |

**Note:** This directory contains the ChargingService-specific attributes (v1). Other related attribute bundles are available as standalone folders:
- `../../EvChargingOffer/v1/` - ChargingOffer attributes (Offer.attributes)
- `../../EvChargingSession/v1/` - ChargingSession attributes (Order/Fulfillment.attributes)  
- `../../EvChargingPointOperator/v1/` - ChargingPointOperator attributes (Provider.attributes)


## 🏷️ Tags
`ev-charging, mobility, energy, transport, electric-vehicle, sustainability, item, offer, order, fulfillment, provider, location, geo, discovery, reservation, session, connector, power, ocpp, ocpi, open-standards, beckn, json-ld, schema.org, openapi, ocpi, ocpp, iso-15118, schema-geoshape, iso4217`

These tags help implementers and schema registries discover and classify this attribute bundle quickly.