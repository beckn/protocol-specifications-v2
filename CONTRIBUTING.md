# Contributing to Beckn Protocol Specifications v2

This document defines how contributors should propose, discuss, implement, and submit changes to Beckn API and schema artifacts.

---

## 1. Contribution principles

All contributions should be:
- interoperability-first,
- semantic-first (not structure-only),
- testable,
- migration-conscious,
- security-aware,
- and aligned with repository governance.


### 1.1 Interoperability evolution policy

Contribution review now prioritizes **semantic interoperability** over purely structural interoperability.

Before proposing new schema structures, contributors MUST check [schema.beckn.io](https://schema.beckn.io) for existing use-case-specific schemas and prefer extension/contribution there.


Before opening implementation work, read:
- [`GOVERNANCE.md`](./GOVERNANCE.md)
- [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md)

---

## 2. Contribution flow

1. Start with a Discussion.
2. Build consensus.
3. Create an Issue.
4. Wait for PWG legitimacy confirmation.
5. Raise PR to `draft` (never directly to `main`).

---

## 3. Issue creation guideline

### 3.1 Before opening an Issue

- Link to an existing Discussion.
- Confirm consensus exists to move to Issue.
- Confirm design-principle checks were considered.

### 3.2 Required fields in every Issue

- **Title** (clear and implementation-oriented)
- **Problem statement**
- **Scope** (`api`, `schema`, or both)
- **Current behavior**
- **Proposed change**
- **Conformance impact** (`hotfix`, `patch`, `minor`, `major`)
- **Backward compatibility** (compatible or breaking)
- **Migration notes**
- **Security/privacy impact**
- **Test plan**
- **Design-principle check**
- **Linked Discussion URL**

### 3.3 Suggested labels

- `area:api`
- `area:schema`
- `type:hotfix` / `type:patch` / `type:minor` / `type:major`
- `needs-pwg-review`

### 3.4 When an Issue becomes implementation-ready

An Issue is implementation-ready only after PWG confirms legitimacy and scope.

---

## 4. Branch and PR rules

- Contributors MUST target `draft`.
- Contributors MUST NOT open direct merge PRs to `main`.
- PR descriptions should include: compatibility impact, test evidence, and migration notes.

---

## 5. Quality checklist for contributors

Before requesting review, confirm:

- [ ] API/schema changes are logically consistent with existing contracts
- [ ] Conformance impact is correctly classified
- [ ] Security/privacy impact is explicitly stated
- [ ] Examples/tests are updated
- [ ] Links/references are updated
- [ ] Change aligns with design principles in governance

---

## 6. Conduct expectations

Contributors must follow [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md).

Contributors must not pressure the working group to force a merge.
