# EV Charging — Charging Session Definition Bundle (v1)

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