# Keyword Definitions

## 1. Document Details
- **ID:** NFH-002
- **Status:** PUBLISHED
- **Authors:** 
  - **[Ravi Prakash, V](https://github.com/ravi-prakash-v)**, [Networks for Humanity](https://github.com/Networks-for-Humanity)
- **Created:** 27th April, 2026
- **Updated:** 27th April, 2026
- **Version history:** Repository history on `main` does not yet show commits for this file
- **Latest editor's draft:** Click [here](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Keyword_Definitions.md)
- **Implementation report:** Informative RFC; no standalone implementation report required.
- **Stress test report:** -NA-
- **Conformance impact:** -NA-
- **Security/privacy implications:** -NA-
- **Replaces / relates to:** -NA-
- **Feedback:** Issues Click [here](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%NFH-002%22), discussions Click [here](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-003%22), pull requests Click [here](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-003%22).
- **Errata:** -NA-

## 2. Abstract

This document outlines the normative definitions of keywords that are commonly used in technical specifications, standards, and protocols. The aim is to provide a uniform interpretation of these terms to avoid ambiguity and misinterpretation.

## 3. Table of Contents

- [Keyword Definitions](#keyword-definitions)
  - [1. Document Details](#1-document-details)
  - [2. Abstract](#2-abstract)
  - [3. Table of Contents](#3-table-of-contents)
  - [4. Introduction](#4-introduction)
  - [5. Definitions](#5-definitions)
    - [MUST](#must)
    - [MUST NOT](#must-not)
    - [REQUIRED](#required)
    - [SHALL](#shall)
    - [SHALL NOT](#shall-not)
    - [SHOULD](#should)
    - [SHOULD NOT](#should-not)
    - [RECOMMENDED](#recommended)
    - [MAY](#may)
    - [OPTIONAL](#optional)
  - [Examples and Correct Usage](#examples-and-correct-usage)
    - [Example 1: Using "REQUIRED" and "MUST"](#example-1-using-required-and-must)
    - [Example 2: Using "RECOMMENDED" and "SHOULD"](#example-2-using-recommended-and-should)
  - [Conclusion](#conclusion)
  - [6. Conclusion](#6-conclusion)
  - [7. Acknowledgements](#7-acknowledgements)
  - [8. References](#8-references)

## 4. Introduction

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described below. These definitions aim to ensure that the terms are understood precisely and consistently to avoid confusion in the interpretation of standards, specifications, and protocols.
## 5. Definitions

### MUST

The term "MUST" implies an absolute requirement.

### MUST NOT

The term "MUST NOT" indicates an absolute prohibition.

### REQUIRED

The term "REQUIRED" is synonymous with "MUST".

### SHALL

The term "SHALL" is equivalent to "MUST".

### SHALL NOT

The term "SHALL NOT" is equivalent to "MUST NOT".

### SHOULD

The term "SHOULD" indicates a strong recommendation.

### SHOULD NOT

The term "SHOULD NOT" indicates a strong recommendation against.

### RECOMMENDED

The term "RECOMMENDED" is synonymous with "SHOULD".

### MAY

The term "MAY" indicates that an item is truly optional.

### OPTIONAL

The term "OPTIONAL" is synonymous with "MAY".

## Network Actor Definitions

The following terms identify the principal actors and infrastructure components of the Beckn Protocol. These definitions apply across all Beckn Protocol RFCs unless explicitly qualified otherwise.

### BAP (Beckn Application Platform)

A software platform that initiates value-exchange transactions on behalf of a user or agent by invoking Beckn Protocol APIs. The BAP is the caller in all stateless transaction endpoints and receives callback responses from the BPP.

### BPP (Beckn Provider Platform)

A software platform that receives transaction requests from a BAP, processes them, and responds via callback endpoints. The BPP is the implementer of all stateless transaction endpoints and produces the canonical response objects — such as `Catalog` and `Contract` — that are consumed by the BAP.

### NFH (Networks for Humanity Foundation)

The foundation that governs, hosts, and evolves the Universal Value-exchange Fabric. NFH publishes the canonical Beckn Protocol Specification and operates the shared infrastructure that Beckn network participants connect to.

### Fabric

The Universal Value-exchange Fabric, hosted by the Networks for Humanity Foundation. The Fabric provides shared infrastructure — including the Discovery Service, Registry, and catalog infrastructure — through which BAPs and BPPs discover each other, establish trust, and coordinate transactions.

### Discovery Service (DS)

A Fabric-hosted service that indexes BPP catalogs and responds to discovery requests from BAPs. The Discovery Service enables catalog-first discovery without requiring BAPs to query BPPs directly at runtime.

### Registry

A Fabric-hosted service that maintains the authoritative list of network participants (BAPs and BPPs), their signing keys, and their callback URIs. The Registry is used to validate the identity and authorisation of participants in a Beckn network.

## Examples and Correct Usage

In this section, we provide examples that demonstrate the correct usage of the key words defined in this document. The examples are related to a hypothetical Beckn Application Platform (BAP) that interacts with a Beckn Provider Platform (BPP) using beckn protocol APIs.

### Example 1: Using "REQUIRED" and "MUST"

- REQUIRED. The BPP MUST implement the `search` endpoint to receive an `Intent` object sent by BAPs.
- REQUIRED. The BPP MUST return a catalog of products on the `on_search` callback endpoint specified in the `context.bpp_uri` field of the `search` request body.
- REQUIRED. Any provider-related information like `name`, `logo`, `short_desc` MUST be mapped to the `Provider.descriptor` schema.
- REQUIRED. If the BPP does not want to respond to a `search` request, it MUST return an `ack.status` value equal to `NACK`.

### Example 2: Using "RECOMMENDED" and "SHOULD"
- RECOMMENDED. Upon receiving a `search` request, the BPP SHOULD return a `Catalog` that best matches the `Intent`. This can be done by indexing the catalog against the various probable paths in the `Intent` schema relevant to the use case.

## Conclusion

The definitions provided in this document are intended to clarify the interpretation of key terms used in technical specifications, standards, and protocols. Adherence to these definitions will ensure a consistent understanding and implementation of such documents.

> Note : This document is subject to change and may be updated to include additional terms or to refine existing definitions.

## 6. Conclusion

The Beckn protocol stack provides a consistent implementation model by separating networking, trust, structural data validation, semantic interpretation, policy enforcement, and application behavior into explicit layers. Future standardization work may still be useful for formal actor capability profiles and policy-layer conformance profiles across networks, but these questions do not change the stack definition established here.

## 7. Acknowledgements

This RFC reflects contributions from Beckn Protocol contributors who developed and reviewed the architecture, interoperability, and trust-model guidance represented in this stack description.

## 8. References

- Click [here](./00_Keyword_Definitions.md)
- Click [here](../api/v2.0.0/beckn.yaml)
- Click [here](https://docs.beckn.io/introduction-to-beckn/beckn-protocol)
- Click [here](https://docs.beckn.io/introduction-to-beckn/fabric-the-value-exchange-infrastructure)
