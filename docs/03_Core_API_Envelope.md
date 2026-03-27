# Core API Envelope (v2.0.0)
## CWG Working Draft - 2026-03-27

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-27 | Migrated to v2 RFC template structure |

## 1.2 Latest editor's draft
- ./03_Core_API_Envelope.md

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
  - [1. Normative source](#1-normative-source)
  - [2. Envelope shape](#2-envelope-shape)
  - [3. Context requirements](#3-context-requirements)
  - [4. Message requirements](#4-message-requirements)
  - [5. Ack contract](#5-ack-contract)
  - [6. Response contract](#6-response-contract)
  - [7. Endpoint-action coupling](#7-endpoint-action-coupling)
  - [8. v2.0.0 profile note](#8-v200-profile-note)
<!-- TOC END -->

# 2. Context

## 1. Normative source

The machine-verifiable transport contract is defined in:
- ../api/v2.0.0/beckn.yaml

This document summarizes the envelope semantics that all participants must follow.

## 2. Envelope shape

Every protocol call uses:
- context
- message

Callbacks additionally bind request/response lineage through callback semantics defined in the schema set.

## 3. Context requirements

Context is mandatory and includes:
- action
- version (2.0.0)
- messageId
- transactionId
- timestamp
- participant identity and URIs required for routing/auth

## 4. Message requirements

message carries action payload typed by the corresponding action schema. The payload semantics are action-specific (discover/select/init/... and catalog extension actions).

## 5. Ack contract

Ack is not just delivery confirmation. It includes CounterSignature for non-repudiation.

## 6. Response contract

Transport-level responses:
- Ack (200)
- AckNoCallback (409)
- NackBadRequest (400)
- NackUnauthorized (401)
- ServerError (500)

## 7. Endpoint-action coupling

Implementations must enforce:
- endpoint and context.action consistency,
- request and callback payload schema alignment,
- action-family lifecycle correctness.

## 8. v2.0.0 profile note

This repository profile is explicit-endpoint based and does not rely on a single path token for all actions.
