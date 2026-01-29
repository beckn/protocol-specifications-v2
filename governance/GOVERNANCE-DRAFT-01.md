# Beckn Protocol Governance Model (2.x)

**Status:** Draft  
**Applies to:** Beckn Protocol (Core), Domain Specifications, and Network Profiles built on Beckn

---

## 0. Notice

This document is part of the **Governance Model of the Beckn Protocol** and is the **highest-precedence governance artifact** for specification evolution and interpretation.

All other documents (e.g., attribution guidelines, contribution guidelines, style guide, domain charters, network publishing guides, implementation guides) are **derived artifacts**.

When any derived artifact conflicts with this document, **this document prevails**.

## 1. Purpose and non-goals

### 1.1 Purpose

Establish a governance framework that is:

- **Lightweight:** minimal roles and minimal ceremony.
- **Airtight:** unambiguous precedence, decision rules, compatibility rules, and dispute handling.
- **Composable:** explicitly supports the reality of **Core → Domain → Network** evolution without breaking interoperability.

### 1.2 Non-goals

This governance model does not aim to:

- create membership structures, gatekeeping, or bureaucracy;
- force every network to move at the pace of core/domain;
- mandate a single reference implementation as “the” Beckn.

## 2. The Beckn credo (constitutional intent)

Beckn is an open protocol designed to expand interoperable digital commerce and coordination across diverse actors and ecosystems—globally, across domains, and across regions—while preserving agency, choice, and competition.

Governance exists to protect:
- interoperability,
- user and participant safety (security, privacy, consent),
- predictable evolution,
- and the long-term coherence of the protocol.

## 3. Constitutional principles

These principles are the primary basis for approving changes, resolving ambiguity, and interpreting disputes.

### 3.1 Interoperability-first

Any change that reduces interoperability is presumed harmful unless a compelling, globally-relevant justification and migration path exists.

### 3.2 Abstraction over specificity

Core remains domain-agnostic. Domain and network specificity belongs in the appropriate layer.

### 3.3 Optimal ignorance

If a feature is not required to achieve interoperability, it should not be standardized in the core. Prefer extension mechanisms and profiles when feasible.

### 3.4 Security by design

Changes must not introduce avoidable security vulnerabilities, ambiguity around trust, or unsafe defaults.

### 3.5 Privacy and consent by default

Changes must not weaken privacy expectations or expand data collection without explicit, scoped rationale and safeguards.

### 3.6 Scalability neutrality

The protocol should remain viable across scales—from small deployments to large ecosystems—without requiring centralized control.

### 3.7 Reusability before novelty

Prefer general patterns that can be reused across domains and regions over one-off solutions.

### 3.8 Unification over forced standardization

Aim to unify patterns and meaning while allowing diversity through profiles and extensions, instead of imposing rigid, premature uniformity.

### 3.9 Dependency over duplication (2.x emphasis)

Prefer **upstream dependencies** (versioned references, overlays, profiles) over copying, forking, and rebranding upstream content. This reduces drift and preserves interoperability.

### 3.10 Automation-first governance (2.x emphasis)

If a rule can be validated, it should be enforced through tooling/CI rather than social process.

## 4. Scope and layering (Core → Domain → Network)

### 4.1 Core

The global, domain-agnostic protocol contract: verbs, baseline schemas, semantics, normative behaviors, and conformance rules.

### 4.2 Domain

Domain specializations: domain vocabulary bindings, domain IGs, domain-level conformance guidance, and recommended workflows.

### 4.3 Network

Network-specific constraints and additions: regional policy requirements, identifiers, compliance constraints, stricter validation rules, and network-specific implementation guidance.

**Key constraint:** Network rules MUST NOT silently alter core semantics. Networks may constrain (be stricter than) the domain/core, but must not contradict core conformance.

## 5. Artifact hierarchy and precedence

### 5.1 Normative vs informative

