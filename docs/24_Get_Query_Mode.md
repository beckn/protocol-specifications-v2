# legacy GET Query mode Note
## CWG Working Draft - 2026-03-27

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-27 | Migrated to v2 RFC template structure |

## 1.2 Latest editor's draft
- ./24_Get_Query_Mode.md

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
  - [Status in this repository profile](#status-in-this-repository-profile)
  - [Why this note exists](#why-this-note-exists)
  - [Implementation guidance](#implementation-guidance)
  - [Migration guidance from old drafts](#migration-guidance-from-old-drafts)
<!-- TOC END -->

# 2. Context

## Status in this repository profile

The current v2.0.0 API profile in this repository is defined by explicit action-specific POST endpoints in:
- ../api/v2.0.0/beckn.yaml

legacy GET Query mode is not part of the normative transport surface in this profile.

## Why this note exists

Earlier drafts discussed body-less URL-driven transport variants. This document is retained as historical guidance context only.

## Implementation guidance

For conformance to the current profile:
- use signed POST requests to the declared action endpoints,
- use asynchronous callback endpoints for business responses,
- use Ack/CounterSignature transport semantics from the core schema.

## Migration guidance from old drafts

If an implementation previously supported legacy GET Query mode:
- treat it as non-normative extension,
- keep it behind network policy controls,
- do not claim baseline v2.0.0 conformance on legacy GET Query mode support alone.
