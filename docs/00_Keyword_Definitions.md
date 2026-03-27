# Keyword Definitions for Technical Specifications
## CWG Working Draft - 2026-03-27

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-27 | Migrated to v2 RFC template structure |

## 1.2 Latest editor's draft
- ./00_Keyword_Definitions.md

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
- https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-029%22

### 1.7.2 Discussions
- https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-029%22

### 1.7.3 Pull Requests
- https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-029%22

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
  - [1. Introduction](#1-introduction)
  - [2. Definitions](#2-definitions)
    - [MUST](#must)
    - [MUST NOT](#must-not)
    - [SHOULD](#should)
    - [SHOULD NOT](#should-not)
    - [MAY](#may)
  - [3. Usage Examples](#3-usage-examples)
    - [Example 1 — MUST and REQUIRED](#example-1-must-and-required)
    - [Example 2 — SHOULD and RECOMMENDED](#example-2-should-and-recommended)
    - [Example 3 — MAY and OPTIONAL](#example-3-may-and-optional)
  - [4. Conformance Requirements](#4-conformance-requirements)
  - [5. References](#5-references)
  - [6. Changelog](#6-changelog)
<!-- TOC END -->

# 2. Context

**Status:** Released  
**Author(s):** Ravi Prakash (Beckn Labs)  
**Created:** 2023-09-01  
**Updated:** 2026-02-01  
**Conformance impact:** Informative  
**Security/privacy implications:** No security or privacy implications identified.  
**Replaces / Relates to:** Adapted from BECKN-010 (legacy pre-v2). Aligned with [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) and [RFC 8174](https://datatracker.ietf.org/doc/html/rfc8174).

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

> RECOMMENDED. Upon receiving a `discover` request, the DS SHOULD return a `Catalog` that best matches the `Intent` in the request.

> Participants SHOULD cache registry lookup results for the duration of the key's validity period.

### Example 3 — MAY and OPTIONAL

> The DS MAY support synchronous (non-callback) responses for `discover` requests, subject to network policy.

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
| Draft-01 | 2023-09-01 | Ravi Prakash | Initial draft (BECKN-010 in legacy pre-v2) |
| Draft-02 | 2026-02-01 | — | Updated for v2 governance model; added RFC 8174 alignment; added examples |