- **Normative** text uses MUST/SHOULD/MAY and defines conformance.
- **Informative** text includes examples, diagrams, tutorials, and explanatory material unless explicitly declared normative.

### 5.2 Precedence order (highest → lowest)

1. **Governance Model (this document)**
2. **Core Specification (normative sections)**
3. **Domain Charters and Domain Specifications (normative sections)**
4. **Network Profiles and Network Conformance Rules (normative within that network)**
5. **Implementation Guides, examples, tutorials (informative unless declared normative)**

### 5.3 Conflict handling

If two artifacts conflict:
1) follow precedence order;  
2) if still ambiguous, apply **constitutional principles**;  
3) final interpretation authority lies with the **Core Stewardship Council** (Section 6).

## 6. Roles (minimal and accountable)

### 6.1 Core Stewardship Council (CSC)

**Mandate:** protect constitutional principles and decide final interpretations.

**Responsibilities:**
- approve governance amendments;
- appoint and remove Editors;
- arbitrate disputes escalated beyond Editors;
- ratify major releases (as defined in Section 9);
- publish binding interpretations when ambiguity arises.

**Size:** 5 stewards (default), adjustable only by governance amendment.

**Term:** 2 years, rolling/staggered when possible.

**Transparency:** all decisions must be documented publicly with rationale, except sensitive disclosures (Section 11).

### 6.2 Editors

**Mandate:** maintain coherence and quality of the specification.

**Responsibilities:**
- merge changes that meet requirements;
- ensure changelogs, migration notes, and conformance impact are included;
- enforce process gates and CI requirements;
- maintain release readiness and documentation hygiene.

### 6.3 Release Captain (per release)

Time-bounded role responsible for:
- coordinating release checklist completion;
- publishing release artifacts;
- ensuring validation and migration material is complete.

### 6.4 Domain Stewards (per domain)

Domains follow this governance model, adapted through a **Domain Charter** that must remain consistent with this document.

---

## 7. Selection, rotation, and removal (lightweight but real)

### 7.1 CSC selection (default mechanism)

- A public call for nominations is opened.
- Nominations must include:
  - statement of intent,
  - relevant experience,
  - disclosure of conflicts of interest (employment, advisory roles, major commercial dependencies).
- The CSC selects candidates via rough consensus; if contested, a 2/3 CSC vote applies.
- A time-boxed public objection window is provided before finalizing appointments.

### 7.2 Removal

A steward/editor may be removed for:
- sustained inactivity,
- repeated bypassing of governance gates,
- serious misconduct (as defined by the project’s Code of Conduct),
- undisclosed conflicts of interest that materially affect trust.

Removal requires:
- documented rationale,
- an opportunity to respond,
- CSC vote (2/3).

---

## 8. Decision-making

### 8.1 Default: rough consensus + recorded objections

A decision passes when:
- objections are addressed, or
- objections are recorded with rationale and the decision proceeds with documented tradeoffs.

### 8.2 Fallback: time-boxed vote

If consensus stalls:
- Editors or CSC may call a vote with a defined deadline.
- Vote outcomes and rationale must be documented in the issue/PR.

### 8.3 Interpretation authority

When ambiguity exists in the spec:
- Editors attempt resolution using principles;
- unresolved disputes escalate to CSC;
- CSC interpretations are binding until superseded by a release.

---

## 9. Specification change lifecycle (simple, enforceable)

### 9.1 Stages

1. **Proposal** (issue/RFC with use case + motivation)
2. **Draft** (PR with working text/schema + examples)
3. **Candidate** (passes validation + includes migration notes if needed)
4. **Release** (tagged and published)
5. **Deprecated** (sunset clock starts)
6. **Removed** (major versions only)

### 9.2 Minimum requirements for normative changes

Any normative change MUST include:
- clear statement of **conformance impact**;
- **compatibility classification** (patch/minor/major);
- updated or new machine-verifiable examples when applicable;
- security/privacy implications (even if “no impact”, explicitly stated).

