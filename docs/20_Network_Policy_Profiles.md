# Network Policy Profiles and Overlays
## CWG Working Draft - 2026-03-27

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-27 | Migrated to v2 RFC template structure |

## 1.2 Latest editor's draft
- ./20_Network_Policy_Profiles.md

## 1.3 Implementation report
- To be published by implementation working group.

## 1.4 Stress Test Report
- To be published by testing and certification working group.

## 1.5 Editors
- Beckn Protocol Core Working Group editors.

## 1.6 Authors
- Beckn Protocol contributors.

## 1.7 Feedback
### 1.7.1 Issues
- https://github.com/beckn/protocol-specifications-v2/issues

### 1.7.2 Discussions
- https://github.com/beckn/protocol-specifications-v2/discussions

### 1.7.3 Pull Requests
- https://github.com/beckn/protocol-specifications-v2/pulls

## 1.8 Errata
- To be published.

<!-- TOC START -->
## Table of Contents

  - [CWG Working Draft - 2026-03-27](#cwg-working-draft-2026-03-27)
- [1. Document Details](#1-document-details)
  - [1.1 Version History](#11-version-history)
  - [1.2 Latest editor's draft](#12-latest-editors-draft)
  - [1.3 Implementation report](#13-implementation-report)
  - [1.4 Stress Test Report](#14-stress-test-report)
  - [1.5 Editors](#15-editors)
  - [1.6 Authors](#16-authors)
  - [1.7 Feedback](#17-feedback)
    - [1.7.1 Issues](#171-issues)
    - [1.7.2 Discussions](#172-discussions)
    - [1.7.3 Pull Requests](#173-pull-requests)
  - [1.8 Errata](#18-errata)
- [2. Context](#2-context)
  - [Abstract](#abstract)
  - [1. Context](#1-context)
  - [2. Network Policy Layering](#2-network-policy-layering)
  - [3. Network Profile Document](#3-network-profile-document)
    - [3.1 Required Schema Packs](#31-required-schema-packs)
    - [3.2 Supported Actions](#32-supported-actions)
    - [3.3 Context Constraints](#33-context-constraints)
    - [3.4 Fulfillment Types](#34-fulfillment-types)
    - [3.5 Geographic Coverage](#35-geographic-coverage)
    - [3.6 PS and DS Endpoints](#36-ps-and-ds-endpoints)
  - [4. Policy Categories](#4-policy-categories)
  - [5. Policy Publication and Discovery](#5-policy-publication-and-discovery)
  - [6. Policy Enforcement](#6-policy-enforcement)
  - [7. Constraint Rule](#7-constraint-rule)
  - [8. Conformance Requirements](#8-conformance-requirements)
  - [9. References](#9-references)
  - [10. Changelog](#10-changelog)
<!-- TOC END -->

# 2. Context

**Status:** Draft  
**Author(s):**  
**Created:**  
**Updated:**  
**Conformance impact:** Informative for core; Normative for network implementors  
**Security/privacy implications:** Network policies govern data transmission rules. Policies MUST not introduce security vulnerabilities or override core authentication requirements.  
**Replaces / Relates to:** Adapted from BECKN-001 (legacy pre-v2: Layering Network Policy) and BECKN-004 (legacy pre-v2: Policy Administration). Replaces OpenAPI `allOf` overlay mechanism with JSON-LD profiles and DeDi-publishable policy records.

---

## Abstract

This RFC defines how Beckn v2 networks publish and enforce network-specific policies on top of the core protocol. Networks publish a **Network Profile** document that specifies required schema packs, allowed action subsets, constraint rules, and DS/PS configuration. Participants discover and adopt these policies at onboarding and at runtime. This RFC does not modify the core protocol — it defines the layer above it.

---

## 1. Context

Beckn Protocol is domain-agnostic. Networks built on Beckn must add specificity — which sectors they serve, which schema packs are required, what fulfillment types are allowed, what geographic coverage applies. In legacy pre-v2, this was done via OpenAPI `allOf` overlays. In v2, it is done via JSON-LD profiles, network policy documents, and DeDi directory records.

---

## 2. Network Policy Layering

```
Core Protocol (this repo)
    └── Domain Specification (sector working group)
            └── Network Profile (network operator)
                    └── Participant Overlay (individual participant extensions)
```

- **Core Protocol**: defines the transport envelope. Immutable for a given version.
- **Domain Specification**: adds sector-specific schema packs and recommended flows.
- **Network Profile**: constrains the domain specification for a specific deployment. May be stricter but MUST NOT contradict core.
- **Participant Overlay**: participant-specific extensions. Must not violate network policy.

---

## 3. Network Profile Document

A Network Profile is a machine-readable JSON-LD document that defines:

### 3.1 Required Schema Packs

```json
{
  "@type": "NetworkProfile",
  "networkId": "mynetwork.example.org",
  "protocolVersion": "2.0.1",
  "schemaPacks": {
    "required": [
      "https://schema.beckn.io/retail/v1/context.jsonld"
    ],
    "optional": [
      "https://schema.beckn.io/sustainability/v1/context.jsonld"
    ]
  }
}
```

### 3.2 Supported Actions

Networks MAY restrict which Beckn actions are required or allowed:

```json
{
  "actions": {
    "required": ["discover", "select", "init", "confirm"],
    "optional": ["status", "cancel", "update", "rate"],
    "prohibited": []
  }
}
```

### 3.3 Context Constraints

Networks MAY add constraints to `Context` fields:

```json
{
  "contextConstraints": {
    "domain": {
      "enum": ["beckn:retail", "beckn:grocery"]
    },
    "ttl": {
      "maximum": "PT2M"
    }
  }
}
```

### 3.4 Fulfillment Types

```json
{
  "fulfillmentTypes": ["HOME_DELIVERY", "STORE_PICKUP", "DIGITAL_DELIVERY"]
}
```

### 3.5 Geographic Coverage

```json
{
  "spatialCoverage": {
    "type": "Polygon",
    "coordinates": [[[72.8, 18.9], [73.0, 18.9], [73.0, 19.1], [72.8, 19.1], [72.8, 18.9]]]
  }
}
```

### 3.6 PS and DS Endpoints

```json
{
  "infrastructure": {
    "cps": [
      { "subscriberId": "cps.mynetwork.example.org", "url": "https://cps.mynetwork.example.org" }
    ],
    "cds": [
      { "subscriberId": "cds.mynetwork.example.org", "url": "https://cds.mynetwork.example.org" }
    ],
    "registry": {
      "subscriberId": "registry.mynetwork.example.org",
      "url": "https://registry.mynetwork.example.org"
    }
  }
}
```

---

## 4. Policy Categories

Networks SHOULD categorize policies using these standard categories (adapted from legacy pre-v2 BECKN-004):

| Category | Description |
|---|---|
| Implementation | Technical requirements for participant implementations |
| Registration | Requirements for joining the network (KYC, certification, etc.) |
| Subscription | Key rotation schedules, TTL limits, etc. |
| Transaction | Required/optional actions, fulfillment types, schema constraints |
| Payment | Supported payment terms, settlement windows |
| Data Transmission | Mandatory/optional fields, PII handling rules |
| Communication | Timeout rules, retry policies, TTL limits |

---

## 5. Policy Publication and Discovery

Network operators MUST publish their Network Profile:
1. As a publicly accessible JSON-LD document at a stable URL.
2. As a reference in the network's DeDi registry directory entry.

Participants MUST retrieve and validate the Network Profile at onboarding. Participants SHOULD re-validate periodically to detect policy updates.

---

## 6. Policy Enforcement

Participants enforce network policy by:
- Validating incoming `context.domain` against allowed domains.
- Rejecting messages with prohibited actions.
- Validating `message` payloads against required schema packs.
- Applying `contextConstraints` to outgoing requests.

The core transport layer MUST NOT enforce network policies — enforcement is the responsibility of each participant's application middleware.

---

## 7. Constraint Rule

Networks MAY be stricter than the core and domain specifications. Networks MUST NOT:
- Redefine or override core transport schemas.
- Override Beckn Signature requirements.
- Reduce the mandatory `Context` field set.

---

## 8. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-019-01 | Network operators MUST publish a Network Profile document | MUST |
| CON-019-02 | Network Profile MUST specify `protocolVersion` | MUST |
| CON-019-03 | Network Profile MUST specify required schema packs | MUST |
| CON-019-04 | Network Profile MUST be accessible at a stable public URL | MUST |
| CON-019-05 | Participants MUST retrieve and apply the Network Profile at onboarding | MUST |
| CON-019-06 | Network policies MUST NOT contradict core transport requirements | MUST |

---

## 9. References

- [09_Network_Architecture.md](./09_Network_Architecture.md)
- [15_Schema_Distribution_Model.md](./15_Schema_Distribution_Model.md)
- [GOVERNANCE.md](../GOVERNANCE.md) — Section 11: Core–Domain–Network interaction rules

---

## 10. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft — adapted from BECKN-001 and BECKN-004 (legacy pre-v2) |
