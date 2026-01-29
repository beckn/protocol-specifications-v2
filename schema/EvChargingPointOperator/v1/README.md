# EV Charging — Charging Point Operator Definition Bundle (v1)

This bundle defines **EV-specific attribute extensions for Provider** (operator profile). It reuses Beckn core objects and adds only domain-specific attributes relevant to charging operators.

Attach these schemas as follows:

| **Attribute Schema** | **Attach To** | **Purpose** |
| --- | --- | --- |
| ChargingPointOperator | Provider.attributes | Operator identifiers, statutory registrations, extended contact details, and network information. |
| --- | --- | --- |

## **🧭 Role and Design**

- **Aligned with Beckn Core**
  Uses canonical Beckn schemas for common objects and reuses canonical components from:
  - [core.yaml](../../core/v2/attributes.yaml) - Catalog, Item, Offer, Provider, Attributes, Location, Address, GeoJSONGeometry
  - [api/beckn.yaml](../../../api/beckn.yaml) - Unified API specification for discovery and transaction endpoints
- **Adds EV semantics only**
  Introduces operator-specific elements such as operator IDs, roaming network IDs, and support contacts.
- **Designed for interoperability**
  Enables CPOs, aggregators, and apps to exchange structured operator data across Beckn networks.

## **🗺️ Local Namespace Mapping**

The beckn namespace is mapped **locally**:

{ "beckn": "./vocab.jsonld#" }

Vocabulary files live in ./vocab.jsonld and use this same local mapping.

When publishing, replace ./vocab.jsonld# with an absolute URL, e.g.:

<https://schemas.example.org/ev-charging-cpo/v1/vocab.jsonld#>

This supports both local development and public hosting.

## **📂 Files and Folders**

| **File / Folder** | **Purpose** |
| --- | --- |
| **attributes.yaml** | OpenAPI 3.1.1 attribute schema for ChargingPointOperator (Provider.attributes), annotated with x-jsonld. |
| **context.jsonld** | Maps properties to schema.org and local beckn: IRIs for ChargingPointOperator. |
| **vocab.jsonld** | Local vocabulary for CPO domain terms (operatorId, registrations, contacts, networks). |
| **profile.json** | Lists included schemas, operational/index hints, and guidance for implementers. |
| **renderer.json** | Templates for rendering provider profile UI elements. |
| **examples/** | Working examples showing how ChargingPointOperator attaches to Beckn Provider. |
| --- | --- |

## 🏷️ Tags
`ev-charging, charging-point-operator, provider, operator, roaming, registry, beckn, json-ld, schema.org, openapi`
