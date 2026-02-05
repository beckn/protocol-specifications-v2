# EV Charging — Charging Session Definition Bundle (v1)

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

This bundle defines **EV-specific attribute extensions for Order/Fulfillment** (ChargingSession). It reuses Beckn core objects and adds domain-specific attributes for session state, telemetry, and billing snapshots.

Attach these schemas as follows:

| **Attribute Schema** | **Attach To** | **Purpose** |
| --- | --- | --- |
| ChargingSession | Order.fulfillments[].attributes | Real-time or completed charging session data – energy, duration, cost, telemetry intervals, and simple tracking identifiers. |
| --- | --- | --- |

## **🧭 Role and Design**

- **Aligned with Beckn Core**
  Uses canonical Beckn schemas for common objects and reuses canonical components from:
  - core.yaml – Catalog, Item, Offer, Provider, Attributes, Location, Address, GeoJSONGeometry
  - discover.yaml – Discovery API endpoints and request/response schemas
  - transaction.yaml – Transaction API endpoints and Order, Fulfillment, Payment schemas
- **Adds EV semantics only**
  Introduces session-specific elements such as sessionStatus, authorizationMode, telemetry, and totalCost.
- **Designed for interoperability**
  Enables CPOs, aggregators, and apps to exchange structured session data across Beckn networks.

## **🗺️ Local Namespace Mapping**

The beckn namespace is mapped **locally**:

{ "beckn": "./vocab.jsonld#" }

Vocabulary files live in ./vocab.jsonld and use this same local mapping.

When publishing, replace ./vocab.jsonld# with an absolute URL, e.g.:

<https://schemas.example.org/ev-charging-session/v1/vocab.jsonld#>

This supports both local development and public hosting.

## **📂 Files and Folders**

| **File / Folder** | **Purpose** |
| --- | --- |
| **attributes.yaml** | OpenAPI 3.1.1 attribute schema for ChargingSession (Order.fulfillments[].attributes), annotated with x-jsonld. |
| **context.jsonld** | Maps properties to schema.org and local beckn: IRIs for ChargingSession. |
| **vocab.jsonld** | Local vocabulary for session domain terms (sessionStatus, authorizationMode, telemetry, totalCost, etc.). |
| **profile.json** | Lists included schemas, operational/index hints, and guidance for implementers. |
| **renderer.json** | Templates for rendering session status views. |
| **examples/** | Working examples showing how ChargingSession attaches to Beckn Fulfillment. |
| --- | --- |

## 🏷️ Tags
`ev-charging, charging-session, telemetry, billing, reservation, beckn, json-ld, schema.org, openapi`