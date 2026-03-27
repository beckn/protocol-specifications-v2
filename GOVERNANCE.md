# Beckn Protocol Governance (API and Schema Evolution)

**Status:** Active Draft  
**Scope:** Evolution of Beckn API contracts and schema contracts

---

## 1. Governance intent

This governance model is intentionally simple and is based on one principle:

> Beckn evolves through logical, testable improvements to API and schema contracts while preserving interoperability.

The model applies to:
- API surface evolution (endpoints, transport behavior, request/response contracts)
- Schema evolution (core and extension schema behavior, conformance semantics)
- Release cadence and merge discipline

---

## 2. Design-principle gate (mandatory)

All contributions MUST be tested against design principles before formal review.

At minimum, contributors MUST validate that a change:
1. Improves or preserves interoperability
2. Does not introduce ambiguous semantics
3. Does not regress security/trust assumptions
4. Is migration-conscious (or explicitly breaking with justification)
5. Is implementable and testable in real integrations

If this gate is not satisfied, the contribution is not review-ready.

---

## 3. Simple approval lifecycle

### Step 1 — Start a Discussion
A contributor starts with a GitHub Discussion describing the problem, proposal, and expected API/schema impact.

### Step 2 — Reach Discussion Consensus
When sufficient consensus is reached in Discussion, the contributor creates a formal Issue.

### Step 3 — Issue Review by Protocol Working Group (PWG)
The PWG meets once a month to review open Issues, respond, and comment.

If the PWG verifies the legitimacy and scope of the Issue, it is marked ready for implementation.

### Step 4 — Contributor raises PR to `draft` only
Contributors may then raise a PR **only to `draft`**.

PRs to `main` are not allowed for normal evolution work.

### Step 5 — Core Working Group (CWG) merge cycle
Once every **x months** (as scheduled by CWG), the Core Working Group reviews eligible PRs and performs merge decisions for release progression.

---

## 4. Review cadence by change class

Default cadence by urgency and version impact:

- **Hotfixes:** PWG/CWG review on an as-needed basis
- **Patch updates:** working group review once every 2 weeks
- **Minor updates:** working group review once every 2 months
- **Major updates:** working group review once every 6 months

These cadences guide planning and expectations; WG may adjust sequencing for release risk management.

---

## 5. Working group interaction norms

- WG may invite contributors to review meetings when clarification is needed.
- Meeting invites do not guarantee merge; they are clarification channels.
- Review outcomes must be documented in the associated Issue/PR thread.

---

## 6. Branching and merge policy

- Contributors implement against `draft`.
- Direct contributor merges to `main` are not part of the normal process.
- `main` reflects approved and release-managed integration outcomes.

---

## 7. Required repository artifacts

Contributors MUST follow:
- [`CONTRIBUTING.md`](./CONTRIBUTING.md)
- [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md)

---

## 8. Enforcement

Contributions that bypass process, skip design-principle validation, or violate conduct rules may be closed or deferred without merge.
