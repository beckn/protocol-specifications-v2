# Keyword Definitions for Technical Specifications

**Status:** Released  
**Author(s):** Ravi Prakash (FIDE / Beckn Foundation)  
**Created:** 2023-09-01  
**Updated:** 2026-02-01  
**Conformance impact:** Informative  
**Security/privacy implications:** No security or privacy implications identified.  
**Replaces / Relates to:** Adapted from BECKN-010 (v1.x). Aligned with [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) and [RFC 8174](https://datatracker.ietf.org/doc/html/rfc8174).

---

## Abstract

This document defines the key words used in all Beckn Protocol v2 technical specifications, standards, and RFCs. Uniform interpretation of these terms is required to avoid ambiguity in the implementation of the protocol.

---

## 1. Introduction

The key words defined in this document are commonly used in technical specifications to express levels of requirement. When these words appear in **uppercase** in a Beckn specification document, they MUST be interpreted as defined here.

This definition is aligned with IETF [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) and the clarifications in [RFC 8174](https://datatracker.ietf.org/doc/html/rfc8174). When these words appear in lowercase in a specification, they have their ordinary English meaning and do not carry normative weight.

---

## 2. Definitions

### MUST

The term **MUST** implies an absolute requirement. Implementations that do not satisfy a MUST requirement are not conformant.

Synonyms: **REQUIRED**, **SHALL**

### MUST NOT

The term **MUST NOT** indicates an absolute prohibition. Implementations that violate a MUST NOT are not conformant.

Synonym: **SHALL NOT**

### SHOULD

The term **SHOULD** indicates a strong recommendation. There may be valid reasons in particular circumstances to deviate from a SHOULD requirement, but the implementor must fully understand the implications before doing so.

Synonym: **RECOMMENDED**

### SHOULD NOT

The term **SHOULD NOT** indicates a strong recommendation against a behavior. There may be valid reasons in particular circumstances to permit the behavior, but the full implications must be understood.

Synonym: **NOT RECOMMENDED**

### MAY

The term **MAY** indicates that an item is truly optional. Implementors are free to include or omit the feature according to their needs. Interoperability MUST NOT depend on the presence or absence of an optional feature.

Synonym: **OPTIONAL**

---

## 3. Usage Examples

The following examples illustrate correct usage in the context of Beckn Protocol v2.

### Example 1 — MUST and REQUIRED

> REQUIRED. The BPP MUST implement the `publish` endpoint to receive catalog publication requests from BPPs.

> REQUIRED. Every `RequestContainer` MUST include a valid `Context` object.

> REQUIRED. If the BPP does not wish to respond to a request, it MUST return a `Nack` response with an appropriate error code.

### Example 2 — SHOULD and RECOMMENDED

> RECOMMENDED. Upon receiving a `discover` request, the CDS SHOULD return a `Catalog` that best matches the `Intent` in the request.

> Participants SHOULD cache registry lookup results for the duration of the key's validity period.

### Example 3 — MAY and OPTIONAL

> The CDS MAY support synchronous (non-callback) responses for `discover` requests, subject to network policy.

> Participants MAY implement additional response schemas beyond those defined in `beckn.yaml` for network-specific error conditions.

---

## 4. Conformance Requirements

These keyword definitions apply to all normative text in this repository and all documents published under the Beckn Protocol v2 governance model. Editors MUST use these words consistently and in uppercase when expressing normative requirements.

---

## 5. References

- [RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels](https://datatracker.ietf.org/doc/html/rfc2119)
- [RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words](https://datatracker.ietf.org/doc/html/rfc8174)
- [GOVERNANCE.md](../GOVERNANCE.md)

---

## 6. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | 2023-09-01 | Ravi Prakash | Initial draft (BECKN-010 in v1.x) |
| Draft-02 | 2026-02-01 | — | Updated for v2 governance model; added RFC 8174 alignment; added examples |
