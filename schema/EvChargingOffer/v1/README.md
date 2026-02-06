# EV Charging — Charging Offer Definition Bundle (v1)

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

## This schema is being moved. **Migrate now.**

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

> [!CAUTION]
> #### Heads-up:If you maintain downstream specs or SDKs, pin versions and communicate timelines clearly.

<p align="center">
  <img
    alt="Migration Notice End"
    src="https://capsule-render.vercel.app/api?type=soft&color=0:b42318,100:7a271a&height=25&section=header&text=End%20of%20notice&fontSize=15&fontColor=ffffff&animation=fadeIn"
  />
</p>

---

# Overview

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