### 9.3 Optional maturity labels (for clarity, not ceremony)

Governance tooling MAY use labels such as:
- `proposal`, `draft`, `candidate`, `released`, `deprecated`, `removed`.

---

## 10. Versioning, compatibility, and deprecation

### 10.1 Semantic versioning (SemVer)

- **PATCH**: clarifications, fixes, non-breaking tightening with explicit rationale.
- **MINOR**: backward-compatible additions.
- **MAJOR**: breaking changes, removals, or semantic shifts.

### 10.2 Deprecation policy (airtight rule)

Deprecations MUST specify:
- replacement guidance;
- migration plan (or “no migration possible” with rationale);
- earliest version where removal may occur (MAJOR only).

---

## 11. Core–Domain–Network interaction rules (2.x foundation)

### 11.1 Networks publish profiles, overlays, and extensions—not forks

Networks SHOULD publish:
- **Network Profile**: the subset/constraints of core+domain they adopt, plus stricter validations.
- **Overlays/Addenda**: network-specific guidance layered atop domain IGs.
- **Extensions**: network-specific fields using approved extension containers or namespaces.
- **Pinned dependencies**: exact upstream versions used (core + domain).

### 11.2 Upstreaming classification (fast, explicit)

Changes discovered in networks/domains should be categorized as:
- **Core-candidate** (domain-agnostic, broadly reusable),
- **Domain-candidate** (sector-wide),
- **Network-only** (regional/policy/operational constraints).

### 11.3 Constraint rule

Networks may be **stricter** than domain/core, but must not:
- contradict core semantics,
- redefine core meanings incompatibly,
- claim core conformance while violating core requirements.

---

## 12. Attribution, licensing, and redistribution (constitutional framing)

Attribution and licensing are governance concerns because they affect trust, reuse, and interoperability.

Minimum expectations for derived works:
- preserve upstream license notices;
- include a `NOTICE` artifact listing upstream dependencies and versions;
- ensure documentation sites and compiled outputs visibly credit upstream sources.

(Operational details live in derived “Attribution Guidelines”, which must not conflict with this model.)

---

## 13. Transparency and confidentiality

The process should be transparent by default.

Exceptions:
- sensitive customer/partner information,
- security vulnerabilities prior to coordinated disclosure,
- legal or privacy-sensitive content.

If discussion happens privately, the final decision MUST be published with an anonymized rationale.

---

## 14. Enforcement (automation-first)

To keep governance lightweight and real:

- Normative PRs MUST pass automated validation (schemas, examples, conformance rules) where applicable.
- Editors MUST refuse merges that omit required change metadata.
- Repeated bypassing of gates triggers escalation to CSC.

---

## 15. Amendments to this governance model

Because this document is constitutional:

- Amendments require:
  - written proposal,
  - documented rationale tied to principles,
  - a time-boxed public review window,
  - CSC approval (2/3 minimum).
- Amendment history MUST be maintained in a changelog section or linked artifact.

---

## 16. Derived governance artifacts (registry)

The following documents are derived from (and subordinate to) this model:

- Attribution Guidelines
- Contribution Guidelines
- Style Guide
- Release Guide / Checklist
- Domain Charter Template
- Network Profile Publishing Guide
- Code of Conduct (if adopted)

Each derived document MUST include the Notice statement defined in Section 0.

---

## 17. Key changes from Governance 1.x (summary)

- Governance is now explicitly **constitutional**: precedence and interpretation are formal.
- The **Core → Domain → Network** layering is first-class and rules are explicit.
- Roles are compressed into a minimal set (CSC, Editors, Release Captain, Domain Stewards).
- Change lifecycle is tied to **enforceable gates** (validation + migration + conformance impact).
- Dependency-over-duplication is elevated as a governance principle to reduce drift and preserve interoperability.
- Deprecation and removal rules are formalized (sunset clocks; removal via major versions only).
- Automation-first enforcement is emphasized to reduce human bureaucracy.
