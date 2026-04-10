# RFC-004: Universal Value Exchange Fabric

## 1. Document Details

- **Status:** Draft.
- **Authors:** Beckn Protocol contributors.
- **Created:** 2026-04-10.
- **Updated:** 2026-04-10.
- **Version history:** No commits found on `main` for `docs/04_Universal_Value_Exchange_Fabric.md`.
- **Latest editor's draft:** Click [here](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/04_Universal_Value_Exchange_Fabric.md).
- **Implementation report:** To be published by infrastructure implementation working group.
- **Stress test report:** To be published for production-scale deployment profiles.
- **Conformance impact:** Informative with normative guidance for fabric service behavior.
- **Security/privacy implications:** Registry and credentialing responsibilities impact trust and participant safety.
- **Replaces / Relates to:** Replaces non-RFC-form content in `04_Universal_Value_Exchange_Fabric.md`.
- **Feedback:** Issues: Click [here](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-004%22). Discussions: Click [here](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-004%22). Pull Requests: Click [here](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-004%22).
- **Errata:** To be published.

## 2. Abstract

This RFC describes the Universal Value Exchange Fabric as a set of reusable infrastructure services for Beckn-aligned networks and clarifies how catalog, registry, credentialing, and connectivity capabilities support interoperability at scale.

## 3. Table of Contents

- [Introduction](#4-introduction)
- [Specification](#5-specification)
- [Conclusion](#6-conclusion)
- [Acknowledgements](#7-acknowledgements)
- [References](#8-references)

## 4. Introduction

Beckn networks rely on shared infrastructure services such as registry, catalog handling, credentialing, and connectivity. Without a formal baseline, participants may re-implement these capabilities inconsistently; this RFC clarifies fabric responsibilities so deployments remain composable, interoperable, and easier to govern at scale.

Within this document, fabric refers to reusable, standards-aligned infrastructure services that support Beckn network operations. Catalog publishing service refers to infrastructure for ingesting, validating, and processing supply-side catalog updates. Registry refers to the trust directory for participant identity, endpoints, capabilities, and public keys. Credentialing service refers to the capability for issuing and verifying claims used in trust workflows. ONIX connectivity refers to the standardized connectivity approach for inter-service and inter-network integration. Composable deployment refers to adopting services independently without breaking protocol compatibility.

The fabric is guided by four principles: composable infrastructure, so services SHOULD be independently deployable and adoptable; protocol alignment, so behavior MUST not break Beckn transport and schema contracts; operational simplicity, so services SHOULD reduce participant-side integration complexity; and trust preservation, so identity and credential services MUST support secure network operations.

## 5. Specification

The key words MUST, SHOULD, and MAY in this document are to be interpreted as described in Click [here](./00_Keyword_Definitions.md).

### 5.1 Fabric scope and operating model

Fabric is a suite of cloud-based, reusable, standards-aligned services that provide operational capabilities for multi-participant digital networks.

Fabric services:

1. MUST remain independent and composable.
2. MAY be adopted incrementally by a network.
3. SHOULD be usable both by network facilitators and participants.

### 5.2 Catalog Publishing service

Catalog publishing service provides ingestion and processing of supply-side catalog updates.

- BPP-facing publish APIs MUST support reliable acceptance semantics.
- Service SHOULD validate and normalize catalogs before downstream indexing.
- Service MAY expose result callbacks and pull-compatible processing metadata.
- Reference: Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/publish-catalogs-using-catalg)

### 5.3 Network Registry

Registry is a trust directory for participant metadata.

- Registry MUST maintain participant identity, endpoint, capability, and key data.
- Implementations MUST support lookup flows used for signature verification and routing trust.
- Reference: Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/build-trusted-networks-using-registr)

### 5.4 Credentialing service

Credentialing supports verifiable claims across participants.

- Credential issuance and verification semantics SHOULD be network-governed.
- Credential workflows MUST align with trust and privacy constraints of the network.
- Reference: Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/prove-anything-using-vc-on-edge)

### 5.5 Beckn ONIX connectivity service

ONIX enables standardized connectivity patterns across networks and services.

- ONIX integration SHOULD preserve Beckn protocol interoperability requirements.
- ONIX deployment MAY vary by network topology and scale profile.
- Reference: Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/connect-to-everything-using-beckn-onix)

### 5.6 Operational example and conformance

Typical fabric-assisted flow:

```text
BPP -> Catalog Publishing Service -> Discovery index
BAP/BPP/DS/PS -> Registry lookup for trust and key resolution
Participant -> Credentialing service for verifiable claims
```

Conformance requirements:

| ID | Requirement | Level |
|---|---|---|
| CON-004-01 | Fabric services MUST preserve protocol compatibility and MUST NOT alter Beckn transport contract semantics. | MUST |
| CON-004-02 | Registry service implementations MUST provide identity and key resolution suitable for signature verification workflows. | MUST |
| CON-004-03 | Fabric services SHOULD remain independently deployable and composable. | SHOULD |

### 5.7 Security and deployment considerations

Registry and credentialing services are security-critical. Misconfigured trust directories, stale keys, or weak credential verification can compromise non-repudiation and participant trust. Deployments SHOULD enforce strict key lifecycle and access controls.

This RFC restructures existing fabric guidance into RFC form and does not introduce wire-level protocol changes. Future standardization work MAY define minimum SLA and availability baselines for shared fabric services and MAY define credentialing interoperability profiles as separate normative artifacts.

## 6. Conclusion

This RFC consolidates fabric context, terminology, design principles, service requirements, operational examples, conformance expectations, security considerations, and migration guidance into a single structure for Beckn-aligned networks. It establishes a reusable baseline for catalog publishing, registry, credentialing, and connectivity services while preserving protocol compatibility.

## 7. Acknowledgements

This document reflects contributions from Beckn Protocol contributors and the infrastructure implementation working group shaping reusable trust and interoperability services for Beckn-aligned networks.

## 8. References

- Click [here](./00_Keyword_Definitions.md)
- Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure)
- Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/publish-catalogs-using-catalg)
- Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/build-trusted-networks-using-registr)
- Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/prove-anything-using-vc-on-edge)
- Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure/connect-to-everything-using-beckn-onix)
